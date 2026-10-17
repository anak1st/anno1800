# Anno 1800 Mod 参考

本目录的文档：

| 文件 | 内容 |
|---|---|
| `reference.md` | 本文件 —— mod 安装位置、文件夹结构、`modinfo.json` 字段、加载顺序 |
| `game.md` | 游戏基础信息 —— 版本、区域、DLC、卡牌模板与数据结构 |
| `cards.md` | 全部卡牌清单（装槽 → 稀有度），标出在不在 `all-items-unlocked` 卡池、可否研发（⚙️ 脚本生成） |
| `cards-special.md` | 带 `ScenarioFilter` 的剧本专用卡（✍️ 手工维护处置列） |

`reference.md` 的内容分两部分：

- **【本机实测】** —— 在你这台机器上验证过的，可直接照用。
- **【官方】** —— 来自 Ubisoft / Anno Union 官方说明。

游戏版本 `v18.4.1412158`，原版内置加载器（`anno-mod-loader` 这类社区 modloader **未安装**）。

---

## 1. mod 放哪里

**两个位置，任选其一，都会被加载**【官方】：

```
<game_dir>\mods\                               ← 当前用的（game_dir 见 anno.json）
%USERPROFILE%\Documents\Anno 1800\mods\
```

mod.io 平台另有自己的库（订阅的 mod 存这里，由平台管理）：

```
%PUBLIC%\mod.io\4169\mods\                    ← 4169 是 Anno 1800 在 mod.io 的编号
```

---

## 2. 一个 mod 文件夹的结构

```
某个-mod/
├── data/
│   └── config/export/main/asset/assets.xml     ← 真正起作用的就是这个文件
├── modinfo.json                                ← 元信息（建议有）
└── README.md                                   ← 说明（可选，加载器不解析）
```

### 硬性要求

| 要求 | 后果 |
|---|---|
| **`assets.xml` 里至少一条真实 `<ModOp>`** | 空 `<ModOps>` → **游戏静默闪退**，日志只有 `Load mods` 一行 |
| **`modinfo.json` 里 `Version` 必须写** | 缺失 → 日志报 `[error] ... Version is missing`（不崩，但版本号为空） |

---

## 3. `modinfo.json` 的字段

**【本机实测】** 原版加载器会读这个文件，实测结果：

| 字段 | 结果 |
|---|---|
| `Version` | **必需**。三段式如 `"1.0.0"` |
| `ModID` | 被读取。**它决定 mod 身份** —— 有它，改文件夹名不影响识别 |
| `ModName` | 被读取，用于日志与游戏内显示。**多语言对象格式可用** |
| `LoadAfterIds` | ✅ **生效，且会压过默认的字母序** |
| `Anno` | **不必要** —— 不写没有任何报错 |

本备份用的最小可用集：

```json
{
  "Version": "1.0.0",
  "ModID": "local-mr-long",
  "ModName": { "English": "Mr.Long the Persuader", "Chinese": "传销头子" }
}
```

指定加载顺序时加一条：

```json
"LoadAfterIds": ["local-all-items-unlocked"]
```

> **不写 `modinfo.json` 也能加载**，此时日志显示 `(unversioned, 文件夹名)`，ModID 就是文件夹名 —— 缺点是**改文件夹名等于换 mod 身份**。

### 何时需要 `LoadAfterIds`

**当两个 mod 改同一棵对象树时。** 典型例子：

- `all-items-unlocked` 用 `replace` **整个替换** 商人的 `/Values/RewardPool`
- `mr-long` 往它的**子节点** `/Values/RewardPool/ItemsPool` 里 `add` 传销头子

如果 `mr-long` 先加载，它加的物品会被随后整个替换掉，**且游戏不报警**。声明 `LoadAfterIds` 后顺序不再依赖字母序的巧合。

---

## 4. 加载顺序

**【本机实测】**

