# docklands-cooldown

把「贸易合同」的商人往返时间缩短到 5 分钟。

## 基本信息

| 项 | 值 |
|---|---|
| 来源 | 本地 |
| 状态 | ✅ 已在游戏中使用 |
| 旧目录名 | `[Gameplay] Docklands Cooldown 5min`（备份里曾叫 `... Cooldown 5`） |
| **ModID** | `local-docklands-cooldown` |
| 备份校验 | ✅ 与游戏目录逐字节一致 |

## 改了什么

```xml
<ModOp Type="Replace" GUID='131764' Path="/Values/TradeContractFeature/TraderTransferTime">
  <TraderTransferTime>300000</TraderTransferTime>
</ModOp>
```

| 项目 | 改后 |
|---|---|
| `TraderTransferTime`（GUID `131764` = `TradeContractFeature`） | `300000` ms = **5 分钟** |

## 注意

备份里曾有两个命名（`[Gameplay] Docklands Cooldown 5` 与 `... 5min`），**内容完全相同**（同一 `assets.xml`，MD5 `E2B2F513...`）。现已在备份与游戏目录中**统一为 `docklands-cooldown`**，不再有重复加载的风险。
