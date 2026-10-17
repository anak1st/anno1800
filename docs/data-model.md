# 数据层设计：`temp`（原始）→ `data`（JSON 数据库）→ `docs`（渲染）

> 状态：**已实施**（2026-10-18）。实现在 `src/anno/`，旧工具链整套归档在 `old/`；本文数量都是实测值。
> 目标：卡牌为核心，其他游戏概念作辅助，**一个 ID 一个文件**，检索/阅读都方便。

---

## 1. 分层

```
temp/   原始层（不进 git）
├── db/...assets.xml          解包出的原始游戏数据
├── card-tables.tsv           卡表底稿（范围由它定）
├── research-cards.txt        可研发清单
└── card-profile.tsv          人看的档案（由 data 渲染）

data/   解析层（本设计的产物）
├── index.json                清单：schema 版本、统计、各目录说明
├── names.json                名字 → (概念, ID) 反查表（CLI 用）
├── cards/<GUID>.json         卡（核心，2149 个）
├── target-groups/<GUID>.json 目标组（「所有作物农场」这类，砍掉卡牌没引用的，79 个）
├── buildings/<GUID>.json     卡牌作用目标里的建筑（447 个）
├── goods/<GUID>.json         商品（产物 / 原料 / 需求，212 个）
├── fertilities/<GUID>.json   作物（肥料，30 个被卡或建筑引用）
├── item-sets/<GUID>.json     物品套装（44 个）
├── dlc/<GUID>.json           DLC（卡牌引用到的 9 个）
├── traders/<GUID>.json       商人（9 个）
└── buffs/<GUID>.json         使用型道具的 Buff（约 124 个）

docs/   展示层：`cards.md`、`cards-special.md` 全部从 data/ 读，不再碰 temp/
```

原则：
- **`temp/` 只放原始/底稿**；解析过的数据一律进 `data/`。
- **一个资产一个文件**，文件名 = GUID，路径可预测：`data/cards/125131.json`。
- 文档（md）由 `data/` 渲染；`data/` 不手改（重跑 `build_db.py` 即重建）。

---

## 2. 概念探索结果（实测）

| 概念 | 游戏里怎么认 | 数量 | 与本设计的关系 |
|---|---|---|---|
| **卡（物品）** | `Template ∈ ITEM_TPL`（GuildhouseItem / TownhallItem / HarborOfficeItem / ShipSpecialist / CultureItem / VehicleItem / ItemWithUI…） | 表内 **2149**（扫描出 2154，含 2 张继承变体） | **核心** |
| **作用目标组** | `Template = ItemEffectTargetPool`，成员在 `EffectTargetGUIDs` | **194**（全部有成员） | 卡的目标常指向它（564 次引用，79 个被用到） |
| **建筑** | `Template` 含 `Building`/`Farm`/`Factory`/`Mall`/`Restaurant`/`WarShip`… | 卡牌目标展开后 **447 座** | 卡的目标落点；有产线信息 |
| **商品** | `Template = Product` | 全库 656，卡牌引用 **173** | 配方 / 额外产出 / 换原料 / 需求 |
| **作物（肥料）** | `Template = Fertility` | 33（另有 121 个 `FertilitySet`，卡牌不引用） | `AddedFertility`（18 个被引用） |
| **物品套装** | `Template = ItemSet` | 44（32 个被卡牌引用） | 卡的 `Item/ItemSet` |
| **DLC** | `Template = UplayProduct` | 86，卡牌引用 **9** | `Locked/DLCDependency` |
| **Buff** | `Template` 以 Buff 结尾（VehicleBuff / GuildhouseBuff / TownhallBuff），由 ItemAction/ActiveBuff 引用 | 约 **124**（133 个被引用，含少量噪声） | **入库**：使用型道具的「用了会得到什么」 |
| **商人** | `<Values><Trader>` + `Profile_3rdParty*` | 27 个带 `<Trader>`，其中 **9 位卖卡** | 原版档位池 + 本 mod 池 |
| **远征** | `ExpeditionAttribute`（属性/难度/区域） | 属性 20 种、难度 3 种、区域 10 种 | 嵌在卡里，不单独建文件 |
| **使用动作** | `ItemAction` | 10 种（HEAL_INCIDENT / PLACE_MINE / KAMIKAZE…） | 嵌在卡里 |
| **商店分类** | `Product/ProductCategory` → `Text` 资产 | 11 类（资源 / 加工品 / 基本需求 / 奢侈品 / 建设材料 / 商业需求…） | 写进商品文件 |

