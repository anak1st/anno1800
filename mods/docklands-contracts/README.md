# docklands-contracts

港湾主要码头 `601470` 的进出口贸易合同槽位从 `1` 提高到 `7`，每座岛各自 7 份。

- **ModID**：`local-docklands-contracts`
- 依赖：港湾 DLC `410083`

```xml
<ModOp Type="merge" GUID="601470" Path="/Values/Dockland">
  <TradeContractSlotsForMainBuilding>7</TradeContractSlotsForMainBuilding>
</ModOp>
```

全游戏只有 `601470` 用这个字段，各区域的港湾主要码头共用同一资产，改一处即全部生效。

## 注意

与社区「更多贸易合同」类 mod 改同一字段，同时启用会按加载顺序互相覆盖。
