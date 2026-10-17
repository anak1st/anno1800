"""文档渲染：`docs/cards.md`、`temp/card-profile.tsv`、`temp/merchant-pools.md`。

只读 `data/`（`CardView` / 商人文档），不碰 XML —— 改排版一秒出结果。
"""

from __future__ import annotations

from collections import Counter, defaultdict

from . import paths, placement, tables, util
from .cards import CardView

USAGE_MAX_TARGETS = 3           # 每组最多列几个目标，多的写成「等 N 项」
USAGE_MAX_CHARS = 90
PROFILE_TARGET_MAX = 6


# ---------------------------------------------------------------------- cards.md
def write_cards_doc(cards: dict[str, CardView]) -> None:
    """`docs/cards.md`：大类 → 装槽 → 稀有度，每张卡一行。"""
    place = {guid: placement.place(card) for guid, card in cards.items()}
    tree: dict[str, dict[str, list[CardView]]] = defaultdict(lambda: defaultdict(list))
    for guid, card in cards.items():
        if place[guid] is not None:
            tree[place[guid]][placement.rarity_of(card)].append(card)

    lines: list[str] = []
    write_header(lines, cards, place, tree)
    write_overview(lines, cards, tree)
    write_dlc_table(lines, cards)
    write_big_table(lines, tree)
    write_place_table(lines, tree)
    write_details(lines, tree)
    util.write_lines(paths.CARDS_MD, lines)


def write_header(lines: list[str], cards: dict, place: dict, tree: dict) -> None:
    """抬头：列说明 + 装槽是怎么定的。"""
    total = len(cards)
    kept = sum(len(rarities) for places in tree.values() for rarities in places.values())
    dropped = total - kept
    drop_reason = Counter(card.template for guid, card in cards.items() if place[guid] is None)
    drop_text = "、".join(f"`{tpl}` {count} 张" for tpl, count in drop_reason.most_common())

    lines += [
        "# 卡牌清单",
        "",
        "层级：**大类（建筑 / 载具 / 娱乐 / 其他） → 装槽 → 稀有度**。每张卡一行，列为：",
        "",
    ]
    lines += util.md_table(["列", "含义"], [
        ["`GUID`", "游戏内资产 GUID（唯一键，反查用；`data/cards/<GUID>.json`）"],
        ["中文名", "游戏中文名（取自 `texts_chinese.xml`，按**资产 GUID** 查）"],
        ["DLC", "卡牌 `<Locked><DLCDependency>` 指向的 DLC；没有这个字段的记「本体」"],
        ["Mod", "本 mod 里卖这张卡的商人，多个用 ` + ` 连接；`—` = 本 mod 没有商人卖"],
        ["原版商人", "原版里卖这张卡的商人（只算商人档位池）；两个海盗合并显示为「海盗」"],
        ["合成", "**常规游戏**里可合成 ✅（老奈特工坊）；剧本专用的配方不算（只能在那剧本里造）"],
        ["研发", "研究所可造 ✅ / 不可造 ❌"],
        ["用途", "**这张卡影响哪些地区的什么**：`地区（目标，目标），地区（目标）`。"
                 "地区从卡牌 `EffectTargets` 展开后的建筑区域算，判据见 `docs/game.md` 第 8 节"],
    ])
    lines += ["", "只看装槽，不看这张卡影响什么（一张卡常影响多个建筑，混进来会乱）。", ""]
    lines += ["> 数据来自 `data/`（`build_db.py` 生成，一个资产一个 JSON）。", ""]
    write_slot_section(lines)
    lines += [
        f"**本清单展示全部卡牌**，只排除 {dropped} 张非卡牌物件：{drop_text}。",
        "它们都是战役剧本许可 / 纯装饰，既不在 mod 卡池也不可研发。",
        "",
    ]


