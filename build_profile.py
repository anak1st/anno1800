#!/usr/bin/env python
"""读 `data/` 出人看的卡牌档案。

    uv run build_profile.py   # temp/card-profile.tsv
"""

from __future__ import annotations

from anno import database, paths, render
from anno.console import console


def main() -> int:
    cards = database.load_cards()
    written = render.write_profile(cards)
    console.print(f"  {written} 行 -> {paths.CARD_PROFILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
