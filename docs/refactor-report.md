# 读取 / 分析 / 卡牌模型 结构审查与重构建议

> 报告日期：2026-10-17 ｜ 对象：`src/game`（读取）、`src/cards`（装配与文档）、`src/merchants`（归属）
> **历史审查报告**：文中路径指重构前的代码（现已归档到 `old/code/`）。现行结构见 [`data-model.md`](data-model.md)。
> 结论先行：**吃力不是"数据难"，是解析层只留了"块名"没留"数值"**，加上语义散在三处。建议按 P0→P3 分四步重构，每步都可独立发布。

---

## 1. 结论（TL;DR）

| # | 问题 | 证据 | 建议 |
|---|---|---|---|
| 1 | **数值效果没落地**：`Values` 下 272 个带值字段，卡表只解析约 12 个 | `assets.py:40` 只有 11 个白名单标签；`read_blocks()`（`assets.py:316`）只记"块非空" | 新增无损 `RawValues` + 声明式 `BONUS_SPECS`，产出 `bonuses` / `bonus_text` |
| 2 | **同一语义算两遍、判两遍** | 目标展开在 `table.purpose_of`（`table.py:203`）和 `assign.targets_of`（`assign.py:93`）各做一次；zone 到中文的映射在 `classify.world_label`（`classify.py:143`）和 assign 里各写一份 | 抽出唯一的 `TargetSet`（区域 + 权重 + 建筑族），上层只消费 |
| 3 | **展示与语义混在一起** | `classify.place()` 返回中文串（`classify.py:98`），`assign.decide()` 拿中文串当路由键（`assign.py:129`） | `Place` / `Merchant` 用枚举，中文只留在渲染层 |
| 4 | **规则与文档手工对齐** | 规则是 `assign.py` 的 if 链，规则表 + 张数手写在 `mods/all-items-unlocked/README.md` | 规则表数据化（`RULES` 列表），文档表从代码生成 |
| 5 | **每次分析都要重扫 276 MB** | 4 个入口各自 `AssetIndex.scan`（`build_data.py:24`、`build_profile.py:27`、`build_research.py:18`、`edit_pools.py:175`），单次 4.8 s | 扫描结果落盘缓存（pickle/msgpack + 源文件指纹），分析走缓存 |

**如果只做一件事**：做 P1（效果解析）。它解决 80% 的"描述一张卡"的痛，且完全不碰归属逻辑，风险最低。

---

## 2. 这两轮"吃力"的账

上一轮被问"这几张卡作用介绍一下"，我最后写 **8 个一次性脚本**（`_fx1.._fx6`、`_ana1..2`），每次都把 276 MB 的 `assets.xml` 重扫一遍（约 5 s/次，累计 ~40 s），才拼出「+20% 生产力 / 维护费 +20% / 远征 医疗+20」这种句子。这是**管线缺陷**，不是数据缺陷：

- 卡表里 `effects` 字段只有 30 个块名（"工厂加成""建筑加成"），**没有数值**；
- `info_desc` 是**风味文案**（例：鸟屋 → "我相信你的心胸至少容得下一栋。"），不是效果；
- 远征属性 1782 张卡都有，卡表里只剩"远征属性"四个字；
- 换原料 / 额外产出 / 新增作物里的商品名全是 GUID（`114347`），没有解析成"木蓝"。

同理，判归属时我必须自己再展一遍目标、再写一遍 zone 判定——因为 `cards.json` 里的 `usage` 是给读者看的分组，`assign` 并不消费它。

---

## 3. 现状结构与根因

### 3.1 数据流（今天）

```
assets.xml (276 MB)
   │  AssetIndex.scan()                      ← 每次运行都重来（4 个入口各一次）
   ▼
ItemCard / AssetFacts / Pool                 ← 只留 tpl/base/name/region/members + 11 个字段 + 块名
   │  table.build_one()                       ← 再叠加 card-tables.tsv 底稿、templates.xml 装槽
   ▼
CardRecord (28 个平铺字段)                    ← 无 schema 版本；数值已在上一步丢失
   │  report.write_*()                        ← cards.md / profile.tsv / merchant-pools.md
   ▼
docs/cards.md
```

### 3.2 五个根因（按影响排序）

