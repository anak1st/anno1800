#!/usr/bin/env python
"""研发展开 → `temp/research-cards.txt`（可研发物品 GUID 清单）。

    uv run build_research.py
"""

from __future__ import annotations

from anno import paths, research, scan
from anno.console import console


def main() -> int:
    index = scan.scan(paths.VANILLA_ASSETS, verbose=False)
    for name, counts in research.report(index):
        console.print(f"  {name:<22} " + " / ".join(str(count) for count in counts))
    total = research.write_list(index)
    console.print(f"  {total} 个 GUID -> {paths.RESEARCH_CARDS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
