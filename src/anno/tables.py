"""游戏侧常量表 —— 每张表都能在游戏文件里核对出来。

这里只放**游戏事实**：模板清单、效果块中文、区域、交易商、研发展开、远征枚举。
我们自己的归类/路由习惯在 `placement.py` 与 `rules.py`。
"""

from __future__ import annotations

# ---------------------------------------------------------------- 物品类模板
# 只有这些模板的资产算「卡」；FluffItem / ScenarioWorkshopItem 是装饰和剧本物件。
ITEM_TPL: frozenset[str] = frozenset({
    "GuildhouseItem", "TownhallItem", "CultureItem", "HarborOfficeItem", "ShipSpecialist",
    "VehicleItem", "ItemWithUI", "ItemWithUICrafting", "ActiveItem", "ItemSpecialAction",
    "ItemSpecialActionVisualEffect", "FluffItem", "ScenarioWorkshopItem", "QuestItem",
    "QuestItemMagistrate",
})

# 效果块中文名（`<Values>` 下的块标签）。空块写成 `<X />`，有内容才写 `<X>…</X>`。
BLOCK_ZH: dict[str, str] = {
    "CultureUpgrade": "文化展馆加成", "FactoryUpgrade": "工厂加成", "BuildingUpgrade": "建筑加成",
    "ResidenceUpgrade": "住所加成", "PopulationUpgrade": "人口加成", "ModuleOwnerUpgrade": "模块主人加成",
    "IncidentInfluencerUpgrade": "事件影响力", "IncidentInfectableUpgrade": "事件抗性",
    "EcoSystemProviderUpgrade": "生态系统", "TradeShipUpgrade": "贸易船加成",
    "DivingBellUpgrade": "潜水钟加成", "ShipyardUpgrade": "造船厂加成",
    "IndustrializableUpgrade": "工业化加成", "PassiveTradeGoodGenUpgrade": "被动产出",
    "VisitorHarborUpgrade": "观光港加成", "RepairCraneUpgrade": "修理起重机加成",
    "PierUpgrade": "码头加成", "IrrigationUpgrade": "灌溉加成", "KontorUpgrade": "贸易站加成",
    "VehicleUpgrade": "载具加成", "AttackerUpgrade": "攻击加成", "AttackableUpgrade": "受击加成",
    "HeaterUpgrade": "加热器加成", "PowerplantUpgrade": "发电厂加成", "CraftableItem": "可合成",
    "ExpeditionAttribute": "远征属性", "ItemAction": "使用动作",
}
CRAFT_BLOCK_ZH = BLOCK_ZH["CraftableItem"]

# ---------------------------------------------------------------- 区域
ZONE_MODERATE = "Moderate"
ZONE_COLONY = "Colony01"
ZONE_AFRICA = "Africa"
ZONE_ARCTIC = "Arctic"

ZONE_VALUES: list[str] = [ZONE_MODERATE, ZONE_COLONY, ZONE_AFRICA, ZONE_ARCTIC]   # 固定顺序
ZONE_ZH: dict[str, str] = {
    ZONE_MODERATE: "旧世界", ZONE_COLONY: "新世界", ZONE_AFRICA: "安贝沙", ZONE_ARCTIC: "北极",
}
ZONE_GENERIC = "通用"        # 船、港湾模块这类没有区域的资产
ZONE_ALL = "全区域"          # 四个区域全命中

# 资产没写 AssociatedRegions 时的补救线索
ARCTIC_TPL_SUFFIX = "_Arctic"
AFRICA_TPL_SUFFIX = "_Africa"
ARCTIC_NAME_HINT = "arctic"


def zones_zh(zones) -> str:
    """区域内部值 -> 中文，按固定顺序拼接；空集合记「通用」。"""
    named = [ZONE_ZH[zone] for zone in ZONE_VALUES if zone in zones]
    if len(named) == len(ZONE_VALUES):
        return ZONE_ALL
    return "+".join(named) or ZONE_GENERIC


# ---------------------------------------------------------------- 交易商
# 区块键 = 商人档位池的 GUID（本 mod 的 7 个 replace 用的就是它）。
# 值 = (中文简称, 英文名, 区域内部值)
TRADERS: dict[str, tuple[str, str, tuple[str, ...]]] = {
    "192069": ("布莱克", "Sir Archibald Blake", (ZONE_MODERATE,)),
    "190774": ("伊莱", "Eli Bleakworth", (ZONE_MODERATE,)),
    "192068": ("卡希纳", "Madame Kahina", (ZONE_MODERATE,)),
    "192073": ("萨曼托", "Isabel Sarmento", (ZONE_COLONY,)),
    "193452": ("老奈特", "Old Nate", (ZONE_MODERATE, ZONE_ARCTIC)),
    "193835": ("库马克", "Qumaq", (ZONE_ARCTIC,)),
    "127480": ("柯提马", "Emperor Ketema", (ZONE_AFRICA,)),
    "192070": ("安·哈洛", "Anne Harlow", (ZONE_MODERATE,)),      # 海盗（原版有，本 mod 移出）
    "192071": ("拉福图", "Jean La Fortune", (ZONE_COLONY,)),      # 海盗
}
TRADER_BY_NAME: dict[str, str] = {name: guid for guid, (name, _en, _zone) in TRADERS.items()}
TRADER_ZONE_LABEL: dict[str, str] = {"老奈特": "崔老妮海角 / 北极"}   # 比「旧世界+北极」更贴切
VANILLA_LABEL: dict[str, str] = {"安·哈洛": "海盗", "拉福图": "海盗"}   # 卡表里两个海盗合并显示

