#!/usr/bin/env python
"""读 `data/` 出文档（不碰 XML，一秒内跑完）。

    uv run build_cards.py     # docs/cards.md + temp/merchant-pools.md
"""

from __future__ import annotations

from anno import database, paths, render
from anno.console import console


def main() -> int:
    cards = database.load_cards()
    render.write_cards_doc(cards)
    render.write_merchant_pools(database.load_docs("traders"))
    console.print(f"  {len(cards)} 张卡 -> {paths.CARDS_MD}")
    console.print(f"  商人卡池 -> {paths.MERCHANT_POOLS_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())