# mr-long

同一个 mod 里两张「传销头子」卡：

| 卡 | 装槽 | 物品 GUID | 状态 |
|---|---|---|---|
| 传销头子法瑞斯·阿瑟雷密 | 工会（GuildHouse） | `1400000006` | ✅ 已在游戏中使用 |
| 传销头子法瑞斯·阿瑟雷密（北极版） | **北极小屋（Lodge）** | `1400000008` | 🆕 新加，待进游戏验证 |

## 基本信息

| 项 | 值 |
|---|---|
| 来源 | 本地自制 / 中文社区 |
| 旧目录名 | `[chuan xiao tou zi]Mr.LongV1.0` |
| **ModID** | `local-mr-long`（写死在 `modinfo.json`，改文件夹名不影响） |
| 分类 | Cheat |
| 加载顺序 | `LoadAfterIds: ["local-all-items-unlocked"]`（**不要删**，见根 README 第二节） |

---

## 卡一：传销头子（工会，`1400000006`）

一个自定义**传奇专家（Specialist）**物品：

| 属性 | 数值 | 效果 |
|---|---|---|
| `ProductivityUpgrade` | +300% | 生产力翻 4 倍 |
| `MaintenanceUpgrade` | −75% | 维护费大幅下降 |
| `WorkforceAmountUpgrade` | −75% | 人力需求大幅下降 |
| `IncidentRiot/Fire/Illness/Explosion` | −99% | 几乎不会起义 / 起火 / 传染病 / 爆炸 |
| `ProvideIndustrialization` | `Powerplant` | 自身提供电力 |
| `TradePrice` / `TradePriceOnlineCurrency` | 1000 / 50 | 交易售价 |

**生效目标**（`EffectTargets`）：生产建筑 `193856`、果园/化学厂/工匠工作坊/生产线 `194008`、`194011`、`194023`、`194024`。

**获取方式**：把该物品塞进 8 个 NPC 的奖励池（`RewardPool/ItemsPool`，权重 `100`，很容易刷出）—— 这正是「传销头子」这个名字的由来。**库马克（北极）不上架老卡**，因为老卡是工会卡，北极没有工会。

- 旧世界：Sir Archbald `192069`、Eli Bleakworth `190774`、Madame Kahina `192068`、Anne Harlow `192070`
- 新世界：Isabel Sarmento `192073`、Jean La Fortune `192071`
- Cape Trelawney：Old Nate `193452`
- Enbesa：Emperor Ketema `127480`

---

## 卡二：传销头子·北极版（北极小屋，`1400000008`）

同一个头像、同一个名字，加「（北极版）」后缀；装槽改成 **北极小屋 `Lodge`**。

| 属性 | 数值 | 效果 |
|---|---|---|
| `FactoryUpgrade/ProductivityUpgrade` | **+300%** | 18 座北极生产建筑产量 ×4（**天然气矿场产量也 ×4**），与卡一同档 |
| `BuildingUpgrade/MaintenanceUpgrade` | **−75%** | 维护费降到 1/4，与卡一同档 |
| `BuildingUpgrade/WorkforceAmountUpgrade` | **−75%** | 人力需求降到 1/4 —— 等效「多出 3 倍可用人口」 |
| `IncidentInfectableUpgrade/IncidentFireIncreaseUpgrade` | **−99%** | 火灾风险几乎归零 |
| `IncidentInfectableUpgrade/IncidentExplosionIncreaseUpgrade` | **−99%** | 爆炸风险几乎归零（北极天然气矿场基础值 16） |
| `ExpeditionAttribute` | 医学 30 / 制作 30 / 狩猎 15 / 信仰 10 / 男性 | 远征属性 |
| `TradePrice` / `TradePriceOnlineCurrency` | 1000 / 50 | 交易售价 |

**两条设计口径**（刻意不写独立字段）：

1. **天然气不单挂 `AdditionalOutput`** —— 气矿产量被 `ProductivityUpgrade` 覆盖，生产力 +300% 就等于天然气 +300%；顺带 17 座其它北极工厂也一起 ×4。
2. **「加人口」不写 `ResidentsUpgrade`** —— 改用 `WorkforceAmountUpgrade −75%`：同样的人口能养 4 倍的工厂，等效于加人口，而且不碰住所、不产生「生产建筑 + 住所」的混装目标。