def write_slot_section(lines: list[str]) -> None:
    """「装槽怎么定的」一节。"""
    lines += [
        "## 装槽怎么定的",
        "",
        "**优先取卡牌自己声明的 `<Allocation>`；没写就继承 `templates.xml` 里该模板的默认装槽**"
        "【游戏文件】：",
        "",
    ]
    lines += util.md_table(["模板", "默认装槽"], [
        ["`GuildhouseItem`", "工会（`GuildHouse`）"],
        ["`TownhallItem`", "市政厅（`TownHall`）"],
        ["`HarborOfficeItem`", "港务总管办公室（`HarborOffice`）"],
        ["`ShipSpecialist`", "船只（`Ship`）"],
        ["`CultureItem`", "动物园（`Zoo`）"],
        ["`VehicleItem`", "船只（`Ship`）"],
        ["`QuestItem` / `ItemWithUI` / `FluffItem` …", "没有装槽（`None`）"],
    ])
    lines += [
        "",
        "> 这些专家**不是「多用途」**：466 张工会物品、254 张市政厅物品、56 张港务物品、"
        "37 张船只专家各有归属，只是其中很多**同时带远征属性**，看着像哪儿都能装。",
        "",
        "装槽的中文名取自游戏自己的 UI 配置（`assets.xml` 的 `AllocationText`），不是自造的：",
        "",
    ]
    lines += util.md_table(["内部名", "官方中文", "谁在用"], [
        ["`GuildHouse`", "工会", "贸易工会"],
        ["`TownHall`", "市政厅", "市政厅"],
        ["`HarborOffice`", "港务总管办公室", "港务总管办公室"],
        ["`Lodge`", "北极小屋", "航道 DLC"],
        ["`Museum`", "博物馆", "文化展馆"],
        ["`Zoo`", "动物园", "文化展馆"],
        ["`BotanicGarden`", "植物园", "文化展馆"],
        ["`Pavilion`", "音乐演奏场", "文化展馆模块"],
        ["`Ship`", "船只", "**任何船**都能装（通用）"],
        ["`SailShip`", "帆船", "风帆时代"],
        ["`SteamShip`", "蒸汽船", "蒸汽时代"],
        ["`Warship`", "军舰", "军用"],
        ["`Tradeship`", "商船", "民用"],
        ["`DivingVessel`", "打捞船", "沉没的宝藏 DLC"],
        ["`AirShip`", "飞船", "帝国领空 DLC"],
        ["`BuildPermit`", "建筑执照", "战役"],
        ["`AarhantShip`", "阿尔罕的船", "战役"],
    ])
    lines += [
        "",
        "> **舰船是怎么分的**【游戏文件】：每艘船在 `templates.xml` / 资产里声明 `SocketAllocation`，"
        "说明它的槽位能装哪几类物品 —— 帆船 `Ship;SailShip`、风帆军舰 `Ship;SailShip;Warship`、"
        "蒸汽军舰 `Ship;SteamShip;Warship`、蒸汽商船 `Ship;SteamShip;Tradeship`、"
        "打捞船 `Ship;SteamShip;Tradeship;DivingVessel`、飞船 `AirShip`。"
        "所以「时代」和「军民」是两条独立的轴，详见 [`game.md`](game.md) 第 6 节。",
        "",
        "## 几类需要说明的卡",
        "",
    ]
    lines += util.md_table(["归类", "判据"], [
        ["**剧本专用**", "卡牌带 `ScenarioFilter` 字段（指向限定剧本）"],
        ["**任务道具**", "`QuestItem` 模板；`ItemWithUI` 里名字像文档 / 信函 / 史诗 / 蓝图 / 配方 / 货箱的；"
                         "以及只装在战役专属槽位（阿尔罕的船、总部）的东西"],
        ["**无装槽的其他物品**", "`ItemWithUI` / `ItemWithUICrafting` —— 用一下会弹出界面的道具"],
        ["其余", "卡牌自己的 `<Allocation>`，没写就用 `templates.xml` 的模板默认值"],
    ])
    lines += ["", "> 哪些剧本卡算真「专用」由 [`cards-special.md`](cards-special.md) 手工维护。", ""]


def write_overview(lines: list[str], cards: dict, tree: dict) -> None:
    """总览数字。"""
    total = len(cards)
    kept = sum(len(rarities) for places in tree.values() for rarities in places.values())
    quest = sum(len(rarities) for rarities in tree.get("任务道具", {}).values())
    scenario = sum(len(rarities) for rarities in tree.get("剧本专用", {}).values())
    count = lambda key: sum(1 for card in cards.values() if key(card))  # noqa: E731
    both = count(lambda c: c.in_mod and c.sell_vanilla)
    lines += ["## 总览", ""]
    lines += util.md_table(["项", "张数"], [
        ["游戏卡牌总数", str(total)],
        ["已排除（非卡牌物件）", f"-{total - kept}"],
        ["本清单", str(kept)],
        ["Mod 里有名字（本 mod 卖）", str(count(lambda c: c.in_mod))],
        ["原版商人有名字（原版卖）", str(count(lambda c: bool(c.sell_vanilla)))],
        ["↳ 两个都有名字", str(both)],
        ["↳ 只有 Mod 有名字（只靠本 mod）", f"**{count(lambda c: c.in_mod and not c.sell_vanilla)}**"],
        ["↳ 只有原版有名字（本 mod 没放出来）", str(count(lambda c: not c.in_mod and c.sell_vanilla))],
        ["↳ 两个都是 `—`（没有交易商卖）", str(count(lambda c: not c.in_mod and not c.sell_vanilla))],
        ["带 DLC 标记（`DLCDependency`）", str(count(lambda c: bool(c.dlc)))],
        ["其中可合成（老奈特工坊，常规游戏）", str(count(lambda c: c.craftable))],
        ["其中带 `ScenarioFilter`（剧本专用）", str(count(lambda c: bool(c.scenario)))],
    ])
    lines += [
        "",
        f"另外两组容易和「能装槽的卡」混淆：**任务道具** {quest} 张、"
        f"**剧本专用** {scenario} 张。",
        "",
    ]


