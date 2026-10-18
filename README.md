# Anno 1800 Mod 备份

Anno 1800（Steam appid `916440`）的 mod 备份与索引。游戏安装位置写在根目录 `anno.json` 的 `game_dir` 里（本机配置，不进 git，见第〇节）。

```
Anno1800\
├── scripts\     链路脚本（进 git）：解包游戏数据
├── src\anno\    工具链（唯一一个包，从零重写）：paths / scan / model / effects / cards / entities /
│                traders / database / render / pools / rules / research / placement / tables
├── tests\       单元测试（pytest，只测纯函数）
├── build_db.py         扫游戏数据 → data\（一个资产一个 JSON，见 docs\data-model.md）
├── build_research.py   研发展开   → temp\research-cards.txt
├── build_cards.py      data\ → docs\cards.md + temp\merchant-pools.md
├── build_profile.py    data\ → temp\card-profile.tsv
├── edit_pools.py       改 mod 卡池（report / tidy / add / drop / move / exclusive / assign）
├── query.py           查数据库：card / find / show / trader / building / good
├── pyproject.toml       uv 项目定义（依赖 lxml / typer / rich，dev 是 pytest / ruff）
├── mods\        12 个维护中的 mod，每个含 data\ + modinfo.json + README.md
├── docs\        参考文档（game.md、reference.md、cards.md、cards-special.md、data-model.md）
├── data\        解析层：一个资产一个 JSON（不进 git，可重建）
├── old\         迁移归档：旧的聚合 JSON 与被替换的代码（不进 git）
├── download\    下载来的原始文件（不进 git）
│   ├── RdaConsole.zip           RDA 解包工具
│   ├── AssetViewer.exe          资产浏览器（GUI）
│   └── old\                     封存的原始素材与未采用版本
├── tools\       解包出来的可执行 + PowerShell 脚本（不进 git）
├── temp\        原始层：解包数据、可研发清单、人看的档案（不进 git，见 temp\README.md）
├── saves\       本地存档备份（.a7s，见 saves\README.md，不进 git）
└── README.md    本文件
```

