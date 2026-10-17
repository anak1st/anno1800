"""`assets.xml` 的流式扫描 —— 全链唯一碰原始游戏数据的地方。

一次扫描（276 MB，约 5 秒）拿到后面所有步骤要用的东西：

    facts       每个资产的轻量档案（模板 / 基类 / 名字 / 区域 / 目标组成员）
    pools       池资产：奖励池成员（`ItemLink` / 子池 / `AssetPool` 的 `<Asset>`）
    cards       物品资产：字段、效果块、配方、DLC、作用目标、`Values` 原文
    production  生产建筑的产线（输入 / 输出 / 需要的作物 / 周期）

**一律真 XML**（lxml 流式 + `huge_tree`）：
  * `</ModOp>` 是 `</ModOps>` 的子串 —— 按行切块会漏最后一块；
  * `<CraftableItem>` 标签存在 ≠ 能合成 —— 空配方写成 `<Item />`，得看 `Product`+`Amount`；
  * 逐元素 `clear()` 会把父节点的子节点一起清掉（早期研发池全空就是它）。
"""

from __future__ import annotations

import time
from pathlib import Path

from lxml import etree

from . import tables
from .model import AssetFacts, AssetIndex, ItemCard, Pool, ProductFacts, Production, RawValues

# 卡的松散字段：结构上散在 `Values` 各处，但取法一样（标签名 → 文本）。
CARD_FIELD_TAGS: tuple[str, ...] = (
    "ScenarioFilter", "ExclusiveGroup", "ItemFilterCategory", "InfoDescription",
    "ItemType", "Rarity", "TradePrice", "Allocation", "LineID", "Icon", "IconFilename",
)

# 摊平 `Values` 时跳过的子树：身份 / 文本 / 引用，不是「效果数值」。
VALUES_SKIP: frozenset[str] = frozenset({
    "Standard", "Text", "Locked", "Item", "ItemEffect", "CraftableItem",
    "Buff", "ScenarioWorkshopItem", "SpecialAction", "Cost", "Object",
    "Selection", "AmbientMoodProvider", "Audio", "Sound",
})


# ---------------------------------------------------------------------- 入口
def scan(path: Path, *, verbose: bool = True) -> AssetIndex:
    """流式扫描 assets.xml，建好索引。"""
    start = time.time()
    facts: dict[str, AssetFacts] = {}
    pools: dict[str, Pool] = {}
    cards: dict[str, ItemCard] = {}
    production: dict[str, Production] = {}
    products: dict[str, ProductFacts] = {}
    buffs: dict[str, RawValues] = {}
    variants: list[ItemCard] = []           # 靠 <BaseAssetGUID> 继承的卡的变体
    total = 0

    for _event, elem in etree.iterparse(str(path), events=("end",), tag="Asset", huge_tree=True):
        if not is_asset_definition(elem):
            continue                        # 池里的成员引用 <Item><Asset>192962</Asset>
        total += 1
        guid = text_of(elem.find("Values/Standard/GUID"))
        raw = read_asset(elem, guid) if guid else None
        release(elem)                       # 读完了就释放，内存才守得住
        if raw is None:
            continue
        facts[guid] = raw.facts
        if raw.pool is not None:
            pools[guid] = raw.pool
        if raw.production is not None:
            production[guid] = raw.production
        if raw.product is not None:
            products[guid] = raw.product
        if raw.buff is not None:
            buffs[guid] = raw.buff
        if raw.card is None:
            continue
        if raw.card.tpl in tables.ITEM_TPL:
            cards[guid] = raw.card
        else:
            variants.append(raw.card)

    inherited = merge_inherited_cards(cards, variants)
    if verbose:
        print(f"  扫 {path.name} {time.time() - start:.1f}s ｜ Asset {total} ｜ 池 {len(pools)}"
              f" ｜ 卡 {len(cards)}（含 {inherited} 张继承）｜ 产线 {len(production)}"
              f" ｜ 商品 {len(products)} ｜ Buff {len(buffs)}")
    return AssetIndex(facts, pools, cards, production, products, buffs)


# ---------------------------------------------------------------------- 单资产
def is_asset_definition(elem) -> bool:
    """区分「资产定义」与「池成员引用」。

    `<Asset>` 在 assets.xml 里是复用标签：`<Item><Asset>192962</Asset></Item>` 只是引用。
    判据 = 定义有自己的 `<Values>`（或 `<Template>`）。
    别对引用元素做 `release()` —— 它嵌在父资产里，清掉等于把父资产的数据抹了。
    """
    return elem.find("Values") is not None or elem.find("Template") is not None


