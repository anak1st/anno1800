"""归类与装槽的单元测试（纯函数，不读游戏数据）。"""

from __future__ import annotations

from dataclasses import dataclass

from anno import placement


@dataclass
class FakeCard:
    """只带归类用得着的字段。"""

    template: str = ""
    zh: str = ""
    en: str = ""
    internal: str = ""
    scenario: str = ""
    allocation: str = ""
    rarity: str = ""
    quest_object: bool = False


def test_slot_comes_from_allocation() -> None:
    assert placement.place(FakeCard(template="GuildhouseItem", allocation="GuildHouse")) == "工会"
    assert placement.place(FakeCard(template="ShipSpecialist", allocation="DivingVessel")) == "打捞船"


def test_scenario_wins_over_slot() -> None:
    card = FakeCard(template="GuildhouseItem", allocation="GuildHouse", scenario="650")
    assert placement.place(card) == "剧本专用"


def test_campaign_slots_are_quest_items() -> None:
    assert placement.place(FakeCard(template="VehicleItem", allocation="AarhantShip")) == "任务道具"


def test_item_with_ui_is_decided_before_slot() -> None:
    assert placement.place(FakeCard(template="ItemWithUI", allocation="Headquarter")) == "无装槽的其他物品"


def test_item_with_ui_splits_by_name() -> None:
    assert placement.place(FakeCard(template="ItemWithUI", zh="藏宝图：海湾")) == "地图 / 探险点"
    assert placement.place(FakeCard(template="ItemWithUI", zh="未找回的配方")) == "任务道具"
    assert placement.place(FakeCard(template="ItemWithUI", zh="黑胶唱片：大河")) == "黑胶唱片"
    assert placement.place(FakeCard(template="ItemWithUI", zh="随便什么东西")) == "无装槽的其他物品"


def test_quest_objects_are_quest_items() -> None:
    """ItemWithUI + 触发任务/阅读动作（游戏字段）→ 任务道具，不靠名字猜。"""
    assert placement.place(FakeCard(template="ItemWithUI", zh="被囚禁的海豚",
                                    quest_object=True)) == "任务道具"
    assert placement.place(FakeCard(template="ItemWithUI", zh="被囚禁的海豚")) == "无装槽的其他物品"


def test_decorations_are_dropped() -> None:
    assert placement.place(FakeCard(template="FluffItem")) is None
    assert placement.place(FakeCard(template="ScenarioWorkshopItem")) is None


def test_big_class_and_world_label() -> None:
    assert placement.big_of("工会") == "建筑"
    assert placement.big_of("军舰") == "载具"
    assert placement.big_of("博物馆") == "娱乐"
    assert placement.big_of("任务道具") == "其他"
    assert placement.world_label({"Moderate", "Colony01"}) == "旧世界+新世界"
    assert placement.world_label(set()) == "通用"


def test_building_kind() -> None:
    assert placement.building_kind("FarmBuilding") == "farm"
    assert placement.building_kind("FactoryBuilding7") == "factory"
    assert placement.building_kind("ResidenceBuilding7_Colony") == "residence"
    assert placement.building_kind("Mall") == "shop"