**只跟踪整理好的成品、文档与工具链**：`mods\`、`docs\`、`src\`、根目录的入口脚本。
`download\`、`tools\`、`temp\`、`data\`、`old\`、`saves\` 都在 `.gitignore` 里。

| 目录 / 文件 | 放什么 | 进 git |
|---|---|---|
| `mods\` | **维护中的 12 个 mod** —— 已验证，随时可复制进游戏 | ✅ |
| `docs\` | 参考文档 | ✅ |
| `src\anno\` | 工具链的库（一个包） | ✅ |
| 根目录 `build_*.py`、`edit_pools.py`、`query.py` | 入口脚本，一个脚本一个目标 | ✅ |
| `tests\` | 单元测试 | ✅ |
| `download\` | **下载来的原始文件** —— zip、exe、封存素材 | ❌ |
| `tools\` | 解包出来的可执行与 PowerShell 脚本 | ❌ |
| `temp\` | **原始层** —— 解包出的 `assets.xml`、可研发清单、档案表（说明见 `temp\README.md`） | ❌ |
| `data\` | **解析层** —— 一个资产一个 JSON（`cards/` `buildings/` `goods/` …），可重建 | ❌ |
| `old\` | **迁移归档** —— 旧的 4 个聚合 JSON、被替换的代码快照（说明见 `old\README.md`） | ❌ |
| `saves\` | **本地存档备份** —— `accounts\` 下的 `.a7s`（说明见 `saves\README.md`） | ❌ |

**命名约定**：mod 文件夹统一为**全小写英文 + 中划线（kebab-case）**，不含空格、方括号等特殊字符。见第三节的清单。

> `mods\` 里的 12 个 mod，有 3 个原本来自 mod.io 平台（`more-water`、`whole-island-buildings`、`all-items-unlocked`）。它们**已不再依赖 mod.io 订阅** —— 本地副本齐全，`modinfo.json` 也已补好。

---

## 〇、全流程（从零到能查）

**单向流程**：游戏本体 → `temp\`（解包）→ 代码分析 → `data\` → 文档；**mod 的 `assets.xml` 是这条链最后的输出**，解析时不读它。

```
<game_dir>   --RdaConsole-->  temp\db\…        原始：解包出的 assets.xml / texts_*.xml
temp\db      --build_db.py-->  data\           解析：一个资产一个 JSON（约 3100 个文件）
data\        --build_cards.py--> docs\cards.md  展示：文档
data\        --query.py-->     终端             查询
data\        --edit_pools.py--> mods\…\assets.xml  改卡池，再把 mods\ 同步进游戏
```

| 步 | 命令 | 作用 | 产物 | 耗时 |
|---|---|---|---|---|
| 0 | 新建 `anno.json`（内容见「配置」） | 填 `game_dir`（游戏安装目录） | `anno.json`（不进 git） | — |
| 1 | `pwsh scripts\extract-game-data.ps1` | 解包游戏数据（调用 RdaConsole） | `temp\db\data\config\…`（约 296 MB） | ~3 分钟 |
| 2 | `uv run build_research.py` | 研发展开（四层递归） | `temp\research-cards.txt` | ~4 s |
| 3 | `uv run build_db.py` | **一次扫描 XML → JSON 数据库**（卡牌范围由模板定义） | `data\`（约 3100 个文件） | ~6 s |
| 4 | `uv run build_cards.py` | 渲染文档 | `docs\cards.md`、`temp\merchant-pools.md` | 0.3 s |
| 5 | `uv run build_profile.py` | 人看的档案 | `temp\card-profile.tsv` | 0.3 s |
| 6 | `uv run query.py card 香料大师` | 查一张卡的作用 | 终端 | <1 s |
| 7 | `uv run edit_pools.py report` | 看卡池现状（大小 / 重复 / 双挂） | 终端 | <1 s |
| 8 | `uv run edit_pools.py assign --dry-run` | 按规则重排卡池，先看流动明细（应显示 0 移动） | 终端 | ~6 s |
| 9 | `uv run edit_pools.py assign` | **按规则重建卡池**（收录范围 + 归属，默认不读旧内容；`--keep` 才基于现有文件） | `mods\all-items-unlocked\…\assets.xml` | ~6 s |
| 10 | 复制 `mods\` 到 `<game_dir>\mods\` | 让游戏加载 | — | — |
| 11 | 启动游戏看 `%USERPROFILE%\Documents\Anno 1800\log\mod-loader.log` | 验证 | 12 行 `Load …` + `Loading complete` | — |

第 1–5 步的完整命令（复制即用，`game_dir` / `temp_dir` 都从 `anno.json` 取）：

```powershell
# 1. 解包（首次安装、换游戏版本时跑一次；路径从 anno.json 取）
pwsh scripts\extract-game-data.ps1

# 2. 研发展开 -> temp\research-cards.txt
uv run build_research.py

# 3. 一次扫描 -> data\（一个资产一个 JSON）
uv run build_db.py

# 4. 文档 -> docs\cards.md + temp\merchant-pools.md
uv run build_cards.py