def read_asset(elem, guid: str):
    """读一个 `<Asset>`：轻量档案 + 池定义 + 卡的字段 + 产线。"""
    tpl = elem.findtext("Template", "")
    base = elem.findtext("BaseAssetGUID", "")
    facts = AssetFacts(
        tpl=tpl,
        base=base,
        name=elem.findtext("Values/Standard/Name", ""),
        region=(elem.findtext("Values/Building/AssociatedRegions", "")
                or elem.findtext("Values/Standard/AssociatedRegions", "")),
        members=tuple(texts_of(elem.xpath("Values/ItemEffectTargetPool/EffectTargetGUIDs/Item/GUID"))),
    )
    is_card = tpl in tables.ITEM_TPL or bool(base)
    return RawAssetLike(
        facts=facts,
        pool=read_pool(elem, facts),
        card=read_card(elem, guid, tpl, base, facts.name) if is_card else None,
        production=read_production(elem),
        product=read_product_facts(elem) if tpl == "Product" else None,
        buff=read_values(elem.find("Values")) if tpl.endswith("Buff") else None,
    )


class RawAssetLike:
    """一次扫描的中间结果（只在本模块用）。"""

    __slots__ = ("facts", "pool", "card", "production", "product", "buff")

    def __init__(self, facts, pool, card, production, product=None, buff=None) -> None:
        self.facts = facts
        self.pool = pool
        self.card = card
        self.production = production
        self.product = product
        self.buff = buff


def read_pool(elem, facts: AssetFacts) -> Pool | None:
    """读奖励池 / 资产池的成员关系；不是池就返回 None。"""
    items: list[str] = []
    subpools: list[str] = []
    assets: list[str] = []
    for block in elem.xpath("Values/RewardPool | Values/AssetPool"):
        items += texts_of(block.xpath(".//ItemLink"))
        subpools += texts_of(block.xpath(".//Pool"))
        assets += texts_of(block.xpath(".//Asset"))
    if not (items or subpools or assets):
        return None
    return Pool(name=facts.name, tpl=facts.tpl, items=items, pools=subpools, assets=assets)


def read_card(elem, guid: str, tpl: str, base: str, name: str) -> ItemCard:
    """读一张卡的字段（要遍历整棵子树，所以只对卡调用）。"""
    fields: dict[str, str] = {}
    for node in elem.iter():
        tag = node.tag
        if isinstance(tag, str) and tag in CARD_FIELD_TAGS and tag not in fields:
            fields[tag] = text_of(node)
    return ItemCard(
        guid=guid,
        tpl=tpl,
        base=base,
        name=name,
        en=(elem.findtext("Values/Text/LocaText/English/Text") or "").strip(),
        fields=fields,
        blocks=read_blocks(elem.find("Values")),
        craft_costs=read_craft_costs(elem),
        dlc=texts_of(elem.xpath("Values/Locked/DLCDependency")),
        targets=texts_of(elem.xpath("Values/ItemEffect/EffectTargets/Item/GUID")),
        values=read_values(elem.find("Values")),
        item_set=text_of(elem.find("Values/Item/ItemSet")),
        online_price=text_of(elem.find("Values/Item/TradePriceOnlineCurrency")),
        max_stack=text_of(elem.find("Values/Item/MaxStackSize")),
    )


def read_values(values) -> RawValues:
    """把 `<Values>` 摊平成（相对路径, 文本）；只收叶子，保留文档顺序。"""
    if values is None:
        return RawValues()
    entries: list[tuple[str, str]] = []

    def walk(node, prefix: str) -> None:
        for child in node:
            if not isinstance(child.tag, str):
                continue
            path = prefix + child.tag
            if len(child) == 0:
                text = text_of(child)
                if text:
                    entries.append((path, text))
            else:
                walk(child, path + "/")

    for child in values:
        if not isinstance(child.tag, str) or child.tag in VALUES_SKIP:
            continue
        if len(child) == 0:
            text = text_of(child)
            if text:
                entries.append((child.tag, text))
        else:
            walk(child, child.tag + "/")
    return RawValues(tuple(entries))