# 商人 Profile 资产（`<Values><Trader>` 所在的那个资产）—— 商人文档的 ID 用它
PROFILES: dict[str, tuple[str, str]] = {
    "布莱克": ("45", "Third_party_02 (Archibald Blake)"),
    "伊莱": ("46", "Third_party_07 (Eli Bleakworth)"),
    "卡希纳": ("78", "Third_party_08 (Madame Kahina)"),
    "萨曼托": ("29", "Third_party_05 (Isabel Sarmento)"),
    "老奈特": ("77", "Third_party_06 (Old Nate)"),
    "库马克": ("237", "Third_party_11 (Inuit)"),
    "柯提马": ("119051", "Third_party_13 (Emperor Ketema)"),
    "安·哈洛": ("73", "Third_party_03 (Anne Harlow)"),
    "拉福图": ("76", "Third_party_04 (La Fortune)"),
}

# 原版档位池：每个商人 4~6 个 `RewardItemPool`（档位 → 类别池的入口）
VANILLA_TIERS: dict[str, list[str]] = {
    "布莱克": ["190162", "190163", "190164", "190165", "190166", "192069"],
    "伊莱": ["190167", "190168", "190304", "190305", "190306", "190774"],
    "卡希纳": ["190554", "190555", "190556", "190367", "190387", "192068"],
    "萨曼托": ["190362", "190363", "192072", "192073"],
    "老奈特": ["193447", "193448", "193449", "193450", "193451", "193452"],
    "库马克": ["193830", "193831", "193832", "193833", "193834", "193835"],
    "柯提马": ["127466", "127476", "127477", "127478", "127479", "127480"],
    "安·哈洛": ["190354", "190355", "190356", "190357", "190358", "192070"],
    "拉福图": ["192065", "192066", "192067", "192071"],
}

# ---------------------------------------------------------------- 研发展开
# ResearchSubcategory → 每类的 Low / Medium / High 池（结构：目标组 → 资产池 → 子池 → 物品）
RESEARCH_CATEGORIES: dict[str, tuple[str, tuple[str, str, str]]] = {
    "120301": ("Animals", ("120303", "120304", "120305")),
    "123204": ("Plants", ("123540", "123541", "123542")),
    "123202": ("Artefacts", ("123536", "123537", "123538")),
    "123205": ("ProductionTechnology", ("123545", "123546", "123547")),
    "123209": ("CityTechnology", ("123573", "123574", "123575")),
    "123210": ("HarbourTechnology", ("123576", "123578", "123579")),
    "123212": ("ProductionTalent", ("123676", "123677", "123678")),
    "123214": ("CityTalent", ("123694", "123695", "123696")),
    "123215": ("HarbourTalent", ("123702", "123703", "123704")),
}

# ---------------------------------------------------------------- 远征枚举
EXPEDITION_ATTR_ZH: dict[str, str] = {
    "Might": "力量", "Faith": "信仰", "Hunting": "狩猎", "Crafting": "制作", "Melee": "格斗",
    "Navigation": "航海", "Medicine": "医疗", "Diplomacy": "外交",
    "PerkFemale": "女性", "PerkMale": "男性", "PerkFormerPirate": "前海盗", "PerkDiver": "潜水员",
    "PerkZoologist": "动物学家", "PerkArcheologist": "考古学家", "PerkAnthropologist": "人类学家",
    "PerkMilitaryShip": "军舰特长", "PerkHypnotist": "催眠师", "PerkPolyglot": "语言学家",
    "PerkJackOfAllTraits": "全能", "PerkEntertainer": "艺人",
}
EXPEDITION_DIFFICULTY_ZH: dict[str, str] = {"Easy": "简单", "Average": "平均", "Hard": "困难"}
EXPEDITION_REGION_ZH: dict[str, str] = {
    "NorthernEurope": "北欧", "CentralEurope": "中欧", "SouthernEurope": "南欧",
    "NorthAmerica": "北美", "NorthernNorthAmerica": "北北美",
    "SouthAmerica": "南美", "SouthernSouthAmerica": "南南美",
    "NorthAfrica": "北非", "Africa": "非洲", "Arctic": "北极",
}

# ---------------------------------------------------------------- 使用动作
ITEM_ACTION_ZH: dict[str, str] = {
    "NOACTION": "无动作", "HEAL_INCIDENT": "平息事件", "REPAIR": "修理", "KAMIKAZE": "自毁",
    "CHANNEL": "引导", "BUFF_OTHER": "增益他人", "PLACE_MINE": "布雷",
    "SONARPING": "声呐探测", "ITEM": "使用物品", "SHIELD": "护盾",
}
