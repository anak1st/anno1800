"""归属规则（规则 5–7：殖民地归区 + 跨区生产卡双挂）的单元测试。"""

from __future__ import annotations

from dataclasses import dataclass

from anno import rules


@dataclass
class FakeCard:
    template: str = "GuildhouseItem"
    allocation: str = "GuildHouse"
    zh: str = ""
    en: str = ""
    internal: str = ""
    scenario: str = ""
    dlc: str = ""


def targets(zones: tuple[str, ...], templates: tuple[str, ...] = ("FarmBuilding",)) -> rules.CardTargets:
    return rules.CardTargets(zones=frozenset(zones), names=("农场",) * len(zones),
                             templates=frozenset(templates))


def test_single_colony_zone_goes_to_local_merchant() -> None:
    assert rules.decide(FakeCard(), targets(("Africa",))) == rules.Decision(("柯提马",), "5 安贝沙")
    assert rules.decide(FakeCard(), targets(("Arctic",))) == rules.Decision(("库马克",), "6 北极")
    assert rules.decide(FakeCard(), targets(("Colony01",))) == rules.Decision(("萨曼托",), "7 新世界")


def test_cross_world_production_card_hangs_on_both_merchants() -> None:
    assert rules.decide(FakeCard(), targets(("Africa", "Colony01"))) == rules.Decision(
        ("柯提马", "萨曼托"), "5 安贝沙+7 新世界")


def test_three_colonies_hang_on_all_three() -> None:
    assert rules.decide(FakeCard(), targets(("Africa", "Arctic", "Colony01"))).merchants == (
        "柯提马", "库马克", "萨曼托")


def test_non_production_cross_world_card_is_not_dual_hung() -> None:
    card = FakeCard(template="TownhallItem", allocation="TownHall")
    assert rules.decide(card, targets(("Africa", "Colony01"), templates=("ResidenceBuilding",))
                        ) == rules.Decision(("卡希纳",), "10 人口")


def test_cards_touching_the_old_world_are_not_regional() -> None:
    assert rules.decide(FakeCard(), targets(("Moderate", "Africa"))) == rules.Decision(("伊莱",), "9 生产")


def test_no_targets_is_not_regional() -> None:
    assert rules.colony_of(targets(())) is None
