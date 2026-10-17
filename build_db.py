#!/usr/bin/env python
"""扫描游戏数据 → `data/`（一个资产一个 JSON）。

**单向流程**：游戏本体 → `temp/`（解包）→ 扫描/规则 → `data/` → 文档；
mod 的 `assets.xml` 是这个流程的输出（`edit_pools.py assign` 生成），**不参与解析**。

    uv run build_db.py          # 约 6 秒（扫 assets.xml + 写约 3100 个文件）
"""

from __future__ import annotations

import time
from pathlib import Path

from anno import cards, database, entities, paths, research, rules, scan, texts, traders, util
from anno.cards import CardView
from anno.console import console


def main() -> int:
    start = time.time()
    index = scan.scan(paths.VANILLA_ASSETS)
    names = texts.Names(texts.load_zh(), lambda guid: index.field(guid, "name"))

    researchable = research.researchable(index)
    inputs = cards.load_inputs(index, research=researchable)
    card_guids = set(inputs.rows)

    # 原版谁卖（游戏档位池）→ 卡文档
    vanilla = traders.vanilla_owners(index, card_guids)
    card_docs = cards.build_docs(index, inputs, vanilla, names)

    # 本 mod 卖什么、挂给谁：纯规则（收录范围 + 归属），不读 mod 文件
    views = {guid: CardView.from_doc(doc) for guid, doc in card_docs.items()}
    decisions = rules.mod_plan(index, views, names)
    unresolved = sorted((guid for guid, view in views.items()
                         if rules.in_mod(view) and guid not in decisions), key=util.as_int)
    if unresolved:
        console.print(f"  [yellow]{len(unresolved)} 张该收录但没匹配到规则：{unresolved[:10]}[/]")
    cards.attach_mod_owners(
        card_docs,
        {guid: [traders.profile_ref(name) for name in traders.order_names(merchants)]
         for guid, merchants in decisions.items()},
    )

    trader_docs, _owners = traders.build(index, card_guids, decisions, names)
    other_docs = entities.build(index, card_docs, names)

    docs = {"cards": card_docs, "traders": trader_docs, **other_docs}
    counts = database.write(docs, {
        "assets_xml": _file_meta(paths.VANILLA_ASSETS),
        "cards": len(card_docs),
        "schema_note": "一个资产一个 JSON；效果数值由 anno.effects 从 Values 原文解析；"
                       "mod 归属由 anno.rules 计算（mod 的 assets.xml 是输出，不是输入）",
    })

    entries = sum(len(merchants) for merchants in decisions.values())
    dual = sum(1 for merchants in decisions.values() if len(merchants) > 1)
    console.print(f"  卡 [bold]{len(card_docs)}[/] 张 ｜ 原版卖 {sum(1 for d in card_docs.values() if d['owners']['vanilla'])}"
                  f" ｜ 本 mod 卖 [bold]{len(decisions)}[/]（{entries} 条，{dual} 张双挂）")
    console.print(f"  data/ 共 [bold]{sum(counts.values())}[/] 个文件："
                  + " ｜ ".join(f"{folder} {count}" for folder, count in counts.items()))
    console.print(f"  用时 {time.time() - start:.1f}s")
    return 0


def _file_meta(path: Path) -> dict:
    stat = path.stat() if path.is_file() else None
    return {"size": stat.st_size if stat else 0,
            "mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)) if stat else ""}


if __name__ == "__main__":
    raise SystemExit(main())
