# docklands-contracts

港湾兑换整合：**槽位 + 货物**。由原来的 `docklands-contracts`（槽位）与 `trade-contracts`（货物）合并，`trade-contracts` 已删除。

- **ModID**：`local-docklands-contracts`
- 依赖：港湾 DLC `410083`

## 改了什么

| # | 目标 | 原版 | 改后 |
|---|---|---|---|
| 1 | `601470` 港湾主要码头 `/Values/Dockland/TradeContractSlotsForMainBuilding` | `1` | **`7`** |
| 2 | `131764` `TradeContractFeature` 里 5 个商人最后一档的 `Trades` | — | 末尾追加 **27 种货** |

**原版资产一个都没动**：`FeatureUnlock`、原版货物的 `Unlock`/`Level` 全部保持原样；新增货物只是追加在原有列表末尾，因此仍受该档位原有的解锁条件约束。

## 追加位置与稀有度

每个商人只加在**最后一档**（`Trades` 末尾），`Level` 保留并**从低到高**排列（Rare → Epic → Legendary），所以新增货物排在原版最后一件之后、一件比一件稀有。

| 商人 | TraderName | 档位 | 追加 |
|---|---|---|---|
| 破烂小郡 Tattershire | `131819` | `131852`（4/4） | 小麦粉、鱼油、甘蔗、棉花（Rare）；糖、树脂、樱桃原木、肉桂、椰子油、柑橘水果、樟脑油、万扎木材（Epic） |
| 女歌手 Chanteuse | `131765` | `131824`（4/4） | 鲸油、海豹皮（Epic）；熊毛皮（Legendary） |
| 老黎凡特 Old Levant | `131767` | `131828`（4/4） | 山羊奶、木槿花瓣、龙虾、药草、牛奶、兰花（Epic） |
| 道听涂说 Ganymedia | `131813` | `131840`（4/4） | 泥金装饰手抄本（Legendary） |
| 承诺信托 Promise Trust | `131817` | `131847`（3/3，该商人只有 3 档） | 口香糖、乙醇、赛璐珞、电梯、亮面漆（Legendary） |

> 原 `trade-contracts` 里 KITEA（`131811`）那条是空 `ModOp`（没有任何货物），合并时没有带过来。

## 注意

- 新增货物**没有**去掉前置解锁：它们和原版同档货物一样，要等该档位的原版解锁条件（进口量 / 出口量 / 进行中协定数）满足后才会出现。
- 原版没有 `Legendary` 进口货；本 mod 的 7 种 Legendary 属于新增梯度顶端，进游戏重点看它们是否正常显示。
- `Level` 很可能是「出口等级」相关的标签（和 `TradeUpgrades` 同枚举）；保留它 = 保留稀有度梯度。
- 与其它改 `131764` 或 `601470` 的 mod 会按加载顺序互相覆盖，别同时启用。

## 验证

复制到 `<game_dir>\mods\` 后启动游戏，看
`%USERPROFILE%\Documents\Anno 1800\log\mod-loader.log`：

```
[info] Load Docklands Trade Slots + Goods (2.0.0, local-docklands-contracts) from mods\docklands-contracts
[info] Loading complete
```

进游戏后点港湾主要码头 →「出口 / 进口」：槽位应为 7；各商人最后一档的列表末尾应能看到新增货物。
