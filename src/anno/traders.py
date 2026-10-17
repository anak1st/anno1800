"""商人：原版档位池 + 本 mod 卡池（由规则算出，不读 mod 文件）。

商人文档的 ID 用 **Profile 资产 GUID**（`119051` = 柯提马）；
本 mod 的档位池 GUID（`127480`）也记在文档里，但池子里有什么**由 `rules` 决定** ——
mod 的 `assets.xml` 是这个流程的**输出**，不是输入。
"""

from __future__ import annotations

from . import tables, util
from .model import AssetIndex
from .texts import Names

TRADER_ORDER: list[str] = [name for name, _en, _zones in tables.TRADERS.values()]


def order_names(names) -> list[str]:
    """按商人的规范顺序排（= 卡池文件里 7 家的顺序）。"""
    return sorted(names, key=lambda name: TRADER_ORDER.index(name) if name in TRADER_ORDER else len(TRADER_ORDER))


def profile_ref(name: str) -> dict[str, str]:
    """商人简称 -> `{id, name}`（卡牌文档的 `owners` 用这个）。"""
    guid = tables.PROFILES.get(name, ("", ""))[0]
    return {"id": guid, "name": tables.VANILLA_LABEL.get(name, name)}


def vanilla_owners(index: AssetIndex, card_guids: set[str]) -> dict[str, dict[str, list[dict]]]:
    """`{卡 GUID: {"vanilla": [{id, name}]}}` —— 原版谁卖，来自游戏档位池。"""
    owners: dict[str, dict[str, list[dict]]] = {}
    for name, tiers in tables.VANILLA_TIERS.items():
        if not tiers:
            continue
        for guid in index.reach(tiers):
            if guid in card_guids:
                _add(owners.setdefault(guid, {"vanilla": [], "mod": []})["vanilla"],
                     profile_ref(name))
    return owners


def build(index: AssetIndex, card_guids: set[str], mod_owners: dict[str, tuple[str, ...]],
          names: Names) -> tuple[dict[str, dict], dict[str, dict[str, list[dict]]]]:
    """返回（商人文档, 卡的归属）。

    `mod_owners` 是 `{卡 GUID: (商人简称, …)}`，来自 `rules.mod_plan`。
    归属形如 `{卡 GUID: {"vanilla": [{id, name}], "mod": [{id, name}]}}`。
    """
    docs: dict[str, dict] = {}
    owners: dict[str, dict[str, list[dict]]] = {}
    for pool_guid, (name, en, zones) in tables.TRADERS.items():
        profile, internal = tables.PROFILES[name]
        tiers = tables.VANILLA_TIERS.get(name, [])
        reached = index.reach(tiers) if tiers else set()
        vanilla_cards = sorted((guid for guid in reached if guid in card_guids), key=util.as_int)
        mod_cards = sorted((guid for guid, merchants in mod_owners.items() if name in merchants),
                           key=util.as_int)

        for guid in vanilla_cards:
            _add(owners.setdefault(guid, {"vanilla": [], "mod": []})["vanilla"], profile_ref(name))
        for guid in mod_cards:
            _add(owners.setdefault(guid, {"vanilla": [], "mod": []})["mod"], profile_ref(name))

        doc = {
            "id": profile,
            "type": "trader",
            "name": {"zh": names.zh(profile) or name, "en": en},
            "label": name,
            "zone": {"ids": list(zones), "zh": tables.TRADER_ZONE_LABEL.get(name) or tables.zones_zh(zones)},
            "profile": internal,
            "pool": pool_guid,
            "vanilla": {"tiers": tiers, "cards": vanilla_cards, "count": len(vanilla_cards)},
            "mod": None,
        }
        if mod_cards:
            # 规则算出来的池子天然没有重复、也不会有卡表外的 GUID
            doc["mod"] = {"pool": pool_guid, "cards": mod_cards, "count": len(mod_cards),
                          "entries": len(mod_cards), "duplicates": 0,
                          "repeated": [], "unknown": []}
        docs[profile] = doc
    return docs, owners


def _add(bucket: list[dict], ref: dict) -> None:
    """按显示名去重（两个海盗在卡表里都叫「海盗」）。"""
    if all(item["name"] != ref["name"] for item in bucket):
        bucket.append(ref)
