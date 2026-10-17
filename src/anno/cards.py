"""卡牌文档：一张卡一个 JSON（`data/cards/<GUID>.json`）+ 读回用的 `CardView`。

范围由 `temp/card-tables.tsv` 决定（2149 行）；其余字段全部现算：装槽、稀有度、效果、
目标、来源、谁在卖。`CardView` 是给渲染/规则用的轻量视图（不依赖原始 XML）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace

from . import effects, paths, placement, tables, util
from .model import AssetIndex, RawValues
from .texts import Names

# card-tables.tsv 的列名（表里有两个 `Chinese` 列，dict(zip) 取到的是最后一个）
COL_TEMPLATE = "Template"
COL_EN = "English"
COL_INTERNAL = "Name"
COL_ZH = "Chinese"
COL_RARITY = "Rarity"
COL_ALLOCATION = "Allocation"
COL_TYPE = "ItemType"
COL_PRICE = "TradePrice"
COL_LINE_ID = "LineID"
COL_ICON = "Icon"

NONE_SLOT = "none"

# 「任务物件」判据：ItemWithUI 且带这两个动作之一 —— 游戏自己就是这么标的，
# 比按名字猜可靠（被囚禁的动物、可阅读的书、密封信件都是这种）。
QUEST_ACTION_PATHS: tuple[str, ...] = ("/ActionStartQuest", "/ActionTriggerTextBook")


def is_quest_object(values) -> bool:
    """这个 ItemWithUI 是不是「点一下触发任务 / 阅读」的任务物件。"""
    return any(marker in path for path, _value in values.entries for marker in QUEST_ACTION_PATHS)


@dataclass
class CardInputs:
    """装配卡牌文档需要的输入。"""

    rows: dict[str, dict[str, str]]        # 卡表底稿的每一行
    template_slots: dict[str, str]         # templates.xml：模板 -> 默认装槽
    research: set[str]                     # 可研发的卡 GUID
    texts: dict[str, str]                  # 中文文本表


def load_inputs(index: AssetIndex, *, research: set[str] | None = None,
                verbose: bool = True) -> CardInputs:
    """卡牌范围 = 扫描出来的卡（`ITEM_TPL` 模板 + `<BaseAssetGUID>` 继承变体）。

    `research` 是可研发的 GUID 集合；不传就从 `temp\research-cards.txt` 读（兼容旧用法，
    正式流程由 `build_db.py` 现场算好传进来，不依赖那个文件）。
    """
    from . import templates, texts

    zh = texts.load_zh()
    if research is None:
        research = ({line.strip() for line in paths.RESEARCH_CARDS.read_text(encoding="utf-8").split()}
                    if paths.RESEARCH_CARDS.is_file() else set())
    rows = rows_from_index(index, zh)
    if verbose:
        print(f"  卡牌 {len(rows)} 张（模板 + 继承变体，来自扫描）")
    return CardInputs(rows=rows, template_slots=templates.default_slots(), research=research, texts=zh)


def rows_from_index(index: AssetIndex, zh: dict[str, str]) -> dict[str, dict[str, str]]:
    """卡字段从扫描结果来：`ItemCard` 的字段 + `texts_chinese.xml` 的中文名。"""
    return {
        guid: {
            COL_TEMPLATE: card.tpl,
            COL_EN: card.en,
            COL_INTERNAL: card.name,
            COL_ZH: zh.get(guid, ""),
            COL_RARITY: card.fields.get("Rarity", ""),
            COL_ALLOCATION: card.fields.get("Allocation", ""),
            COL_TYPE: card.fields.get("ItemType", ""),
            COL_PRICE: card.fields.get("TradePrice", ""),
            COL_LINE_ID: card.fields.get("LineID", ""),
            COL_ICON: card.fields.get("IconFilename", ""),
        }
        for guid, card in index.cards.items()
    }


# ---------------------------------------------------------------------- 生成
def build_docs(index: AssetIndex, inputs: CardInputs,
               owners: dict[str, dict[str, list[str]]], names: Names) -> dict[str, dict]:
    """`{GUID: 卡片文档}`。`owners` 是 `{GUID: {"vanilla": [商人名], "mod": [商人名]}}`。"""
    docs: dict[str, dict] = {}
    for guid, row in inputs.rows.items():
        docs[guid] = build_one(index, guid, row, inputs, owners.get(guid, {}), names)
    return docs


def build_one(index: AssetIndex, guid: str, row: dict, inputs: CardInputs,
              own: dict[str, list[str]], names: Names) -> dict:
    card = index.cards.get(guid)
    fields = card.fields if card else {}
    template = row.get(COL_TEMPLATE, "")
    allocation = (row.get(COL_ALLOCATION) or fields.get("Allocation", "")).strip()
    if not allocation or allocation.lower() == NONE_SLOT:
        allocation = inputs.template_slots.get(template, "")
    scenario = (fields.get("ScenarioFilter", "") or "").strip()
    dlc = util.dedup(card.dlc) if card else []
    effect = effects.effects(card.values if card else RawValues(), names)
    travel = effects.expedition(card.values) if card else None
    act = effects.action(card.values, names) if card else None
    targets = targets_doc(index, card.targets if card else [], names)
    zh = inputs.texts.get(guid, "") or row.get(COL_ZH, "")
    rarity = (row.get(COL_RARITY, "") or "").strip() or infer_rarity(index, guid)

    quest_object = bool(card and is_quest_object(card.values))
    slots = SimpleNamespace(template=template, zh=zh, en=row.get(COL_EN, ""),
                            internal=row.get(COL_INTERNAL, ""), scenario=scenario,
                            allocation=allocation, rarity=rarity, quest_object=quest_object)
    place = placement.place(slots)
    vanilla = own.get("vanilla", [])
    mod = own.get("mod", [])
    craftable = bool(card.craft_costs) if card else False
    return {
        "id": guid,
        "type": "card",
        "name": {"zh": zh, "en": row.get(COL_EN, ""), "internal": row.get(COL_INTERNAL, "")},
        "summary": effects.summary(effect),
        "template": template,
        "slot": {"id": allocation, "zh": placement.ALLOC_ZH.get(allocation, allocation)},
        "categories": {"big": placement.big_of(place) if place else "", "place": place or ""},
        "rarity": rarity,
        "prices": {"trade": _number(row.get(COL_PRICE, "")),
                   "online": _number(card.online_price if card else "")},
        "stack": _number(card.max_stack if card else ""),
        "dlc": [names.ref(value) for value in dlc],
        "item_set": names.ref(card.item_set) if card and card.item_set else None,
        "scenario": scenario or None,
        "exclusive": fields.get("ExclusiveGroup", "") or None,
        "quest_object": quest_object,
        "blocks": card.blocks if card else [],
        "effects": effect,
        "expedition": travel,
        "action": act,
        "targets": targets,
        "recipe": [{"product": names.ref(cost["product"]), "amount": cost["amount"]}
                   for cost in (card.craft_costs if card else [])],
        "flags": {"researchable": guid in inputs.research,
                  "craftable": craftable and not scenario,
                  "craftable_in_scenario": craftable and bool(scenario),
                  "scenario_only": bool(scenario)},
        "owners": {
            "vanilla": vanilla,
            "mod": mod,
            "in_vanilla_pool": bool(vanilla),
            "in_mod": bool(mod),
        },
        "usage": targets["usage"],
        "world": tables.zones_zh(targets["zones"]) if targets["zones"] else "",
        "line_id": row.get(COL_LINE_ID, ""),
        "icon": row.get(COL_ICON, ""),
        "filter_cat": fields.get("ItemFilterCategory", ""),
        "item_type": row.get(COL_TYPE) or fields.get("ItemType", ""),
        "info_desc": fields.get("InfoDescription", ""),
        "flavor": inputs.texts.get(fields.get("InfoDescription", ""), ""),
    }


def targets_doc(index: AssetIndex, targets: list[str], names: Names) -> dict:
    """作用目标：引用 / 展开建筑 / 区域 / 建筑族 / 按区域分组的用途。"""
    empty = {"refs": [], "buildings": [], "zones": [], "zones_zh": [], "kinds": [], "usage": []}
    if not targets:
        return empty
    refs: list[dict] = []
    usage: dict[tuple[str, ...], list[str]] = {}
    building_ids: set[str] = set()
    for guid in targets:
        facts = index.facts.get(guid)
        refs.append({**names.ref(guid), "kind": "group" if facts and facts.members else "building"})
        expanded = index.expand_targets([guid])
        building_ids |= expanded
        zones = {index.zone(b) for b in expanded}
        key = tuple(zone for zone in tables.ZONE_VALUES if zone in zones)
        usage.setdefault(key, []).append(names.label(guid))

    buildings = []
    for guid in sorted(building_ids, key=util.as_int):
        zone = index.zone(guid)
        buildings.append({**names.ref(guid),
                          "kind": placement.building_kind(index.field(guid, "tpl")),
                          "zone": zone, "zone_zh": tables.ZONE_ZH.get(zone, "")})
    zones = {index.zone(guid) for guid in building_ids} & set(tables.ZONE_VALUES)
    kinds = {placement.building_kind(index.field(guid, "tpl")) for guid in building_ids}
    return {
        "refs": refs,
        "buildings": buildings,
        "zones": [zone for zone in tables.ZONE_VALUES if zone in zones],
        "zones_zh": [tables.ZONE_ZH[zone] for zone in tables.ZONE_VALUES if zone in zones],
        "kinds": sorted(kinds),
        "usage": [{"zones": list(key), "zones_zh": [tables.ZONE_ZH[zone] for zone in key],
                   "names": labels} for key, labels in usage.items()],
    }


def infer_rarity(index: AssetIndex, guid: str) -> str:
    """没写稀有度的卡，按它所在的池推断最低档 `Common`（原版池按稀有度分层）。"""
    return "Common" if any(is_common_pool(name) for name in index.pool_names_of(guid)) else ""


def is_common_pool(name: str) -> bool:
    """池名能不能说明「这是 Common 档」。"""
    if "Uncommon" in name:
        return False
    return "Common" in name or name.endswith(" C") or name.endswith("C/U")


def _number(text: str):
    value = util.number(str(text or "").strip())
    return value


# ---------------------------------------------------------------------- 读回
@dataclass
class UsageGroup:
    """用途分组：影响同一批地区的目标放在一起。"""

    zones: list[str] = field(default_factory=list)
    targets: list[str] = field(default_factory=list)


@dataclass
class CardView:
    """渲染 / 规则用的卡片视图（从 `data/cards/*.json` 读回）。"""

    guid: str
    zh: str = ""
    en: str = ""
    internal: str = ""
    template: str = ""
    dlc: str = ""
    rarity: str = ""
    allocation: str = ""
    scenario: str = ""
    craftable: bool = False
    researchable: bool = False
    in_mod: bool = False
    in_vanilla_pool: bool = False
    sell_mod: list[str] = field(default_factory=list)
    sell_vanilla: list[str] = field(default_factory=list)
    usage: list[UsageGroup] = field(default_factory=list)
    world: str = ""
    info_desc: str = ""
    item_type: str = ""
    place: str = ""
    big: str = ""
    summary: str = ""
    quest_object: bool = False

    @classmethod
    def from_doc(cls, doc: dict) -> CardView:
        name = doc.get("name") or {}
        return cls(
            guid=doc["id"],
            zh=name.get("zh", ""),
            en=name.get("en", ""),
            internal=name.get("internal", ""),
            template=doc.get("template", ""),
            dlc="、".join(item.get("name", "") for item in doc.get("dlc") or []),
            rarity=doc.get("rarity", ""),
            allocation=(doc.get("slot") or {}).get("id", ""),
            scenario=doc.get("scenario") or "",
            craftable=bool((doc.get("flags") or {}).get("craftable")),
            researchable=bool((doc.get("flags") or {}).get("researchable")),
            in_mod=bool((doc.get("owners") or {}).get("in_mod")),
            in_vanilla_pool=bool((doc.get("owners") or {}).get("in_vanilla_pool")),
            sell_mod=[item.get("name", "") for item in (doc.get("owners") or {}).get("mod") or []],
            sell_vanilla=[item.get("name", "") for item in (doc.get("owners") or {}).get("vanilla") or []],
            usage=[UsageGroup(zones=list(group.get("zones") or []),
                              targets=list(group.get("names") or []))
                   for group in doc.get("usage") or []],
            world=doc.get("world", ""),
            info_desc=doc.get("info_desc", ""),
            item_type=doc.get("item_type", ""),
            place=(doc.get("categories") or {}).get("place", ""),
            big=(doc.get("categories") or {}).get("big", ""),
            summary=doc.get("summary", ""),
            quest_object=bool(doc.get("quest_object")),
        )

    # 兼容旧渲染代码的只读属性
    @property
    def sell_names(self) -> list[str]:
        return self.sell_mod or self.sell_vanilla

def attach_mod_owners(docs: dict[str, dict], mod_refs: dict[str, list[dict]]) -> None:
    """把规则算出来的 mod 归属写回卡文档（`owners.mod` / `in_mod`）。

    `mod_refs` 是 `{卡 GUID: [{id, name}]}`，由 `build_db.py` 从 `rules.mod_plan`
    转成商人引用后传进来 —— 因此 data/ 与文档只依赖规则，不依赖 mod 的 XML。
    """
    for guid, refs in mod_refs.items():
        doc = docs.get(guid)
        if doc is None:
            continue
        doc["owners"]["mod"] = refs
        doc["owners"]["in_mod"] = bool(refs)