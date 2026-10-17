# whole-island-buildings

让全岛只需**一座**公共建筑即可满足全岛需求。

## 基本信息

| 项 | 值 |
|---|---|
| 来源 | 原创作者 GlacialPigeon69，原 mod.io ID `3294467`（AIO - Buildings Affect Whole Island） |
| 状态 | ✅ 使用中 |
| ModID | `local-whole-island-buildings` |
| 规模 | **45 条 `ModOp`**，覆盖 4 个区域的公共建筑 |

## 改了什么

核心手法：把满意度距离撑到接近全岛尺寸。

| 属性 | 含义 | 设为 |
|---|---|---|
| `FullSatisfactionDistance` | 完全满足的距离 | `995` |
| `NoSatisfactionDistance` | 完全无效的距离 | `1000` |
| `IndustrializationDistance` | 电力/工业化覆盖距离 | `1000` |
| `BaseStreetRange`（总督府） | 街道连接范围 | `1000`（每模块 +`100`） |
| `ProductionBuffDistance` | 生产加成距离 | `175` |
| `SocketScopeRadius` | 插座/模块作用半径 | `125` / `150` / `250` |
| `HaciendaRadius` | 新世界庄园半径 | `200` |
| `HeatRange`（北极加热器） | 供暖范围 | `1000` |
| `ActivationRadius`（公交站） | 生效半径 | `175`（街道连接 `1500`） |

### 覆盖的建筑（按文件注释）

| 区域 | 建筑 |
|---|---|
| **旧世界 & Cape Trelawney** | 总督府、市场、酒馆、教堂、学校、综艺剧院、大学、银行、会员俱乐部、广播塔、燃油电厂、燃气电厂、邮局、百货店/家具店/药店、酒吧、公交站、咖啡馆、铁塔、餐厅 |
| **新世界** | 市场、礼拜堂、水坝、燃料电厂、发电站、邮局、庄园、桑巴学校、海滩、电影院、拳击场 |
| **Enbesa** | 市场、乐师庭院、修道院 |
| **北极** | 邮局、北极加热器、食堂 |

## 注意

- 大部分用 `merge`（只改数值，不动其他节点）；少数节点原本不存在，改用 `add`。
- 与 `harbour-area` **不冲突**：本 mod 改满意度/供电距离，`harbour-area` 改港口建造范围，字段不同。
- 与 `all-items-unlocked` **不冲突**：后者改商人的 `RewardPool`。