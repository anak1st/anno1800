"""本 mod 卡池（`mods/all-items-unlocked/.../assets.xml`）的读 / 排版 / 增删挪。

每个商人一个 `ModOp Type="replace" GUID='…' Path="/Values/RewardPool"`，里面是
`<Item><ItemLink>GUID</ItemLink><Weight>n</Weight></Item>`。`render()` 负责
「读池子 → 按大类两层重排 → 重写抬头注释」，所以任何改动写回后计数都是最新的。

一张卡可以挂多家（跨新世界+安贝沙的生产卡），`apply_assignment` 收 `{GUID: (商人, …)}`。
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass

from lxml import etree

from . import paths, placement, tables, util

# 池 GUID -> (中文简称, 英文名, 区域) —— 与 tables.TRADERS 同一份数据
TRADERS = {guid: (name, en, zones) for guid, (name, en, zones) in tables.TRADERS.items()}
TRADER_BY_NAME: dict[str, str] = {name: guid for guid, (name, _en, _zones) in TRADERS.items()}
UNKNOWN_GROUP = "其他（不在卡表）"

MODOP_RE = re.compile(r'<ModOp Type="(\w+)" GUID=\'(\d+)\' Path="([^"]+)"')
POOL_PATH = "/Values/RewardPool"
INDENT = "\t\t\t\t"
DEFAULT_WEIGHT = "10"


@dataclass
class PoolEntry:
    """池里的一条：GUID + 权重。"""

    guid: str
    weight: str = DEFAULT_WEIGHT


# ---------------------------------------------------------------------- 读
def read_raw() -> str:
    return paths.ALL_ITEMS_ASSETS.read_text(encoding="utf-8")


def read_pools(text: str) -> dict[str, list[PoolEntry]]:
    """`{商人名: [条目]}`，顺序沿用文件里的顺序。"""
    root = etree.fromstring(text.encode("utf-8"))
    pools: dict[str, list[PoolEntry]] = {}
    for modop in root:
        if modop.get("Type") != "replace" or modop.get("Path") != POOL_PATH:
            continue
        guid = modop.get("GUID")
        if guid not in TRADERS:
            continue
        pools[TRADERS[guid][0]] = read_entries(modop)
    return pools


def read_entries(modop) -> list[PoolEntry]:
    """一个商人 `ModOp` 里的所有条目。

    注意：`iter()` 也会吐出注释节点（tag 不是字符串），上游还混用 `<Item>` / `<item>`。
    """
    entries: list[PoolEntry] = []
    for item in modop.iter():
        if not isinstance(item.tag, str) or item.tag.lower() != "item":
            continue
        link = item.find("ItemLink")
        if link is None or not link.text:
            continue
        weight = item.find("Weight")
        entries.append(PoolEntry(link.text.strip(),
                                 (weight.text or DEFAULT_WEIGHT).strip()
                                 if weight is not None else DEFAULT_WEIGHT))
    return entries


def read_assigned(cards: dict) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """读 mod 卡池：返回（只含卡表已知 GUID 的归属，原样条目）。"""
    pools = read_pools(read_raw())
    assigned = {name: sorted({entry.guid for entry in entries if entry.guid in cards},
                             key=util.as_int)
                for name, entries in pools.items()}
    raw = {name: [entry.guid for entry in entries] for name, entries in pools.items()}
    return assigned, raw


def write(text: str) -> None:
    paths.ALL_ITEMS_ASSETS.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------- 改
def drop(pools: dict[str, list[PoolEntry]], guids: set[str]) -> None:
    """从所有池里删掉这些卡。"""
    for name, entries in pools.items():
        pools[name] = [entry for entry in entries if entry.guid not in guids]


def add(pools: dict[str, list[PoolEntry]], trader: str, guids: set[str]) -> None:
    """把卡加进某家（已经在池里的不重复加）。"""
    have = {entry.guid for entry in pools[trader]}
    for guid in sorted(guids - have, key=util.as_int):
        pools[trader].append(PoolEntry(guid))


def move(pools: dict[str, list[PoolEntry]], trader: str, guids: set[str]) -> None:
    """把卡归到某家：先从所有池里删掉，再补进目标池。"""
    drop(pools, guids)
    add(pools, trader, guids)


def apply_assignment(pools: dict[str, list[PoolEntry]], owners: dict[str, tuple[str, ...]]) -> None:
    """按 `{GUID: (商人, …)}` 重排所有池子（`assign` 子命令用）。

    一张卡可以挂多家（跨新世界+安贝沙的生产卡），每家各一条；权重沿用原值。
    """
    weights = {entry.guid: entry.weight for entries in pools.values() for entry in entries}
    members: dict[str, list[str]] = {name: [] for name in pools}
    for guid, wanted in owners.items():
        for owner in wanted:
            members.setdefault(owner, []).append(guid)
    for name, guids in members.items():
        pools[name] = [PoolEntry(guid, weights.get(guid, DEFAULT_WEIGHT))
                       for guid in sorted(guids, key=util.as_int)]


def exclusive_of(cards: dict, trader: str) -> set[str]:
    """原版**只有这位商人卖**的卡。"""
    return {guid for guid, card in cards.items() if card.sell_vanilla == [trader]}


def by_dlc(cards: dict, dlc: str) -> set[str]:
    return {guid for guid, card in cards.items() if dlc in card.dlc}


# ---------------------------------------------------------------------- 排版
def groups(entries: list[PoolEntry], cards: dict) -> dict[str, dict[str, list[str]]]:
    """`{大类: {细类: [GUID]}}`；卡表里查不到的 GUID 归「其他（不在卡表）」。"""
    buckets: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for entry in entries:
        card = cards.get(entry.guid)
        place = (placement.place(card) or UNKNOWN_GROUP) if card else UNKNOWN_GROUP
        buckets[placement.big_of(place)][place].append(entry.guid)
    return {big: dict(places) for big, places in buckets.items()}


def sort_key(guid: str, cards: dict) -> tuple[str, int]:
    """细类内排序：卡表里的英文名（退回内部名 / 中文名），最后按 GUID 兜底。"""
    card = cards.get(guid)
    name = (card.en or card.internal or card.zh or "").lower() if card else ""
    return (name, util.as_int(guid))


def header(name: str, entries: list[PoolEntry], cards: dict) -> str:
    """商人抬头：`<!-- 中文名（英文名） - 区域 | 共 N 项：大类 计数 -->`"""
    _zh, en, zones = TRADERS[TRADER_BY_NAME[name]]
    counts = Counter(placement.big_of(place_of(entry.guid, cards)) for entry in entries)
    parts = "、".join(f"{big} {count}" for big, count in
                      sorted(counts.items(), key=lambda item: placement.bigkey(item[0])))
    zone = tables.TRADER_ZONE_LABEL.get(name) or tables.zones_zh(zones)
    return f"\t<!-- {name}（{en}） - {zone} | 共 {len(entries)} 项：{parts} -->"


def place_of(guid: str, cards: dict) -> str:
    card = cards.get(guid)
    return (placement.place(card) or UNKNOWN_GROUP) if card else UNKNOWN_GROUP


def entry_lines(name: str, entries: list[PoolEntry], cards: dict) -> list[str]:
    """一个池的正文：大类注释 + 细类注释 + 条目。"""
    grouped = groups(entries, cards)
    weights = {entry.guid: entry.weight for entry in entries}
    lines: list[str] = []
    for big in sorted(grouped, key=placement.bigkey):
        places = grouped[big]
        total = sum(len(guids) for guids in places.values())
        lines.append(f"{INDENT}<!-- ===== {big}（{total} 项） ===== -->")
        for place in sorted(places, key=placement.pkey):
            guids = sorted(places[place], key=lambda guid: sort_key(guid, cards))
            lines.append(f"{INDENT}<!-- {place}（{len(guids)} 项） -->")
            for guid in guids:
                weight = weights.get(guid, DEFAULT_WEIGHT)
                lines.append(f"{INDENT}<Item><ItemLink>{guid}</ItemLink><Weight>{weight}</Weight></Item>")
    return lines


def render(text: str, pools: dict[str, list[PoolEntry]], cards: dict) -> str:
    """按「大类 → 细类」重排每个 `ItemsPool` 并重写抬头注释，其余内容原样保留。"""
    out: list[str] = []
    current: str | None = None
    inside = False
    for line in text.split("\n"):
        match = MODOP_RE.search(line)
        if match:
            kind, guid, path = match.groups()
            is_pool = kind == "replace" and path == POOL_PATH and guid in TRADERS
            current = TRADERS[guid][0] if is_pool else None
            if current:
                while out and "<!--" in out[-1] and "-->" in out[-1]:
                    out.pop()                                   # 丢掉旧抬头
                out.append(header(current, pools[current], cards))
            inside = False
            out.append(line)
            continue
        if current and "<ItemsPool>" in line:
            out.append(line)
            inside = True
            out.extend(entry_lines(current, pools[current], cards))
            continue
        if current and "</ItemsPool>" in line:
            inside = False
            out.append(line)
            continue
        if inside:
            continue                                            # 丢掉旧条目与旧段落注释
        out.append(line)
    return "\n".join(out)


# ---------------------------------------------------------------------- 报数
@dataclass
class PoolStat:
    """一位商人池子的现状。"""

    name: str
    entries: int
    duplicates: int
    known: int
    unknown: list[str]


def stats(pools: dict[str, list[PoolEntry]], cards: dict) -> list[PoolStat]:
    result: list[PoolStat] = []
    for name, entries in pools.items():
        guids = [entry.guid for entry in entries]
        unique = set(guids)
        unknown = sorted((guid for guid in unique if guid not in cards), key=util.as_int)
        result.append(PoolStat(name=name, entries=len(guids),
                               duplicates=len(guids) - len(unique),
                               known=len(unique) - len(unknown), unknown=unknown))
    return result
