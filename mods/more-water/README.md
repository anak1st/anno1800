# more-water

扩大 Enbesa（非洲）的水源灌溉范围与管道容量。

## 基本信息

| 项 | 值 |
|---|---|
| 来源 | 原创作者 schwubbe，原 mod.io ID `3225680`（More water for Enbesa） |
| 状态 | ✅ 使用中 |
| ModID | `local-more-water` |
| 依赖 | DLC `LandOfions`（帝国之狮 / Enbesa） |

## 改了什么

| 项目 | GUID | 改后 |
|---|---|---|
| `PipeFillCapacity` | `114544` | `1000` |
| 河流 `Source_River` 灌溉扩散 | `114759` | `8` 格 |
| 运河 `Source_Canal` | `114759` | `8` 格 |
| 小湖 `Source_Lake_Small` | `114759` | `8` 格 |
| 中湖 `Source_Lake_Medium` | `114759` | `9` 格 |
| 大湖 `Source_Lake_Large` | `114759` | `11` 格 |

所有水源都加了 `TileItselfIsIrrigated = 1`（水源自身也算已灌溉）。

## 注意

- `PipeFillCapacity` 用的是 `Type="replace"`，Path 到 `/Values/IrrigationSource/PipeFillCapacity`。**改动时留意 `replace` 会丢弃未写出的子节点。**
- `download\old\mods-public-service-range\` 里【非洲】全建筑距离那个 zip 改**同一批 GUID**（`114544`、`114759`）。若启用它需自行决定谁生效。