def write_dlc_table(lines: list[str], cards: dict) -> None:
    """各 DLC 统计。"""
    groups: dict[str, list[CardView]] = defaultdict(list)
    for card in cards.values():
        groups[card.dlc or "本体"].append(card)
    ordered = sorted(groups, key=lambda name: (name == "本体", -len(groups[name]), name))
    lines += ["## 各 DLC 统计", ""]
    lines += util.md_table(["DLC", "张数", "Mod ✅", "原版商人 ✅", "都没有", "研发"],
                           [[name, str(len(groups[name])),
                             str(sum(1 for c in groups[name] if c.in_mod)),
                             str(sum(1 for c in groups[name] if c.sell_vanilla)),
                             str(sum(1 for c in groups[name] if not c.in_mod and not c.sell_vanilla)),
                             str(sum(1 for c in groups[name] if c.researchable))]
                            for name in ordered])
    lines += [""]


def write_big_table(lines: list[str], tree: dict) -> None:
    """各大类统计。"""
    lines += ["## 各大类统计", ""]
    rows = []
    for big in sorted({placement.big_of(place) for place in tree}, key=placement.bigkey):
        records = cards_in(tree, [place for place in tree if placement.big_of(place) == big])
        places = sorted((place for place in tree if placement.big_of(place) == big), key=placement.pkey)
        rows.append([f"**{big}**", str(len(records)), "、".join(places), *summary(records)])
    lines += util.md_table(["大类", "张数", "装槽", "Mod ✅", "原版商人 ✅", "都没有", "研发"], rows)
    lines += [""]


def write_place_table(lines: list[str], tree: dict) -> None:
    """各装槽统计。"""
    lines += ["## 各装槽统计", ""]
    rows = [[place, placement.big_of(place), str(len(cards_in(tree, [place]))),
             *summary(cards_in(tree, [place]))]
            for place in sorted(tree, key=placement.pkey)]
    lines += util.md_table(["装槽", "大类", "总数", "Mod ✅", "原版商人 ✅", "都没有", "研发"], rows)
    lines += [""]


def write_details(lines: list[str], tree: dict) -> None:
    """正文：每个大类 → 每个装槽 → 每个稀有度一张表。"""
    for big in sorted({placement.big_of(place) for place in tree}, key=placement.bigkey):
        places = sorted((place for place in tree if placement.big_of(place) == big), key=placement.pkey)
        records = cards_in(tree, places)
        lines += ["---", "", f"## {big}（{len(records)} 张）", "",
                  f"总数 **{len(records)}** ｜ Mod ✅ **{sum(1 for c in records if c.in_mod)}** ｜ "
                  f"原版商人 ✅ **{sum(1 for c in records if c.sell_vanilla)}** ｜ "
                  f"都没有 **{count_missing(records)}** ｜ "
                  f"可研发 **{sum(1 for c in records if c.researchable)}**", ""]
        lines += util.md_table(["装槽", "张数", "Mod ✅", "原版商人 ✅", "都没有", "研发"],
                               [[place, str(len(cards_in(tree, [place]))), *summary(cards_in(tree, [place]))]
                                for place in places])
        lines += [""]
        for place in places:
            write_place_details(lines, place, tree[place])


def write_place_details(lines: list[str], place: str, rarities: dict) -> None:
    """一个装槽：稀有度统计 + 每个稀有度一张卡表。"""
    records = [card for group in rarities.values() for card in group]
    lines += [f"### {place}（{len(records)} 张）", "",
              f"总数 **{len(records)}** ｜ Mod ✅ **{sum(1 for c in records if c.in_mod)}** ｜ "
              f"原版商人 ✅ **{sum(1 for c in records if c.sell_vanilla)}** ｜ "
              f"都没有 **{count_missing(records)}** ｜ "
              f"可研发 **{sum(1 for c in records if c.researchable)}**", ""]
    lines += util.md_table(["稀有度", "张数", "Mod ✅", "原版商人 ✅", "都没有", "研发"],
                           [[rarity, str(len(rarities[rarity])), *summary(rarities[rarity])]
                            for rarity in sorted(rarities, key=placement.rkey)])
    lines += [""]
    for rarity in sorted(rarities, key=placement.rkey):
        group = sorted(rarities[rarity], key=lambda card: util.as_int(card.guid))
        lines += [f"#### {rarity}（{len(group)} 张）", ""]
        lines += util.md_table(
            ["GUID", "中文名", "DLC", "Mod", "原版商人", "合成", "研发", "用途"],
            [[f"`{card.guid}`", card.zh or "—", card.dlc or "本体",
              sellers(card.sell_mod), sellers(card.sell_vanilla),
              "✅" if card.craftable else "❌", "✅" if card.researchable else "❌",
              usage_cell(card)] for card in group])
        lines += [""]


