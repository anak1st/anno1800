# no-forest-planting

让所有需要种植森林/果园的建筑**不再需要外部种植区**。

## 基本信息

| 项 | 值 |
|---|---|
| 来源 | 本地（中文社区 mod 的整合版） |
| 状态 | ✅ 已在游戏中使用 |
| 旧目录名 | `[Gameplay] Radius Factory No Limit` |
| **ModID** | `local-no-forest-planting` |
| 备份校验 | ✅ 与游戏目录逐字节一致 |

## 改了什么

共 **21 条 `ModOp`**，覆盖 **24 个 GUID**，统一把 `NeededAreaPercent` 设为 `0`（其中 3 条 ModOp 各覆盖多个 GUID）：

```xml
<ModOp Type="merge" GUID='1010266,24657' Path="Values/FreeAreaProductivity">
  <NeededAreaPercent>0</NeededAreaPercent>
</ModOp>
```

| 类别 | 覆盖建筑 |
|---|---|
| 炭窑 | 旧世界 `1010298`、新世界 `24860,2396,1345`、北极 `114705` |
| 伐木工人棚屋 | 旧世界 `1010266,24657`、新世界 `101260`、北极 `114703`、非洲万扎 `122963` |
| 狩猎小屋 | 旧世界 `1010558`、北极 `116034`、驯鹿猎人小屋 `112667`、北极熊猎人小屋 `112673` |
| 榨油机 | 新世界工业榨油机 `1418` |
| 果园 | 旧世界建筑 `132933`/果酱 `133496`/树脂 `135085`/樱桃木 `135088`；新世界建筑 `133010`/橘子 `133031`/肉桂 `133030`/椰子油 `133004`/樟脑油 `134614` |

## 注意

- 这个 mod 与 `download/mods-no-forest-planting/` 里那 5 个 zip **是同一批东西**。zip 里的文件夹虽叫 `...(Woods)` / `(Fruits)` / `(Hunt)` / `(Coal)`，但改的是同一批 GUID、同一个 `FreeAreaProductivity` 属性；`【整合版】` 的 GUID 集合与本 mod 基本一致。**也就是说本 mod 就是那批 zip 的整合版**，那些 zip 对当前配置是冗余的。
- 那些 zip 里的 XML 是 **GBK 编码**，按 UTF-8 读会显示乱码。
