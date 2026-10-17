#!/usr/bin/env python
"""查 `data/` 数据库 —— 人类友好的一组命令。

    uv run query.py card 125131           # 也可写中文名：card 香料大师
    uv run query.py find --effect productivity --zone 安贝沙
    uv run query.py find --owner 柯提马 --place 工会 --text 农场
    uv run query.py trader 柯提马
    uv run query.py building 辛香料农场
    uv run query.py good 木蓝染料
    uv run query.py show 114452           # 不知道类型时自动识别

先跑一次 `uv run build_db.py`（data/ 不进 git）。
"""

from __future__ import annotations

import json

import typer
from rich.table import Table

from anno import config as config_mod
from anno import database, paths, util
from anno.console import console

app = typer.Typer(add_completion=False, no_args_is_help=True,
                  help="查询 data/ 下的 JSON 数据库")

USE_ZH: dict[str, str] = {"input": "原料", "output": "产物", "recipe": "配方",
                         "need": "需求", "workforce": "劳动力"}

FOLDERS: dict[str, str] = {
    "card": "cards", "building": "buildings", "target-group": "target-groups",
    "good": "goods", "fertility": "fertilities", "item-set": "item-sets",
    "dlc": "dlc", "trader": "traders", "buff": "buffs",
}


# ---------------------------------------------------------------------- 解析
def resolve(query: str, folder: str | None = None) -> tuple[str, dict] | None:
    """按 GUID 或名字找文档；`folder` 限定概念。"""
    if query.isdigit():
        for name in ([folder] if folder else list(FOLDERS.values())):
            doc = database.load_doc(name, query)
            if doc:
                return name, doc
        return None
    for candidate in database.load_names().get(query, []):
        name = FOLDERS.get(candidate["type"])
        if not name or (folder and name != folder):
            continue
        doc = database.load_doc(name, candidate["id"])
        if doc:
            return name, doc
    return None


def require(query: str, folder: str) -> dict:
    found = resolve(query, folder)
    if found is None:
        raise typer.BadParameter(f"找不到 {query}（先跑 build_db.py？）")
    return found[1]


# ---------------------------------------------------------------------- 卡
@app.command()
def card(query: str = typer.Argument(..., help="GUID 或中文名"),
         as_json: bool = typer.Option(False, "--json", help="输出原始 JSON")) -> None:
    """看一张卡的详细作用。"""
    doc = require(query, "cards")
    if as_json:
        console.print_json(json.dumps(doc, ensure_ascii=False))
        return
    print_card(doc)


def print_card(doc: dict) -> None:
    name = doc["name"].get("zh") or doc["name"].get("internal") or doc["id"]
    console.print(f"[bold]{name}[/]  [dim]{doc['id']}[/]")

    head = [doc.get("rarity") or "—", f"装槽 {doc['slot']['zh']}"]
    if doc["prices"].get("trade"):
        head.append(f"价格 {doc['prices']['trade']:,}")
    if doc["prices"].get("online"):
        head.append(f"在线货币 {doc['prices']['online']}")
    if doc["dlc"]:
        head.append("DLC " + "、".join(item["name"] for item in doc["dlc"]))
    if doc["flags"].get("researchable"):
        head.append("研究所可研发")
    if doc["flags"].get("craftable"):
        head.append("老奈特可合成")
    if doc["flags"].get("scenario_only"):
        head.append("剧本专用")
    console.print("  " + " ｜ ".join(head))

    console.print(f"  归类  {doc['categories']['big'] or '—'} / {doc['categories']['place'] or '—'}")
    console.print(f"  效果  {doc['summary']}")

    travel = doc.get("expedition")
    if travel:
        console.print(f"  远征  {fmt_expedition(travel)}")

    targets = doc.get("targets") or {}
    if targets.get("refs"):
        zones = {name: "、".join(group["zones_zh"]) or "通用"
                 for group in targets.get("usage", []) for name in group["names"]}
        parts = [f"{ref['name']}（{zones.get(ref['name'], '—')}）" for ref in targets["refs"]]
        console.print("  目标  " + "；".join(parts))

    recipe = doc.get("recipe") or []
    if recipe:
        console.print("  配方  " + "、".join(f"{item['product']['name']} ×{item['amount']}" for item in recipe))

    owners = doc.get("owners") or {}
    vanilla = "、".join(item["name"] for item in owners.get("vanilla") or []) or "—"
    mod = "、".join(item["name"] for item in owners.get("mod") or []) or "—"
    console.print(f"  来源  原版 {vanilla} ｜ 本 mod {mod}")

    action = doc.get("action")
    if action:
        buff = f"，获得「{action['buff']['name']}」" if action.get("buff") else ""
        console.print(f"  使用  {action['label']}{buff}")

    if doc.get("flavor"):
        console.print(f"  [dim]{doc['flavor']}[/]")


