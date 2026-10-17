"""数据模型：扫描出来的原始结构 + 索引查询。

`AssetIndex` 只回答「这是什么、在哪、影响谁、产什么」；解释语义（效果数值、归属）
在 `effects.py` / `rules.py`，写文件在 `database.py`。
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import tables


@dataclass(frozen=True)
class AssetFacts:
    """一个资产的轻量档案（10 万条，字段能省就省）。"""

    tpl: str = ""
    base: str = ""
    name: str = ""
    region: str = ""
    members: tuple[str, ...] = ()       # `ItemEffectTargetPool` 的成员建筑


@dataclass(frozen=True)
class RawValues:
    """`<Values>` 的原文摊平：按文档顺序的（相对路径, 文本）。

    只收叶子节点，路径相对 `Values`（如 `FactoryUpgrade/ProductivityUpgrade/Value`）。
    不解释语义 —— 解释在 `effects.py`，所以加新效果不必回改扫描层。
    """

    entries: tuple[tuple[str, str], ...] = ()

    def get(self, path: str, default: str = "") -> str:
        for key, value in self.entries:
            if key == path:
                return value
        return default

    def all(self, path: str) -> tuple[str, ...]:
        return tuple(value for key, value in self.entries if key == path)

    def items(self, prefix: str) -> list[dict[str, str]]:
        """`prefix/Item/<键>` 分组：按文档顺序，同一个键再次出现就开新组。"""
        marker = prefix.rstrip("/") + "/Item/"
        groups: list[dict[str, str]] = []
        current: dict[str, str] | None = None
        for path, value in self.entries:
            if not path.startswith(marker):
                continue
            key = path[len(marker):]
            if "/" in key:
                continue
            if current is None or key in current:
                current = {}
                groups.append(current)
            current[key] = value
        return groups


@dataclass(frozen=True)
class ProductFacts:
    """商品档案（`Template = Product`，656 个）。"""

    category: str = ""      # 商店分类（指向一个 Text 资产）
    base_price: int = 0
    civ_level: int = 0
    region: str = ""        # 产出区域（内部值）


@dataclass(frozen=True)
class Production:
    """生产建筑的产线。"""

    inputs: tuple[tuple[str, int], ...] = ()      # (商品 GUID, 数量)
    outputs: tuple[tuple[str, int], ...] = ()
    fertility: str = ""                           # 农场需要的作物 GUID
    cycle: int = 0                                # 生产周期（秒）


@dataclass
class ItemCard:
    """一张卡的原始字段 —— 还没套分类规则。"""

    guid: str
    tpl: str
    base: str
    name: str
    en: str
    fields: dict[str, str]
    blocks: list[str]
    craft_costs: list[dict]
    dlc: list[str]
    targets: list[str]
    values: RawValues = field(default_factory=RawValues)
    item_set: str = ""
    online_price: str = ""
    max_stack: str = ""

    @property
    def craftable(self) -> bool:
        """能合成 = 配方里真有材料（空 `<Item />` 不算）。"""
        return bool(self.craft_costs)


@dataclass
class Pool:
    """奖励池 / 资产池：成员是物品、子池或资产。"""

    name: str = ""
    tpl: str = ""
    items: list[str] = field(default_factory=list)
    pools: list[str] = field(default_factory=list)
    assets: list[str] = field(default_factory=list)


class AssetIndex:
    """按 GUID 查资产 + 展开池。"""

    INHERIT_MAX_DEPTH = 8

    def __init__(self, facts: dict[str, AssetFacts], pools: dict[str, Pool],
                 cards: dict[str, ItemCard], production: dict[str, Production] | None = None,
                 products: dict[str, ProductFacts] | None = None,
                 buffs: dict[str, RawValues] | None = None) -> None:
        self.facts = facts
        self.pools = pools
        self.cards = cards
        self.production = production or {}
        self.products = products or {}
        self.buffs = buffs or {}

    # ------------------------------------------------------------------ 字段
    def field(self, guid: str, name: str) -> str:
        """取资产字段；自己没写就沿 `<BaseAssetGUID>` 往上继承。"""
        for _ in range(self.INHERIT_MAX_DEPTH):
            facts = self.facts.get(guid)
            if facts is None:
                return ""
            value = getattr(facts, name)
            if value:
                return value
            guid = facts.base
            if not guid:
                break
        return ""

    def zone(self, guid: str) -> str:
        """资产属于哪个区域（内部值）；船 / 港湾模块这类跨区资产返回空串。

        `Values/Building/AssociatedRegions` 是权威字段；少数没写的按模板后缀和
        内部名补线索（北极的庇护所、安贝沙的消防局属于这种）。
        """
        zone = self.field(guid, "region")
        if zone:
            return zone
        tpl = self.field(guid, "tpl")
        if tpl.endswith(tables.ARCTIC_TPL_SUFFIX) or tables.ARCTIC_NAME_HINT in self.field(guid, "name").lower():
            return tables.ZONE_ARCTIC
        if tpl.endswith(tables.AFRICA_TPL_SUFFIX):
            return tables.ZONE_AFRICA
        return ""

    # ------------------------------------------------------------------ 展开
    def expand_targets(self, guids, seen: frozenset[str] = frozenset()) -> set[str]:
        """作用目标 → 具体建筑。目标组（`ItemEffectTargetPool`）可以套目标组。"""
        out: set[str] = set()
        for guid in guids:
            facts = self.facts.get(guid)
            if facts and facts.members:
                if guid not in seen:
                    out |= self.expand_targets(facts.members, seen | {guid})
            else:
                out.add(guid)
        return out

    def reach(self, roots) -> set[str]:
        """池递归展开到底，返回**所有**碰到过的 GUID（含中间池）。"""
        reached: set[str] = set()
        stack = list(roots)
        while stack:
            guid = stack.pop()
            if guid in reached:
                continue
            reached.add(guid)
            pool = self.pools.get(guid)
            if pool:
                stack += pool.items + pool.pools + pool.assets
        return reached

    def expand_pools(self, roots) -> set[str]:
        """池递归展开到**叶子** —— 只留不是池的 GUID（研发池用这个）。"""
        leaves: set[str] = set()
        seen: set[str] = set()
        stack = list(roots)
        while stack:
            guid = stack.pop()
            if guid in seen:
                continue
            seen.add(guid)
            pool = self.pools.get(guid)
            if pool:
                stack += pool.items + pool.pools + pool.assets
            else:
                leaves.add(guid)
        return leaves

    def pool_names_of(self, guid: str) -> list[str]:
        """这个 GUID 出现在哪些池里（缺稀有度的卡靠它推断 Common）。"""
        return [pool.name for pool in self.pools.values() if guid in pool.items]