**不入库（只留 ID / 名字内联）**：文化模块（145 个 `ChangeModule`，只是展馆皮肤）、动物/鱼/鸟（`ForcedFeedbackVariation`，是展品的视觉效果，不是独立玩法概念，名字内联到卡里）、任务、音频、视觉、`Profile`。"三级概念" 等有需求再加目录，不影响现有 schema。

---

## 3. 公共约定

| 项 | 约定 |
|---|---|
| 文件名 | `<GUID>.json`，GUID 用游戏内十进制 ID（与 `texts`、`card-tables.tsv` 一致） |
| 编码 | UTF-8 无 BOM，`indent=2`，`ensure_ascii=false`（能直接读） |
| 每个文件必备 | `id`、`type`、`name`（`{zh, en?, internal}`） |
| 引用 | 一律 `{"id": "...", "name": "..."}`：**ID 是权威，name 是冗余的显示名**（避免查文件时还要 join） |
| 反向引用 | 辅助概念里带 `cards: [GUID…]`（谁引用了我） |
| 区域值 | 内部值 `Moderate/Colony01/Africa/Arctic` + 中文 `旧世界/新世界/安贝沙/北极`（两个都给） |
| schema 版本 | `data/index.json` 的 `schema: 1`；解析口径变了就 +1，并留一条迁移说明 |

---

## 4. 各概念的 JSON 结构

### 4.1 `data/cards/<GUID>.json` —— 核心

```jsonc
{
  "id": "125131",
  "type": "card",
  "name": { "zh": "香料大师", "en": "Spice Master", "internal": "Spice expert" },
  "summary": "Rare ｜ 工会 ｜ 生产力 +20%，目标农场获得「辛香料」 ｜ 远征：男性、全能",

  "template": "GuildhouseItem",
  "slot": { "id": "GuildHouse", "zh": "工会" },
  "categories": { "big": "建筑", "place": "工会" },
  "rarity": "Rare",
  "prices": { "trade": 116900, "online": null },
  "stack": 1,
  "dlc": [{ "id": "410071", "name": "狮子大地" }],
  "item_set": null,
  "scenario": null,
  "exclusive": null,

  "effects": {
    "bonuses": [
      { "key": "productivity", "label": "生产力", "value": 20, "unit": "%", "group": "production" },
      { "key": "crop", "label": "新增作物", "ref": { "id": "114348", "name": "辛香料" } }
    ],
    "extra_outputs": [],
    "replace_inputs": [],
    "input_amounts": [],
    "other": []                       // 没归一化的数值叶子，兜底不丢数据
  },
  "expedition": {
    "morale": 0,
    "attributes": [{ "key": "PerkMale", "zh": "男性", "value": 1 },
                   { "key": "PerkJackOfAllTraits", "zh": "全能", "value": 1 }],
    "difficulties": [],
    "regions": []
  },
  "action": null,

  "targets": {
    "refs": [ { "id": "114452", "name": "辛香料农场", "kind": "building" },
              { "id": "25020", "name": "庄园辛香料农场", "kind": "building" } ],
    "buildings": [ { "id": "114452", "name": "辛香料农场", "zone": "Africa" },
                   { "id": "25020", "name": "庄园辛香料农场", "zone": "Colony01" } ],
    "zones": ["Africa", "Colony01"],
    "zones_zh": ["安贝沙", "新世界"],
    "kinds": ["farm"],
    "usage": [ { "zones": ["Africa"], "names": ["辛香料农场"] },
               { "zones": ["Colony01"], "names": ["庄园辛香料农场"] } ]
  },
  "recipe": [],
  "flags": { "researchable": true, "craftable": false, "scenario_only": false },
  "owners": {
    "vanilla": [{ "id": "119051", "name": "柯提马" }],
    "mod": [{ "id": "119051", "name": "柯提马" }, { "id": "29", "name": "萨曼托" }],
    "in_vanilla_pool": true,
    "in_mod": true
  }
}
```