def read_blocks(values) -> list[str]:
    """这张卡真的带哪几种效果块（空块 `<X />` 不算）。"""
    if values is None:
        return []
    return [tables.BLOCK_ZH[child.tag] for child in values
            if child.tag in tables.BLOCK_ZH and (len(child) > 0 or text_of(child))]


def read_craft_costs(elem) -> list[dict]:
    """合成配方。必须同时有 `Product` 和 `Amount` —— 空配方写成 `<Item />`。"""
    costs: list[dict] = []
    for item in elem.xpath("Values/CraftableItem/CraftingCosts/Item"):
        product = text_of(item.find("Product"))
        amount = text_of(item.find("Amount"))
        if product and amount.isdigit():
            costs.append({"product": product, "amount": int(amount)})
    return costs


def read_production(elem) -> Production | None:
    """生产建筑的产线：`FactoryBase` 的输入/输出 + 需要的作物 + 周期。"""
    factory = elem.find("Values/FactoryBase")
    if factory is None:
        return None
    cycle = text_of(factory.find("CycleTime"))
    return Production(
        inputs=read_goods(factory, "FactoryInputs"),
        outputs=read_goods(factory, "FactoryOutputs"),
        fertility=text_of(elem.find("Values/Factory7/NeededFertility")),
        cycle=int(cycle) if cycle.isdigit() else 0,
    )


def read_goods(factory, block: str) -> tuple[tuple[str, int], ...]:
    """`FactoryInputs` / `FactoryOutputs` 下的（商品 GUID, 数量）列表。"""
    pairs: list[tuple[str, int]] = []
    for item in factory.xpath(f"{block}/Item"):
        product = text_of(item.find("Product"))
        if product:
            amount = text_of(item.find("Amount"))
            pairs.append((product, int(amount) if amount.isdigit() else 1))
    return tuple(pairs)


def read_product_facts(elem) -> ProductFacts:
    """商品档案：分类 / 基准价 / 公民等级 / 产出区域。"""
    def digits(path: str) -> int:
        text = text_of(elem.find(path))
        return int(text) if text.isdigit() else 0

    return ProductFacts(
        category=text_of(elem.find("Values/Product/ProductCategory")),
        base_price=digits("Values/Product/BasePrice"),
        civ_level=digits("Values/Product/CivLevel"),
        region=text_of(elem.find("Values/Product/AssociatedRegion")),
    )


# ---------------------------------------------------------------------- 继承
def merge_inherited_cards(cards: dict[str, ItemCard], variants: list[ItemCard]) -> int:
    """把 `<BaseAssetGUID>` 变体叠到基础卡上，返回合并了几张。

    变体只写自己要改的（名字、稀有度、配方），模板和装槽靠继承；基类不是卡的忽略。
    """
    inherited = 0
    for variant in variants:
        parent = cards.get(variant.base)
        if parent is None:
            continue
        cards[variant.guid] = merge_card(parent, variant)
        inherited += 1
    return inherited


def merge_card(base: ItemCard, over: ItemCard) -> ItemCard:
    """变体叠到基础卡上：非空字段覆盖，块 / DLC / 目标取并集，模板认基础卡的。"""
    return ItemCard(
        guid=over.guid,
        tpl=base.tpl,
        base=over.base,
        name=over.name or base.name,
        en=over.en or base.en,
        fields={**base.fields, **{key: value for key, value in over.fields.items() if value}},
        blocks=list(dict.fromkeys(base.blocks + over.blocks)),
        craft_costs=over.craft_costs or base.craft_costs,
        dlc=list(dict.fromkeys(base.dlc + over.dlc)),
        targets=list(dict.fromkeys(base.targets + over.targets)),
        values=over.values if over.values.entries else base.values,
        item_set=over.item_set or base.item_set,
        online_price=over.online_price or base.online_price,
        max_stack=over.max_stack or base.max_stack,
    )


# ---------------------------------------------------------------------- 杂项
def text_of(elem) -> str:
    """元素文本，去空白（None 安全）。"""
    return (elem.text or "").strip() if elem is not None else ""


def texts_of(elems) -> list[str]:
    """一组元素的文本，丢掉空的。"""
    return [text for text in (text_of(elem) for elem in elems) if text]


def release(elem) -> None:
    """释放已处理的元素：清空内容 + 删掉处理过的前兄弟节点。"""
    elem.clear()
    parent = elem.getparent()
    if parent is None:
        return
    while elem.getprevious() is not None:
        del parent[0]