**生效目标**（`EffectTargets`）：只有一个 —— **所有北极生产建筑 `193770`**（18 座：伐木工人棚屋、锯木厂、炭窑、北极天然气矿场、深层金矿、鲸鱼/海豹/驯鹿/熊猎人、一级狩猎小屋、鹅农场、哈士奇农场、干肉饼工厂、油灯工厂、连帽大衣工厂、睡袋工厂、雪橇骨架工厂、犬雪橇工厂）。

**获取方式**：只放在**库马克 Qumaq `193835`（北极）**的池子里（`RewardPool/ItemsPool`，权重 `100`）。北极只刷这张卡，老卡不上架；老奈特据点在崔老妮海角、那边没有北极小屋，所以不给他加新卡。

**每个字段的原版原型**（都在北极小屋卡里出现过）：

| 本卡字段 | 原型卡 |
|---|---|
| 目标集合 = 全部 18 座北极生产建筑 | `116160` 音乐盒（`EffectTargets` 与 `193770` 完全一致） |
| `ProductivityUpgrade` | `116098` 象牙雪地护目镜 +60% |
| `MaintenanceUpgrade`（本卡 −75，同卡一） | `116069` 三齿鱼叉 −50% / 卡一 −75% |
| `WorkforceAmountUpgrade`（本卡 −75，同卡一） | `116043` 皮筏 / `116071` 鱼叉头 −50% / 卡一 −75% |
| `IncidentFire/ExplosionIncreaseUpgrade −99` | 小屋卡本身没有先例（工会卡有 40 张在用）；同 mod 的工会卡就是 −99 |
| `Allocation Lodge` + `GuildhouseItem` | `1772`、`116158` 等全部北极小屋卡 |

---

## 文件构成

```
data/config/export/main/asset/assets.xml          两张卡的物品定义 + 商人池
data/config/gui/texts_chinese.xml                 中英文文本
data/modgraphics/icons/icon_chuanxiaotouzi.png    两张卡共用的头像
```

文本 GUID：

| GUID | 内容 |
|---|---|
| `1400000006` | 卡一名称（键 = 物品资产 GUID） |
| `1400000007` | 卡一简介 / `InfoDescription` / 远征 `FluffText` |
| `1400000008` | 卡二名称（键 = 物品资产 GUID） |
| `1400000009` | 卡二简介 / `InfoDescription` / 远征 `FluffText` |

## 注意

- **卡一是原版物品 `192450`「说服者法瑞斯·阿瑟雷密」（史诗，生产力 +50%）的传奇强化克隆**：名字、头像和效果结构都来自它。原版那张仍然存在，两张可以同时持有。
- 卡一原本 `InfoDescription` 借用原版文本 `21354`、`LineID` 借用 `29139`，等于把原版那张卡的简介一起改掉；现已拆成自有编号 `1400000007`，原版文本恢复原样。
- 卡二依赖 **航道 DLC（`410042`）**：北极小屋本身就在该 DLC 里。
- **商人池按据点分**：老奈特 `193452` 是崔老妮那个交易商（`77 Third_party_06`，`Profile_3rdParty_ItemCrafter`）的 EndGame 池，上架老卡；库马克 `193835` 是北极交易商（`237 Third_party_11`）的 EndGame 池，只上架新卡。
- **北极的老奈特不卖卡**：他是另一个资产 `117422 Third_party_06b (Old Nate Arctic)`，`GoodsTrader=0`、六个档位的 `OfferingItems` 全是 `0`、没有 `RewardPool`，只是个制作中心——那里没有池子可加，本 mod 也不往里加东西。
- 卡二只作用**生产建筑**，北极住所的人口上限不变；「加人口」是通过人力 −75% 等效实现的。
- 防火/防爆字段在北极小屋卡上没有原版先例（工会卡有 40 张），属于同一机制，风险低但**未实测**；若游戏里不生效，把这两块删掉即可，其它字段不受影响。
- 卡一与 `download/mods-mr-long/mr-long-v1-2` **是同一物品、同一 GUID（`1400000006`）**，只能保留其一。
- V1.2 数值更弱（生产力 +200%、维护费 −25%、人力 −25%），但额外改了全球运输参数。