1. **读取层"有损"**：`ItemCard` 只存 `fields`（`CARD_FIELD_TAGS` 的 11 个标签）与 `blocks`（块名）。数值在这一层被丢弃 → 任何"想要数字"的需求都必须重扫 XML。这是"吃力"的第一来源。
2. **解释层不存在**：解析规则散在 `read_blocks`、`read_craft_costs`、`table.build_one`、`classify.place`、`assign.targets_of` 五处，都是"边长边判"，没有独立的"把 `Values` 解释成语义"的模块，因此**无法单测**（`tests/` 里没有一条解析层测试）。
3. **语义双份**：目标展开、区域判定、装槽映射各有两份实现（见 TL;DR #2）。改一处必忘另一处——这正是"跨区卡漏给旧世界"那个 bug 的土壤：`purpose_of` 里 7 张卡已经算出 `{Africa, Colony01}`，`assign` 却另算一套并用了 `==` 精确比较。
4. **展示与语义耦合**：`place()` 返回中文串，既当分类又当路由键；`world` 是拼接好的中文标签（"新世界+安贝沙"），下游要再拆回来。加一个卖点就要动串。
5. **产物无契约**：`cards.json` 没有 `schema_version`，`CardRecord.from_json` 靠"字段名对上就收、对不上就丢"（`table.py:86`）静默兼容；4 个入口互相读 JSON，谁先跑谁后跑只有 docstring 记着。

---

## 4. 重构设计

### 4.1 分层（目标）

```
[0] 读取层   assets.xml → RawAsset{facts, pool, values}     ← 无损，可缓存
[1] 解释层   values + names → Bonus / Expedition / Action / TargetSet   ← 纯函数，可单测
[2] 模型层   Card（枚举化的 Place / Merchant，语义字段）      ← 无中文串
[3] 规则层   RULES: tuple[Rule, ...] → 归属 + 文档表格        ← 单一事实源
[4] 产物层   cards.json(v2) / cards.md / profile / 规则表      ← 只做渲染
```

### 4.2 读取层：无损 + 可缓存

```python
@dataclass(frozen=True)
class RawValues:
    """`<Values>` 的结构化摘要：不解释，只记录。"""
    scalars: Mapping[str, str]              # "FactoryUpgrade/ProductivityUpgrade/Value" -> "20"
    refs: Mapping[str, tuple[str, ...]]     # "FactoryUpgrade/AddedFertility" -> ("114347",)
    blocks: tuple[str, ...]                 # 有内容的块名（现有 BLOCK_ZH 的输入）
    text_en: str = ""
    line_id: str = ""
```

- 只存"叶子文本"，键是相对 `Values` 的路径 —— 272 个字段全覆盖，体积可控（每张卡平均 ~20 条）。
- **扫描缓存**：`AssetIndex.scan()` 写 `temp/db/index.pickle` + `meta.json{size, mtime, sha256}`；源文件未变则直接加载（~0.3 s）。`edit_pools assign` 从 5 s 降到亚秒级，临时分析也不必再写一次性脚本。
- 现有 `ItemCard` 字段（tpl/base/name/fields/blocks/craft_costs/dlc/targets）保留为兼容层，`fields` 改成从 `RawValues` 派生。

### 4.3 解释层：效果 = 声明式映射 + 三个特殊处理器

```python
# 一个字段一条声明，加效果只加行，不写代码
@dataclass(frozen=True)
class Spec:
    path: str          # "BuildingUpgrade/MaintenanceUpgrade/Value"
    key: str           # "maintenance"
    label: str         # "维护费"
    unit: str = "%"    # "%" / "count" / ""
    negative_is_good: bool = False

BONUS_SPECS: tuple[Spec, ...] = (
    Spec("FactoryUpgrade/ProductivityUpgrade/Value", "productivity", "生产力"),
    Spec("FactoryUpgrade/ProductivityUpgrade/Percental", "productivity_pct", ""),   # 标记位
    Spec("BuildingUpgrade/MaintenanceUpgrade/Value", "maintenance", "维护费", negative_is_good=True),
    Spec("BuildingUpgrade/WorkforceAmountUpgrade/Value", "workforce", "所需劳动力", negative_is_good=True),
    Spec("ModuleOwnerUpgrade/ModuleLimitPercent", "module_limit", "模块上限"),
    Spec("CultureUpgrade/AttractivenessUpgrade/Value", "attractiveness", "吸引力"),
    ...  # 约 40 条，覆盖附录 A 里的常用字段
)
```

三个必须"看上下文"的处理器（其余全是查表）：

