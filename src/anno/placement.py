"""归类口径：装槽（细类）→ 大类 → 世界。

这里是**我们自己的归类习惯**（哪些细类算建筑、哪些算娱乐），不是游戏事实；
游戏事实（模板、区域、效果块）在 `tables.py`。
"""

from __future__ import annotations

import re

from . import tables

# ---------------------------------------------------------------- 装槽
# 内部名 -> 官方中文（取自游戏 UI 配置 `AllocationText`，不是自造的）。
ALLOC_ZH: dict[str, str] = {
    "GuildHouse": "工会", "TownHall": "市政厅", "HarborOffice": "港务总管办公室",
    "Museum": "博物馆", "Zoo": "动物园", "BotanicGarden": "植物园", "Pavilion": "音乐演奏场",
    "Lodge": "北极小屋", "Dockland": "港湾主要码头", "Headquarter": "总部",
    "BuildPermit": "建筑执照", "Culture": "文化", "RadiusBuilding": "周边建筑",
    # 舰船类：游戏分成「船只（通用）/ 帆船 / 蒸汽船 / 军舰 / 商船」+ 三种特殊船
    "Ship": "船只", "SailShip": "帆船", "SteamShip": "蒸汽船", "Warship": "军舰",
    "Tradeship": "商船", "DivingVessel": "打捞船", "AirShip": "飞船", "AarhantShip": "阿尔罕的船",
}

# 模板分组。前四种在 templates.xml 里有默认装槽，正常轮不到这里，只是兜底。
MULTI_TPL = frozenset({"GuildhouseItem", "TownhallItem", "HarborOfficeItem", "ShipSpecialist"})
NO_SLOT_TPL = frozenset({"ItemWithUI", "ItemWithUICrafting"})
QUEST_TPL = frozenset({"QuestItem", "QuestItemMagistrate"})
DROP_TPL = frozenset({"ScenarioWorkshopItem", "FluffItem"})
EXCLUSIVE_ALLOC = frozenset({"AarhantShip", "Headquarter"})   # 战役专属装槽 → 任务道具

# ---------------------------------------------------------------- 展示顺序
PLACE_ORDER: list[str] = [
    "市政厅", "工会", "港务总管办公室", "建筑执照",
    "博物馆", "植物园", "音乐演奏场", "文化藏品（展馆未定）",
    "北极小屋",
    "船只", "帆船", "蒸汽船", "军舰", "商船",
    "打捞船", "飞船", "阿尔罕的船", "载具",
    "多用途专家", "任务道具", "地图 / 探险点", "黑胶唱片", "无装槽的其他物品", "剧本专用",
]
RAR_ORDER: list[str] = ["Legendary", "Epic", "Rare", "Uncommon", "Common", "Quest",
                        "Narrative", "（无稀有度）"]

# 顶层大类：在细类之上再包一层
BIG_ORDER: list[str] = ["建筑", "载具", "娱乐", "其他"]
BIG_OF: dict[str, str] = {
    "市政厅": "建筑", "工会": "建筑", "港务总管办公室": "建筑", "北极小屋": "建筑",
    "建筑执照": "建筑", "总部": "建筑", "港湾主要码头": "建筑", "多用途专家": "建筑",
    "船只": "载具", "帆船": "载具", "蒸汽船": "载具", "军舰": "载具", "商船": "载具",
    "打捞船": "载具", "飞船": "载具", "阿尔罕的船": "载具", "载具": "载具",
    "博物馆": "娱乐", "动物园": "娱乐", "植物园": "娱乐", "音乐演奏场": "娱乐",
    "文化藏品（展馆未定）": "娱乐",
}

# ---------------------------------------------------------------- ItemWithUI 名字分流
RE_MAP = re.compile(r"地图|藏宝|探险|素描本|Map|Lair|Abyss|Portal|Gates|Pit|Nest|"
                    r"Wreck|Reef|Trench|Skirmish|Incursion|Battlesite|Outpost|Estate|"
                    r"Camp|Ruins|Temple|Pyramid|Palace|Baiea|Paititi|Hyperborea|"
                    r"Megalodon|Jormungandr|Gukulmatz|Kraken|Clipper|Vault", re.I)
