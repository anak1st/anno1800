# airship-loading-speed

提高飞艇码头的装卸速度。

## 基本信息

| 项 | 值 |
|---|---|
| 来源 | 本地 |
| 状态 | ✅ 已在游戏中使用 |
| 旧目录名 | `[Gameplay] Airship Loading Speed` |
| **ModID** | `local-airship-loading-speed` |
| 备份校验 | ✅ 与游戏目录逐字节一致 |

## 改了什么

```xml
<!-- Old World 962, New World 963 -->
<!-- Original LoadingSpeed == 2 -->
<ModOp Type="merge" GUID="962,963" Path="/Values/LoadingPier">
  <LoadingSpeed>8</LoadingSpeed>
</ModOp>
```

| 项目 | 原版 | 改后 |
|---|---|---|
| `LoadingSpeed`（飞艇码头） | `2` | **`8`**（4 倍） |

覆盖旧世界 GUID `962` 与新世界 GUID `963`。
