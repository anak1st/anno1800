"""把 `Values` 原文解释成结构化效果 —— 卡牌文档的「效果」就来自这里。

输入是 `model.RawValues`（相对路径 → 文本，保留文档顺序），输出是可直接落盘的 dict，
所以这一层**不碰 XML，可以纯函数测试**：

    effects(values, names)     -> bonuses / extra_outputs / replace_inputs / input_amounts / other
    expedition(values)         -> 士气 / 属性 / 难度 / 可用区域
    action(values, names)      -> 使用动作（平息事件 / 布雷 …）+ 给的 Buff
    summary(...)               -> 一句话给人看

加一种新效果 = 在 `BONUS_SPECS` 里加一行；三个"要看上下文"的（额外产出 / 换原料 /
新增作物）由专门函数处理。
"""

from __future__ import annotations

from dataclasses import dataclass

from . import tables, util
from .model import RawValues
from .texts import Names

# 特殊处理器的前缀：这些路径下的叶子由专门函数消费，不算「未归类」
SPECIAL_PREFIXES: tuple[str, ...] = (
    "FactoryUpgrade/AdditionalOutput",
    "FactoryUpgrade/ReplaceInputs",
    "FactoryUpgrade/InputAmountUpgrade",
    "FactoryUpgrade/AddedFertility",
    "ResidenceUpgrade/GoodConsumptionUpgrade",
    "ResidenceUpgrade/NeedProvideNeedUpgrade",
    "PopulationUpgrade/InputBenefitModifier",
    "BuildingUpgrade/ReplacingWorkforce",
)


@dataclass(frozen=True)
class Spec:
    """一条「字段 → 效果」的声明。"""

    path: str
    key: str
    label: str
    unit: str = "%"
    group: str = "misc"


BONUS_SPECS: tuple[Spec, ...] = (
    # 生产 / 建筑
    Spec("FactoryUpgrade/ProductivityUpgrade/Value", "productivity", "生产力", group="production"),
    Spec("BuildingUpgrade/MaintenanceUpgrade/Value", "maintenance", "维护费", group="building"),
    Spec("BuildingUpgrade/WorkforceAmountUpgrade/Value", "workforce", "所需劳动力", group="building"),
    Spec("ModuleOwnerUpgrade/ModuleLimitPercent", "module_limit", "模块上限", group="building"),
    Spec("BuildingUpgrade/PublicServiceFullSatisfactionDistance/Value",
         "service_range_full", "服务范围（满）", unit="", group="range"),
    Spec("BuildingUpgrade/PublicServiceNoSatisfactionDistance/Value",
         "service_range_zero", "服务范围（零）", unit="", group="range"),
    # 文化
    Spec("CultureUpgrade/AttractivenessUpgrade/Value", "attractiveness", "吸引力", unit="", group="culture"),
    Spec("CultureUpgrade/ItemSetUpgrade/Item/AttractivenessUpgradePercent",
         "set_attractiveness", "套装吸引力", group="culture"),
    # 住所 / 人口
    Spec("ResidenceUpgrade/AdditionalHappiness", "happiness", "幸福度", unit="", group="residence"),
    Spec("ResidenceUpgrade/TaxModifierInPercent", "tax", "税收", group="residence"),
    Spec("ResidenceUpgrade/WorkforceModifierInPercent", "workforce_mod", "劳动力", group="residence"),
    Spec("PopulationUpgrade/ResidentsUpgrade/Value", "residents", "居民", unit="", group="population"),
    # 事件
    Spec("IncidentInfectableUpgrade/IncidentFireIncreaseUpgrade/Value", "fire", "火灾风险", group="incident"),
    Spec("IncidentInfectableUpgrade/IncidentRiotIncreaseUpgrade/Value", "riot", "暴动风险", group="incident"),
    Spec("IncidentInfectableUpgrade/IncidentIllnessIncreaseUpgrade/Value", "illness", "疾病风险", group="incident"),
    Spec("IncidentInfectableUpgrade/IncidentExplosionIncreaseUpgrade/Value",
         "explosion", "爆炸风险", group="incident"),
    # 船 / 载具
    Spec("VehicleUpgrade/ForwardSpeedUpgrade/Value", "speed", "速度", group="ship"),
    Spec("VehicleUpgrade/IgnoreWeightFactorUpgrade/Value", "weight", "载重", group="ship"),
    Spec("VehicleUpgrade/IgnoreDamageFactorUpgrade/Value", "damage_reduction", "损伤减免", group="ship"),
    Spec("VehicleUpgrade/MaintainanceUpgrade/Value", "ship_maintenance", "维护费", group="ship"),
    Spec("AttackerUpgrade/BaseDamageUpgrade/Value", "damage", "伤害", group="ship"),
    Spec("AttackerUpgrade/AttackSpeedUpgrade", "attack_speed", "攻速", group="ship"),
    Spec("AttackerUpgrade/AttackRangeUpgrade/Value", "attack_range", "射程", group="ship"),
    Spec("AttackableUpgrade/MaxHitpointsUpgrade/Value", "hitpoints", "耐久", group="ship"),
    Spec("AttackableUpgrade/SelfHealUpgrade/Value", "self_heal", "自愈", group="ship"),
    # 其他
    Spec("EcoSystemProviderUpgrade/DeltaValueUpgrade/Value", "eco", "生态", group="misc"),
    Spec("IrrigationUpgrade/...", "irrigation", "灌溉", group="misc"),
)
# 占位/未知路径不参与（保留结构，删掉这条即可）
BONUS_SPECS = tuple(spec for spec in BONUS_SPECS if not spec.path.endswith("..."))


