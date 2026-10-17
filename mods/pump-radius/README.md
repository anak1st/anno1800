# pump-radius

扩大油井/气井的模块建造半径。

## 基本信息

| 项 | 值 |
|---|---|
| 来源 | 本地 |
| 状态 | ✅ 已在游戏中使用 |
| 旧目录名 | `[Gameplay] Increased Radius for Pump` |
| **ModID** | `local-pump-radius` |
| 备份校验 | ✅ 与游戏目录逐字节一致 |

## 改了什么

| 目标 | GUID | 属性 | 改后 |
|---|---|---|---|
| 气矿（Gas） | `112690` | `ModuleBuildRadius` | **`20`** |
| 油矿（Oil） | `101331` | `ModuleBuildRadius` | **`20`** |

两条 `ModOp` 都作用于 `/Values/ModuleOwner`，即扩大可挂载模块的半径：

```xml
<!-- Gas -->
<ModOp Type="merge" GUID='112690' Path="/Values/ModuleOwner">
  <ModuleBuildRadius>20</ModuleBuildRadius>
</ModOp>
<!-- Oil -->
<ModOp Type="merge" GUID='101331' Path="/Values/ModuleOwner">
  <ModuleBuildRadius>20</ModuleBuildRadius>
</ModOp>
```
