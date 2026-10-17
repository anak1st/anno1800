"""文本表与名字解析。

`texts_chinese.xml` 是扁平结构：`<Text><GUID>112552</GUID><Text>海底振动器</Text></Text>`，
键是**资产 GUID**（不是 LineID —— 早期按 LineID 查，名字全错）。

`Names` 是所有模块取中文名的唯一入口：文本表查不到时回退资产内部名。
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from lxml import etree

from . import paths


def load(path: Path) -> dict[str, str]:
    """读一份文本表，返回 `{文本 GUID: 文本}`。"""
    root = etree.parse(str(path)).getroot()
    table: dict[str, str] = {}
    for node in root.iter("Text"):
        guid = (node.findtext("GUID") or "").strip()
        if guid:
            table[guid] = (node.findtext("Text") or "").strip()
    return table


def load_zh() -> dict[str, str]:
    """中文文本表 —— 文档里所有中文名都来自这里。"""
    return load(paths.TEXTS_ZH)


def load_en() -> dict[str, str]:
    """英文文本表（只用来对照）。"""
    return load(paths.TEXTS_EN)


class Names:
    """GUID → 名字。`label()` 是「中文名 or 内部名 or GUID」的三级回退。"""

    def __init__(self, zh: dict[str, str], internal: Callable[[str], str] | None = None) -> None:
        self._zh = zh
        self._internal = internal or (lambda guid: "")

    def zh(self, guid: str) -> str:
        return self._zh.get(guid, "")

    def internal(self, guid: str) -> str:
        return self._internal(guid) or ""

    def label(self, guid: str) -> str:
        return self.zh(guid) or self.internal(guid) or guid

    def ref(self, guid: str) -> dict[str, str]:
        """JSON 里统一用 `{id, name}` 引用别的资产。"""
        return {"id": guid, "name": self.label(guid)} if guid else {}
