# mr-long

中文名「传销头子法瑞斯·阿瑟雷密」，英文名 `Feras Alsarami the Persuader`。

## 基本信息

| 项 | 值 |
|---|---|
| 来源 | 本地自制 / 中文社区 |
| 状态 | ✅ 已在游戏中使用 |
| 旧目录名 | `[chuan xiao tou zi]Mr.LongV1.0` |
| 物品 GUID | `1400000006` |
| **ModID** | `local-mr-long`（写死在 `modinfo.json`，改文件夹名不影响） |
| 分类 | Cheat |
| 备份校验 | ✅ 与游戏目录逐字节一致（3 个文件） |

## 改了什么

往游戏中加入一个自定义**传奇专家（Specialist）**物品：

| 属性 | 数值 | 效果 |
|---|---|---|
| `ProductivityUpgrade` | +300% | 生产力翻 4 倍 |
| `MaintenanceUpgrade` | −75% | 维护费大幅下降 |
| `WorkforceAmountUpgrade` | −75% | 人力需求大幅下降 |
| `IncidentRiotIncreaseUpgrade` | −99% | 几乎不会起义 |
| `IncidentFireIncreaseUpgrade` | −99% | 几乎不会起火 |
| `IncidentIllnessIncreaseUpgrade` | −99% | 几乎不会传染病 |
| `IncidentExplosionIncreaseUpgrade` | −99% | 几乎不会爆炸 |
| `ProvideIndustrialization` | `Powerplant` | 自身提供电力 |
| `TradePrice` / `TradePriceOnlineCurrency` | 1000 / 50 | 交易售价 |

**生效目标**（`EffectTargets`）：生产建筑 `193856`、果园/化学厂/工匠工作坊/生产线 `194008`、`194011`、`194023`、`194024`。

**获取方式**：同一个 mod 把该物品塞进 9 个 NPC 的奖励池（`RewardPool/ItemsPool`，权重 `100`，很容易刷出）—— 这正是"传销头子"这个名字的由来：

- 旧世界：Sir Archbald `192069`、Eli Bleakworth `190774`、Madame Kahina `192068`、Anne Harlow `192070`
- 新世界：Isabel Sarmento `192073`、Jean La Fortune `192071`
- Cape Trelawney：Old Nate `193452`
- 北极：Qumaq `193835`
- Enbesa：Emperor Ketema `127480`

## 文件构成

```
data/config/export/main/asset/assets.xml   物品定义
data/config/gui/texts_chinese.xml          中英文文本（GUID 1400000006 / 21354）
data/modgraphics/icons/icon_chuanxiaotouzi.png   物品图标
```

## 注意

- 与 `download/mods-mr-long/mr-long-v1-2` **是同一物品、同一 GUID**，只能保留其一。
- V1.2 数值更弱（生产力 +200%、维护费 −25%、人力 −25%），但额外改了全球运输参数。
