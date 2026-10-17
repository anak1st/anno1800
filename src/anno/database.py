"""`data/` 的读写：一个资产一个 JSON 文件。

目录划分（合理分组，避免单个 JSON 太大）：

    data/cards/          2149 张卡（核心）
    data/buildings/      卡牌目标里的建筑
    data/target-groups/  目标组（「所有作物农场」这类）
    data/goods/          商品（产物 / 原料 / 需求）
    data/fertilities/    作物
    data/item-sets/      物品套装
    data/dlc/            DLC
    data/traders/        商人
    data/buffs/          使用型道具的 Buff

外加两个索引：`index.json`（schema / 统计 / 目录说明）、`names.json`（名字反查，CLI 用）。
"""

from __future__ import annotations

import json
from pathlib import Path

from . import paths
from .cards import CardView

SCHEMA = 1

FOLDER_DOCS: dict[str, str] = {
    "cards": "卡牌：一张卡一个文件（核心）",
    "target-groups": "作用目标组（ItemEffectTargetPool）",
    "buildings": "卡牌作用目标里的建筑（含产线）",
    "goods": "商品：产物 / 原料 / 需求",
    "fertilities": "作物（肥料）",
    "item-sets": "物品套装",
    "dlc": "DLC",
    "traders": "商人：原版档位池 + 本 mod 池",
    "buffs": "使用型道具给的 Buff",
}


# ---------------------------------------------------------------------- 写
def write(docs: dict[str, dict[str, dict]], meta: dict) -> dict[str, int]:
    """把各概念的文档写进 `data/`，返回每个目录的文件数。"""
    counts: dict[str, int] = {}
    for folder, path in paths.DATA_FOLDERS.items():
        folder_docs = docs.get(folder, {})
        path.mkdir(parents=True, exist_ok=True)
        for guid, doc in folder_docs.items():
            _write_json(path / f"{guid}.json", doc)
        counts[folder] = len(folder_docs)

    _write_json(paths.DATA_INDEX, {
        "schema": SCHEMA,
        "generated_from": meta,
        "counts": counts,
        "folders": FOLDER_DOCS,
    })
    _write_json(paths.DATA_NAMES, names_index(docs))
    return counts


def _write_json(path: Path, payload: dict) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text + "\n")


def names_index(docs: dict[str, dict[str, dict]]) -> dict[str, list[dict]]:
    """名字 -> [{type, id}]；中文名和内部名都收，重名给多个候选。"""
    index: dict[str, list[dict]] = {}
    for folder, folder_docs in docs.items():
        for guid, doc in folder_docs.items():
            for key in {(doc.get("name") or {}).get("zh", ""),
                        (doc.get("name") or {}).get("internal", ""),
                        doc.get("label", "")}:
                if not key:
                    continue
                entry = {"type": doc.get("type", folder), "id": guid}
                bucket = index.setdefault(key, [])
                if entry not in bucket:
                    bucket.append(entry)
    return index


# ---------------------------------------------------------------------- 读
def load_cards() -> dict[str, CardView]:
    """读回所有卡（渲染、改卡池用）。"""
    return {guid: CardView.from_doc(doc) for guid, doc in load_docs("cards").items()}


def load_docs(folder: str) -> dict[str, dict]:
    """读一个概念目录下的全部文档。"""
    path = paths.DATA_FOLDERS[folder]
    if not path.is_dir():
        return {}
    return {file.stem: doc for file in sorted(path.glob("*.json"))
            for doc in [_read_json(file)] if doc}


def load_doc(folder: str, guid: str) -> dict | None:
    path = paths.DATA_FOLDERS[folder] / f"{guid}.json"
    return _read_json(path) if path.is_file() else None


def load_index() -> dict:
    return _read_json(paths.DATA_INDEX) if paths.DATA_INDEX.is_file() else {}


def load_names() -> dict[str, list[dict]]:
    return _read_json(paths.DATA_NAMES) if paths.DATA_NAMES.is_file() else {}


def _read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)
