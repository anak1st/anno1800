"""辅助概念的文档：目标组 / 建筑 / 商品 / 作物 / 套装 / DLC / Buff。

输入是卡牌文档（已经算好引用），输出是 `data/<概念>/<GUID>.json` 的内容。
反向引用（`cards`）在这里一次算好，浏览器里点开一个建筑就能看到谁影响它。
"""

from __future__ import annotations

from collections import defaultdict

from . import effects, placement, tables, util
from .model import AssetIndex, RawValues
from .texts import Names


def build(index: AssetIndex, card_docs: dict[str, dict], names: Names) -> dict[str, dict[str, dict]]:
    """返回 `{目录名: {GUID: 文档}}`。"""
    refs = Refs()
    for guid, doc in card_docs.items():
        refs.collect(index, guid, doc)

    return {
        "target-groups": _groups(index, refs, names),
        "buildings": _buildings(index, refs, names),
        "goods": _goods(index, refs, names),
        "fertilities": _fertilities(refs, names),
        "item-sets": _simple(refs.item_sets, "item-set", names),
        "dlc": _simple(refs.dlc, "dlc", names),
        "buffs": _buffs(index, refs, names),
    }


class Refs:
    """卡片文档里出现过的所有外部引用（反向索引的原料）。"""

    def __init__(self) -> None:
        self.groups: dict[str, set[str]] = defaultdict(set)
        self.buildings: dict[str, set[str]] = defaultdict(set)
        self.goods: dict[str, set[str]] = defaultdict(set)
        self.good_use: dict[str, set[str]] = defaultdict(set)
        self.fertilities: dict[str, set[str]] = defaultdict(set)
        self.item_sets: dict[str, set[str]] = defaultdict(set)
        self.dlc: dict[str, set[str]] = defaultdict(set)
        self.buffs: dict[str, set[str]] = defaultdict(set)

    def collect(self, index: AssetIndex, guid: str, doc: dict) -> None:
        targets = doc.get("targets") or {}
        for ref in targets.get("refs", []):
            bucket = self.groups if ref.get("kind") == "group" else self.buildings
            bucket[ref["id"]].add(guid)
        for ref in targets.get("buildings", []):
            self.buildings[ref["id"]].add(guid)

        effect = doc.get("effects") or {}
        for bonus in effect.get("bonuses", []):
            if bonus.get("key") == "crop" and bonus.get("ref"):
                self.fertilities[bonus["ref"]["id"]].add(guid)
            elif bonus.get("key") == "workforce_goods" and bonus.get("ref"):
                self._good(bonus["ref"]["id"], guid, "workforce")
        for extra in effect.get("extra_outputs", []):
            if extra.get("product"):
                self._good(extra["product"]["id"], guid, "output")
        for change in effect.get("replace_inputs", []):
            self._good(change["from"]["id"], guid, "input")
            self._good(change["to"]["id"], guid, "input")
        for item in effect.get("input_amounts", []):
            if item.get("product"):
                self._good(item["product"]["id"], guid, "input")
        for need in effect.get("need_consumption", []):
            if need.get("ref"):
                self._good(need["ref"]["id"], guid, "need")
        for change in effect.get("need_substitutes", []):
            self._good(change["ref"]["id"], guid, "need")
            self._good(change["substitute"]["id"], guid, "need")
        for cost in doc.get("recipe", []):
            self._good(cost["product"]["id"], guid, "recipe")
        if doc.get("item_set"):
            self.item_sets[doc["item_set"]["id"]].add(guid)
        for ref in doc.get("dlc", []):
            self.dlc[ref["id"]].add(guid)
        buff = (doc.get("action") or {}).get("buff")
        if buff:
            self.buffs[buff["id"]].add(guid)

        # 目标建筑的产线会引用商品：把那些商品也收进来
        for ref in targets.get("buildings", []):
            production = index.production.get(ref["id"])
            if production is None:
                continue
            for product, _amount in production.inputs:
                self._good(product, guid, "input")
            for product, _amount in production.outputs:
                self._good(product, guid, "output")
            if production.fertility:
                self.fertilities[production.fertility].add(guid)

    def _good(self, guid: str, card: str, use: str) -> None:
        self.goods[guid].add(card)
        self.good_use[guid].add(use)