# 5. 人看的档案 -> temp\card-profile.tsv
uv run build_profile.py
```

几条规则：

- **只改归类 / 归属规则 / 排版** → 不用重跑 1–2（解包、研发）；改归类/规则跑 `build_db.py`，只改排版跑 `build_cards.py`。
- **只查数据** → `data\` 已存在就够，`query.py` 不读 XML。
- **改了 mod 卡池**（`edit_pools.py`）→ 重跑 `build_db.py` + `build_cards.py`，再把 `mods\` 同步进游戏。
- `data\`、`temp\`、`old\` 都不进 git：新克隆的仓库要先走 1–3 才能用 `query.py`。

### 配置（`anno.json`）

根目录的 `anno.json` 是**本机配置**（不进 git），只放跟本机有关的东西 —— 仓库结构和业务规则不在这里：

| 键 | 含义 | 默认 |
|---|---|---|
| `game_dir` | 游戏安装目录（解包、同步 mod、比对时用） | `""`（必须填） |
| `data_dir` | 解析层目录 | `data` |
| `temp_dir` | 原始层目录 | `temp` |
| `docs_dir` | 文档目录 | `docs` |

新建 `anno.json`，内容就四个键（缺的用默认值）：

```json
{
  "game_dir": "<Anno 1800 安装目录，例如 Steam 库里的 .../common/Anno 1800>",
  "data_dir": "data",
  "temp_dir": "temp",
  "docs_dir": "docs"
}
```

- **`anno.json` 不进 git**（每台机器一份）；想换机器/换盘只改它。
- 仓库里的示例脚本都从 `anno.json` 取路径，不硬编码盘符。
- `uv run query.py config` 打印最终取值，并标出 `temp\` / `data\` / `docs\` / `game_dir` 是否存在。
- 脚本里一律从配置取游戏目录，比如解包、比对都用 `$cfg = Get-Content anno.json | ConvertFrom-Json`。

---

## 一、mod 该放哪里（官方说明）

依据 Ubisoft 官方 FAQ [Modding in Anno 1800](https://www.anno-union.com/modding-in-anno-1800-faq/) 与社区维护的 [Anno Modloader Reference](https://jakobharder.github.io/anno-mod-loader/)：

**① mod.io 平台库**（游戏内置 mod 浏览器订阅的 mod 存这里）

```
C:\Users\Public\mod.io\4169\mods
```

- `4169` 是 mod.io 上 Anno 1800 的游戏 ID。
- 位置可用 `%LOCALAPPDATA%\mod.io\globalsettings.json` 里的 `RootLocalStoragePath` 改。

**② 手动安装位置**（官方给了两个，任选）

```
<game_dir>\mods                        ← 本仓库用这个（game_dir 见 anno.json）
%USERPROFILE%\Documents\Anno 1800\mods  ← 官方也认（可任选一处）
```

**关键：这两处是并列加载的，不是复制关系。** 游戏把 mod.io 库当作第二个 mod 源直接扫描，**mod.io 的 mod 不需要复制到游戏目录**。证据是 `Documents\Anno 1800\log\mod-loader.log` 用两种路径格式区分来源：

```
Load [Cheat] More Water (1.0, More Water) from C:\Users\Public\mod.io\4169\mods\3225680\[Cheat] More Water
Load [Gameplay] Airship Loading Speed (unversioned, ...) from mods\[Gameplay] Airship Loading Speed
```

`Bin\Win64` 下没有独立 loader 插件，加载逻辑内置在 `Anno1800.exe`（Python 3）里。

---

## 二、一个 mod 文件夹里该放什么

```
某个-mod/
├── data/
│   └── config/export/main/asset/assets.xml     ← 真正起作用的就是这个文件
├── modinfo.json                                ← 元信息（建议有，见下）
└── README.md                                   ← 说明（可选）
```

### `modinfo.json`：建议有，但 `Version` 是必需的

原版内置加载器**会读 `modinfo.json`**，字段实测结果：

| 字段 | 实测 |
|---|---|
| **`Version`** | **必需** —— 缺失时报 `[error] ... Version is missing`（不崩，但会报错，且日志里版本号为空） |
| **`ModID`** | 被读取。**它决定 mod 身份**，有了它改文件夹名不影响识别 |
| **`ModName`** | 被读取，用于显示。**多语言对象格式**（`{"English": "...", "Chinese": "..."}`）可用 |
| **`LoadAfterIds`** | ✅ **生效，且能完全压过字母序** —— 用来指定加载顺序 |
| `Anno` | **不需要** —— 写了也不报错，但不写完全没问题 |

本备份每个 mod 用的就是最小可用集：

```json
{
  "Version": "1.0.0",
  "ModID": "local-harbour-area",
  "ModName": { "English": "Increased Harbour Area", "Chinese": "港口建造范围扩大" }
}
```

需要指定加载顺序时再加一条：

```json
"LoadAfterIds": ["local-all-items-unlocked"]
```

> **没有 `modinfo.json` 也能加载**，此时日志显示 `(unversioned, 文件夹名)`，ModID 就是文件夹名 —— 缺点是**改文件夹名等于换 mod 身份**。

### 另外两条规则

| 规则 | 说明 |
|---|---|
| **`assets.xml` 里至少一条 `<ModOp>`** | 空 `<ModOps>` 会导致游戏**静默闪退** |
| **想自己改数值，就改 `assets.xml`** | 里面是 `<ModOp Type="merge" GUID='...' Path="...">` + 新值，改数字即可 |

### 什么时候需要 `LoadAfterIds`

**当两个 mod 改同一棵对象树的不同层级时。** 本集合里就有一例：

- `all-items-unlocked` 用 `replace` **整个替换** 7 个商人的 `/Values/RewardPool`（原版 9 位，两个海盗已移出）
- `mr-long` 往它的**子节点** `/Values/RewardPool/ItemsPool` 里 `add` 传销头子

如果 `mr-long` 先加载，它加的物品会被随后整个替换掉，**且游戏不报警**。所以 `mr-long` 声明了：

```json
"LoadAfterIds": ["local-all-items-unlocked"]
```

顺序就不再依赖字母序的巧合。**不要删掉这一条。**

### 怎么判断 mod 加载成功了

看 `C:\Users\<用户名>\Documents\Anno 1800\log\mod-loader.log`：

```
[info] Load mods
[info] Load Increased Harbour Area (1.0.0, local-harbour-area) from mods\harbour-area
[info] Loading complete        ← 有这行才算成功
```

- 格式是 `Load <ModName> (<Version>, <ModID>) from <路径>`
- **只有 `Load mods` 一行就结束 = 出问题** → 检查有没有空 `<ModOps>`
- 缺 `Version` 会单独打印 `[error]` 行

---

## 三、`mods\` —— 维护中的 12 个 mod

每个文件夹含 `data\`、`modinfo.json`、`README.md`，可直接复制进游戏 `mods\`。

| mod | 分类 | 一句话说明 |
|---|---|---|
| `mr-long` | Cheat | 两张传奇专家「传销头子」：工会版（生产力 +300%、维护/人力 −75%、四类事故 −99%、自带电力）+ 北极小屋版（生产力 +100%、维护 −50%、人力 −75%、防火防爆 −99%） |
| `airship-loading-speed` | Gameplay | 飞艇码头装卸速度 `2 → 8` |
| `docklands-cooldown` | Gameplay | 贸易合同商人往返时间 → 5 分钟 |
| `docklands-contracts` | Gameplay | 港湾兑换槽位增加（`1 → 3`） |
| `harbour-area` | Misc | 港口建造范围 `28 → 56` |
| `pump-radius` | Misc | 油井/气井模块半径 → `20` |
| `no-forest-planting` | Gameplay | 21 条 ModOp / 24 个 GUID，种植类建筑不再需要种森林 |
| `research-easy` | Cheat | 研发成本固定 500 不递增、研发时间 1 分钟封顶、气矿可移动 |
| `trade-contracts` | Gameplay | 6 个商人贸易合同追加货物，含 5 条 Legendary DLC 货 |
| `more-water` | Cheat | Enbesa 灌溉范围 8/8/8/9/11 格，管道容量 1000 |
| `whole-island-buildings` | Gameplay | 45 条 ModOp，一座公共建筑满足全岛 |
| `all-items-unlocked` | Misc | 49 条 ModOp（7 replace + 42 merge），整体替换 7 位商人的奖励池（两个海盗已移出） |

**每个 mod 的详细说明（改了什么、原版值、注意事项）都写在该 mod 文件夹内的 `README.md` 里。**

### 其中 3 个原本来自 mod.io

| mod | 原 mod.io ID |
|---|---|
| `more-water` | 3225680 |
| `whole-island-buildings` | 3294467 |
| `all-items-unlocked` | 4302450 |

它们原本由 mod.io 平台管理（存在 `C:\Users\Public\mod.io\`）。**现在已脱离平台**：本地副本齐全，`modinfo.json` 已补好，不依赖订阅。

---

## 四、还原与验证

1. **还原 mod**：把 `mods\` 下的 12 个文件夹整个复制到
   `<game_dir>\mods\`（或官方的 `%USERPROFILE%\Documents\Anno 1800\mods\`），`game_dir` 见 `anno.json`。
   每个都带 `modinfo.json`，复制即可用，**不依赖 mod.io 订阅**。

2. **`download\old\` 里的原始 zip**：需解压后把文件夹放进 mod 目录，**不要直接放 zip**（原版加载器不读 zip）。解压出来的 mod 若要加 `modinfo.json`，必须写 `Version`。

3. **验证**：启动游戏后查看 `%USERPROFILE%\Documents\Anno 1800\log\mod-loader.log`。每个 mod 显示 `Load <名字> (<版本>, <ModID>)`，结尾应有 **`Loading complete`**。**若日志只有 `Load mods` 一行就结束，说明某个 `assets.xml` 是空 `<ModOps>`。**

### 备份与游戏目录的一致性

对全部 mod 做过**全文件 SHA-256 逐字节比对**。过程中修正过这些：

| mod | 原先 | 现在 |
|---|---|---|
| `research-easy` | 备份是旧版（3 条 ModOp） | ✅ 已换为游戏中的 7 条版本 |
| `trade-contracts` | 备份是旧版（2240 B） | ✅ 已换为游戏中的 3875 B 版本 |
| 3 个 mod.io mod | 只在平台上、无本地 `modinfo` | ✅ 已复制进 `mods\` 并补好 `modinfo.json` |
| 全部 11 个 | 无 `modinfo.json` | ✅ 已补 `Version` + `ModID` + 多语言 `ModName` |

**最近一次比对结果（36 个文件对 36 个）**：

| 项 | 结果 |
|---|---|
| 11 个 `assets.xml`（真正生效的） | ✅ 逐字节一致 |
| 其余 25 个文件（`modinfo.json` × 11、`README.md` × 11、`more-water/content.txt`、`mr-long/texts_chinese.xml`、`mr-long` 的 PNG 图标） | ✅ 逐字节一致（文本统一 UTF-8 无 BOM + CRLF；PNG 未改动） |
| 仅备份有 / 仅游戏有 | 0 / 0 |

> `docklands-contracts` 是后加的第 12 个 mod：已复制进游戏目录并逐字节核对，**但还没启动游戏验证**，
> 所以上面「11 个 / 36 个」是上一次比对时的快照，不代表现在的目录内容。

> **同步方向以本备份为准**：改了 `mods\` 里的东西要往游戏目录复制。
> 文本文件的换行已经统一成 **CRLF**（`mods\` 下的文件要和游戏目录逐字节一致），
> 并由 [`.gitattributes`](.gitattributes) 固定（`mods/**/*.{md,json,xml,txt} text eol=crlf`），
> 所以"逐字节比对"现在直接看哈希即可，不必再忽略换行。

比对命令（只读，不改任何文件）：

```powershell
$cfg = Get-Content anno.json | ConvertFrom-Json
$a = Join-Path $PWD 'mods'; $b = Join-Path $cfg.game_dir 'mods'
foreach ($f in Get-ChildItem $a -Recurse -File) {
    $p = Join-Path $b $f.FullName.Substring($a.Length + 1)
    if (-not (Test-Path -LiteralPath $p)) { "缺失: $($f.Name)"; continue }
    $ta = [IO.File]::ReadAllText($f.FullName); $tb = [IO.File]::ReadAllText($p)
    if (($ta -replace "`r`n", "`n") -ne ($tb -replace "`r`n", "`n")) { "内容不同: $p" }
}
```

### 关于那 3 个原本来自 mod.io 的 mod

它们的 **mod 实体**（`assets.xml`）与平台原件**逐字节一致**。原始的平台 `modinfo.json` 已被替换为我们的版本（固定 `local-*` ModID）—— **因此原始平台元数据不在磁盘上**，若日后要与平台对照需重新订阅。

**不要拿这份备份反向覆盖游戏目录**：`docklands-cooldown` 已是规范名（旧名 `Docklands Cooldown 5` / `5min` 已合并），`research-easy` / `trade-contracts` 已是同步后的最新版。

---

## 五、目录分工

### `download\` —— 下载来的原始文件（不进 git）

```
download\
├── RdaConsole.zip              RDA 解包工具（来自 anno-mods/RdaConsole）
├── AssetViewer.exe             资产浏览器，GUI（同类工具，需人工操作）
└── old\                        封存的原始素材与未采用版本
    ├── mods-mr-long\           Mr.Long 未采用的两个版本
    ├── mods-no-forest-planting\ 全0格种植的原始 zip
    └── mods-public-service-range\ 公共服务建筑距离的原始 zip
