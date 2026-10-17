"""终端输出：把编码钉死在 UTF-8，并提供共用的 rich Console。

Windows 控制台默认 GBK，中文注释和卡名会变成乱码 —— 所有入口脚本都要先 `force_utf8()`。
"""

from __future__ import annotations

import sys

from rich.console import Console


def force_utf8() -> None:
    """把 stdout / stderr 改成 UTF-8。要在 import rich 之后、打印之前调用。"""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


force_utf8()
console = Console()