# ---------------------------------------------------------------------- 效果
def effects(values: RawValues, names: Names) -> dict:
    """`Values` → 结构化效果。"""
    bonuses: list[dict] = []
    used: set[str] = set()

    for spec in BONUS_SPECS:
        raw = values.get(spec.path)
        value = util.number(raw) if raw else None
        if value is None:
            continue
        used.add(spec.path)
        bonuses.append({"key": spec.key, "label": spec.label, "value": value,
                        "unit": spec.unit, "group": spec.group})

    for guid in values.all("FactoryUpgrade/AddedFertility"):
        bonuses.append({"key": "crop", "label": "新增作物", "group": "production",
                        "ref": names.ref(guid), "crop": crop_name(names.label(guid))})

    bonuses += _population_benefits(values, names)
    for guid in values.all("BuildingUpgrade/ReplacingWorkforce"):
        bonuses.append({"key": "workforce_goods", "label": "劳动力替代", "group": "building",
                        "ref": names.ref(guid)})

    return {
        "bonuses": bonuses,
        "extra_outputs": _extra_outputs(values, names),
        "replace_inputs": _replace_inputs(values, names),
        "input_amounts": _input_amounts(values, names),
        "need_consumption": _need_consumption(values, names),
        "need_substitutes": _need_substitutes(values, names),
        "other": _other(values, used),
    }


def _population_benefits(values: RawValues, names: Names) -> list[dict]:
    """居民投入产出：额外供给 / 收入 / 幸福度，绑在某个商品上。"""
    labels = (("AdditionalSupply", "supply", "额外供给", ""),
              ("AdditionalMoney", "money", "收入", ""),
              ("AdditionalHappiness", "happiness", "幸福度", ""))
    out: list[dict] = []
    for item in values.items("PopulationUpgrade/InputBenefitModifier"):
        product = names.ref(item.get("Product", "")) if item.get("Product") else None
        for field, key, label, unit in labels:
            value = util.number(item.get(field, ""))
            if value is None:
                continue
            out.append({"key": key, "label": label, "value": value, "unit": unit,
                        "group": "population", "ref": product})
    return out


def _extra_outputs(values: RawValues, names: Names) -> list[dict]:
    out: list[dict] = []
    for item in values.items("FactoryUpgrade/AdditionalOutput"):
        product = item.get("Product", "")
        out.append({
            "product": names.ref(product) if product else None,
            "amount": util.number(item.get("Amount", "")) or 1,
            "cycle": util.number(item.get("AdditionalOutputCycle", "")) or 1,
            "same_as_output": item.get("ForceProductSameAsFactoryOutput") == "1",
        })
    return out


def _replace_inputs(values: RawValues, names: Names) -> list[dict]:
    out: list[dict] = []
    for item in values.items("FactoryUpgrade/ReplaceInputs"):
        old, new = item.get("OldInput", ""), item.get("NewInput", "")
        if old and new:
            out.append({"from": names.ref(old), "to": names.ref(new)})
    return out


def _input_amounts(values: RawValues, names: Names) -> list[dict]:
    out: list[dict] = []
    for item in values.items("FactoryUpgrade/InputAmountUpgrade"):
        product = item.get("Product", "")
        amount = util.number(item.get("Amount", ""))
        if product and amount is not None:
            out.append({"product": names.ref(product), "amount": amount})
    return out


def _need_consumption(values: RawValues, names: Names) -> list[dict]:
    """住所：某个需求商品的消耗量变化。"""
    out: list[dict] = []
    for item in values.items("ResidenceUpgrade/GoodConsumptionUpgrade"):
        need = item.get("ProvidedNeed", "")
        value = util.number(item.get("AmountInPercent", ""))
        if need and value is not None:
            out.append({"key": "need_consumption", "label": "需求消耗", "value": value,
                        "unit": "%", "group": "residence", "ref": names.ref(need)})
    return out


def _need_substitutes(values: RawValues, names: Names) -> list[dict]:
    """住所：A 顶替 B（需求替换）。"""
    out: list[dict] = []
    for item in values.items("ResidenceUpgrade/NeedProvideNeedUpgrade"):
        provided, substitute = item.get("ProvidedNeed", ""), item.get("SubstituteNeed", "")
        if provided and substitute:
            out.append({"key": "need_substitute", "label": "需求替换", "group": "residence",
                        "ref": names.ref(provided), "substitute": names.ref(substitute)})
    return out


