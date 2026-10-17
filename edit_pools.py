#!/usr/bin/env python
"""改 `mods/all-items-unlocked` 的商人卡池（增 / 删 / 挪 / 重排 / 报数）。

    uv run edit_pools.py report                    只看数
    uv run edit_pools.py tidy                      只重排 + 重写抬头注释
    uv run edit_pools.py add --to 库马克 2226 2232   加进某家
    uv run edit_pools.py drop 132348 132350         从所有池删掉
    uv run edit_pools.py move --to 萨曼托 --from 伊莱
    uv run edit_pools.py exclusive 库马克           原版独占的卡收回本人
    uv run edit_pools.py assign [--dry-run]         按规则整体重排（含跨区双挂）

改完记得重跑 `build_db.py` + `build_cards.py`，让 data/ 与文档跟上。
"""

from __future__ import annotations

from collections import Counter

import typer
from rich.table import Table

from anno import database, paths, pools, rules, scan, texts, util
from anno.console import console

app = typer.Typer(add_completion=False, no_args_is_help=True,
                  help="改 all-items-unlocked 的商人卡池")
DRY_RUN = typer.Option(False, "--dry-run", help="只打印计划，不写文件")


def load() -> tuple[str, dict, dict]:
    """读 mod 文件 + 卡表：返回（原文, 池子, 卡表）。"""
    text = pools.read_raw()
    return text, pools.read_pools(text), database.load_cards()


def save(text: str, pool_map: dict, cards: dict) -> None:
    pools.write(pools.render(text, pool_map, cards))
    console.print(f"  已写回 {paths.ALL_ITEMS_ASSETS}")
    show_stats(pool_map, cards)


def show_stats(pool_map: dict, cards: dict) -> None:
    stats = pools.stats(pool_map, cards)
    view = Table("商人", "池内条目", "重复", "卡表内")
    for stat in stats:
        view.add_row(stat.name, str(stat.entries), str(stat.duplicates), str(stat.known))
    view.add_row("[bold]合计[/]",
                 f"[bold]{sum(s.entries for s in stats)}[/]",
                 f"[bold]{sum(s.duplicates for s in stats)}[/]",
                 f"[bold]{sum(s.known for s in stats)}[/]")
    console.print(view)
    for stat in stats:
        if stat.unknown:
            console.print(f"  [yellow]{stat.name} 池里有 {len(stat.unknown)} 条 GUID 不在卡表里："
                          + "、".join(stat.unknown) + "[/]")


def name_of(cards: dict, guid: str) -> str:
    card = cards.get(guid)
    return f"{card.zh}({guid})" if card else f"（不在卡表）{guid}"


@app.command()
def report() -> None:
    """只看现状：每家池子大小、重复、覆盖率、双挂。"""
    _text, pool_map, cards = load()
    show_stats(pool_map, cards)
    sold = {entry.guid for entries in pool_map.values() for entry in entries}
    missing = [guid for guid, card in cards.items() if card.sell_vanilla and guid not in sold]
    only = [guid for guid in sold if guid in cards and not cards[guid].sell_vanilla]
    console.print(f"  原版卖但 mod 没卖：[bold]{len(missing)}[/]"
                  + ("　" + "、".join(name_of(cards, g) for g in missing) if missing else ""))
    console.print(f"  只有 mod 卖（原版没人卖）：[bold]{len(only)}[/]")
    where: dict[str, list[str]] = {}
    for name, entries in pool_map.items():
        for entry in entries:
            where.setdefault(entry.guid, []).append(name)
    dual = sorted((g for g, names in where.items() if len(names) > 1), key=util.as_int)
    console.print(f"  双挂（一张卡挂多家）：[bold]{len(dual)}[/]"
                  + ("　" + "、".join(f"{name_of(cards, g)}→{'+'.join(where[g])}" for g in dual)
                     if dual else ""))


@app.command()
def tidy(dry_run: bool = DRY_RUN) -> None:
    """按大类两层重排 + 重写抬头注释（内容不变）。"""
    text, pool_map, cards = load()
    if dry_run:
        console.print("  --dry-run：不写文件")
        return
    save(text, pool_map, cards)


@app.command()
def add(to: str = typer.Option(..., help="商人名"),
        guids: list[str] = typer.Argument(..., help="要加的 GUID"),
        dry_run: bool = DRY_RUN) -> None:
    """把卡加进某家。"""
    text, pool_map, cards = load()
    wanted = {guid.strip() for guid in guids}
    new = wanted - {entry.guid for entry in pool_map[to]}
    console.print(f"  加进 {to}：{len(new)} 张"
                  + (f"（已在池里 {len(wanted - new)} 张）" if wanted - new else ""))
    for guid in sorted(new, key=util.as_int):
        console.print(f"    + {name_of(cards, guid)}")
    pools.add(pool_map, to, wanted)
    if not dry_run:
        save(text, pool_map, cards)


