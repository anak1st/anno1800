"""本机配置：根目录 `anno.json`（不进 git）。

只放**跟本机有关**的东西：游戏装在哪、要不要把 data/ temp/ docs/ 指到别处。
仓库结构与业务规则不在这里；没建这个文件时全部用默认值（`game_dir` 为空）。

    {
      "game_dir": "<Anno 1800 安装目录>",
      "data_dir": "data",
      "temp_dir": "temp",
      "docs_dir": "docs"
    }
"""

from __future__ import annotations

import json
from pathlib import Path

DEFAULTS: dict[str, str] = {
    "game_dir": "",          # 游戏安装目录（RDA 解包、同步 mod 用）
    "data_dir": "data",      # 解析层
    "temp_dir": "temp",      # 原始层
    "docs_dir": "docs",      # 文档
}
CONFIG_PATH = Path("anno.json")


def load() -> dict[str, str]:
    """读 `anno.json`，缺的键用默认值。"""
    config = dict(DEFAULTS)
    if not CONFIG_PATH.is_file():
        return config
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise RuntimeError(f"{CONFIG_PATH} 不是合法 JSON：{error}") from error
    config.update({key: value for key, value in data.items() if value not in (None, "")})
    return config


def describe() -> list[tuple[str, str, str]]:
    """给 CLI 看的配置清单（键、值、来源）。"""
    from_file: dict[str, str] = {}
    if CONFIG_PATH.is_file():
        from_file = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    config = load()
    return [(key, str(config[key]), "anno.json" if key in from_file else "默认")
            for key in DEFAULTS]
