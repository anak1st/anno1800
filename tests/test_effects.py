"""效果解析的单元测试：直接喂 `RawValues`，不读 XML。"""

from __future__ import annotations

from anno import effects
from anno.model import RawValues


class FakeNames:
    """只回名字的最小解析器。"""

    def __init__(self, table: dict[str, str]) -> None:
        self._table = table

    def zh(self, guid: str) -> str:
        return self._table.get(guid, "")

    def label(self, guid: str) -> str:
        return self._table.get(guid, guid)

    def ref(self, guid: str) -> dict[str, str]:
        return {"id": guid, "name": self.label(guid)}


def values(*entries: tuple[str, str]) -> RawValues:
    return RawValues(tuple(entries))


def test_productivity_and_maintenance() -> None:
    parsed = effects.effects(values(
        ("FactoryUpgrade/ProductivityUpgrade/Value", "20"),
        ("FactoryUpgrade/ProductivityUpgrade/Percental", "1"),
        ("BuildingUpgrade/MaintenanceUpgrade/Value", "20"),
    ), FakeNames({}))
    keys = {bonus["key"]: bonus["value"] for bonus in parsed["bonuses"]}
    assert keys == {"productivity": 20, "maintenance": 20}
    assert effects.summary(parsed) == "生产力 +20%；维护费 +20%"


def test_crop_uses_fertility_name() -> None:
    parsed = effects.effects(values(("FactoryUpgrade/AddedFertility", "114348")),
                             FakeNames({"114348": "辛香料生产力"}))
    bonus = parsed["bonuses"][0]
    assert bonus["key"] == "crop"
    assert bonus["crop"] == "辛香料"
    assert "新增作物「辛香料」" in effects.summary(parsed)


def test_extra_output_and_replace_inputs() -> None:
    parsed = effects.effects(values(
        ("FactoryUpgrade/AdditionalOutput/Item/Product", "114369"),
        ("FactoryUpgrade/AdditionalOutput/Item/Amount", "1"),
        ("FactoryUpgrade/AdditionalOutput/Item/AdditionalOutputCycle", "2"),
        ("FactoryUpgrade/AdditionalOutput/Item/ForceProductSameAsFactoryOutput", "1"),
        ("FactoryUpgrade/ReplaceInputs/Item/OldInput", "5383"),
        ("FactoryUpgrade/ReplaceInputs/Item/NewInput", "114364"),
    ), FakeNames({"114369": "香料", "5383": "药草", "114364": "木槿花瓣"}))
    assert parsed["extra_outputs"][0]["cycle"] == 2
    assert parsed["replace_inputs"][0] == {"from": {"id": "5383", "name": "药草"},
                                           "to": {"id": "114364", "name": "木槿花瓣"}}
    text = effects.summary(parsed)
    assert "每 2 周期额外产出 1 个同种产物" in text
    assert "药草 → 木槿花瓣" in text


def test_expedition_and_action() -> None:
    travel = effects.expedition(values(
        ("ExpeditionAttribute/BaseMorale", "10"),
        ("ExpeditionAttribute/ExpeditionAttributes/Item/Attribute", "Medicine"),
        ("ExpeditionAttribute/ExpeditionAttributes/Item/Amount", "20"),
        ("ExpeditionAttribute/ItemDifficulties", "Easy;Average"),
    ))
    assert travel["morale"] == 10
    assert travel["attributes"] == [{"key": "Medicine", "zh": "医疗", "value": 20}]
    assert [item["zh"] for item in travel["difficulties"]] == ["简单", "平均"]

    act = effects.action(values(
        ("ItemAction/ItemAction", "HEAL_INCIDENT"),
        ("ItemAction/Charges", "3"),
        ("ItemAction/ActiveBuff", "114891"),
    ), FakeNames({"114891": "急救包"}))
    assert act["label"] == "平息事件"
    assert act["charges"] == 3
    assert act["buff"]["name"] == "急救包"


def test_pier_speed_and_passive_goods() -> None:
    """霍加斯这类港口专家：码头装卸速度 + 被动产出（GenPool 解析成商品名）。"""
    parsed = effects.effects(values(
        ("PierUpgrade/PierSpeedUpgrade/Value", "100"),
        ("PassiveTradeGoodGenUpgrade/GenProbability", "30"),
        ("PassiveTradeGoodGenUpgrade/GenPool", "193483"),
    ), FakeNames({"193483": "Trelawney Logistics"}), pool_names=lambda guid: ["咖啡", "金"])
    keys = {bonus["key"] for bonus in parsed["bonuses"]}
    assert {"pier_speed", "passive_goods"} <= keys
    text = effects.summary(parsed)
    assert "码头装卸速度 +100%" in text
    assert "每周期 30% 概率被动产出（咖啡、金）" in text
    assert parsed["other"] == []


def test_no_effect_is_reported() -> None:
    assert effects.summary(effects.effects(values(), FakeNames({}))) == "（无直接数值效果）"


def test_crop_name_strips_suffix() -> None:
    assert effects.crop_name("辛香料生产力") == "辛香料"
    assert effects.crop_name("Spices Fertility") == "Spices"
    assert effects.crop_name("鱼繁殖地") == "鱼繁殖地"