要点：
- `effects.bonuses` 是**按字段声明表**解析出来的数值（见 4.10）；`extra_outputs / replace_inputs / input_amounts` 是结构化的特殊效果。
- `targets` 同时给"引用"和"展开后的建筑"，并给出区域与建筑族（`farm/factory/residence/culture/shop/harbor`…）。
- `usage` 保留今天的「按区域分组」口径，直接喂 `cards.md` 的用途列。
- 英文名、内部名都留着，方便和游戏文件对照；中文名缺失时回退内部名。

### 4.2 `data/buildings/<GUID>.json`

```jsonc
{
  "id": "114452",
  "type": "building",
  "name": { "zh": "辛香料农场", "internal": "agriculture_colony02_06 (Spice Grower)" },
  "template": "FarmBuilding",
  "kind": "farm",
  "zone": { "id": "Africa", "zh": "安贝沙" },
  "production": {
    "inputs": [],
    "outputs": [{ "id": "114369", "name": "香料", "amount": 1 }],
    "fertility": { "id": "114348", "name": "辛香料" },
    "cycle": 60
  },
  "cards": ["125131", "8908"]          // 谁影响这座建筑
}
```

产线信息来自 `FactoryBase/FactoryOutputs`、`FactoryInputs`、`Factory7/NeededFertility`（实测：辛香料农场 → 产 `114369`「香料」，需要肥料 `114348`「辛香料」）。

### 4.3 `data/target-groups/<GUID>.json`

```jsonc
{
  "id": "125109",
  "type": "target-group",
  "name": { "zh": "所有安贝沙作物农场", "internal": "all africa crop farms" },
  "members": [
    { "id": "114447", "name": "木槿农场", "zone": "Africa" },
    { "id": "25020", "name": "庄园辛香料农场", "zone": "Colony01" }
  ],
  "zones": ["Africa", "Colony01"],
  "cards": ["125058", "125059", "125060"]
}
```

### 4.4 `data/goods/<GUID>.json`

```jsonc
{
  "id": "114368",
  "type": "good",
  "name": { "zh": "木蓝染料", "internal": "Indigo" },
  "category": { "id": "11703", "name": "加工品" },
  "base_price": 25,
  "civ_level": 1,
  "region": { "id": "Africa", "zh": "安贝沙" },
  "used_as": { "recipe": false, "input": true, "output": true, "need": false },
  "cards": ["8908"]
}
```

### 4.5 `data/fertilities/<GUID>.json`

```jsonc
{ "id": "114348", "type": "fertility",
  "name": { "zh": "辛香料生产力", "internal": "Spices Fertility" },
  "crop": "辛香料", "cards": ["125131"] }
```
`crop` = 名称去掉「生产力」后缀。

### 4.6 `data/item-sets/<GUID>.json`

```jsonc
{ "id": "191116", "type": "item-set", "name": { "zh": "绝种物种", "internal": "extinct animals" },
  "cards": ["191067", "191055"] }
```

### 4.7 `data/dlc/<GUID>.json`

```jsonc
{ "id": "410071", "type": "dlc", "name": { "zh": "狮子大地", "internal": "Anno 1800 DLC - Land of Lions" },
  "cards": ["125058", "125131"] }
```

### 4.8 `data/traders/<GUID>.json` —— 商人的 ID 用 **Profile 资产 GUID**（`119051` 柯提马）

```jsonc
{
  "id": "119051",
  "type": "trader",
  "name": { "zh": "柯提马皇帝", "en": "Emperor Ketema" },
  "label": "柯提马",                    // cards.md 用的简称
  "zone": { "id": "Africa", "zh": "安贝沙" },
  "profile": "Third_party_13 (Emperor Ketema)",
  "vanilla": {
    "tiers": [{ "name": "EndGame", "pool": "192068", "cards": 109 }],
    "cards": ["125058", "8908"]
  },
  "mod": { "pool": "127480", "entries": 106, "duplicates": 0, "unknown": [], "cards": ["125058"] }
}
```
- 原版 9 位（含两个海盗）都有文件；海盗没有 mod 池时 `mod: null`。
- 档位池 GUID 来自 `VANILLA_TIERS`，池展开结果用今天的 `AssetIndex.reach`。

### 4.9 `data/index.json` + `data/names.json`

