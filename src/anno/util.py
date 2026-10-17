"""通用小工具：TSV 读写、markdown 表格、字符串处理。全是纯函数，好测。"""

from __future__ import annotations

from pathlib import Path

TAB = "\t"
NEWLINE = "\n"


# ---------------------------------------------------------------- TSV
def read_tsv(path: Path) -> dict[str, dict[str, str]]:
    """读带表头的 TSV，返回 `{第一列的值: 整行 dict}`（卡表底稿第一列是 GUID）。"""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return {}
    header = lines[0].split(TAB)
    rows: dict[str, dict[str, str]] = {}
    for line in lines[1:]:
        if not line.strip():
            continue
        cells = line.split(TAB)
        rows[cells[0]] = dict(zip(header, cells, strict=False))
    return rows


def write_tsv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    """写带表头的 TSV（制表符会破坏结构，替换成空格）。"""
    safe = [[str(value).replace(TAB, " ") for value in row] for row in rows]
    body = NEWLINE.join(TAB.join(row) for row in [header, *safe])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline=NEWLINE) as handle:
        handle.write(body + NEWLINE)


# ---------------------------------------------------------------- markdown
def md_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    """一个 markdown 表格：表头 + 分隔行 + 数据行（缺列补空，多列截掉）。"""
    lines = [
        "| " + " | ".join(cell(head) for head in headers) + " |",
        "|" + "|".join(["---"] * len(headers)) + "|",
    ]
    for row in rows:
        cells = [cell(value) for value in row]
        cells += [""] * (len(headers) - len(cells))
        lines.append("| " + " | ".join(cells[:len(headers)]) + " |")
    return lines


def cell(text: object) -> str:
    """表格单元格：竖线会破坏表格结构，换成斜杠。"""
    return str(text).replace("|", "/")


def write_lines(path: Path, lines: list[str], *, crlf: bool = False) -> None:
    """写文本文件（默认 LF；`crlf=True` 用于要同步进游戏目录的 mod 文件）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    newline = "\r\n" if crlf else NEWLINE
    body = newline.join(lines) + newline
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(body)


# ---------------------------------------------------------------- 字符串
def dedup(items) -> list:
    """保序去重。"""
    return list(dict.fromkeys(items))


def truncate(text: str, limit: int, ellipsis: str = "…") -> str:
    """超长就截断加省略号。"""
    return text if len(text) <= limit else text[:limit] + ellipsis


def as_int(text: str) -> int:
    """GUID 排序键：非数字当 0，混进字母时也不崩。"""
    return int(text) if str(text).isdigit() else 0


def number(text: str) -> int | float | None:
    """把 XML 里的数字文本转成 int / float；不是数字返回 None。"""
    try:
        return float(text) if "." in text else int(text)
    except (TypeError, ValueError):
        return None