def fmt_expedition(travel: dict) -> str:
    attributes = []
    for attr in travel.get("attributes", []):
        if attr.get("value"):
            attributes.append(f"{attr['zh']} {attr['value']:+}")
        else:
            attributes.append(attr["zh"])
    if travel.get("morale"):
        attributes.append(f"士气 {travel['morale']:+}")
    difficulties = "、".join(item["zh"] for item in travel.get("difficulties", []))
    regions = "、".join(item["zh"] for item in travel.get("regions", []))
    parts = ["、".join(attributes)] if attributes else []
    if difficulties:
        parts.append(f"难度 {difficulties}")
    if regions:
        parts.append(f"区域 {regions}")
    return "，".join(parts) or "—"


# ---------------------------------------------------------------------- 检索
@app.command()
def find(effect: str = typer.Option(None, help="效果键：productivity / maintenance / crop / workforce …"),
         zone: str = typer.Option(None, help="区域：安贝沙 / 新世界 / 北极 / 旧世界 或内部值"),
         owner: str = typer.Option(None, help="商人简称"),
         dlc: str = typer.Option(None, help="DLC 名（子串）"),
         place: str = typer.Option(None, help="装槽中文：工会 / 市政厅 / 船只 …"),
         rarity: str = typer.Option(None, help="Legendary / Epic / Rare / Uncommon / Common"),
         text: str = typer.Option(None, help="名字或摘要里的子串"),
         target: str = typer.Option(None, help="作用目标名（子串）"),
         researchable: bool = typer.Option(None, "--researchable/--not-researchable"),
         limit: int = typer.Option(40, help="最多显示多少行"),
         as_json: bool = typer.Option(False, "--json", help="输出原始 JSON")) -> None:
    """按条件检索卡牌。"""
    docs = database.load_docs("cards")
    console.print(f"[dim]读 {len(docs)} 张卡…[/]")
    hits = [doc for doc in docs.values() if match(doc, effect, zone, owner, dlc, place,
                                                  rarity, text, target, researchable)]
    hits.sort(key=lambda doc: util.as_int(doc["id"]))
    if as_json:
        console.print_json(json.dumps(hits[:limit], ensure_ascii=False))
        return
    for doc in hits[:limit]:
        name = doc["name"].get("zh") or doc["name"].get("internal", "")
        mod = " + ".join(item["name"] for item in doc["owners"]["mod"]) or "—"
        console.print(f"[dim]{doc['id']:<7}[/] [bold]{util.truncate(name, 14)}[/]"
                      f"  [dim]{doc.get('rarity') or '—'} / {doc['slot']['zh']} / {mod}[/]")
        console.print(f"        {util.truncate(doc['summary'], 96)}")
    console.print(f"  命中 [bold]{len(hits)}[/] 张" + (f"（只显示前 {limit}）" if len(hits) > limit else ""))


def match(doc: dict, effect, zone, owner, dlc, place, rarity, text, target, researchable) -> bool:
    if effect:
        keys = {bonus.get("key") for bonus in doc["effects"]["bonuses"]}
        if doc["effects"].get("extra_outputs"):
            keys.add("extra_output")
        if doc["effects"].get("replace_inputs"):
            keys.add("replace_input")
        if effect not in keys:
            return False
    if zone:
        zones = set(doc["targets"].get("zones", [])) | set(doc["targets"].get("zones_zh", []))
        if zone not in zones:
            return False
    if owner:
        names = {item["name"] for item in doc["owners"].get("vanilla", [])} | \
                {item["name"] for item in doc["owners"].get("mod", [])}
        if owner not in names:
            return False
    if dlc and not any(dlc in item["name"] for item in doc.get("dlc", [])):
        return False
    if place and doc["categories"].get("place") != place:
        return False
    if rarity and (doc.get("rarity") or "") != rarity:
        return False
    if text:
        haystack = " ".join([doc["name"].get("zh", ""), doc["name"].get("internal", ""),
                             doc.get("summary", "")])
        if text not in haystack:
            return False
    if target:
        refs = {ref["name"] for ref in doc["targets"].get("refs", [])}
        if not any(target in name for name in refs):
            return False
    return not (researchable is not None
                and bool(doc["flags"].get("researchable")) != researchable)


