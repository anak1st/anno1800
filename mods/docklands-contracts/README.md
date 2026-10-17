# docklands-contracts

把「港湾」（Docklands）**港湾主要码头**给的**进出口贸易合同（兑换）槽位**从 `1` 提高到 `3`
—— 一座岛的港湾就能同时挂 3 份合同，不用为了多开几份兑换而在多座岛上各建一套港湾。

## 基本信息

| 项 | 值 |
|---|---|
| 来源 | 本地（新做） |
| 状态 | ⚠️ 已复制进游戏 `mods\`，**但还没启动游戏验证**（数值与路径已按游戏文件核对） |
| **ModID** | `local-docklands-contracts` |
| 显示名 | **港湾兑换槽位增加**（英文 `More Docklands Trade Slots`） |
| 目标资产 | `601470` 港湾主要码头（模板 `DocklandMain`） |
| 依赖 | 港湾 DLC `410083` |

## 改了什么

```xml
<ModOp Type="merge" GUID="601470" Path="/Values/Dockland">
  <TradeContractSlotsForMainBuilding>3</TradeContractSlotsForMainBuilding>
</ModOp>
```

| 项目 | 原版 | 改后 |
|---|---|---|
| `TradeContractSlotsForMainBuilding`（GUID `601470`） | `1` | **`3`** |

### 为什么只改一处就够

- 用的是 `merge`，只动 `/Values/Dockland` 里的这一个子节点；同级的
  `AdditionalModuleLimitsPerExportLevel`、`LoadingSpeedBoostPerModule` 原样保留。
- 原版 `assets.xml` 里**只有这一个资产**带 `TradeContractSlotsForMainBuilding`
  （`DocklandMain` 模板也只被 `601470` 使用），而各区域的港湾主要码头共用这个资产，
  所以改这一处，每一座岛的港湾主要码头都跟着变，不需要按区域分别改。
- 这个数是**每座岛**的：每座岛各算各的 3 份合同，不是全地图共 3 份。

## 注意

- **没有港湾 DLC 就没有这座建筑**，这条 ModOp 找不到目标时的行为未验证（理论上整条跳过、不影响其他 mod）。
- 与社区「更多贸易合同」类 mod（50 / 100 / 200 份那种）改的是**同一个字段**，
  同时启用会互相覆盖，按加载顺序定胜负。若两者都装，用 `modinfo.json` 的
  `LoadAfterIds` 明确顺序，或只保留一个。
- 给已有存档加这个 mod 属于改建筑数值，通常安全；**按官方说明，装过的 mod 再从存档里移除不推荐**。
- 从备份复制进游戏时整文件夹一起复制（`modinfo.json` 必须带 `Version`）。

## 验证

复制到 `<game_dir>\mods\`（`game_dir` 见 `anno.json`）后启动游戏，看
`%USERPROFILE%\Documents\Anno 1800\log\mod-loader.log`：

```
[info] Load More Docklands Trade Slots (1.0.0, local-docklands-contracts) from mods\docklands-contracts
…
[info] Loading complete
```

进游戏后点港湾主要码头 →「出口 / 进口」，合同槽位应显示 3 个。

## 原版数据出处

`temp/db/data/config/export/main/asset/assets.xml` 第 `3939377` 行（资产 `601470`，`/Values/Dockland`）：
`<TradeContractSlotsForMainBuilding>1</TradeContractSlotsForMainBuilding>`。