- 默认按 **mod 文件夹名字母序**。
- **`LoadAfterIds` 可以完全覆盖字母序** —— 用 5 个探针链式声明（方向与字母序相反）验证，加载顺序完全按链走。
- 括号里显示 `(<Version>, <ModID>)`；无 `modinfo.json` 时显示 `unversioned`。

**排序是否区分大小写**：未验证。

---

## 5. ModOp：怎么改游戏数值

**【本机实测】** mod 就是一个 XML 补丁文件，里面每条 `<ModOp>` 对应一次改动。

### 定位目标

```xml
<!-- 用 GUID 指定资产，支持逗号分隔多个 -->
<ModOp Type="merge" GUID='2001241' Path="/Values/BuildingBaseTiles">
  <HarbourConstructionAreaRadius>56</HarbourConstructionAreaRadius>
</ModOp>
```

- `Type` —— 操作类型
- `GUID` —— 目标资产编号（可写多个，逗号分隔）
- `Path` —— 目标节点（XPath）

### 常用类型【社区文档】

| 类型 | 作用 |
|---|---|
| **`merge`** | 有则改、无则加。**不会删除其他节点** —— 最安全，优先用 |
| `replace` | 替换选中内容，**旧内容全部丢弃**。避免用于大结构 |
| `add` | 在选中节点内部**追加**。**不检查是否已存在** |
| `addNextSibling` / `addPrevSibling` | 插到选中节点之后 / 之前（同级） |
| `remove` | 删除选中节点 |

### 实例

```xml
<!-- 把飞艇码头装卸速度从 2 改成 8 -->
<ModOp Type="merge" GUID="962,963" Path="/Values/LoadingPier">
  <LoadingSpeed>8</LoadingSpeed>
</ModOp>
```

---

## 6. 怎么确认 mod 加载成功

看日志结尾：

```
%USERPROFILE%\Documents\Anno 1800\log\mod-loader.log
```

正常的样子：

```
[info] Load mods
[info] Load Mr.Long the Persuader (1.0.0, local-mr-long) from mods\mr-long
…
[info] Loading complete        ← 有这行才算成功
```

| 现象 | 含义 |
|---|---|
| 结尾有 `Loading complete` | 正常 |
| **只有 `Load mods` 一行** | 某个 `assets.xml` 是空 `<ModOps>` |
| `[error] ... Version is missing` | 某個 `modinfo.json` 缺 `Version` |

`(unversioned, 名字)` 表示该 mod 没有 `modinfo.json`，用文件夹名当 ID。

---

## 7. 用 `.zip` 包装的 mod

**【本机实测】** 原版加载器**不读 zip**，必须解压成文件夹。

---

## 8. 关于存档的注意事项【官方】

> Removing mods from a save game is not recommended. Mods often leave trails in your save game. Adding removed mods at a later stage again can also lead to problems.
>
> Only remove mods from an existing save game if you encounter serious problems with it.

**加 mod 到已有存档**：取决于 mod 本身，看它的说明。
**从已有存档移除 mod**：不推荐，只在存档出严重问题时才做。

主菜单里、加载存档之前可以调整启用的 mod 组合。

---

## 9. 官方来源

| 内容 | 链接 |
|---|---|
| 官方 FAQ（安装位置、存档注意事项） | <https://www.anno-union.com/modding-in-anno-1800-faq/> |
| 官方 mod 总览页 | <https://www.anno-union.com/mods-1800-en/> |
| mod.io 上的 Anno 1800 | <https://mod.io/g/anno-1800> |
| 社区 modloader 文档（**部分适用**，见下） | <https://jakobharder.github.io/anno-mod-loader/> |

### 关于社区文档

`anno-mod-loader` 由社区开发者 **Jakob Harder** 维护，Ubisoft 官方 DevBlog 指名推荐它作为文档。

但**它描述的是社区 modloader 的完整规范，原版内置加载器只实现了其中一部分**。本机已确认可用的是第 3 节列出的字段；至于 `Category`、`Description`、`Anno`、`Difficulty`、`GameSetup`、`Conditions`、`Group`、`Include` 等，**是否生效未验证** —— 想用先在本机试。
