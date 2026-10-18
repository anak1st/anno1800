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
AIRSHIP_OWNERS: tuple[str, ...] = ("库马克", "老奈特")


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
        return Decision(AIRSHIP_OWNERS, "2 飞船")
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

# ---------------------------------------------------------------- 本 mod 的收录范围
# 结构判据：**原版商人卖 / 研究所可研发 / 老奈特可合成**。
# 剧情、活动、战役奖励默认不进池（原版没人卖、不可研发、也不能合成），
# 只有下面这张人工审核名单里的卡例外 —— 逐张确认过、明确要放到商人处出售。
MANUAL_INCLUDES: frozenset[str] = frozenset({
    "112825",  # 纳达斯基司令的军刀（向传奇致敬）
    "113473",  # 纳达斯基的勋章（向传奇致敬）
    "113792",  # 崔老妮的老兵——港口主人霍加斯（向传奇致敬）
    "113799",  # 黑暗中的微光——光明之女苏珊娜（大型展览）
    "113800",  # 全能恶棍与咖啡爱好者——费尔南多·德·法罗（大型展览）
    "114795",  # 女王的黑帝斯号仿制品（救命之恩）
    "116174",  # 特别好拉的滑轮（救命之恩）
    "130777",  # 瓦哈德瑟的古老石板（先知纪念碑的祝福）
    "130937",  # 安贝沙编年史（Legendary，狮子史诗）
    # 第二批：事件/活动/剧情奖励，同样逐张确认
    "110955",  # 莫西尔医生的狂热自由同盟旗帜（无神无主 5——混乱状态）
    "111024",  # 爵士身份宣言（无神无主 5——秩序）
    "137281",  # 黄金表现奖章（Reward Patent / 唐纳·贝德二世）
    "118103",  # 多国语言专家学者拉喜姆（迷人北方—探索）
    "13302",   # 交易经纪商基尔纳博士（市场回忆录）
    "13898",   # 名媛邮票（帕洛玛的贵重包裹）
    "132840",  # 「泡水沃尔特的美酒知性之旅」传单（游客行程）
    "132844",  # 「醉酒大卫的酒厂深度之旅」传单（游客行程）
    "132847",  # 「坎特伯里的乡村行」传单（游客行程）
    "133321",  # 来自女王洋洋洒洒的字条（A Delicious Idea）
    "136203",  # 原本的浴室屏风广告（Reward Patent / 唐纳·贝德二世）
})


def in_mod(card) -> bool:
    """这张卡该不该被本 mod 卖：三个结构判据 + 人工审核名单。"""
    return (bool(card.sell_vanilla) or card.researchable or card.craftable
            or card.guid in MANUAL_INCLUDES)

def mod_plan(index: AssetIndex, cards: dict, names: Names) -> dict[str, tuple[str, ...]]:
    """`{卡 GUID: 挂给哪几家}` —— 收录范围 + 规则归属，一次算好。"""
    wanted = [guid for guid, card in cards.items() if in_mod(card)]
    decisions = plan(index, cards, wanted, names)
    return {guid: decision.merchants for guid, decision in decisions.items()}