```

### `scripts\` —— 链路脚本（进 git）

```
scripts\
├── extract-game-data.ps1   解包 <game_dir>\maindata\data*.rda -> temp\db（调用 RdaConsole）
```

脚本从 `anno.json` 取路径；`extract-game-data.ps1` 支持 `-DryRun` 只打印命令、`-Out` / `-Filter` 用于试跑。

### `tools\` —— 二进制与一次性分析脚本（不进 git）

```
tools\
├── RdaConsole\build\RdaConsole.exe   RdaConsole.zip 解压出来的可执行（解包用）
├── compare-pools.ps1                 原版池 vs mod 池对比（一次性分析用）
├── extract-researchable.ps1          研发展开（已被 build_research.py 取代）
├── lookup-guids.ps1                  反查 mod 用到的 GUID 名称与原版数值
└── lookup-items.ps1                  反查 mod 引用的物品
```

### `temp\` —— 原始层（不进 git）

`db\`（解包出的游戏数据，约 296 MB）、`research-cards.txt`（可研发清单）、
`card-profile.tsv`（人看的档案）、`merchant-pools.md`（各家商人卡池大小）。
解析好的数据在 `data\`，不在 `temp\`。
**完整说明与重新生成步骤见 [`temp\README.md`](temp\README.md)。**

```powershell
# 一条链：解包 -> 研发展开 -> data/ -> 文档
pwsh scripts\extract-game-data.ps1