| 处理器 | 负责字段 | 输出 |
|---|---|---|
| `additional_output` | `AdditionalOutput/Item/{Amount, Product, AdditionalOutputCycle}` | "每 2 周期额外产出 1 个同种产物" |
| `replace_inputs` | `ReplaceInputs/Item/{OldInput, NewInput}` + `InputAmountUpgrade` | "药草 → 木槿花瓣（木蓝染料 +2）" |
| `added_fertility` | `AddedFertility` | "获得作物：木蓝"（`Fertility` 资产名 → 去后缀） |

产品模型：

```python
@dataclass(frozen=True)
class Bonus:
    key: str                 # 规范化键，便于过滤/统计
    value: float
    unit: str                # "%" / "count"
    subject: str = ""        # 商品 / 肥料 / 需求的中文名
    note: str = ""           # "每 2 周期" 之类的补充语义

@dataclass(frozen=True)
class Expedition:
    morale: int
    attributes: tuple[tuple[str, int], ...]   # (属性, 数值)，属性用中文
    difficulties: tuple[str, ...]             # 简单 / 平均 / 困难
    regions: tuple[str, ...]

@dataclass(frozen=True)
class ItemAction:
    kind: str                # HEAL_INCIDENT / PLACE_MINE / …
    duration: int            # ms
    charges: int
    cooldown: int
    scope: str               # Self / Target / SelfRadius / …
```

渲染只在一处：`render.bonus(bonus) -> "生产力 +20%"`、`render.expedition(exp) -> "医疗 +20、狩猎 +15、士气 +10"`。

**为什么这样就不吃力了**：上述 6 张卡的效果描述变成 3 行代码（读 `card.bonuses` + `card.expedition`），不必碰 XML；新增字段只加一行 `Spec`；解析结果是数据，可进快照测试。

### 4.4 目标模型：`TargetSet`（唯一事实）

```python
@dataclass(frozen=True)
class TargetSet:
    groups: tuple[str, ...]              # 原始 EffectTargets（目标组或建筑）
    zones: frozenset[str]                # {"Africa", "Colony01"}
    weights: Mapping[str, int]           # 每区展开后的建筑数（今天被删掉的 counts）
    names: tuple[str, ...]               # 目标组名（优先）或建筑中文名
    kinds: frozenset[str]                # 规范化的建筑族：farm/factory/residence/culture/port/shop/…
```

- `kinds` 由模板族推导（`FarmBuilding*` → `farm`），**替换掉 `assign.py` 里 20 多个模板前缀的裸字符串判断**。
- `purpose_of`（给读者看的用途分组）与 `targets_of`（给规则用的区域集合）都从这一个对象渲染/判断，不再各展一遍。实测这能把每张卡的目标展开从 2–3 次降到 1 次。

### 4.5 卡牌类：语义与展示分离

```python
class Place(StrEnum):        # 装槽（细类）
    GUILD = "guild"; TOWNHALL = "townhall"; HARBOR = "harbor"; ...

class Merchant(StrEnum):
    BLAKE = "blake"; ELI = "eli"; KAHINA = "kahina"; ...

@dataclass(frozen=True)
class Card:
    # 身份
    guid: str
    name: Localized                 # zh / en / internal（inherit 已解析）
    template: str
    # 静态属性
    rarity: Rarity; price: int
    dlc: tuple[str, ...]            # 存 GUID，渲染时取名
    allocation: Place
    scenario: str; exclusive: str; set_guid: str
    recipe: tuple[CraftCost, ...]   # 今天叫 craft_costs，名字容易和"可合成"混
    # 语义（新增）
    bonuses: tuple[Bonus, ...]
    expedition: Expedition | None
    action: ItemAction | None
    targets: TargetSet
    # 状态
    researchable: bool
    owners: Owners                  # vanilla / mod 两套 frozenset[Merchant]
```

- `place` 从"函数 + 中文串"变成**字段 + 枚举**，`classify.place()` 变成构造时的一次计算；`ALLOC_ZH` / `PLACE_ORDER` 等表只留给渲染。
- `rarity` 用枚举（`Quest` / `Narrative` 也在其中），避免"（无稀有度）"这种展示串参与排序。
- 与今天的 `CardRecord` 相比：字段从 28 个平铺变成 4 组嵌套，**语义字段类型化**，展示字段（`world`、`usage`、`sell_*`）移到渲染/查询层或保留为派生属性。

