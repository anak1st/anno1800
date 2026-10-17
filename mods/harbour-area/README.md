# harbour-area

扩大港口的建造范围。

## 基本信息

| 项 | 值 |
|---|---|
| 来源 | 本地 |
| 状态 | ✅ 已在游戏中使用 |
| 旧目录名 | `[Gameplay] Increased Harbourarea` |
| **ModID** | `local-harbour-area` |
| 备份校验 | ✅ 与游戏目录逐字节一致 |

## 改了什么

```xml
<!-- Original Building Size for Harbors/Beachlines == 28, original for creative mode == 56 -->
<ModOp Type="merge" GUID='2001241' Path="/Values/BuildingBaseTiles">
  <HarbourConstructionAreaRadius>56</HarbourConstructionAreaRadius>
</ModOp>
```

| 项目 | 原版 | 改后 |
|---|---|---|
| `HarbourConstructionAreaRadius` | `28` | **`56`**（2 倍，与创造模式持平） |

## 注意

- mod 文件里把创造模式的 `HarbourConstructionAreaRadiusCreativeMode` **注释掉了**，未生效。
- `download/mods-public-service-range/` 里【海岸线】距离那个 zip 改的是**同一个 GUID `2001241`**，但数值为 `80`。**两者同时启用会互相覆盖**（按加载顺序定胜负）。
