# airship-loading-speed

飞艇码头装卸速度从 `2` 提高到 `8`（4 倍），旧世界 `962`、新世界 `963` 两座都改。

- **ModID**：`local-airship-loading-speed`

## 改动

| 项目 | 原版 | 改后 |
|---|---|---|
| `LoadingSpeed`（`/Values/LoadingPier`） | `2` | **`8`** |

```xml
<ModOp Type="merge" GUID="962,963" Path="/Values/LoadingPier">
  <LoadingSpeed>8</LoadingSpeed>
</ModOp>
```