def sellers(names: list[str]) -> str:
    return " + ".join(names) or "—"


def usage_cell(card: CardView) -> str:
    """用途列：`地区（目标、目标），【地区、地区】（目标）`。没有目标记 `—`。"""
    if not card.usage:
        return "—"
    parts: list[str] = []
    for group in card.usage:
        names = "、".join(group.targets[:USAGE_MAX_TARGETS])
        if len(group.targets) > USAGE_MAX_TARGETS:
            names += f" 等 {len(group.targets)} 项"
        labels = [tables.ZONE_ZH[zone] for zone in group.zones if zone in tables.ZONE_ZH]
        zones = "、".join(labels)
        if len(labels) > 1:
            zones = f"【{zones}】"
        parts.append(f"{zones or tables.ZONE_GENERIC}（{names}）")
    return util.truncate("，".join(parts), USAGE_MAX_CHARS)


def cards_in(tree: dict, places: list[str]) -> list[CardView]:
    return [card for place in places for group in tree[place].values() for card in group]


def summary(records: list[CardView]) -> list[str]:
    return [str(sum(1 for card in records if card.in_mod)),
            str(sum(1 for card in records if card.sell_vanilla)),
            str(count_missing(records)),
            str(sum(1 for card in records if card.researchable))]


def count_missing(records: list[CardView]) -> int:
    return sum(1 for card in records if not card.in_mod and not card.sell_vanilla)


# ---------------------------------------------------------------------- 人看的档案
def write_profile(cards: dict[str, CardView]) -> int:
    """`temp/card-profile.tsv`：一卡一行，效果直接是数值摘要。"""
    header = ["GUID", "中文名", "英文名", "内部名", "Template", "稀有度", "类型",
              "装槽", "效果", "作用目标", "在mod卡池", "所在交易商", "可研发", "特殊任务道具"]
    rows: list[list[str]] = []
    for card in cards.values():
        targets = "、".join(util.dedup(name for group in card.usage for name in group.targets)[:PROFILE_TARGET_MAX])
        rows.append([
            card.guid, card.zh, card.en, card.internal, card.template, card.rarity, card.item_type,
            card.allocation, card.summary, targets,
            "是" if card.in_mod else "否",
            ",".join(card.sell_mod),
            "是" if card.researchable else "否",
            "是" if card.template.startswith("QuestItem") else "否",
        ])
    util.write_tsv(paths.CARD_PROFILE, header, rows)
    return len(rows)


# ---------------------------------------------------------------------- 商人卡池
def write_merchant_pools(traders: dict[str, dict]) -> None:
    """`temp/merchant-pools.md`：本 mod 每家商人卡池多大。"""
    order = [doc for doc in traders.values() if doc.get("mod")]
    rows: list[list[str]] = []
    notes: list[str] = []
    total_entries = total_dup = 0
    all_cards: set[str] = set()
    for doc in sorted(order, key=lambda item: -item["mod"]["entries"]):
        mod = doc["mod"]
        total_entries += mod["entries"]
        total_dup += mod["duplicates"]
        all_cards |= set(mod["cards"])
        rows.append([doc["label"], str(mod["entries"]), str(mod["duplicates"]), str(mod["count"])])
        if mod["duplicates"]:
            notes.append(f"{doc['label']} 池里有 {mod['duplicates']} 条重复")
        if mod["unknown"]:
            notes.append(f"{doc['label']} 池里有 {len(mod['unknown'])} 条 GUID 不在卡表里："
                         + "、".join(mod["unknown"]))
    rows.append(["**合计**", f"**{total_entries}**", f"**{total_dup}**",
                 f"**{len(all_cards)}**（跨商人去重）"])
    lines = [
        "# 各商人卡池大小（本 mod）",
        "",
        "> 由 `build_cards.py` 每次从 `data/` 渲染，**不要手改**。",
        "",
    ]
    lines += util.md_table(["商人", "池内条目", "池内重复", "卡牌（去重）"], rows)
    lines += [
        "",
        "- 「池内条目」是池里 `<ItemLink>` 的条数，「卡牌（去重）」是其中能在卡表里查到的张数"
        "（合计行跨商人去重）。",
        "- 本 mod 只做 7 家商人：布莱克、伊莱、卡希纳、萨曼托、老奈特、库马克、柯提马"
        "（原版还有两个海盗，本 mod 已整体移除）。",
    ]
    lines += [f"- {note}。" for note in notes]
    util.write_lines(paths.MERCHANT_POOLS_MD, lines)
