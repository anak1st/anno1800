# research-easy

大幅降低研究所（Research Institute）的物品研发成本与时间。

## 基本信息

| 项 | 值 |
|---|---|
| 来源 | 本地 |
| 状态 | ✅ 已在游戏中使用 |
| 旧目录名 | `[Gameplay] Research Easy` |
| **ModID** | `local-research-easy` |
| 备份校验 | ✅ 与游戏目录逐字节一致（已同步为游戏版，1878 B） |

## 改了什么

共 **7 条 `ModOp`**：

### 1. 研发成本固定为 500，不再递增

作用于 8 个 `ProgressBalancing` 对象，统一 `<Value>500</Value>`，并把 `ThresholdInterval` 与 `ValueIncrease` 归零：

| GUID | 含义（文件内注释） |
|---|---|
| `128475` | Item Crafting Research Costs Common |
| `128952` | Item Crafting Research Costs Uncommon |
| `128953` | Item Crafting Research Costs Rare |
| `128954` | Item Crafting Research Costs Epic |
| `128955` | Item Crafting Research Costs Legendary |
| `129525` | Permit Crafting Costs Balancing |
| `126888` | Godlike Research Costs Balancing |
| `123401` | Recipe Research Costs Balancing |

### 2. 研发时间：1 分钟内封顶

| 项目 | 改后 |
|---|---|
| `MaximumWorkforceTime`（GUID `120244`） | `60000` ms = **1 分钟** |
| `MaximumWorkforceAmount` | `10000`（1 万工程师达到最快） |

### 3. 神级研发同样处理

两条全文档匹配（`//Godlike/CraftingConfig/...`）的 `ModOp`，把神级研发的 `MaximumWorkforceTime` 设为 `60000`、`MaximumWorkforceAmount` 设为 `10000`。

### 4. 气矿可移动（署名 By Taube）

```xml
<ModOp GUID = '112691' Path = "/Values/Building" Type = "add">
  <Movable>1</Movable>
  <MoveRequiredGodlike>MoveOil</MoveRequiredGodlike>
</ModOp>
```

需神级「MoveOil」解锁才能移动气矿。

## 版本历史

| 版本 | ModOp 数 | 内容 |
|---|---|---|
| 当前（游戏目录） | 7 | 含上述全部四项 |
| 早期（备份旧版） | 3 | **缺**研发时间与神级研发修改 |

备份已于同步时更新为当前版本，旧版内容仅作记录。
