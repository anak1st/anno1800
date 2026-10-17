"""商人：原版档位池 + 本 mod 池，以及「谁卖」的反向归属。

商人文档的 ID 用 **Profile 资产 GUID**（`119051` = 柯提马）；
本 mod 的 `replace` 用的是档位池 GUID（`127480`），两个都记在文档里。
"""

from __future__ import annotations

from collections import Counter

from . import tables, util
from .model import AssetIndex
from .texts import Names


def profile_ref(name: str) -> dict[str, str]:
    """商人简称 -> `{id, name}`（卡牌文档的 `owners` 用这个）。"""
    guid = tables.PROFILES.get(name, ("", ""))[0]
    return {"id": guid, "name": tables.VANILLA_LABEL.get(name, name)}


def build(index: AssetIndex, card_guids: set[str], mod_pools: dict[str, list[str]],
          mod_raw: dict[str, list[str]], names: Names
          ) -> tuple[dict[str, dict], dict[str, dict[str, list[dict]]]]:
    """返回（商人文档, 卡的归属）。

    `mod_pools` 是去重后的卡 GUID；`mod_raw` 是池里的原始条目（含重复，用来报数）。
    归属形如 `{卡 GUID: {"vanilla": [{id, name}], "mod": [{id, name}]}}`。
    """
    docs: dict[str, dict] = {}
    owners: dict[str, dict[str, list[dict]]] = {}
    for pool_guid, (name, en, zones) in tables.TRADERS.items():
        profile, internal = tables.PROFILES[name]
        tiers = tables.VANILLA_TIERS.get(name, [])
        reached = index.reach(tiers) if tiers else set()
        vanilla_cards = sorted((guid for guid in reached if guid in card_guids), key=util.as_int)
        mod_cards = sorted(mod_pools.get(name, []), key=util.as_int)
        raw_entries = mod_raw.get(name, [])

        for guid in vanilla_cards:
            _add(owners.setdefault(guid, {"vanilla": [], "mod": []})["vanilla"], profile_ref(name))
        for guid in mod_cards:
            _add(owners.setdefault(guid, {"vanilla": [], "mod": []})["mod"], profile_ref(name))

        doc = {
            "id": profile,
            "type": "trader",
            "name": {"zh": names.zh(profile) or name, "en": en},
            "label": name,
            "zone": {"ids": list(zones), "zh": tables.zones_zh(zones)},
            "profile": internal,
            "pool": pool_guid,
            "vanilla": {"tiers": tiers, "cards": vanilla_cards, "count": len(vanilla_cards)},
            "mod": None,
        }
        if raw_entries or mod_cards:
            doc["mod"] = {"pool": pool_guid, "cards": mod_cards, "count": len(mod_cards),
                          **pool_stats(raw_entries, card_guids)}
        docs[profile] = doc
    return docs, owners


def _add(bucket: list[dict], ref: dict) -> None:
    """按显示名去重（两个海盗在卡表里都叫「海盗」）。"""
    if all(item["name"] != ref["name"] for item in bucket):
        bucket.append(ref)


def pool_stats(entries: list[str], known: set[str]) -> dict:
    """池子现状：条目 / 重复 / 不在卡表里的 GUID。"""
    seen = Counter(entries)
    repeated = sorted((guid for guid, count in seen.items() if count > 1), key=util.as_int)
    unknown = sorted((guid for guid in seen if guid not in known), key=util.as_int)
    return {"entries": len(entries), "duplicates": len(repeated), "repeated": repeated,
            "unknown": unknown}
