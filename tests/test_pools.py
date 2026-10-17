"""卡池排版 / 归属写入的单元测试（纯函数）。"""

from __future__ import annotations

from dataclasses import dataclass

from anno import pools


@dataclass
class FakeCard:
    template: str = "GuildhouseItem"
    allocation: str = "GuildHouse"
    zh: str = ""
    en: str = ""
    internal: str = ""
    scenario: str = ""
    rarity: str = ""


def test_pool_groups_put_unknown_guids_in_their_own_bucket() -> None:
    entries = [pools.PoolEntry("958"), pools.PoolEntry("424242")]
    known = {"958": FakeCard()}
    grouped = pools.groups(entries, known)
    assert grouped["建筑"]["工会"] == ["958"]
    assert grouped["其他"][pools.UNKNOWN_GROUP] == ["424242"]


def test_apply_assignment_can_hang_one_card_on_two_merchants() -> None:
    """跨新世界+安贝沙的生产卡：两家各一条，权重沿用。"""
    pool_map = {"萨曼托": [pools.PoolEntry("125131", "25")], "柯提马": []}
    pools.apply_assignment(pool_map, {"125131": ("柯提马", "萨曼托")})
    assert pool_map["柯提马"] == [pools.PoolEntry("125131", "25")]
    assert pool_map["萨曼托"] == [pools.PoolEntry("125131", "25")]


def test_apply_assignment_drops_stale_owner() -> None:
    pool_map = {"伊莱": [pools.PoolEntry("125131")], "柯提马": []}
    pools.apply_assignment(pool_map, {"125131": ("柯提马",)})
    assert pool_map["伊莱"] == []
    assert [entry.guid for entry in pool_map["柯提马"]] == ["125131"]