### 4.6 规则层：规则表数据化

```python
@dataclass(frozen=True)
class Rule:
    code: str                       # "5" / "5+7" / "9"
    title: str                      # "跨新世界+安贝沙的生产卡"
    match: Callable[[Card], frozenset[Merchant] | None]

RULES: tuple[Rule, ...] = (
    Rule("1", "海军", navy),
    ...
    Rule("5", "只影响安贝沙", colony_single),
    Rule("7", "只影响新世界", colony_single),
    Rule("5+7", "跨新世界+安贝沙的生产卡", colony_production_both),
    Rule("9", "生产", production),
    ...
)
```

- `decide()` 变成 `for rule in RULES: if (hit := rule.match(card)) is not None: return Assignment(rule.code, hit)`。
- **规则表文档自动生成**：`edit_pools.py report --rules` 或 `build_cards.py` 顺带把「规则 / 商人 / 张数」写进 `mods/all-items-unlocked/README.md` 的标记块。这两轮我手改过 4 次计数（39→45、66→67、342→335、加 `5+7` 行），这类漂移以后不可能再发生。

### 4.7 产物契约

- `cards.json` 顶部加 `{"schema_version": 2, "cards": {...}}`；`CardRecord.from_json` 保留 v1 适配一层，切完删掉。
- 体积估算：`bonuses`（≈1460 张 × 2.2 条）+ `expedition`（1782 张）≈ +350–450 KB，`cards.json` 1.5 MB → ~1.9 MB；若要控制体积，可拆 `cards.json`（轻） + `effects.json`（重）。
- 所有入口只读 `temp/data/*.json`，扫描只在 `build_data.py` 里发生（缓存后仍快）；`build_cards.py` / `build_profile.py` 不再需要 `AssetIndex`。

---

## 5. 迁移计划（四步，各自可发布）

| 阶段 | 内容 | 产物 / 验收 | 风险 | 估时 |
|---|---|---|---|---|
| **P0** | `RawValues` + 扫描缓存 + 名称服务（`Names`：一次加载 8 MB 文本，`zh/ref` 带继承回退与缓存） | 产物字节不变（`cards.json` 哈希不变）；`edit_pools assign` < 1 s | 低 | 0.5–1 天 |
| **P1** | `BONUS_SPECS` + 三个特殊处理器 + `bonus_text`；`cards.md` 加「效果」列；`profile` 的"效果概述"改成数值、风味文案另起一列 | 七张跨区卡 + 20 张代表卡的 `bonus_text` 快照通过 | 中（映射表要逐条核对符号/单位） | 1–2 天 |
| **P2** | `TargetSet` 统一目标展开；`Place`/`Merchant` 枚举化；`RULES` 数据化 + 文档表自动生成 | `cards.json` 的归属与今天**逐卡相同**（用 diff 脚本验证）；README 规则表由脚本重写 | 中（触及 classify/report/assign/pools） | 1–2 天 |
| **P3** | 管线收拢（一个入口 / 依赖图）、golden 快照测试、卡级 diff 工具（`anno diff`：这次改动动了哪些卡） | 全量测试 + 文档可一键重建 | 低 | 0.5–1 天 |

P0 不动产物、P1 只加字段、P2 行为等价、P3 只动工具——每步都能单独提交、单独回滚。

---

## 6. 测试策略

1. **解析快照（golden）**：选 24 张代表卡存 `tests/golden/effects.json`（七张跨区卡、安贝沙使节、纯远征卡、使用型道具、剧本卡、无目标卡…），断言 `bonus_text` 与结构化 `bonuses`。解析层改动必须让 diff 可解释。
2. **纯函数单测**：手写 `RawValues` 直接喂 `parse_bonuses()` —— 不读 XML，毫秒级。
3. **等价性测试（P2）**：对 2149 张卡对比新旧两套归属，断言 `old == new`；这是把"跨区漏判"这类 bug 钉死的地方。
4. **产物稳定性**：`build_data` 连跑两次，`cards.json` 哈希一致；`docs/cards.md` 由 JSON 生成，纳入 diff 审查。
5. **数据校验器**（可放 P4）：`key` 在允许集合内、`targets.zones` 非空/一致、`weights` 之和 = 展开建筑数、每张卡至少一个 `bonus` 或 `expedition` 或 `action`（否则报警"有卡但看不出作用"）。