RE_VINYL = re.compile(r"黑胶|唱片|Vinyl", re.I)
RE_BLUEPRINT = re.compile(r"蓝图|配方|设计图|Blueprint|Schematic|Recipe", re.I)
RE_LETTER = re.compile(r"信|笔记|日记|清单|报告|纪录|名册|文档|文件|日志|日志簿|史诗|"
                       r"协议|自白|确认书|规则|提示|草稿|剪贴板|"
                       r"Letter|Note|Diary|Journal|List|Report|Registry|Document|"
                       r"Chronicle|Manifest|Confession|Treaty|Records|Logbook", re.I)
RE_CRATE = re.compile(r"货箱|废弃物|Crate|Scrap|Goods|Brigade", re.I)

# 建筑族：用于把「模板」翻成「这是什么建筑」（卡牌目标、建筑文档共用）
BUILDING_KINDS: tuple[tuple[str, str], ...] = (
    ("ResidenceBuilding", "residence"), ("FarmBuilding", "farm"), ("RecipeFarm", "farm"),
    ("Factory", "factory"), ("Multifactory", "factory"), ("SlotFactory", "factory"),
    ("HeavyFactory", "factory"), ("FreeArea", "factory"), ("Mine", "mine"),
    ("Powerplant", "power"), ("Culture", "culture"), ("Mall", "shop"), ("Restaurant", "shop"),
    ("Harbor", "harbor"), ("Warehouse", "storage"), ("Dockland", "harbor"),
    ("PublicService", "service"), ("CityInstitution", "service"), ("WarShip", "ship"),
    ("TradeShip", "trade_ship"), ("Airship", "airship"), ("WorkforceConnector", "harbor"),
    ("Ornamental", "decor"),
)


def building_kind(template: str) -> str:
    """模板 → 建筑族（farm / factory / residence / …）。"""
    for prefix, kind in BUILDING_KINDS:
        if template.startswith(prefix):
            return kind
    return "other"


# ---------------------------------------------------------------- 归类
def rarity_of(card) -> str:
    """稀有度；没写的单列「（无稀有度）」。"""
    return (getattr(card, "rarity", "") or "").strip() or "（无稀有度）"


def place(card) -> str | None:
    """卡牌细类；`None` = 不进清单（纯装饰 / 剧本许可物件）。

    规则顺序（先命中先赢）：`ItemWithUI` 名字分流 → 丢弃类 → 剧本专用 →
    `QuestItem` → 战役专属装槽 → 按 `Allocation` / 模板。
    """
    tpl = getattr(card, "template", "") or ""
    zh = getattr(card, "zh", "") or ""
    en = (getattr(card, "en", "") or "") + " " + (getattr(card, "internal", "") or "")
    both = zh + " " + en

    if tpl in NO_SLOT_TPL:
        if RE_MAP.search(both):
            return "地图 / 探险点"
        if RE_VINYL.search(both):
            return "黑胶唱片"
        if RE_BLUEPRINT.search(both) or RE_LETTER.search(both) or RE_CRATE.search(both):
            return "任务道具"
        return "无装槽的其他物品"
    if tpl in DROP_TPL:
        return None
    if (getattr(card, "scenario", "") or "").strip():
        return "剧本专用"
    if tpl in QUEST_TPL:
        return "任务道具"
    allocation = (getattr(card, "allocation", "") or "").strip()
    if allocation in EXCLUSIVE_ALLOC:
        return "任务道具"
    if allocation:
        return ALLOC_ZH.get(allocation, allocation)
    if tpl in MULTI_TPL:
        return "多用途专家"
    if tpl == "CultureItem":
        return "文化藏品（展馆未定）"
    if tpl == "VehicleItem":
        return "载具"
    return "（未分类）"


def big_of(place_name: str) -> str:
    """细类 → 顶层大类；没列到的（任务道具、地图、剧本…）都归「其他」。"""
    return BIG_OF.get(place_name, "其他")


def world_label(zones) -> str:
    """一组区域内部值 → 给读者看的世界标签。"""
    return tables.zones_zh(set(zones))


# ---------------------------------------------------------------- 排序键
def bigkey(place_name: str) -> tuple[int, str]:
    return (BIG_ORDER.index(place_name) if place_name in BIG_ORDER else len(BIG_ORDER), place_name)


def pkey(place_name: str) -> tuple[int, str]:
    return (PLACE_ORDER.index(place_name) if place_name in PLACE_ORDER else len(PLACE_ORDER), place_name)


def rkey(rarity: str) -> tuple[int, str]:
    return (RAR_ORDER.index(rarity) if rarity in RAR_ORDER else len(RAR_ORDER), rarity)