uv run build_research.py     # -> temp\research-cards.txt
uv run build_db.py           # -> data\（一个资产一个 JSON）
uv run build_cards.py        # -> docs\cards.md + temp\merchant-pools.md
uv run build_profile.py      # -> temp\card-profile.tsv（人看的档案）
```

---

## 六、工具链 —— `src\anno\` + 根目录入口

**一个包，职责单一**（从零重写，旧的 `game/ cards/ merchants/ common/` 已归档到 `old\code\`）：

```
src\anno\
├── paths.py       三层路径（temp / data / docs）+ 读 anno.json
├── scan.py        扫 assets.xml（唯一碰原始 XML 的地方）
├── effects.py     Values 原文 → 数值效果 / 远征 / 使用动作 + 一句话摘要
├── cards.py       卡牌文档（data/cards/<GUID>.json）+ CardView（给渲染/规则用）
├── entities.py    辅助概念：目标组 / 建筑 / 商品 / 作物 / 套装 / DLC / Buff
├── traders.py     商人：原版档位池 + 本 mod 池 + 「谁卖」归属
├── database.py    写/读 data/（index.json、names.json）
├── placement.py   装槽 / 大类 / 世界（归类口径）
├── rules.py       归属规则（含跨区生产卡双挂）
├── pools.py       本 mod 卡池读写 / 排版
├── render.py      docs\cards.md、档案表、商人卡池表
├── config.py      根目录 anno.json 的本机配置（game_dir / 目录覆盖）
├── texts.py       文本表 + 名字解析（zh / 内部名 / GUID 三级回退）
├── templates.py   templates.xml 的默认装槽
├── tables.py      游戏常量表（模板、区域、交易商、远征枚举…）
├── model.py       数据类 + AssetIndex（field / zone / expand_targets / reach）
├── console.py     UTF-8 终端与 rich Console
└── util.py        表格 / TSV / markdown 小工具
```

| 入口 | 作用 | 产物 | 耗时 |
|---|---|---|---|
| `build_db.py` | **一次 XML 扫描** → 一个资产一个 JSON | `data\`（约 3100 个文件） | ~6 s |
| `build_cards.py` | 只读 `data\` 排版 | `docs\cards.md`、`temp\merchant-pools.md` | **0.3 s** |
| `build_profile.py` | 只读 `data\` | `temp\card-profile.tsv` | **0.3 s** |
| `build_research.py` | 研发展开（四层：`ResearchSubcategory → RecipePool → AssetPool → 卡`） | `temp\research-cards.txt` | ~4 s |
| `edit_pools.py` | **改 mod 卡池的唯一入口**：`report` / `tidy` / `drop` / `add` / `move` / `exclusive` / `assign`（都支持 `--dry-run`） | 直接改 `mods\all-items-unlocked\...\assets.xml` | **< 2 s** |
| `query.py` | **查数据**：`card` / `find` / `show` / `trader` / `building` / `good` | 终端输出 | **< 1 s** |

> **解析一律用真 XML**（lxml 流式），不用字符串切块+正则：
> 后者会把 `</ModOps>` 当成 `</ModOp>`（子串误判），也看不出
> `<CraftableItem><Item /></CraftableItem>` 这种空配方（曾把 33 张空配方误判成可合成）。
>
> **数据只解析一次**：`build_db.py` 是全链唯一读 `assets.xml` 的地方；改归类/规则/排版只跑
> `build_cards.py`（0.3 秒）。改完 mod 卡池（`edit_pools.py`）之后重跑 `build_db.py` + `build_cards.py`。

> **`docs\cards.md` 是生成物** —— 要改内容改脚本，别手改文件（下次生成会覆盖）。
> 反过来 **`docs\cards-special.md` 是手工维护的**，没有生成脚本，可以放心直接编辑。
> 库里没有的东西（例如某张卡「是不是真剧本专用」的结论）都记在 `cards-special.md` 里。

---

## 七、`docs\` 参考

| 文件 | 内容 | 来源 |
|---|---|---|
| [`docs/game.md`](docs/game.md) | **游戏基础信息** —— 版本、安装位置、5 个区域、DLC 列表、卡牌模板与数据结构、规模统计 | 手写 + 【游戏文件】标注 |
| [`docs/reference.md`](docs/reference.md) | **写 mod 的规则** —— mod 放哪里、文件夹结构、`modinfo.json` 字段（**本机实测**）、加载顺序、`ModOp` 写法、日志排查 | 手写 |
| [`docs/cards.md`](docs/cards.md) | **卡牌清单** —— 2149 张卡，按「大类 → 装槽 → 稀有度」分层，每张标出谁在卖、可研发性、影响的世界与目标 | ⚙️ `build_cards.py` 从 `data/` 生成 |
| [`docs/cards-special.md`](docs/cards-special.md) | **特殊卡清单** —— 带 `ScenarioFilter` 的 98 张剧本卡（逐张留「处置」列），外加卡表上的特例 | ✍️ 手工维护 |
| [`docs/data-model.md`](docs/data-model.md) | **数据层设计** —— `temp/`（原始）→ `data/`（一个资产一个 JSON）→ `docs/`，各概念的 JSON 结构与 `query.py` 用法 | ✍️ 设计文档 |

> `game.md` / `reference.md` 里的每条信息都标注 **【游戏文件】** / **【本机实测】** / **【官方】** 来源。
>
> **只有 `cards.md` 是生成物**（`build_cards.py` 从 `data/` 渲染）—— 改它要改脚本。其余几份都可以直接编辑。

## 八、已知注意事项

- **`modinfo.json` 里 `Version` 是必需字段** —— 缺失会报 `[error] ... Version is missing`。
- **`assets.xml` 里至少要有一条真实 `ModOp`** —— 空 `<ModOps>` 会导致**静默闪退**。
- **排查闪退看日志结尾**：正常应有 `Loading complete`。若只有 `Load mods` 一行，就是空 `<ModOps>`。
- **有了 `modinfo.json`，ModID 就固定了** —— 重命名文件夹不再改变 mod 身份。没有它时 ModID = 文件夹名。
- **`LoadAfterIds` 可以确定性地指定加载顺序**，会压过默认的字母序。
- 路径含 `[` `]` 方括号，PowerShell 里必须用 `-LiteralPath`，否则会被当通配符。
- **PowerShell 变量名不区分大小写** —— `$B` 和 `$b` 是同一个变量。写批处理脚本时务必用不同名字（如 `$BackupRoot` / `$bp`），否则循环里会互相覆盖（本次排查中因此出过多次误判）。
- Anno 1800 与 Anno 117 的 mod 目录不要混淆。
- 部分地区性 mod 的 XML 是 **GBK 编码**（`download\old\mods-no-forest-planting`、`download\old\mods-public-service-range`），按 UTF-8 读会显示乱码。
- **`download\` 里的 zip 不能直接放进游戏目录** —— 原版内置加载器不读 zip，必须解压。

