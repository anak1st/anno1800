"""按规则决定每张卡挂给谁（规则有序，先命中先赢）。

判定依据全是**游戏文件里的结构**：装槽（`Item/Allocation`）、模板、作用目标的区域。
区域规则只对「不碰旧世界」的卡生效（旧世界没有单一地方商人，是按职能分的）；
跨殖民地的**生产卡**两家都挂（新世界 + 安贝沙 → 萨曼托 + 柯提马），不做二选一。
"""

from __future__ import annotations

from dataclasses import dataclass

from . import placement, tables
from .model import AssetIndex
from .texts import Names

# ---------------------------------------------------------------- 判定用的表
PRODUCTION_TPL: tuple[str, ...] = (
    "FactoryBuilding7", "FarmBuilding", "SlotFactoryBuilding7", "HeavyFactoryBuilding",
    "HeavyFreeAreaBuilding", "Multifactory", "RecipeFarm", "FreeAreaBuilding",
    "FreeAreaRecipeBuilding", "FactoryModuleElectric", "PowerplantBuilding",
    "IrrigationPropagationSource", "Heater", "Resource", "BuffFactory", "Recipe",
)
RESIDENCE_TPL = "ResidenceBuilding"
CULTURE_TPL: tuple[str, ...] = ("CultureBuilding", "CultureModule")
DEFENCE_TPL: tuple[str, ...] = ("WarShip", "HarborBuildingAttacker")
AIRSHIP_TPL: tuple[str, ...] = ("AirshipPlatform",)
SHOP_TPL: tuple[str, ...] = ("Mall", "Restaurant")

SHIP_SLOTS: tuple[str, ...] = ("船只", "蒸汽船", "帆船", "港务总管办公室")
CULTURE_SLOTS: tuple[str, ...] = ("博物馆", "动物园", "植物园", "音乐演奏场", "文化藏品（展馆未定）")
AIRSHIP_WORDS: tuple[str, ...] = ("飞船", "飞艇")        # 飞船月台没有区域字段，只能按名字认

# 娱乐：DLC 新加的展品归当地商人，其余（本体 / 植物园）归萨曼托
CULTURE_DLC_LOCAL: dict[str, str] = {"航道": "库马克", "狮子大地": "柯提马", "沉没的宝藏": "老奈特"}
CULTURE_DEFAULT = "萨曼托"

# 殖民地 → 当地商人。表里的顺序就是规则编号 5 / 6 / 7。
ZONE_MERCHANT: dict[str, tuple[str, str]] = {
    tables.ZONE_AFRICA: ("柯提马", "5 安贝沙"),
    tables.ZONE_ARCTIC: ("库马克", "6 北极"),
    tables.ZONE_COLONY: ("萨曼托", "7 新世界"),
}
COLONY_ORDER: tuple[str, ...] = (tables.ZONE_AFRICA, tables.ZONE_ARCTIC, tables.ZONE_COLONY)

PRODUCTION_OWNER = "伊莱"
POPULATION_OWNER = "卡希纳"
SERVICE_OWNER = "卡希纳"
SHOP_OWNER = "卡希纳"
SHIP_OWNER = "布莱克"
AIRSHIP_OWNER = "库马克"


@dataclass(frozen=True)
class CardTargets:
    """一张卡的作用目标概括：区域 / 名字 / 模板。"""

    zones: frozenset[str]
    names: tuple[str, ...]
    templates: frozenset[str]

    def all_of(self, prefixes: tuple[str, ...]) -> bool:
        """所有目标都属于这些模板家族（没有目标时算 False）。"""
        return bool(self.templates) and all(t.startswith(prefixes) for t in self.templates)

    def any_name(self, words: tuple[str, ...]) -> bool:
        return bool(self.names) and all(any(w in n for w in words) for n in self.names)


@dataclass(frozen=True)
class Decision:
    """这张卡挂到哪几家、依据哪条规则。

    `merchants` 一般是 1 家；跨殖民地的**生产卡**是多家，顺序按规则 5→6→7。
    """

    merchants: tuple[str, ...]
    rule: str

    @property
    def merchant(self) -> str:
        return self.merchants[0]


