# trade-contracts

往各个 NPC 商人的**贸易合同**里追加可交易货物。

## 基本信息

| 项 | 值 |
|---|---|
| 来源 | 本地 |
| 状态 | ✅ 已在游戏中使用 |
| 旧目录名 | `[Gameplay] Trade Contracts` |
| **ModID** | `local-trade-contracts` |
| 备份校验 | ✅ 与游戏目录逐字节一致（已同步为游戏版，3875 B） |

## 改了什么

共 **7 条 `ModOp`**，每条往一个商人的 `TradeLevels/Item[...]/Trades` 里追加 `<Item>`：

| 商人 | TraderName | 追加的货物 |
|---|---|---|
| Tattershire | `131819` | 小麦粉、鱼油、甘蔗、棉花、糖、树脂、樱桃原木、肉桂、椰子油、柑橘水果、樟脑油、万扎木材 |
| Chanteuse（FEEDL） | `131765` | 鲸油、海豹皮、熊毛皮 |
| Old Levant & Co.（Qinsa Mining） | `131767` | 山羊奶、木槿、龙虾、药草、牛奶、兰花 |
| KITEA | `131811` | **空块**（无货物，占位） |
| The Promise Trust（Ganymedia） | `131813` | 手抄本 |
| Ganymedia | `131817` | **口香糖、乙醇、赛璐珞、电梯、亮面漆**（Legendary，DLC 货物） |

所有 `ModOp` 的 `GUID` 都是 `131764`（`TradeContractFeature`），通过 XPath 里的 `TraderName` 与 `Unlock` 定位具体商人。

## 版本历史

| 版本 | 大小 | 内容 |
|---|---|---|
| 当前（游戏目录） | 3875 B | 含 `131817` 的口香糖/乙醇/赛璐珞/电梯/亮面漆 5 条 Legendary |
| 早期（备份旧版） | 2240 B | **缺**这 5 条 DLC 货物 |

备份已于同步时更新为当前版本，旧版内容仅作记录。