```jsonc
// index.json
{ "schema": 1, "generated_from": { "assets_xml": { "size": 289123456, "mtime": "..." } },
  "counts": { "cards": 2149, "buildings": 447, "target-groups": 79, "goods": 212,
              "fertilities": 30, "item-sets": 44, "dlc": 9, "traders": 9, "buffs": 120 },
  "folders": { "cards": "一张卡一个文件", "buildings": "卡牌作用目标里的建筑", ... } }

// names.json —— 名字检索（重名时给多个候选）
{ "香料大师": [{ "type": "card", "id": "125131" }],
  "辛香料农场": [{ "type": "building", "id": "114452" }],
  "柯提马": [{ "type": "trader", "id": "119051" }] }
```

### 4.10 效果解析口径（`src/anno/effects.py`）

字段 → 语义用**声明表**，加效果只加一行：

| `Values` 路径 | key | 标签 | 单位 |
|---|---|---|---|
| `FactoryUpgrade/ProductivityUpgrade/Value` | productivity | 生产力 | % |
| `BuildingUpgrade/MaintenanceUpgrade/Value` | maintenance | 维护费 | % |
| `BuildingUpgrade/WorkforceAmountUpgrade/Value` | workforce | 所需劳动力 | % |
| `ModuleOwnerUpgrade/ModuleLimitPercent` | module_limit | 模块上限 | % |
| `CultureUpgrade/AttractivenessUpgrade/Value` | attractiveness | 吸引力 | — |
| `ResidenceUpgrade/AdditionalHappiness` | happiness | 幸福度 | — |
| `ResidenceUpgrade/TaxModifierInPercent` | tax | 税收 | % |
| `PopulationUpgrade/ResidentsUpgrade/Value` | residents | 居民 | — |
| `IncidentInfectableUpgrade/*IncreaseUpgrade/Value` | fire/riot/illness/explosion | 火灾/暴动/疾病/爆炸风险 | % |
| `BuildingUpgrade/PublicService*Distance/Value` | service_range | 服务范围 | — |
| `VehicleUpgrade/*` | speed/weight/… | 速度 / 载重 … | % |
| `AttackerUpgrade/*`、`AttackableUpgrade/*` | damage/speed/hitpoints | 伤害 / 攻速 / 耐久 | % |

三个特殊处理器（其余都是查表）：

| 处理器 | 输入 | 输出字段 |
|---|---|---|
| 额外产出 | `FactoryUpgrade/AdditionalOutput/Item/{Product,Amount,AdditionalOutputCycle}` | `extra_outputs[]`（含"每 N 周期"） |
| 换原料 / 原料增量 | `ReplaceInputs/Item/{OldInput,NewInput}`、`InputAmountUpgrade/Item/*` | `replace_inputs[]`、`input_amounts[]` |
| 新增作物 | `FactoryUpgrade/AddedFertility` | `bonuses[key=crop]` |

符号约定写死在规格里：**维护费 / 所需劳动力 / 事件风险为负=更好**；`summary` 直接渲染成 `+20%` / `−50%`。

---

## 5. 生成管线（`temp` → `data` → `docs`）

```powershell
uv run build_db.py       # assets.xml + 底稿 -> data/（约 6 秒；一个 ID 一个文件）
uv run build_cards.py    # data/ -> docs/cards.md（0.3 秒，不碰 XML）
uv run build_profile.py  # data/ -> temp/card-profile.tsv
uv run build_research.py # assets.xml -> temp/research-cards.txt（原始层，不变）
```

- `build_data.py` **删除**，由 `build_db.py` 取代。
- `edit_pools.py` 改读 `data/cards/*.json`（卡表范围与售价不变，只是来源变了）；`assign` 仍然扫 XML（后续可加扫描缓存，不在本次范围）。
- `docs/cards.md` 的「Mod / 原版商人 / 用途」列由 `owners` + `targets.usage` 渲染，**不再从 temp 读任何 JSON**。

---

## 6. CLI 设计（人类友好）

新增根目录 `query.py`（typer + rich，与 `edit_pools.py` 同风格）：

```powershell
uv run query.py card 125131          # 也可用中文名：query.py card 香料大师
uv run query.py find --effect productivity --zone 安贝沙 --rarity Epic
uv run query.py find --owner 柯提马 --place 工会 --text 农场
uv run query.py trader 柯提马
uv run query.py building 辛香料农场
uv run query.py good 木蓝染料
uv run query.py show 114452          # 不知道类型时自动识别
```

`card` 的输出（即"这张卡到底干什么"）：

