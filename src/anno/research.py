"""研发展开：研究所里能造哪些东西。

结构是四层嵌套，必须展到底：

    ResearchSubcategory（9 类）
      → RecipePool 里的 Pool（每类 Low / Medium / High）
        → AssetPool（成员是子池，不是物品）
          → 一路展到叶子才是物品

漏掉最后一层就只能拿到池 GUID、拿不到物品 —— 那是 282 与 1130 的差别。
叶子里有 39 个不是卡（装饰 / 建筑），所以清单比卡数多几条。
"""

from __future__ import annotations

from . import paths, tables, util
from .model import AssetIndex

RESEARCH_POOLS: list[str] = [pool for _name, pools in tables.RESEARCH_CATEGORIES.values()
                             for pool in pools]


def leaves(index: AssetIndex) -> set[str]:
    """研发池展到底的所有 GUID（含非卡物件）。"""
    return index.expand_pools(RESEARCH_POOLS)


def researchable(index: AssetIndex) -> set[str]:
    """其中真正是卡的那些。"""
    return {guid for guid in leaves(index) if guid in index.cards}


def write_list(index: AssetIndex) -> int:
    """写 `temp/research-cards.txt`（每行一个 GUID，升序），返回条数。"""
    guids = sorted(leaves(index), key=util.as_int)
    paths.RESEARCH_CARDS.write_text("\n".join(guids) + "\n", encoding="utf-8")
    return len(guids)


def report(index: AssetIndex) -> list[tuple[str, list[int]]]:
    """每类三个档位各展开出多少 —— 给终端看。"""
    return [(name, [len(index.expand_pools([pool])) for pool in pools])
            for _guid, (name, pools) in tables.RESEARCH_CATEGORIES.items()]