@app.command()
def drop(guids: list[str] = typer.Argument(..., help="要删的 GUID"),
         dry_run: bool = DRY_RUN) -> None:
    """从所有池里删掉这些卡。"""
    text, pool_map, cards = load()
    hit = {entry.guid for entries in pool_map.values() for entry in entries} & set(guids)
    for guid in sorted(set(guids) - hit, key=util.as_int):
        console.print(f"  （{guid} 本来就不在任何池里）")
    console.print(f"  从所有池删除 {len(hit)} 张："
                  + "、".join(name_of(cards, guid) for guid in sorted(hit, key=util.as_int)))
    pools.drop(pool_map, hit)
    if not dry_run:
        save(text, pool_map, cards)


@app.command()
def move(to: str = typer.Option(..., help="归到哪位商人"),
         guids: list[str] = typer.Argument(None, help="指定 GUID"),
         from_: str = typer.Option(None, "--from", help="整池搬过来"),
         dlc: str = typer.Option(None, help="这个 DLC 的卡全要"),
         exclusive_of: str = typer.Option(None, "--exclusive-of", help="原版只有他卖的卡"),
         dry_run: bool = DRY_RUN) -> None:
    """把卡归到某家（从别家删掉、缺的补上）。"""
    text, pool_map, cards = load()
    wanted: set[str] = set(guids or [])
    if from_:
        wanted |= {entry.guid for entry in pool_map[from_]}
    if dlc:
        wanted |= pools.by_dlc(cards, dlc)
    if exclusive_of:
        wanted |= pools.exclusive_of(cards, exclusive_of)
    if not wanted:
        raise typer.BadParameter("要写 GUID，或用 --from / --dlc / --exclusive-of")
    where = {entry.guid: name for name, entries in pool_map.items() for entry in entries}
    moving = {guid for guid in wanted if where.get(guid) != to}
    console.print(f"  归到 {to}：{len(wanted)} 张（需要动的 {len(moving)} 张）")
    pools.move(pool_map, to, wanted)
    if not dry_run:
        save(text, pool_map, cards)


@app.command()
def exclusive(who: str = typer.Argument(..., help="商人名"),
              dry_run: bool = DRY_RUN) -> None:
    """把某位商人原版独占的卡收回他本人。"""
    move(to=who, guids=[], from_=None, dlc=None, exclusive_of=who, dry_run=dry_run)


@app.command()
def assign(restore: list[str] = typer.Argument(None, help="额外放回 mod 的 GUID"),
           dry_run: bool = DRY_RUN) -> None:
    """按规则重排全部卡池（先看 --dry-run 的流动明细）。"""
    text, pool_map, cards = load()
    index = scan.scan(paths.VANILLA_ASSETS, verbose=False)
    names = texts.Names(texts.load_zh(), lambda guid: index.field(guid, "name"))
    current = {entry.guid: name for name, entries in pool_map.items() for entry in entries}
    base = sorted(set(current) | set(restore or []), key=util.as_int)
    decisions = rules.plan(index, cards, base, names)

    for guid in (g for g in base if g not in decisions):
        console.print(f"  [yellow]{guid} {name_of(cards, guid)} 没有匹配的规则，留在原处[/]")

    view = Table("规则", "商人", "张数")
    counts = Counter((d.rule, merchant) for d in decisions.values() for merchant in d.merchants)
    for (rule, merchant), count in sorted(counts.items()):
        view.add_row(rule, merchant, str(count))
    console.print(view)

    flow = Counter()
    for guid, decision in decisions.items():
        was = current.get(guid)
        for merchant in decision.merchants:
            if merchant != was:
                flow[(was or "（新增）", merchant)] += 1
        if was and was not in decision.merchants:
            flow[(was, "（移出）")] += 1
    moves = Table("从", "到", "张数")
    for (src, dst), count in flow.most_common():
        moves.add_row(src, dst, str(count))
    moves.add_row("[bold]合计[/]", "", f"[bold]{sum(flow.values())}[/]")
    console.print(moves)

    dual = [guid for guid, d in decisions.items() if len(d.merchants) > 1]
    entries = sum(len(d.merchants) for d in decisions.values())
    console.print(f"  现有池内 {len(current)} 张 ｜ 重排后 {len(decisions)} 张"
                  f"（{entries} 条，其中 {len(dual)} 张双挂）｜ 其中恢复 {len(restore or [])} 张")
    for guid in dual:
        console.print(f"    [cyan]⇄ {name_of(cards, guid)} -> {' + '.join(decisions[guid].merchants)}"
                      f"（{decisions[guid].rule}）[/]")

    if dry_run:
        console.print("  --dry-run：不写文件")
        return
    owners = {guid: (decisions[guid].merchants if guid in decisions else (current[guid],))
              for guid in base}
    pools.apply_assignment(pool_map, owners)
    save(text, pool_map, cards)


def main() -> None:
    app()


if __name__ == "__main__":
    main()