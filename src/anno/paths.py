"""所有路径 —— 仓库内路径 + 根目录 `anno.json` 的本机配置。

    temp/db/...     游戏解包数据（只读）+ 卡表底稿
    data/...        解析好的 JSON 数据库（一个资产一个文件）
    docs/...        从 data/ 渲染的文档

`data/` `temp/` `docs/` 可以在 `anno.json` 里改到别处；游戏安装目录只在需要
解包 / 同步 mod 时用到（`game_dir`），日常跑工具链不需要它。
"""

from __future__ import annotations

from pathlib import Path

from .config import load

CFG = load()

# ---------------------------------------------------------------- 三层
TEMP = Path(CFG["temp_dir"])
DATA = Path(CFG["data_dir"])
DOCS = Path(CFG["docs_dir"])

# 游戏安装目录（未配置时为空，用到它的命令会给出提示）
GAME_DIR: Path | None = Path(CFG["game_dir"]).expanduser() if CFG["game_dir"] else None

# ---------------------------------------------------------------- 游戏解包数据（只读）
GAME_DATA = TEMP / "db/data/config"
VANILLA_ASSETS = GAME_DATA / "export/main/asset/assets.xml"
TEMPLATES = GAME_DATA / "export/main/asset/templates.xml"
TEXTS_ZH = GAME_DATA / "gui/texts_chinese.xml"
TEXTS_EN = GAME_DATA / "gui/texts_english.xml"

# ---------------------------------------------------------------- data/ 下每个概念一个目录
DATA_CARDS = DATA / "cards"
DATA_TARGET_GROUPS = DATA / "target-groups"
DATA_BUILDINGS = DATA / "buildings"
DATA_GOODS = DATA / "goods"
DATA_FERTILITIES = DATA / "fertilities"
DATA_ITEM_SETS = DATA / "item-sets"
DATA_DLC = DATA / "dlc"
DATA_TRADERS = DATA / "traders"
DATA_BUFFS = DATA / "buffs"

DATA_FOLDERS: dict[str, Path] = {
    "cards": DATA_CARDS,
    "target-groups": DATA_TARGET_GROUPS,
    "buildings": DATA_BUILDINGS,
    "goods": DATA_GOODS,
    "fertilities": DATA_FERTILITIES,
    "item-sets": DATA_ITEM_SETS,
    "dlc": DATA_DLC,
    "traders": DATA_TRADERS,
    "buffs": DATA_BUFFS,
}

DATA_INDEX = DATA / "index.json"       # 清单：schema、统计、目录说明
DATA_NAMES = DATA / "names.json"       # 名字 -> (概念, ID)，给 CLI 反查

# ---------------------------------------------------------------- 原始层的底稿与产物
RESEARCH_CARDS = TEMP / "research-cards.txt"  # 可研发清单
CARD_PROFILE = TEMP / "card-profile.tsv"      # 人看的档案（由 data/ 渲染）
MERCHANT_POOLS_MD = TEMP / "merchant-pools.md"  # 各商人卡池大小（由 data/ 渲染）

# ---------------------------------------------------------------- 文档
CARDS_MD = DOCS / "cards.md"

# ---------------------------------------------------------------- mod
MODS = Path("mods")
ALL_ITEMS_ASSETS = MODS / "all-items-unlocked/data/config/export/main/asset/assets.xml"


def game_mods() -> Path:
    """游戏侧的 mod 目录（需要 `anno.json` 里的 `game_dir`）。"""
    return require_game_dir() / "mods"


def require_game_dir() -> Path:
    """取游戏安装目录；没配置就报一个能照着做的错。"""
    if GAME_DIR is None:
        raise RuntimeError(
            "没有配置 game_dir：在根目录新建 anno.json，写 {\"game_dir\": \"<Anno 1800 安装目录>\"}，" +
            "用法见 README 第〇节）")
    return GAME_DIR