def targets_of(index: AssetIndex, guid: str, names: Names) -> CardTargets:
    """把 `EffectTargets` 展到底，汇总成区域 / 名字 / 模板。"""
    card = index.cards.get(guid)
    if card is None or not card.targets:
        return CardTargets(frozenset(), (), frozenset())
    buildings = index.expand_targets(card.targets)
    return CardTargets(
        zones=frozenset(zone for zone in (index.zone(b) for b in buildings)
                        if zone in tables.ZONE_VALUES),
        names=tuple(names.label(b) for b in buildings),
        templates=frozenset(t for t in (index.field(b, "tpl") for b in buildings) if t),
    )


def colony_of(targets: CardTargets) -> Decision | None:
    """规则 5–7：殖民地卡 → 当地商人（判不出来返回 None）。

    **只对「不碰旧世界」的卡生效**：旧世界没有单一地方商人，布莱克 / 伊莱 / 卡希纳
    是按职能分的，所以区域规则只管殖民地。

    **生产卡双挂**：目标落到两个殖民地时两家都挂 —— 池 `125109`「所有安贝沙作物农场」
    除了 5 座安贝沙农场还挂着新世界的「庄园辛香料农场」；「安贝沙使节」直接点了
    新世界 4 座工厂 + 安贝沙 3 座农场。非生产卡跨区就交给后面的功能规则。
    """
    zones = targets.zones
    if not zones or tables.ZONE_MODERATE in zones:
        return None
    hit = tuple(zone for zone in COLONY_ORDER if zone in zones)
    if not hit:
        return None
    if len(hit) > 1 and not targets.all_of(PRODUCTION_TPL):
        return None                     # 只有生产卡双挂
    return Decision(tuple(ZONE_MERCHANT[zone][0] for zone in hit),
                    "+".join(ZONE_MERCHANT[zone][1] for zone in hit))


def decide(card, targets: CardTargets) -> Decision | None:
    """按编号规则判这张卡挂给谁；判不出来返回 None。"""
    place = placement.place(card) or ""
    prefix = tuple(CULTURE_TPL) + tuple(SHOP_TPL)

    if place == "军舰" or targets.all_of(DEFENCE_TPL):                       # 1 海军
        return Decision(("布莱克",), "1 海军")
    if place == "飞船" or targets.all_of(AIRSHIP_TPL) or targets.any_name(AIRSHIP_WORDS):   # 2 飞船
        return Decision((AIRSHIP_OWNER,), "2 飞船")
    if place in ("打捞船", "地图 / 探险点"):                                  # 3 打捞 / 探险
        return Decision(("老奈特",), "3 打捞/探险")
    if place in SHIP_SLOTS:                                                 # 4 船 / 港务
        return Decision((SHIP_OWNER,), "4 船/港务")
    colony = colony_of(targets)                                             # 5–7 殖民地
    if colony is not None:
        return colony
    if place in CULTURE_SLOTS or targets.all_of(CULTURE_TPL):               # 8 娱乐
        local = CULTURE_DLC_LOCAL.get(card.dlc)
        return (Decision((local,), f"8 娱乐·{card.dlc}") if local
                else Decision((CULTURE_DEFAULT,), "8 娱乐·本体/植物园"))
    if targets.all_of(PRODUCTION_TPL):                                      # 9 生产
        return Decision((PRODUCTION_OWNER,), "9 生产")
    if targets.all_of((RESIDENCE_TPL,)):                                    # 10 人口
        return Decision((POPULATION_OWNER,), "10 人口")
    if place == "市政厅":                                                   # 11 城市公共服务
        return Decision((SERVICE_OWNER,), "11 城市公共服务")
    if (targets.all_of(prefix) and targets.templates                    # 12 商业餐饮
            and all(t.startswith(SHOP_TPL) for t in targets.templates)):
        return Decision((SHOP_OWNER,), "12 商业餐饮")
    if place == "无装槽的其他物品":                                          # 13 无装槽
        return Decision(("萨曼托",), "13 无装槽")
    return None


def plan(index: AssetIndex, cards: dict, guids, names: Names) -> dict[str, Decision]:
    """给一批卡算归属（`cards` 是 `{GUID: CardView}`）。"""
    result: dict[str, Decision] = {}
    for guid in guids:
        card = cards.get(guid)
        if card is None:
            continue
        decision = decide(card, targets_of(index, guid, names))
        if decision is not None:
            result[guid] = decision
    return result