# ---------------------------------------------------------------------- 目标组
def _groups(index: AssetIndex, refs: Refs, names: Names) -> dict[str, dict]:
    docs: dict[str, dict] = {}
    for guid, cards in refs.groups.items():
        facts = index.facts.get(guid)
        members = []
        zones: set[str] = set()
        for member in facts.members if facts else ():
            zone = index.zone(member)
            if zone in tables.ZONE_VALUES:
                zones.add(zone)
            members.append({**names.ref(member),
                            "kind": placement.building_kind(index.field(member, "tpl")),
                            "zone": zone})
        docs[guid] = {
            "id": guid,
            "type": "target-group",
            "name": {"zh": names.zh(guid), "internal": names.internal(guid)},
            "members": members,
            "zones": [zone for zone in tables.ZONE_VALUES if zone in zones],
            "zones_zh": [tables.ZONE_ZH[zone] for zone in tables.ZONE_VALUES if zone in zones],
            "cards": sorted(cards, key=util.as_int),
        }
    return docs


# ---------------------------------------------------------------------- 建筑
def _buildings(index: AssetIndex, refs: Refs, names: Names) -> dict[str, dict]:
    docs: dict[str, dict] = {}
    for guid, cards in refs.buildings.items():
        zone = index.zone(guid)
        production = index.production.get(guid)
        docs[guid] = {
            "id": guid,
            "type": "building",
            "name": {"zh": names.zh(guid), "internal": names.internal(guid)},
            "template": index.field(guid, "tpl"),
            "kind": placement.building_kind(index.field(guid, "tpl")),
            "zone": zone,
            "zone_zh": tables.ZONE_ZH.get(zone, ""),
            "production": _production_doc(production, names) if production else None,
            "cards": sorted(cards, key=util.as_int),
        }
    return docs


def _production_doc(production, names: Names) -> dict:
    return {
        "inputs": [{**names.ref(product), "amount": amount} for product, amount in production.inputs],
        "outputs": [{**names.ref(product), "amount": amount} for product, amount in production.outputs],
        "fertility": ({**names.ref(production.fertility), "crop": effects.crop_name(names.label(production.fertility))}
                          if production.fertility else None),
        "cycle": production.cycle,
    }


# ---------------------------------------------------------------------- 商品
def _goods(index: AssetIndex, refs: Refs, names: Names) -> dict[str, dict]:
    docs: dict[str, dict] = {}
    for guid, cards in refs.goods.items():
        facts = index.products.get(guid)
        region = facts.region if facts else ""
        docs[guid] = {
            "id": guid,
            "type": "good",
            "name": {"zh": names.zh(guid), "internal": names.internal(guid)},
            "category": names.ref(facts.category) if facts and facts.category else None,
            "base_price": facts.base_price if facts else None,
            "civ_level": facts.civ_level if facts else None,
            "region": region,
            "region_zh": tables.ZONE_ZH.get(region, ""),
            "used_as": sorted(refs.good_use[guid]),
            "cards": sorted(cards, key=util.as_int),
        }
    return docs


# ---------------------------------------------------------------------- 作物
def _fertilities(refs: Refs, names: Names) -> dict[str, dict]:
    docs: dict[str, dict] = {}
    for guid, cards in refs.fertilities.items():
        label = names.label(guid)
        docs[guid] = {
            "id": guid,
            "type": "fertility",
            "name": {"zh": names.zh(guid), "internal": names.internal(guid)},
            "crop": effects.crop_name(label),
            "cards": sorted(cards, key=util.as_int),
        }
    return docs


# ---------------------------------------------------------------------- 套装 / DLC
def _simple(refs: dict[str, set[str]], kind: str, names: Names) -> dict[str, dict]:
    return {guid: {"id": guid, "type": kind,
                   "name": {"zh": names.zh(guid), "internal": names.internal(guid)},
                   "cards": sorted(cards, key=util.as_int)}
            for guid, cards in refs.items()}


# ---------------------------------------------------------------------- Buff
def _buffs(index: AssetIndex, refs: Refs, names: Names) -> dict[str, dict]:
    docs: dict[str, dict] = {}
    for guid, cards in refs.buffs.items():
        values = index.buffs.get(guid, RawValues())
        effect = effects.effects(values, names)
        docs[guid] = {
            "id": guid,
            "type": "buff",
            "name": {"zh": names.zh(guid), "internal": names.internal(guid)},
            "template": index.field(guid, "tpl"),
            "effects": effect,
            "summary": effects.summary(effect, effects.expedition(values), None),
            "cards": sorted(cards, key=util.as_int),
        }
    return docs
