# research-easy

研究所研发成本固定 500 不递增、时间 1 分钟封顶；气矿可移动。共 7 条 ModOp。

- **ModID**：`local-research-easy`

## 成本

8 个 `ProgressBalancing` 对象统一 `Value = 500`，`ThresholdInterval` 与 `ValueIncrease` 归零。

| GUID | 对象 |
|---|---|
| `128475` | 普通物品 |
| `128952` | 罕见物品 |
| `128953` | 稀有物品 |
| `128954` | 史诗物品 |
| `128955` | 传奇物品 |
| `129525` | 许可证 |
| `126888` | 神级研发 |
| `123401` | 配方 |

## 时间

- `MaximumWorkforceTime`（`120244`）→ `60000` ms（1 分钟）
- `MaximumWorkforceAmount` → `10000`（1 万工程师达到最快）
- 神级研发的两条 ModOp 同值

## 气矿可移动

`112691` 加 `Movable = 1`、`MoveRequiredGodlike = MoveOil`，需神级「MoveOil」解锁。署名 Taube。
