#!/usr/bin/env python
"""扫描游戏数据 → `data/`（一个资产一个 JSON）。

    uv run build_db.py          # 约 6 秒（扫 assets.xml 5 秒 + 写约 2900 个文件）

只写 `data/`；文档由 `build_cards.py` 从这里再渲染。
"""

from __future__ import annotations

import time
from pathlib import Path

from anno import cards, database, entities, paths, pools, scan, texts, traders
from anno.console import console


def main() -> int:
    start = time.time()
    index = scan.scan(paths.VANILLA_ASSETS)
    names = texts.Names(texts.load_zh(), lambda guid: index.field(guid, "name"))

    inputs = cards.load_inputs(index)
    mod_sold, mod_raw = pools.read_assigned(inputs.rows)
    trader_docs, owners = traders.build(index, set(inputs.rows), mod_sold, mod_raw, names)
    card_docs = cards.build_docs(index, inputs, owners, names)
    other_docs = entities.build(index, card_docs, names)

    docs = {"cards": card_docs, "traders": trader_docs, **other_docs}
    counts = database.write(docs, {
        "assets_xml": _file_meta(paths.VANILLA_ASSETS),
        "card_tables": len(inputs.rows),
        "schema_note": "一个资产一个 JSON；效果数值由 anno.effects 从 Values 原文解析",
    })

    total = sum(counts.values())
    console.print(f"  data/ 共 [bold]{total}[/] 个文件：" +
                  " ｜ ".join(f"{folder} {count}" for folder, count in counts.items()))
    console.print(f"  用时 {time.time() - start:.1f}s")
    return 0


def _file_meta(path: Path) -> dict:
    stat = path.stat() if path.is_file() else None
    return {"size": stat.st_size if stat else 0,
            "mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)) if stat else ""}


if __name__ == "__main__":
    raise SystemExit(main())
