# docklands-cooldown

贸易合同商人的往返时间改为 **5 分钟**（`TraderTransferTime` = `300000` ms）。

- **ModID**：`local-docklands-cooldown`
- 目标：`131764`（`TradeContractFeature`）

```xml
<ModOp Type="Replace" GUID='131764' Path="/Values/TradeContractFeature/TraderTransferTime">
  <TraderTransferTime>300000</TraderTransferTime>
</ModOp>
```