def _other(values: RawValues, used: set[str]) -> list[dict]:
    """没归一化的数值叶子 —— 兜底，保证浏览器里不丢数据。"""
    other: list[dict] = []
    for path, raw in values.entries:
        if path in used or path.endswith("Percental"):
            continue
        if any(path == prefix or path.startswith(prefix + "/") for prefix in SPECIAL_PREFIXES):
            continue
        value = util.number(raw)
        if value is not None:
            other.append({"path": path, "value": value})
    return other


# ---------------------------------------------------------------------- 远征
def expedition(values: RawValues) -> dict | None:
    """远征属性：士气 / 属性 / 难度 / 可用区域；没有就返回 None。"""
    attributes: list[dict] = []
    for item in values.items("ExpeditionAttribute/ExpeditionAttributes"):
        key = item.get("Attribute", "")
        if not key:
            continue
        attributes.append({"key": key, "zh": tables.EXPEDITION_ATTR_ZH.get(key, key),
                           "value": util.number(item.get("Amount", "")) or 0})
    morale = util.number(values.get("ExpeditionAttribute/BaseMorale", ""))
    difficulties = _enum(values.get("ExpeditionAttribute/ItemDifficulties", ""),
                         tables.EXPEDITION_DIFFICULTY_ZH)
    regions = _enum(values.get("ExpeditionAttribute/ItemRegions", ""), tables.EXPEDITION_REGION_ZH)
    if not (attributes or morale or difficulties or regions):
        return None
    return {"morale": morale or 0, "attributes": attributes,
            "difficulties": difficulties, "regions": regions}


def _enum(text: str, mapping: dict[str, str]) -> list[dict]:
    return [{"key": part, "zh": mapping.get(part, part)}
            for part in (piece.strip() for piece in text.split(";")) if part]


# ---------------------------------------------------------------------- 使用动作
def action(values: RawValues, names: Names) -> dict | None:
    """使用型道具的动作 + 它给的 Buff。"""
    kind = values.get("ItemAction/ItemAction", "")
    buff = values.get("ItemAction/ActiveBuff", "")
    if not kind and not buff:
        return None
    description = values.get("ItemAction/ActionDescription", "")
    return {
        "kind": kind,
        "label": tables.ITEM_ACTION_ZH.get(kind, kind or "使用"),
        "duration_ms": util.number(values.get("ItemAction/ActionDuration", "")),
        "charges": util.number(values.get("ItemAction/Charges", "")),
        "cooldown_ms": util.number(values.get("ItemAction/ActionCooldown", "")),
        "scope": values.get("ItemAction/ActionScope", ""),
        "distance": util.number(values.get("ItemAction/ActionDistance", "")),
        "description": names.zh(description) if description else "",
        "buff": names.ref(buff) if buff else None,
    }


# ---------------------------------------------------------------------- 摘要
def summary(effect: dict, travel: dict | None = None, act: dict | None = None, limit: int = 200) -> str:
    """一句话描述这张卡做什么。"""
    parts: list[str] = []
    for bonus in effect["bonuses"]:
        parts.append(_bonus_text(bonus))
    for extra in effect["extra_outputs"]:
        same = "同种产物" if extra["same_as_output"] else (extra["product"] or {}).get("name", "产物")
        parts.append(f"每 {extra['cycle']} 周期额外产出 {extra['amount']} 个{same}")
    for item in effect["input_amounts"]:
        parts.append(f"{(item['product'] or {}).get('name', '原料')} 用量 {signed(item['amount'])}")
    for change in effect["replace_inputs"]:
        parts.append(f"{change['from']['name']} → {change['to']['name']}")
    for need in effect["need_consumption"]:
        parts.append(f"{(need['ref'] or {}).get('name', '需求')} 消耗 {signed(need['value'])}%")
    for change in effect.get("need_substitutes", []):
        parts.append(f"{change['ref']['name']} 顶替 {change['substitute']['name']}")
    if travel:
        names = "、".join(f"{attr['zh']} {signed(attr['value'])}"
                         for attr in travel["attributes"] if attr["value"])
        perks = "、".join(attr["zh"] for attr in travel["attributes"] if not attr["value"])
        text = "、".join(piece for piece in (names, perks) if piece)
        if text:
            parts.append(f"远征：{text}")
    if act:
        parts.append(f"使用：{act['label']}")
    return util.truncate("；".join(part for part in parts if part) or "（无直接数值效果）", limit)


def _bonus_text(bonus: dict) -> str:
    if "ref" in bonus:
        name = (bonus["ref"] or {}).get("name", "")
        return f"{bonus['label']}「{bonus.get('crop') or name}」" if name else bonus["label"]
    value = bonus["value"]
    if not value:
        return ""
    return f"{bonus['label']} {signed(value)}{bonus['unit']}"


def signed(value) -> str:
    """`+20` / `−50` —— 用真减号，表格里对齐更好看。"""
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return f"−{abs(value)}" if value < 0 else f"+{value}"


def crop_name(label: str) -> str:
    """「辛香料生产力」→「辛香料」。"""
    for suffix in ("生产力", " Fertility"):
        if label.endswith(suffix):
            return label[: -len(suffix)].strip()
    return label