```
香料大师  125131
  稀有度 Rare ｜ 装槽 工会 ｜ 价格 116,900 ｜ 狮子大地 ｜ 研究所可研发
  归类  建筑 / 工会
  效果  生产力 +20%；目标农场获得作物「辛香料」
  远征  男性、全能
  目标  辛香料农场（安贝沙，产 辛香料）、庄园辛香料农场（新世界）
  来源  原版：柯提马 ｜ 本 mod：柯提马 + 萨曼托
```

`find` 输出表格（GUID / 中文名 / 稀有度 / 装槽 / Mod 商人 / 效果摘要），支持 `--json` 输出原始记录。

---

## 7. 规模与性能

| 项 | 估算 |
|---|---|
| 文件数 | **3099** 个（卡 2149 + 建筑 447 + 其余 ~500） |
| `data/` 总量 | 约 **9.5 MB**（单卡 1–2 KB，缩进过） |
| `build_db.py` | ~6 秒（扫描 5 秒 + 写 1 秒） |
| `query.py card` | < 0.2 秒（只读一个文件 + `names.json`） |
| `query.py find` | 0.5–1 秒（读 2149 个小文件；可选再做 `data/cards/_index.json` 加速） |

---

## 8. 验收标准

1. 计数对得上：`cards 2149 / buildings 447 / target-groups 79 / goods 212 / fertilities 30 / item-sets 44 / dlc 9 / traders 9 / buffs 120`，写进 `index.json`（`build_db.py` 自动写）。
2. **文档零回归**：`docs/cards.md` 除"用途"列会带上更细的区域分组外，逐行与现在一致（用 diff 验证）。
3. 7 张跨区卡的 `owners.mod` 是 `柯提马 + 萨曼托`，`targets.zones` 是 `["Africa","Colony01"]`。
4. `query.py card 125131` 的输出里，效果数值与游戏 XML 一致（人工抽检 10 张）。
5. 单测：`effects` 解析（合成输入）+ 一个卡文档的 snapshot；`pytest` 全绿。
6. 所有 JSON 可被 `json.load` 读回；`data/index.json` 的计数由生成过程自动写（不手填）。

---

## 9. 实施记录（已完成，2026-10-18）

新实现全部在 `src/anno/`（一次写成的 13 个模块），旧工具链整套归档在 `old/code/`。

| 模块 | 职责 |
|---|---|
| `paths.py` | 三层路径（temp / data / docs）+ 每个概念的数据目录 |
| `scan.py` + `model.py` | 流式扫描 assets.xml → `AssetIndex`（facts / pools / cards / production / products / buffs） |
| `effects.py` | `RawValues` → 数值效果 / 远征 / 使用动作 + 一句话摘要（声明表 + 3 个特殊处理器） |
| `cards.py` | 卡牌文档 + `CardInputs` / `CardView` |
| `entities.py` | 目标组 / 建筑 / 商品 / 作物 / 套装 / DLC / Buff 文档与反向引用 |
| `traders.py` | 商人文档（Profile GUID 为 ID）+ 「谁卖」归属 |
| `database.py` | 写/读 `data/`、`index.json`、`names.json` |
| `placement.py` | 装槽 / 大类 / 世界（原 classify） |
| `rules.py` | 归属规则（原 assign，含跨区生产卡双挂） |
| `pools.py` | 本 mod 卡池读写 / 排版（原 merchants.pools） |
| `render.py` | `cards.md` / 档案表 / 商人卡池表（原 cards.report） |
| `research.py` | 研发展开（原 cards.research） |
| `util.py` / `console.py` / `texts.py` / `templates.py` / `tables.py` | 小工具与游戏常量表 |

验收结果：`data/` 共 **3099** 个文件；`docs/cards.md` 与原实现逐行一致（除数据来源说明与 GUID 反查提示）；
`pytest` 23 项通过；`ruff` 干净。

## 10. 已确认的决策（2026-10-18）

| # | 问题 | 决定 |
|---|---|---|
| 1 | `data/` 要不要进 git？ | **不进**（与 `temp/` 同性质，可随时重建）→ 写进 `.gitignore` |
| 2 | 三级概念入不入库？ | **Buff 入库**（约 124 个）；**文化模块不单列**（只是展馆皮肤）；**动物/鱼/鸟不单列**（是展品视觉效果，名字内联进卡） |
| 3 | 旧的 `temp/data/*.json` 怎么办？ | **归档到 `old/`**（连同被替换的代码副本），然后从干净状态写新实现 |