---

## 7. 风险与取舍

- **契约变更**：`cards.json` v2 要让 4 个入口同时切换；用 v1 适配器过渡一个星期即可。
- **映射表的准确性**：40 条 `Spec` 的符号/单位得对着游戏 UI 抽检（维护费的正负、`Percental` 缺省、`ModuleLimitPercent` 的方向）。建议 P1 里先只做"确定无疑"的 20 条，其余按需加。
- **枚举化的摩擦**：外部（`edit_pools` 命令行参数）是中文商人名，内部是枚举；在 CLI 边界做一次映射即可，不要迁就字符串。
- **不要过度建模**：`ItemAction`（使用型道具）字段多且只在 92 张卡上用，可先"原样透传 `scalars` 子集"，等有需求再建模。

---

## 8. 附录 A：`Values` 实测字段覆盖（2149 张卡）

| 字段（相对 `Values`） | 卡数 | 卡表里现在长什么样 |
|---|---|---|
| `ExpeditionAttribute/ExpeditionAttributes/Item/Attribute` | 1782 | "远征属性" |
| `ExpeditionAttribute/ExpeditionAttributes/Item/Amount` | 1781 | 无 |
| `Item/InfoDescription` | 1792 | 风味文案 |
| `ItemEffect/EffectTargets/Item/GUID` | 1567 | ✅ usage（有） |
| `ExpeditionAttribute/ItemDifficulties` | 1379 | 无 |
| `ExpeditionAttribute/BaseMorale` | 1282 | 无 |
| `CultureUpgrade/AttractivenessUpgrade/Value` | 453 | "文化展馆加成" |
| `FactoryUpgrade/ProductivityUpgrade/Value` | 342 | "工厂加成" |
| `BuildingUpgrade/MaintenanceUpgrade/Value` | 216 | "建筑加成" |
| `BuildingUpgrade/WorkforceAmountUpgrade/Value` | 147 | "建筑加成" |
| `FactoryUpgrade/AdditionalOutput/Item/*` | 145 | 无 |
| `ScenarioFilter` | 98 | ✅ |
| `ItemAction/*` | 92 | "使用动作" |
| `ResidenceUpgrade/AdditionalHappiness` | 92 | "住所加成" |
| `ExpeditionAttribute/ItemRegions` | 250 | 无 |
| `FactoryUpgrade/ReplaceInputs/Item/*` | 55 | 无 |
| `FactoryUpgrade/AddedFertility` | 46 | 无 |
| `BuildingUpgrade/PublicService*Distance/Value` | 49 | "建筑加成" |
| `ModuleOwnerUpgrade/ModuleLimitPercent` | 21 | "模块主人加成" |
| `EcoSystemProviderUpgrade/DeltaValueUpgrade/Value` | 18 | "生态系统" |

（全量 272 个字段，其余为 `TradePriceOnlineCurrency` 682、`ItemSet` 204、`Flotsam` 398 等任务/杂项字段。）

## 9. 附录 B：改动前后示例

**香料大师 `125131`（Rare，116,900）**

| | 今天 | 重构后 |
|---|---|---|
| 效果 | `effects: ["工厂加成", "远征属性"]` | `bonuses: [productivity +20%, fertility "辛香料"]`<br>`bonus_text: "生产力 +20%；目标农场获得作物：辛香料"` |
| 远征 | 只有"远征属性" | `expedition: morale 0, [("男性",1),("全能",1)]` |
| 判断归属 | 需再展目标 + zone，`colony_of` 里一条条扫 | `card.targets.zones == {Africa, Colony01}`，`RULES` 直接命中 `5+7` |

**安贝沙使节 `8908`（Rare）**

| | 今天 | 重构后 |
|---|---|---|
| 效果 | `effects: ["工厂加成", "远征属性", "建筑加成"]` | `bonuses: [productivity +35%, extra_output "每2周期+1", replace_input "药草→木槿花瓣", …, maintenance +35%, workforce +25%]` |
| 描述成本 | 6 个一次性脚本、8 次重扫 XML | 3 行渲染函数 |

**鸟屋 `125058`（Uncommon，21,300）**

`+20% 生产力 / 维护费 +20%`（负值才是降价，这与 `mods/mr-long` 里"维护费 −75% = `Value -75`"同一约定）。今天这条符号语义只能靠人记，重构后由 `Spec(negative_is_good=True)` 显式表达。