# ---------------------------------------------------------------------- 其它概念
@app.command()
def trader(query: str = typer.Argument(..., help="GUID 或商人名")) -> None:
    """看一位商人：档位池 + 本 mod 池。"""
    doc = require(query, "traders")
    console.print(f"[bold]{doc['name']['zh']}[/]  [dim]{doc['id']}[/]  ({doc['label']})")
    console.print(f"  区域  {doc['zone']['zh']} ｜ 原版卡 {doc['vanilla']['count']} 张")
    mod = doc.get("mod")
    if mod:
        console.print(f"  本 mod  {mod['entries']} 条 / {mod['count']} 张 ｜ 重复 {mod['duplicates']}"
                      f" ｜ 不在卡表 {len(mod['unknown'])}")
    view = Table("池", "卡数")
    view.add_row("原版档位池", str(doc["vanilla"]["count"]))
    if mod:
        view.add_row("本 mod 池", str(mod["count"]))
    console.print(view)
    cards = set(mod["cards"]) if mod else set()
    if cards:
        names = []
        for guid in sorted(cards, key=util.as_int)[:20]:
            card = database.load_doc("cards", guid)
            names.append(card["name"].get("zh") or guid)
        console.print("  本 mod 卖：" + "、".join(names) + ("…" if len(cards) > 20 else ""))


@app.command()
def building(query: str = typer.Argument(..., help="GUID 或建筑名")) -> None:
    """看一座建筑：区域 / 产线 / 谁影响它。"""
    doc = require(query, "buildings")
    console.print(f"[bold]{doc['name'].get('zh') or doc['name'].get('internal')}[/]  [dim]{doc['id']}[/]")
    console.print(f"  模板  {doc['template']} ｜ 族 {doc['kind']} ｜ 区域 {doc['zone_zh'] or '通用'}")
    production = doc.get("production")
    if production:
        outputs = "、".join(f"{item['name']} ×{item['amount']}" for item in production["outputs"])
        inputs = "、".join(f"{item['name']} ×{item['amount']}" for item in production["inputs"])
        console.print(f"  产出  {outputs or '—'}")
        if inputs:
            console.print(f"  原料  {inputs}")
        if production.get("fertility"):
            crop = production["fertility"].get("crop") or production["fertility"]["name"]
            console.print(f"  作物  {crop}")
        if production.get("cycle"):
            console.print(f"  周期  {production['cycle']} 秒")
    cards = [database.load_doc("cards", guid) for guid in doc.get("cards", [])[:12]]
    names = util.dedup(card["name"].get("zh") or card["id"] for card in cards if card)
    console.print("  影响它的卡  " + "、".join(names) + ("…" if len(doc["cards"]) > 12 else ""))


@app.command()
def good(query: str = typer.Argument(..., help="GUID 或商品名")) -> None:
    """看一个商品：分类 / 基准价 / 被谁用到。"""
    doc = require(query, "goods")
    console.print(f"[bold]{doc['name'].get('zh') or doc['name'].get('internal')}[/]  [dim]{doc['id']}[/]")
    category = (doc.get("category") or {}).get("name", "—")
    console.print(f"  分类  {category} ｜ 基准价 {doc['base_price']} ｜ 区域 {doc['region_zh'] or '通用'}")
    console.print("  用途  " + ("、".join(USE_ZH.get(use, use) for use in doc["used_as"]) or "—"))
    console.print(f"  相关卡  {len(doc['cards'])} 张")


@app.command()
def show(query: str = typer.Argument(..., help="任意 ID 或名字（自动识别类型）")) -> None:
    """不知道类型时用它：自动识别并打印。"""
    found = resolve(query)
    if found is None:
        raise typer.BadParameter(f"找不到 {query}")
    folder, doc = found
    if folder == "cards":
        print_card(doc)
        return
    if folder == "traders":
        trader(query)
        return
    if folder == "buildings":
        building(query)
        return
    if folder == "goods":
        good(query)
        return
    console.print(f"[bold]{doc['name'].get('zh') or doc['name'].get('internal')}[/]  [dim]{doc['id']}[/]")
    console.print(f"  类型  {doc['type']}" + (f" ｜ 模板 {doc['template']}" if doc.get("template") else ""))
    for key in ("summary", "crop", "kind", "zone_zh"):
        if doc.get(key):
            console.print(f"  {key}  {doc[key]}")
    if doc.get("cards"):
        console.print(f"  相关卡  {len(doc['cards'])} 张")


@app.command()
def config() -> None:
    """显示 anno.json 的配置与各路径是否可用。"""
    view = Table("键", "值", "来源")
    for key, value, source in config_mod.describe():
        view.add_row(key, value or "（未配置）", source)
    console.print(view)
    if not paths.GAME_DIR:
        console.print("  [yellow]game_dir 未配置：按 README 第〇节新建 anno.json，填游戏安装目录[/]")
    for label, path in (("temp", paths.TEMP), ("data", paths.DATA), ("docs", paths.DOCS),
                        ("game_dir", paths.GAME_DIR)):
        if path is None:
            continue
        mark = "✅" if path.exists() else "❌ 不存在"
        console.print(f"  {label}: {path}  {mark}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()