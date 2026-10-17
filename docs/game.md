# Anno 1800 游戏基础信息

> 只记录**基础事实**：游戏本体、区域、DLC、卡牌分类的官方名词。
> 装 mod 的方法见 [`reference.md`](reference.md)，卡牌逐张清单见 [`cards.md`](cards.md)。
>
> 标记：【游戏文件】= 直接从本机游戏数据里读出来的（可复现）；【公开资料】= 来自官方商店页/维基。

## 1. 本机游戏

| 项 | 值 |
|---|---|
| 版本 | `v18.4.1412158`（最终版本，官方已停止更新） |
| 安装位置 | 见根目录 `anno.json` 的 `game_dir`（本机配置） |
| 数据本体 | `maindata\data0.rda` … `data33.rda`（打包资源）+ 各语言包 `*_0.rda` |
| mod 目录 | `<game_dir>\mods\`（共 12 个，见 [`reference.md`](reference.md)） |
| 数据副本 | `temp\db\data\config\...` —— 从 `maindata` 解包出的 `assets.xml`（276 MB）与 `texts_chinese.xml`（8 MB），本仓库所有统计都基于它 |

## 2. 区域（Region）

游戏自己的写法只有这 5 个 —— 取自 `texts_chinese.xml` 里的 `区域：X` 条目【游戏文件】：

| 官方中文 | 英文 | 进入条件 | 备注 |
|---|---|---|---|
| 旧世界 | Old World | 本体 | 起始区域 |
| 新世界 | New World | 本体 | 南美风，产棉花/咖啡/甘蔗等 |
| 崔老妮海角 | Cape Trelawney | 沉没的宝藏（第 1 季 DLC） | 大体量旧世界区域，崔老妮战役遗迹 |
| 北极 | The Arctic | 航道（第 2 季 DLC） | 需要暖气、飞艇 |
| 安贝沙 | Enbesa | 狮子大地（第 3 季 DLC） | 非洲风，长老/学者体系 |

> 崔老妮海角在维基里也写作「崔老尼海角」；游戏内文本统一是 **崔老妮海角**。

## 3. DLC

四季通行证共 12 个大型 DLC + 若干装饰/内容包。每个 DLC 在数据里都是一个
**`UplayProduct` 资产**，「游戏内中文名」就是它自己的中文文本【游戏文件】；
商店页/维基的叫法有时不同（见下表脚注）：

| 季 | DLC（英文） | 游戏内中文名 | DLC 资产 GUID | 加了什么 |
|---|---|---|---|---|
| 第 1 季 | Sunken Treasures | 沉没的宝藏 | `410040` | 崔老妮海角区域、打捞船/潜水钟、老奈特 |
| 第 1 季 | Botanica | 植物园 | `410041` | 植物园与文化展馆体系 |
| 第 1 季 | The Passage | 航道 | `410042` | 北极区域、飞艇、天然气 |
| 第 2 季 | Seat of Power | 权力王座 | `410059` | 宫殿与模块 |
| 第 2 季 | Bright Harvest | 丰收在望 | `410070` | 拖拉机、筒仓，农业增产 |
| 第 2 季 | Land of Lions | 狮子大地 | `410071` | 安贝沙区域、学者与研究院 |
| 第 3 季 | Docklands | 港湾 | `410083` | 贸易港区与合约 |
| 第 3 季 | Tourist Season | 旅行旺季 | `410084` | 游客、餐馆/咖啡厅、观光港 |
| 第 3 季 | The High Life | 上流生活 | `410085` | 投资人高楼、铁塔 |
| 第 4 季 | Seeds of Change | 变革之种 | `24961` | 农业改革、庄园 |
| 第 4 季 | Empire of the Skies | 帝国领空 | `24962` | 飞艇体系扩展、邮件 |
| 第 4 季 | New World Rising | 新兴世界 | `24963` | 新世界扩展、庄园 |

> 叫法差异：Bright Harvest 常写作「丰收之光」（游戏内是 **丰收在望**）、
> Tourist Season 常写作「观光季」（游戏内是 **旅行旺季**）、Docklands 的贸易玩法叫
> 「贸易港区」（DLC 本体在游戏内叫 **港湾**）。另有 10 个纯装饰 CDLC
> （游乐园、假日装饰、龙之花园、蒸汽朋克…），它们带的是建筑皮肤，不含卡。

**卡牌怎么归属到 DLC**【游戏文件】：物品资产里的
`<Locked><DLCDependency>410040</DLCDependency></Locked>` 指向上面那张表的 GUID。

- 2149 张卡里 **531 张**带这个字段（沉没的宝藏 148、狮子大地 134、植物园 97、航道 90、
  新兴世界 30、帝国领空 19、上流生活 6、旅行旺季 6、变革之种 1）
- 没有这个字段的记为「**本体**」（1618 张）。注意这只是「**没标 DLC**」，不等于「本体内容」：
  DLC 里没上锁的物品也会落到本体 —— 例：`2226` 精英飞船枪手（内部名 `AirshipDLC11 Gunner`，
  明显是帝国领空那批的飞船专家）就没有 `DLCDependency`
- 逐张的 DLC 见 [`cards.md`](cards.md) 的「DLC」列，各 DLC 的统计见该文档「各 DLC 统计」一节

## 4. 卡的分类（游戏自己的模板）

`assets.xml` 里每个物品靠 `<Template>` 声明类型。全库 10.2 万个资产里有 658 种模板，
和卡牌相关的是这几种【游戏文件】：

| 模板 | 全库数量 | 是什么 |
|---|---|---|
| `GuildhouseItem` | 574 | 可装工会的物品（数量最多） |
| `CultureItem` | 351 | 博物馆 / 动物园 / 植物园展品 |
| `QuestItem` | 322 | 任务流程与任务奖励物品 |
| `TownhallItem` | 259 | 可装市政厅的物品 |
| `ItemWithUI` | 173 | 用了会弹界面的道具（藏宝图、信函、货箱…） |
| `FluffItem` | 117 | 纯装饰物，**不是卡** |
| `ItemSpecialAction` | 102 | 带特殊动作（轰炸、声呐等） |
| `VehicleItem` | 60 | 载具（火车/卡车等） |
| `ScenarioWorkshopItem` | 60 | 战役剧本专用物件，**不是卡** |
| `HarborOfficeItem` | 57 | 可装港务总管办公室的物品 |
| `ShipSpecialist` | 51 | 可装船舰的专家 |
| `ActiveItem` | 14 | 可主动使用的物品 |
| `ItemWithUICrafting` | 8 | 用了会弹合成/建造界面的道具 |
| `QuestItemMagistrate` | 1 | 任务道具（治安官专用） |

分类与判据见 [`cards.md`](cards.md)：它把 2149 张卡按「装槽 → 稀有度」摊开。

## 5. 交易商（商人）

中立 NPC：在他们的岛上买卖货物、**卖装备卡**、部分还卖船、代工合成。全库
**27 个资产带 `<Trader>` 块**，其中 **9 位在沙盒里卖卡**【游戏文件】；其余是战役 / 剧本专用
（`S03_Mercier`、`S03_Mara`、`Sceanrio04_Trader_*`、安贝沙岛民 `Third_party_SI01~03` 等）。

### 5.1 九位卖卡的交易商

| 简称（`cards.md` 用） | 官方中文名 | 英文名 | 内部资产 GUID · 内部名 | 所在区域 | 需要 DLC | 卡池上限 |
|---|---|---|---|---|---|---|
| 布莱克 | 亚奇博德·布莱克爵士 | Sir Archibald Blake | `45` · `Third_party_02 (Archibald Blake)` | 旧世界 | 本体 | 205 |
| 伊莱 | 伊莱·布利克沃斯 | Eli Bleakworth | `46` · `Third_party_07 (Eli Bleakworth)` | 旧世界（握姆威监狱） | 本体 | 300 |
| 卡希纳 | 卡希纳女士 | Madame Kahina | `78` · `Third_party_08 (Madame Kahina)` | 旧世界 | 本体 | 266 |
| 萨曼托 | 伊莎贝尔·萨曼托 | Isabel Sarmento | `29` · `Third_party_05 (Isabel Sarmento)` | 新世界 | 本体 | 222 |
| 老奈特 | 老奈特 | Old Nate | `77` · `Third_party_06 (Old Nate)` | 崔老妮海角 · 北极 | 沉没的宝藏 · 航道 | 106 |
| 库马克 | 库马克 | Qumaq | `237` · `Third_party_11 (Inuit)` | 北极 | 航道 | 66 |
| 柯提马 | 柯提马皇帝 | Emperor Ketema | `119051` · `Third_party_13 (Emperor Ketema)` | 安贝沙 | 狮子大地 | 109 |
| 海盗 | 安·哈洛 | Anne Harlow | `73` · `Third_party_03 (Anne Harlow)` | 旧世界 | 本体（海盗） | 159 |
| 海盗 | 尚·拉福图 | Jean La Fortune | `76` · `Third_party_04 (La Fortune)` | 新世界 | 本体（海盗） | 116 |

- **中文名**取 `texts_chinese.xml` 里**以资产 GUID 为键**的条目（不是 `LineID`）【游戏文件】。
  `cards.md` 的商人列用的是上表简称，两个海盗合并显示为「海盗」。
- **区域**：游戏文件里只有内部值 `Trader/AllowedRegions` —— `Moderate`（旧世界）、
  `Colony01`（新世界）、`Arctic`（北极）、`Africa`（安贝沙）；老奈特是 `Moderate;Arctic`。
  据点名称与身份参考公开资料【公开资料】。
- 两个海盗也是交易商：安·哈洛在**旧世界**、尚·拉福图在**新世界**，都要先有贸易权才能交易。

### 5.2 卡池结构：档位 → 类别池 → 卡

【游戏文件】每个交易商资产里都有 `<Values><Trader><Progression>`，共 **6 个档位**：

```
<EarlyGame>     <OfferingItems>190162</OfferingItems>  <MaxItemsToOffer>3</MaxItemsToOffer>
<EarlyMidGame>  …                                      4
<MidGame>       …                                      5
<LateMidGame>   …                                      6
<LateGame>      …                                      8
<EndGame>       …                                      12
```

- `OfferingItems` 指向一个 **`RewardItemPool`**（例：`190162` = `3rd_party_02 (Sir Archibald Blake) EarlyGame`）。
- 这个「**档位池**」本身几乎不装物品（布莱克每档只有 27 条 `<ItemLink>`），它指向的是「**类别池**」
  （`192851`…），每条带一个 `<Weight>`。
- **`<Weight>0</Weight>` = 该档位不上架**。所以**档位之间的差别是「打开多少个类别池」，不是换一批卡**：
  布莱克 6 个档位引用的 27 个类别池**完全相同**，启用的数量依次是 `3 / 5 / 13 / 20 / 20 / 20`。
- 因此「某商人卖多少张卡」有两个口径：**池上限**（类别池全展开）和**某档位实际能买到的**。
- `MaxItemsToOffer` 是**同时上架件数**（3/4/5/6/8/12），不是卡池大小。

| 商人 | 类别池 | 池上限 | EarlyGame | EarlyMidGame | MidGame | LateMidGame | LateGame | EndGame |
|---|---|---|---|---|---|---|---|---|
| 布莱克 | 27 | 205 | 3 池 / 15 卡 | 5 / 29 | 13 / 165 | 20 / 197 | 20 / 197 | 20 / 197 |
| 伊莱 | 11 | 300 | 3 / 114 | 5 / 163 | 8 / 236 | 10 / 241 | 10 / 241 | 10 / 241 |
| 卡希纳 | 15 | 266 | 3 / 17 | 5 / 24 | 10 / 170 | 10 / 170 | 10 / 170 | 10 / 170 |
| 萨曼托 | 29 | 222 | 14 / 158 | 14 / 158 | 14 / 158 | 22 / 172 | 22 / 172 | 22 / 172 |
| 老奈特 | 20 | 106 | 5 / 31 | 8 / 48 | 13 / 86 | 14 / 90 | 16 / 102 | 15 / 102 |
| 库马克 | 16 | 66 | 3 / 12 | 5 / 25 | 10 / 51 | 11 / 51 | 14 / 57 | 15 / 65 |
| 柯提马 | 20 | 109 | 6 / 27 | 10 / 60 | 15 / 90 | 16 / 93 | 17 / 96 | 17 / 96 |
| 海盗·安·哈洛 | 15 | 159 | 5 / 63 | 8 / 99 | 11 / 124 | 11 / 124 | 11 / 124 | 11 / 124 |
| 海盗·尚·拉福图 | 15 | 116 | — | — | 11 / 86 | 11 / 86 | 11 / 86 | 11 / 86 |

> 每格 = 该档**启用**的类别池数 / 这些池展开后能拿到的卡数。
> 萨曼托的 Early/EarlyMid/Mid 三档共用同一个池 `190362`；尚·拉福图没有前两档（`MidGame` 才开始卖卡）。

### 5.3 交易商资产上的其它字段

| 字段 / 模板 | 含义 | 谁有 |
|---|---|---|
| `Profile_3rdParty` | 普通交易商 | 布莱克、伊莱、卡希纳、萨曼托、库马克、柯提马 |
| `Profile_3rdParty_Pirate` | 海盗交易商 | 安·哈洛、尚·拉福图 |
| `Profile_3rdParty_ItemCrafter` | **能代工合成** | 老奈特 |
| `Profile_3rdParty-PlayerCounter` | 玩家对抗型（战役里会倒戈） | 萨曼托 |
| `Trader/ShipTrader` | 卖船 | 布莱克、卡希纳、萨曼托、柯提马、两个海盗 |
| `Trader/SellShipCooldown` | 卖船冷却 | 布莱克、伊莱、卡希纳、柯提马、安·哈洛 |
| `Trader/ProvidesShipReplacements` | 提供船只替换 | 布莱克、萨曼托、老奈特、库马克、柯提马 |
| `Trader/TraderRerollInterval` | 货架刷新间隔 | 老奈特 |
| `Trader/AllowedRegions` | 出现在哪些 session | 见 5.1 |
| `Trader/UseSessionSpecificProgressLevel` | 档位按各区进度分别算 | 柯提马 |

### 5.4 各家卖什么（公开资料）

| 商人 | 主营 |
|---|---|
| 布莱克 | 市政厅书籍；船只通行证 / 私掠 / 免疫证；港务与船只修理装备；民用船只升级（帆、涡轮、望远镜）；苗床 |
| 伊莱 | 市政厅文书；各类民用专家（市政厅、商会、港务、船） |
| 卡希纳 | 港务与船专家；文化展品（动物、文物，植物园 DLC 后含植物）；稀有通行证 |
| 萨曼托 | 新世界工厂专家；港务与商会物品；稀有民用船装备与修理；稀有通行证 |
| 老奈特 | 各类专家；藏宝图；用打捞来的废料**代工合成**特殊物品（唯一能造的商人） |
| 库马克 | 本区生产加成物品与专家；特殊文物与动物 |
| 柯提马 | 本区生产加成物品与专家；特殊文物与动物 |
| 海盗·安·哈洛 | 海事专家（战斗 / 贸易）；军用与民用船只装备；港务与船只修理；稀有商会 / 港务专家 |
| 海盗·尚·拉福图 | 军用船只装备；海事专家；修理装备；稀有其它专家 |

> 区域、据点与品类参考：[annoinfo.de – Händler](https://www.annoinfo.de/Anno_1800/npc.html)、
> [annoinfo.de – Gegner & Piraten](https://www.annoinfo.de/Anno_1800/npc-2.html)、
> [Anno 1800 Wiki – Neutral Traders](https://anno1800.fandom.com/wiki/Neutral_Traders)。
> 本仓库的 mod 把其中 7 家的档位池整体替换了（含 `MaxItemsToOffer` 512、`IgnoreUnlocks`），
> 见 [`mods/all-items-unlocked/README.md`](../mods/all-items-unlocked/README.md)。

## 6. 业务数据结构（做 mod / 改卡必看）

游戏数据是**扁平的资产表**：每个 `<Asset>` 有 `<Template>`、`<GUID>` 和 `<Values>`。
物品的关键字段都在 `<Values>` 里：

| 路径 | 含义 |
|---|---|
| `Item/Rarity` | 稀有度（`Common`/`Uncommon`/`Rare`/`Epic`/`Legendary`） |
| `Item/TradePrice` | 交易商售价 |
| `Item/Allocation` | 装槽（`GuildHouse`、`TownHall`、`HarborOffice`、`Museum`、`Zoo`…）；**卡牌没写就继承模板默认值**（见下） |
| `Item/ScenarioFilter` | 指向限定剧本，带它 = 剧本专用 |
| `Item/ExclusiveGroup` | 互斥组 |
| `Item/ItemFilterCategory` | UI 分类 |
| `Item/InfoDescription` | 简介（指向文本 GUID） |
| `Locked/DLCDependency` | DLC 归属（指向 DLC 资产 GUID，见第 3 节；没有 = 没标 DLC） |
| `Item/EffectTargets` | **作用目标**（这张卡影响谁）—— 指向 `ItemEffectTargetPool` 目标组或具体建筑，见第 8 节 |
| `FactoryUpgrade` / `ResidenceUpgrade` / `CultureUpgrade` … | 各类加成块（数值） |
| `ExpeditionAttribute` | 远征属性 |
| `CraftableItem` | 合成配方 |

**装槽从哪来**【游戏文件】：卡牌自己的 `<Item><Allocation>` 优先；**没写就继承
`templates.xml` 里该模板的默认装槽** —— 这是「这张卡能装到哪儿」的权威答案：

| 模板 | 默认装槽 | 卡里没写装槽的张数 |
|---|---|---|
| `GuildhouseItem` | `GuildHouse` 工会 | 466 |
| `TownhallItem` | `TownHall` 市政厅 | 254 |
| `HarborOfficeItem` | `HarborOffice` 港务总管办公室 | 56 |
| `ShipSpecialist` | `Ship` 船舰 | 37 |
| `CultureItem` | `Zoo` 动物园 | 133（另有 156 张自己写了 `Museum`、59 张 `BotanicGarden`） |
| `VehicleItem` | `Ship` | 13 |
| `QuestItem` / `ItemWithUI` / `FluffItem` / `ItemWithUICrafting` | `None`（没有装槽） | 571 |

> 所以那 800 多张「没写装槽的专家」**不是多用途**：工会物品 466、市政厅物品 254、
> 港务物品 56、船只专家 37，各有归属。它们当中很多**同时带远征属性**
> （`ExpeditionAttribute`），看着像哪儿都能装，其实装槽是确定的。
> 逐槽张数见 [`cards.md`](cards.md) 的「各装槽统计」。

**装槽的官方中文名**【游戏文件】：`assets.xml` 里有一份 UI 配置（`AllocationText`），
写明了每个装槽在游戏里显示什么名字 —— 我们文档里的名字都从这里取：

| 内部名 | 官方中文 | | 内部名 | 官方中文 |
|---|---|---|---|---|
| `GuildHouse` | 工会 | | `Ship` | 船只 |
| `TownHall` | 市政厅 | | `SailShip` | 帆船 |
| `HarborOffice` | 港务总管办公室 | | `SteamShip` | 蒸汽船 |
| `Lodge` | 北极小屋 | | `Warship` | 军舰 |
| `Museum` | 博物馆 | | `Tradeship` | 商船 |
| `Zoo` | 动物园 | | `DivingVessel` | 打捞船 |
| `BotanicGarden` | 植物园 | | `AirShip` | 飞船 |
| `Pavilion` | 音乐演奏场 | | `AarhantShip` | 阿尔罕的船「奇沙堤」 |
| `Culture` | 文化 | | `BuildPermit` | 允许 |
| `RadiusBuilding` | 周边建筑 | | `Dockland` | 港湾主要码头 |
| `Headquarter` | 总部 | | `Expedition` | 远征 |

### 舰船：两条轴（时代 × 军民）

【游戏文件】每艘船在 `templates.xml` 或自己的资产里写 `SocketAllocation`，声明**它的槽位能装哪几类物品**：

| 船 | `SocketAllocation` | 时代 | 军民 |
|---|---|---|---|
| 纵帆船 / 快速帆船 / 大东方号…（`TradeShip`） | `Ship;SailShip` | 风帆 | 民用 |
| 炮艇 / 护卫舰 / 战列舰 / 火箭船（`WarShip`） | `Ship;SailShip;Warship` | 风帆 | 军用 |
| 战列巡洋舰 / 浅水重炮舰 / 围攻巡洋舰 | `Ship;SteamShip;Warship` | 蒸汽 | 军用 |
| 运煤船 / 油轮 / 大东方号 / 联合号 | `Ship;SteamShip;Tradeship` | 蒸汽 | 民用 |
| 明轮蒸汽船 | `Ship;SteamShip` | 蒸汽 | 民用 |
| 打捞船（`DivingBellShip`） | `Ship;SteamShip;Tradeship;DivingVessel` | 蒸汽 | 民用 |
| 飞船（`AirShip` / `WarAirShip`） | `AirShip`（3 槽） | — | — |
| 渔船 / 阿尔罕的船「奇沙堤」 | `Ship;SailShip;Warship;AarhantShip` | 风帆 | — |
| 音乐演奏场（`CultureModule`） | `Pavilion` | — | — |
| 文化展馆模块 | `Culture;Museum` / `Culture;BotanicGarden` / `Culture;Zoo` | — | — |

> 所以物品侧只有 5 种舰船装槽：**船只**（通用，任何船都能装）、**帆船**（风帆时代专用）、
> **蒸汽船**（蒸汽时代专用）、**军舰**（军用，风帆/蒸汽军舰都能用）、**商船**（民用，蒸汽商船用）。
> 「时代」和「军民」是两条独立的轴，不是 2×2 —— 军舰的物品不分帆船/蒸汽，两个时代的军舰都能装。

商人一侧：

| 路径 | 含义 |
|---|---|
| `<Trader>` 块 | 27 个资产有（见第 5 节），其中 9 位在沙盒里卖卡 |
| `Trader/Progression/<档位>/OfferingItems` | 该档位卖货用的卡池（指向 `RewardItemPool`） |
| `Trader/Progression/<档位>/MaxItemsToOffer` | 同时上架上限 |
| `/Values/RewardPool` | 卡池本体，`ItemsPool` 下是 `<Item><ItemLink>GUID</ItemLink><Weight>n</Weight></Item>` |

档位共 6 档：`EarlyGame` / `EarlyMidGame` / `MidGame` / `LateMidGame` / `LateGame` / `EndGame`。
档位池 → 类别池 → 卡的两层结构、以及各家的具体卡数见 **5.2**。

> 注意模板名：交易商卡池是 **`RewardItemPool`**，不是 `RewardPool`（后者是建筑/任务的奖励池）；
> 用子串筛 `RewardPool` 会把 9 个交易商池全部漏掉。

## 7. 现在这份数据里的规模

【游戏文件】从 `temp/db/data/config/.../assets.xml` + `texts_chinese.xml` 读出来的：

| 项 | 数量 | 来源 |
|---|---|---|
| 资产总数 | 104,190 | `ElementTree.iterparse` 数 `<Asset>` 元素 |
| 模板种类 | 658 | 同上 |
| 中文文本条目 | 58,648 | `texts_chinese.xml` |
| 卡牌 | 2,149 | `data/cards/`（一张卡一个 JSON） |
| 其中可研发 | 1,130 | `temp/research-cards.txt` |
| 其中可合成（老奈特工坊，**常规游戏**） | 93 | `CraftableItem` 里有真材料（`Product`+`Amount`）**且不带 `ScenarioFilter`** |
| ↳ 另有剧本内专属配方 | 13 | 伊甸浴火（`ScenarioFilter 650`）那批，普通局里造不出来 |
| 带 `ScenarioFilter`（剧本专用） | 98 | 卡的 `ScenarioFilter` 非空 |
| 池资产（`RewardPool` / `RewardItemPool` / `AssetPool`） | 1,635 | 有 `ItemLink`/`Pool` 成员的资产 |

复现：`uv run build_db.py`（一次 XML 扫描，约 6 秒）写出 `data/`，
再 `uv run build_cards.py`（0.3 秒）重出清单。

## 8. 卡牌的「作用目标」（影响什么）

一张卡有两套「作用范围」，别混：

| 字段 | 回答的问题 | 取值 |
|---|---|---|
| `Item/Allocation` | 这张卡**能装到哪儿** | 工会 / 市政厅 / 港务 / 各类船槽…（第 3 节、第 6 节） |
| `Item/EffectTargets` | 装上后**影响谁** | 目标组（`ItemEffectTargetPool`）或具体建筑 GUID |

`EffectTargets` 指向两类资产【游戏文件】：

| 指向 | 是什么 | 个数 |
|---|---|---|
| `ItemEffectTargetPool` | **游戏自带的语义分组** —— 名字直接写了区域和类型，如「所有旧世界矿场」「所有投资人与劳工住所」「所有工程师摩天大楼」 | 79 |
| 具体建筑 | 直接点名一座建筑（`FactoryBuilding7` / `FarmBuilding` / `ResidenceBuilding` / `PublicServiceBuilding` / `WarShip` …） | 197 |

2149 张卡里 **935 张**带 `EffectTargets`；目标组还会套目标组，递归展开后一共涉及 **447 座建筑**。

**中文名怎么来的**：全部取自游戏自己的 `texts_chinese.xml`，**按资产 GUID 查**（不是 `LineID` —— 建筑的 `LineID` 在文本表里查不到，而 GUID 键就是游戏内显示的名字）。第三方 wiki 常另有译名，但[灰机wiki 的生产建筑页](https://anno1800.huijiwiki.com/wiki/%E7%94%9F%E4%BA%A7%E5%BB%BA%E7%AD%91)自己就写着「建筑名字请以游戏内为主，大概理解是哪一个建筑即可」——所以下面偶尔出现的怪名字（`铝冶炼机` = Aluminium Smelter、`所有购物中心` = All Shopping Arcades、`消防救护站` = Ranger Station）是**游戏内实际译名**，不是我们抄错。

### 8.1 目标组一览（79 个）

判「这张卡用在哪一世界」主要看这一列 —— 组名里的「旧世界 / 新世界 / 安贝沙 / 北极」就是答案。

| 目标组（游戏中文名） | 覆盖 | 区域构成 | 被引用 | GUID | 游戏英文名 | 内部名 |
|---|---|---|---|---|---|---|
| 所有旧世界矿场 | 5 座 | 旧世界 5 | 1 张 | `1949` | All Old World Mines | all EU mines |
| 所有旧世界果园 | 3 座 | 旧世界 3 | 1 张 | `1962` | All Old World Orchards | all orchards EU |
| 所有旧世界动物农场 | 3 座 | 旧世界 3 | 1 张 | `1965` | All Old World Animal Farms | all animals farms Moderate |
| 所有飞船月台 | 2 座 | 新世界 1、旧世界 1 | 1 张 | `4278` | All Airship Platforms | all Airship Platforms |
| 所有新世界邮局和邮筒 | 2 座 | 新世界 2 | 1 张 | `4455` | All New World post offices and post boxes | All_SAPostGenerators |
| 所有通电牧场 | 3 座 | 新世界 3 | 3 张 | `8389` | All Powered Pastures | all electric Pasture |
| 所有新世界化学厂 | 5 座 | 新世界 5 | 1 张 | `8392` | All New World Chemical Plants | all chemical plants SA |
| （无译名） | 2 座 | 旧世界 1、新世界 1 | 1 张 | `8905` | — | all Advanced Police stations |
| 所有炭窑 | 3 座 | 北极 1、旧世界 1、新世界 1 | 8 张 | `8924` | All Charcoal Kilns | All Charcoal Kilns |
| 可生产所有武器的多功能工厂 | 5 座 | 新世界 3、旧世界 2 | 5 张 | `11404` | All arms producing Multifactories | all weapon producing Multifactories |
| 所有重工业建筑 | 2 座 | 旧世界 2 | 9 张 | `24053` | all heavy industry buildings | all GGJ Residences |
| 所有住所 | 2 座 | 新世界 2 | 2 张 | `103502` | All Residences | S03_Residences |
| 所有安贝沙作物农场 | 6 座 | 安贝沙 5、新世界 1 | 3 张 | `125109` | all Enbesan Crop Farms | all africa crop farms |
| 所有安贝沙住所 | 2 座 | 安贝沙 2 | 11 张 | `125110` | All Enbesan Residences | all residences africa |
| 所有旧世界住所 | 15 座（含 1 个嵌套组） | 旧世界 15 | 6 张 | `190041` | All Old World Residences | all residences EU + Scholars |
| 所有住所 | 23 座（含 1 个嵌套组） | 旧世界 15、新世界 6、安贝沙 2 | 129 张 | `190762` | All Residences | all residences EU & SA + Africa & Scholar |
| 所有消防局 | 5 座 | 旧世界 2、新世界 2、安贝沙 1 | 3 张 | `190775` | All Fire Stations | all fire stations |
| 所有警察局 | 5 座 | 旧世界 2、新世界 2、安贝沙 1 | 4 张 | `190776` | All Police Stations | all police stations |
| 所有医院 | 5 座 | 旧世界 2、新世界 2、安贝沙 1 | 4 张 | `190777` | All Hospitals | all hospitals |
| 所有伐木工人棚屋 | 3 座 | 旧世界 1、新世界 1、安贝沙 1 | 13 张 | `190778` | All Lumberjack's Huts | all timber yards |
| 所有渔场 | 4 座 | 新世界 2、安贝沙 1、旧世界 1 | 9 张 | `190779` | All Fisheries | all fisheries |
| 所有市政厅 | 2 座 | 新世界 1、旧世界 1 | 5 张 | `190781` | All Town Halls | all town halls |
| 所有酒吧 | 1 座 | 旧世界 1 | 11 张 | `190782` | All Pubs | all pubs |
| 所有造船厂 | 3 座 | 旧世界 2、新世界 1 | 12 张 | `190783` | All Shipyards | all shipyards |
| 所有教堂 | 2 座 | 旧世界 1、新世界 1 | 3 张 | `190784` | All Churches | all churches |
| 所有矿山和水泥 | 11 座 | 旧世界 6、新世界 5 | 5 张 | `190786` | All Mines and Cement | all mines and quarries |
| 所有冶炼厂和铸造厂 | 22 座（含 2 个嵌套组） | 旧世界 14、新世界 8 | 9 张 | `190842` | All Ironworks and Foundries | all ironworks and foundry |
| 所有作物农场 | 29 座（含 1 个嵌套组） | 新世界 18、安贝沙 6、旧世界 5 | 19 张 | `190865` | All Crop Farms | all crops farms |
| 所有动物农场 | 8 座 | 旧世界 3、新世界 3、安贝沙 2 | 20 张 | `190872` | All Animal Farms | all animals farms |
| 所有山地矿山 | 10 座 | 旧世界 5、新世界 5 | 11 张 | `190882` | All Mountain Mines | all subsurface mines |
| 所有成衣工厂 | 14 座 | 旧世界 6、新世界 5、安贝沙 3 | 4 张 | `190890` | All Cloth Industries | all cloth industries |
| 所有食物生产 | 12 座 | 新世界 6、旧世界 4、安贝沙 2 | 3 张 | `190897` | All Food Production | all food productions |
| 所有饮品生产 | 16 座（含 1 个嵌套组） | 新世界 8、旧世界 6、安贝沙 2 | 4 张 | `190901` | All Drinks Production | all breweries |
| 所有木工厂 | 7 座 | 旧世界 5、新世界 2 | 9 张 | `190914` | All Carpentry Works | all carpentry works |
| 所有砖块工厂 | 3 座 | 新世界 1、旧世界 1、安贝沙 1 | 7 张 | `190918` | All Brick Factories | all bricks factories |
| 所有油井 | 2 座 | 新世界 1、旧世界 1 | 8 张 | `191042` | All Oil Wells | all oil wells |
| 所有防御炮塔 | 20 座 | 旧世界 6、新世界 6、安贝沙 5、北极 3 | 15 张 | `191443` | All Defence Turrets | all military buildings |
| 所有船只 | 14 座 | 未标区域 13、北极 1 | 1 张 | `191454` | All Ships | all ships |
| 所有旧世界作物农场 | 5 座 | 旧世界 5 | 2 张 | `191471` | All Old World Crop Farms | all EU farms |
| 所有新世界作物农场 | 18 座（含 1 个嵌套组） | 新世界 18 | 1 张 | `191472` | All New World Crop Farms | all SA farms |
| 所有公共服务 | 18 座 | 旧世界 9、新世界 6、安贝沙 3 | 6 张 | `191501` | All Public Services | all public services |
| 所有港口建筑 | 94 座（含 6 个嵌套组） | 旧世界 31、新世界 29、安贝沙 23、未标区域 8、北极 3 | 6 张 | `191508` | All Harbour Buildings | all harbour buildings |
| 所有市场 | 3 座 | 旧世界 1、安贝沙 1、新世界 1 | 11 张 | `191540` | All Marketplaces | all marketplaces |
| 所有动物园 | 2 座 | 新世界 1、旧世界 1 | 1 张 | `191561` | All Zoological Gardens | all zoos |
| 所有博物馆 | 2 座 | 新世界 1、旧世界 1 | 1 张 | `191562` | All Museums | all museums |
| 所有公共停泊处 | 3 座 | 旧世界 2、新世界 1 | 9 张 | `191563` | All Public Moorings | all visitors piers |
| 所有瓷土矿场 | 2 座 | 旧世界 1、新世界 1 | 10 张 | `191592` | All Clay Pits | all clay |
| 所有硝石采石场 | 2 座 | 新世界 1、旧世界 1 | 8 张 | `191593` | All Saltpetre Works | all niter |
| 所有维修起重机 | 4 座 | 未标区域 1、新世界 1、安贝沙 1、旧世界 1 | 4 张 | `191887` | All Repair Cranes | all repair cranes |
| 所有公共建筑 | 42 座（含 4 个嵌套组） | 旧世界 25、新世界 12、安贝沙 5 | 5 张 | `192179` | All Buildings | all residences public buildings EU & SA |
| 所有农夫与工人住所 | 2 座 | 旧世界 2 | 1 张 | `192445` | All Farmer and Worker Residences | all farmers and workers residences |
| 所有投资人与劳工住所 | 8 座（含 1 个嵌套组） | 旧世界 6、新世界 2 | 1 张 | `192446` | All Investor and Obrero Residences | all investor and obrero residences |
| 所有帆船造船厂 | 2 座 | 新世界 1、旧世界 1 | 4 张 | `192466` | All Sailing Shipyards | all sailing shipyards |
| 所有临海生产建筑 | 9 座 | 新世界 4、旧世界 3、安贝沙 2 | 6 张 | `193400` | All Coastal Production Buildings | all harbour productions |
| 所有港口建筑 | 42 座（含 3 个嵌套组） | 旧世界 15、新世界 13、安贝沙 12、未标区域 2 | 1 张 | `193480` | All Harbour Buildings | all loading time buildings |
| 所有文化建筑 | 6 座 | 新世界 3、旧世界 3 | 1 张 | `193666` | All Cultural Buildings | all culture buildings |
| 所有植物园 | 2 座 | 新世界 1、旧世界 1 | 1 张 | `193667` | All Botanical Gardens | all botanical gardens |
| 所有北极生产建筑 | 18 座 | 北极 18 | 1 张 | `193770` | All Arctic Production Buildings | all arctic production |
| 所有重工业 | 24 座（含 2 个嵌套组） | 旧世界 14、新世界 10 | 11 张 | `193771` | All Heavy Industries | all heavy production |
| 所有生产建筑 | 179 座（含 5 个嵌套组） | 新世界 80、旧世界 72、安贝沙 27 | 6 张 | `193856` | All Production Buildings | all production except powerplant |
| 所有贸易站与栈桥 | 28 座（含 3 个嵌套组） | 旧世界 10、安贝沙 8、新世界 8、未标区域 2 | 6 张 | `193897` | All Trading Posts and Piers | all kontors and piers |
| 所有安贝沙作物农场（包含养蜂场） | 7 座 | 安贝沙 6、新世界 1 | 1 张 | `193955` | All Enbesan Crop Farms including Bees | all africa farms |
| 所有旧世界与新世界住所（学者住所除外） | 20 座（含 1 个嵌套组） | 旧世界 14、新世界 6 | 8 张 | `193957` | All Old and New World Residences, except Scholar Residences | all residences EU & SA without Africa & Scholar |
| 所有牛牧场 | 2 座 | 新世界 1、旧世界 1 | 1 张 | `193958` | All Cattle Farms | all cattle farms |
| 所有旧世界酒类生产建筑 | 4 座 | 旧世界 4 | 1 张 | `194005` | All Old World alcohol production buildings | all EU alcohol production buildings |
| 所有谷物、红椒、土豆、樱桃和啤酒花农场 | 7 座 | 旧世界 5、新世界 2 | 1 张 | `194006` | All Grain, Red Pepper, Potato, Cherry and Hops Farms | all EU farms except vineyards |
| 所有果园 | 7 座 | 新世界 4、旧世界 3 | 7 张 | `194008` | All Orchards | all orchards |
| 所有化学厂 | 11 座 | 新世界 7、旧世界 4 | 4 张 | `194011` | All Chemical Plants | all chemical plants |
| 所有新世界果园 | 4 座 | 新世界 4 | 2 张 | `194013` | All New World Orchards | all orchards SA |
| 所有铁塔餐厅 | 6 座 | 旧世界 6 | 2 张 | `194014` | All Iron Tower Restaurants | all monument restaurants |
| 所有旧世界住所（学者住所除外） | 14 座（含 1 个嵌套组） | 旧世界 14 | 1 张 | `194015` | All Old World Residences except Scholar Residences | all residences EU without Scholars |
| 所有摩天大楼 | 9 座 | 旧世界 9 | 15 张 | `194018` | All Skyscrapers | AllSkyscrapers |
| 所有投资人摩天大楼 | 5 座 | 旧世界 5 | 2 张 | `194019` | All Investor Skyscrapers | AllSkyscrapers_Investor |
| 所有工程师摩天大楼 | 3 座 | 旧世界 3 | 1 张 | `194020` | All Engineer Skyscrapers | AllSkyscrapers_Engineer |
| 所有餐厅（非纪念建筑） | 21 座 | 未标区域 21 | 3 张 | `194022` | All Restaurants (Non-Monument) | All restaurants (No Monument) |
| 所有生产线 | 5 座 | 旧世界 5 | 7 张 | `194023` | All Assembly Lines | all assembly lines |
| 所有工匠的工作坊 | 4 座 | 旧世界 4 | 6 张 | `194024` | All Artisan Workshops | all manufacturers |
| 所有购物中心 | 18 座 | 未标区域 18 | 5 张 | `194025` | All Shopping Arcades | All Malls |
| 所有生产建筑 | 171 座（含 2 个嵌套组） | 新世界 75、旧世界 69、安贝沙 27 | 32 张 | `6000018` | All Production Buildings | all production |

### 8.2 具体建筑一览（447 座，按区域分组）

「直接引用」= 有多少张卡**点名**这座建筑；`—` 表示它只被目标组覆盖。

#### 旧世界（159 座）

| 中文名 | 英文名 | 类型 | 直接引用 | GUID | 所属目标组 |
|---|---|---|---|---|---|
| 农夫住所 | Farmer Residence | 住所 | 4 张 | `1010343` | 所有住所、所有公共建筑、所有农夫与工人住所 等 6 个 |
| 天际线高楼 | Skyline Tower | 住所 | 1 张 | `406` | 所有住所、所有公共建筑、所有摩天大楼 等 6 个 |
| 工人住所 | Worker Residence | 住所 | 14 张 | `1010344` | 所有住所、所有公共建筑、所有农夫与工人住所 等 6 个 |
| 工匠住所 | Artisan Residence | 住所 | 19 张 | `1010345` | 所有住所、所有公共建筑、所有旧世界与新世界住所（学者住所除外） 等 5 个 |
| 工程师住所 | Engineer Residence | 住所 | 19 张 | `1010346` | 所有住所、所有公共建筑、所有旧世界与新世界住所（学者住所除外） 等 5 个 |
| 工程师摩天大楼：等级 1 | Engineer Skyscraper: Level 1 | 住所 | — | `601888` | 所有住所、所有公共建筑、所有工程师摩天大楼 等 7 个 |
| 工程师摩天大楼：等级 2 | Engineer Skyscraper: Level 2 | 住所 | — | `601889` | 所有住所、所有公共建筑、所有工程师摩天大楼 等 7 个 |
| 工程师摩天大楼：等级 3 | Engineer Skyscraper: Level 3 | 住所 | — | `601890` | 所有住所、所有公共建筑、所有工程师摩天大楼 等 7 个 |
| 投资人住所 | Investor Residence | 住所 | 14 张 | `1010347` | 所有住所、所有公共建筑、所有投资人与劳工住所 等 6 个 |
| 投资人摩天大楼：等级 1 | Investor Skyscraper: Level 1 | 住所 | — | `601882` | 所有住所、所有公共建筑、所有投资人与劳工住所 等 8 个 |
| 投资人摩天大楼：等级 2 | Investor Skyscraper: Level 2 | 住所 | — | `601883` | 所有住所、所有公共建筑、所有投资人与劳工住所 等 8 个 |
| 投资人摩天大楼：等级 3 | Investor Skyscraper: Level 3 | 住所 | — | `601884` | 所有住所、所有公共建筑、所有投资人与劳工住所 等 8 个 |
| 投资人摩天大楼：等级 4 | Investor Skyscraper: Level 4 | 住所 | — | `601886` | 所有住所、所有公共建筑、所有投资人与劳工住所 等 8 个 |
| 投资人摩天大楼：等级 5 | Investor Skyscraper: Level 5 | 住所 | — | `601891` | 所有住所、所有公共建筑、所有投资人与劳工住所 等 8 个 |
| 学者住所 | Scholar Residence | 住所（战役） | 9 张 | `114445` | 所有住所、所有公共建筑、所有旧世界住所 |
| 酒店 | Hotel | 住所（酒店） | 3 张 | `601445` | 所有公共建筑 |
| 会员俱乐部 | Members Club | 公共服务 | 12 张 | `1010364` | 所有公共建筑、所有公共服务 |
| 医院 | Hospital | 公共服务 | — | `1010464` | 所有医院 |
| 城市医院 | City Hospital | 公共服务 | — | `6355` | 所有医院 |
| 大学 | University | 公共服务 | 11 张 | `1010362` | 所有公共建筑、所有公共服务 |
| 学校 | School | 公共服务 | 10 张 | `1010360` | 所有公共建筑、所有公共服务 |
| 教堂 | Church | 公共服务 | 6 张 | `1010359` | 所有公共建筑、所有公共服务、所有教堂 |
| 无线电塔 | Radio Tower | 公共服务 | 2 张 | `118736` | 所有公共建筑、所有公共服务 |
| 消防局 | Fire Station | 公共服务 | — | `1010463` | 所有消防局 |
| 消防局 | Fire Department | 公共服务 | — | `6354` | 所有消防局 |
| 综艺剧场 | Variety Theatre | 公共服务 | 13 张 | `1010361` | 所有公共建筑、所有公共服务 |
| 警察局 | Police Station | 公共服务 | — | `1010462` | 所有警察局 |
| 警察总部 | Police Headquarters | 公共服务 | — | `6353` | 、所有警察局 |
| 酒吧 | Pub | 公共服务 | 1 张 | `1010358` | 所有公共建筑、所有公共服务、所有酒吧 |
| 银行 | Bank | 公共服务 | 10 张 | `1010365` | 所有公共建筑、所有公共服务 |
| 市政厅 | Town Hall | 公共服务（工会） | — | `100415` | 所有市政厅 |
| 市场 | Marketplace | 公共服务（市场） | — | `1010372` | 所有公共建筑、所有公共服务、所有市场 |
| 港务总管办公室 | Harbourmaster's Office | 公共服务（港务） | — | `100586` | 所有港口建筑 |
| 养猪场 | Pig Farm | 农场 | 5 张 | `1010269` | 所有动物农场、所有旧世界动物农场、所有生产建筑 |
| 啤酒花农场 | Hop Farm | 农场 | 8 张 | `1010264` | 所有作物农场、所有旧世界作物农场、所有生产建筑 等 4 个 |
| 土豆农场 | Potato Farm | 农场 | 8 张 | `1010265` | 所有作物农场、所有旧世界作物农场、所有生产建筑 等 4 个 |
| 炼油厂 | Oil Refinery | 农场 | — | `101331` | 所有冶炼厂和铸造厂、所有油井、所有生产建筑 等 4 个 |
| 牛牧场 | Cattle Farm | 农场 | 1 张 | `1010263` | 所有动物农场、所有旧世界动物农场、所有牛牧场 等 4 个 |
| 红椒农场 | Red Pepper Farm | 农场 | 8 张 | `100654` | 所有作物农场、所有旧世界作物农场、所有生产建筑 等 4 个 |
| 绵羊牧场 | Sheep Farm | 农场 | 1 张 | `1010267` | 所有动物农场、所有旧世界动物农场、所有生产建筑 |
| 葡萄园 | Vineyard | 农场 | 9 张 | `100655` | 所有作物农场、所有旧世界作物农场、所有生产建筑 |
| 谷物农场 | Grain Farm | 农场 | 8 张 | `1010262` | 所有作物农场、所有旧世界作物农场、所有生产建筑 等 4 个 |
| 养猪场 | Pig Farm | 农场（战役） | 3 张 | `24658` | — |
| 伐木工人棚屋 | Lumberjack's Hut | 农牧场（自由区） | — | `1010266` | 所有伐木工人棚屋、所有生产建筑 |
| 狩猎小屋 | Hunting Cabin | 农牧场（自由区） | 12 张 | `1010558` | 所有生产建筑 |
| 燃气发电厂 | Gas-Fired Power Plant | 发电厂 | — | `117547` | 所有生产建筑 |
| 燃油发电厂 | Oil Power Plant | 发电厂 | 4 张 | `100780` | 所有生产建筑 |
| 传单打印机 | Pamphlet Printer | 多功能工厂 | — | `935` | 所有冶炼厂和铸造厂、所有生产建筑、所有重工业 |
| 化学厂：亮面漆 | Chemical Plant: Lacquer | 多功能工厂 | — | `135133` | 所有化学厂 |
| 化学厂：柠檬水 | Chemical Plant: Lemonade | 多功能工厂 | 1 张 | `132777` | 所有化学厂 |
| 化学厂：洗发精 | Chemical Plant: Shampoo | 多功能工厂 | 1 张 | `132786` | 所有化学厂 |
| 化学厂：纪念品 | Chemical Plant: Souvenirs | 多功能工厂 | 1 张 | `133533` | 所有化学厂 |
| 工匠的工作坊：小提琴 | Artisan's Workshop: Violins | 多功能工厂 | — | `135397` | 所有工匠的工作坊 |
| 工匠的工作坊：干邑白兰地 | Artisan's Workshop: Cognac | 多功能工厂 | 1 张 | `135418` | 所有工匠的工作坊 |
| 工匠的工作坊：撞球桌 | Artisan's Workshop: Billiard Tables | 多功能工厂 | — | `135407` | 所有工匠的工作坊 |
| 工匠的工作坊：玩具 | Artisan's Workshop: Toys | 多功能工厂 | — | `135669` | 所有工匠的工作坊 |
| 投水工厂 | Water Drop Factory | 多功能工厂 | — | `937` | 所有冶炼厂和铸造厂、所有生产建筑、所有重工业 |
| 水雷工厂 | Sea Mine Factory | 多功能工厂 | — | `934` | 可生产所有武器的多功能工厂、所有冶炼厂和铸造厂、所有生产建筑 等 4 个 |
| 炸弹工厂 | Bomb Factory | 多功能工厂 | — | `924` | 可生产所有武器的多功能工厂、所有冶炼厂和铸造厂、所有生产建筑 等 4 个 |
| 生产线：打字机 | Assembly Line: Typewriters | 多功能工厂 | — | `135148` | 所有生产线 |
| 生产线：电梯 | Assembly Line: Elevators | 多功能工厂 | — | `134622` | 所有生产线 |
| 生产线：饼干 | Assembly Line: Biscuits | 多功能工厂 | — | `135361` | 所有生产线 |
| 补给包工厂 | Care Package Factory | 多功能工厂 | — | `936` | 所有冶炼厂和铸造厂、所有生产建筑、所有重工业 |
| 工匠厨房 | Artisanal Kitchen | 工厂 | 6 张 | `1010293` | 所有生产建筑、所有食物生产 |
| 沙矿 | Sand Mine | 工厂 | 11 张 | `1010560` | 所有临海生产建筑、所有港口建筑、所有生产建筑 |
| 混凝土工厂 | Concrete Factory | 工厂 | 8 张 | `1010280` | 所有生产建筑 |
| 渔场 | Fishery | 工厂 | 5 张 | `1010278` | 所有临海生产建筑、所有渔场、所有港口建筑 等 4 个 |
| 灯丝工厂 | Filament Factory | 工厂 | — | `1010321` | 所有生产建筑 |
| 灯泡工厂 | Light Bulb Factory | 工厂 | 7 张 | `1010286` | 所有生产建筑 |
| 炸药工厂 | Dynamite Factory | 工厂 | 3 张 | `1010300` | 所有生产建筑 |
| 烈酒酿酒厂 | Schnapps Distillery | 工厂 | 7 张 | `1010294` | 所有旧世界酒类生产建筑、所有生产建筑、所有饮品生产 |
| 燃料站 | Fuel Station | 工厂 | — | `118571` | 所有生产建筑 |
| 玻璃制造厂 | Glassmakers | 工厂 | 3 张 | `1010319` | 所有生产建筑 |
| 珠宝商 | Jewellers | 工厂 | 9 张 | `1010328` | 所有生产建筑 |
| 电话生产商 | Telephone Manufacturer | 工厂 | — | `118735` | 所有生产建筑 |
| 留声机工厂 | Gramophone Factory | 工厂 | 8 张 | `1010326` | 所有木工厂、所有生产建筑 |
| 皮草贸易商 | Fur Dealer | 工厂 | 6 张 | `1010325` | 所有成衣工厂、所有生产建筑 |
| 眼镜工厂 | Spectacle Factory | 工厂 | 8 张 | `101250` | 所有生产建筑 |
| 砖块工厂 | Brick Factory | 工厂 | 1 张 | `1010283` | 所有生产建筑、所有砖块工厂 |
| 硝石采石场 | Saltpetre Works | 工厂 | — | `1010310` | 所有临海生产建筑、所有港口建筑、所有生产建筑 等 4 个 |
| 磨坊 | Flour Mill | 工厂 | 3 张 | `1010313` | 所有生产建筑 |
| 窗户制造厂 | Window Makers | 工厂 | 5 张 | `1010285` | 所有木工厂、所有生产建筑 |
| 精炼工作坊 | Rendering Works | 工厂 | 7 张 | `1010312` | 所有生产建筑 |
| 纺织工厂 | Framework Knitters | 工厂 | 5 张 | `1010315` | 所有成衣工厂、所有生产建筑 |
| 缝纫机器工厂 | Sewing Machine Factory | 工厂 | 8 张 | `1010284` | 所有生产建筑 |
| 罐头工厂 | Cannery | 工厂 | 8 张 | `1010295` | 所有生产建筑、所有食物生产 |
| 肉铺 | Slaughterhouse | 工厂 | 8 张 | `1010316` | 所有生产建筑、所有食物生产 |
| 肥皂工厂 | Soap Factory | 工厂 | 11 张 | `1010281` | 所有生产建筑 |
| 脚踏车工厂 | Bicycle Factory | 工厂 | 11 张 | `1010323` | 所有生产建筑 |
| 船帆制造厂 | Sailmakers | 工厂 | — | `1010288` | 所有成衣工厂、所有生产建筑 |
| 裁缝店 | Tailor's Shop | 工厂 | 6 张 | `118734` | 所有成衣工厂、所有生产建筑 |
| 车辆制造厂 | Coachmakers | 工厂 | — | `1010289` | 所有木工厂、所有生产建筑 |
| 造鞋匠 | Bootmakers | 工厂 | 6 张 | `118733` | 所有成衣工厂、所有生产建筑 |
| 酿酒厂 | Brewery | 工厂 | 6 张 | `1010292` | 所有旧世界酒类生产建筑、所有生产建筑、所有饮品生产 |
| 金匠 | Goldsmiths | 工厂 | — | `1010327` | 所有生产建筑 |
| 钟表匠 | Clockmakers | 工厂 | 12 张 | `1010324` | 所有生产建筑 |
| 锯木厂 | Sawmill | 工厂 | — | `100451` | 所有木工厂、所有生产建筑 |
| 镶嵌工作坊 | Marquetry Workshop | 工厂 | — | `1010320` | 所有木工厂、所有生产建筑 |
| 面包店 | Bakery | 工厂 | 5 张 | `1010291` | 所有生产建筑、所有食物生产 |
| 香槟酒厂 | Champagne Cellar | 工厂 | 7 张 | `100659` | 所有旧世界酒类生产建筑、所有生产建筑、所有饮品生产 |
| 麦芽加工厂 | Malthouse | 工厂 | 1 张 | `1010314` | 所有生产建筑、所有饮品生产 |
| 高端咖啡烘焙厂 | Advanced Coffee Roaster | 工厂（战役） | 5 张 | `124738` | 所有生产建筑、所有饮品生产 |
| 高端朗姆酒工厂 | Advanced Rum Distillery | 工厂（战役） | 7 张 | `124737` | 所有旧世界酒类生产建筑、所有生产建筑、所有饮品生产 |
| 高端棉纺织厂 | Advanced Cotton Mill | 工厂（战役） | — | `124739` | 所有成衣工厂、所有生产建筑 |
| 动物园 | Zoo | 文化建筑 | — | `1010470` | 所有动物园、所有文化建筑 |
| 博物馆 | Museum | 文化建筑 | — | `1010471` | 所有博物馆、所有文化建筑 |
| 植物园 | Botanical Garden | 文化建筑 | — | `110935` | 所有文化建筑、所有植物园 |
| 果园：果酱 | Orchard: Jam | 果园（配方） | 1 张 | `133496` | 所有旧世界果园、所有果园、所有谷物、红椒、土豆、樱桃和啤酒花农场 |
| 果园：树脂 | Orchard: Resin | 果园（配方） | — | `135085` | 所有旧世界果园、所有果园 |
| 果园：樱桃原木 | Orchard: Cherry Wood | 果园（配方） | 1 张 | `135088` | 所有旧世界果园、所有果园 |
| 储油槽 | Oil Store | 港口 | — | `100784` | 所有港口建筑 |
| 库房 | Depot | 港口 | — | `1010519` | 所有港口建筑 |
| 中型原油港口 | Medium Oil Harbour | 港口仓库 | — | `101403` | 所有港口建筑 |
| 中型贸易站 | Medium Trading Post | 港口仓库 | — | `100510` | 所有港口建筑、所有贸易站与栈桥 |
| 中型贸易站 | Medium Trading Post | 港口仓库 | — | `100514` | 所有港口建筑、所有贸易站与栈桥 |
| 大型原油港口 | Large Oil Harbour | 港口仓库 | — | `101404` | 所有港口建筑 |
| 大型贸易站 | Large Trading Post | 港口仓库 | — | `100511` | 所有港口建筑、所有贸易站与栈桥 |
| 大型贸易站 | Large Trading Post | 港口仓库 | — | `100515` | 所有港口建筑、所有贸易站与栈桥 |
| 小型原油港口 | Small Oil Harbour | 港口仓库 | — | `100783` | 所有港口建筑 |
| 小型皇家贸易站 | Small Trading Post | 港口仓库 | — | `1010540` | 所有港口建筑、所有贸易站与栈桥 |
| 小型贸易站 | Small Trading Post | 港口仓库 | — | `1010517` | 所有港口建筑、所有贸易站与栈桥 |
| 豪华原油港口 | Grand Oil Harbour | 港口仓库 | — | `119259` | 所有港口建筑 |
| 豪华贸易站 | Grand Trading Post | 港口仓库 | — | `269867` | 所有港口建筑、所有贸易站与栈桥 |
| 豪华贸易站 | Grand Trading Post | 港口仓库 | — | `269879` | 所有港口建筑、所有贸易站与栈桥 |
| 反装甲炮 | Anti-Armour Gun | 港口防御工事 | — | `3700` | 所有港口建筑、所有防御炮塔 |
| 大贝蒂 | Big Betty | 港口防御工事 | — | `1010524` | 所有港口建筑、所有防御炮塔 |
| 机枪 | Mounted Guns | 港口防御工事 | — | `1010522` | 所有港口建筑、所有防御炮塔 |
| 火焰喷射塔 | Flame Tower | 港口防御工事 | — | `625` | 所有港口建筑、所有防御炮塔 |
| 炮塔 | Cannon Tower | 港口防御工事 | — | `1010523` | 所有港口建筑、所有防御炮塔 |
| 防空炮台 | Flak Emplacement | 港口防御工事 | — | `736` | 所有港口建筑、所有防御炮塔 |
| 高端栈桥 | Advanced Pier | 港口（栈桥·战役） | — | `125028` | 所有港口建筑、所有贸易站与栈桥 |
| 栈桥 | Pier | 港口（栈桥） | — | `100519` | 所有港口建筑、所有贸易站与栈桥 |
| 起重机修理厂 | Repair Crane | 港口（维修起重机） | — | `1010525` | 所有港口建筑、所有维修起重机 |
| 公共停泊处 | Public Mooring | 港口（观光码头） | — | `100429` | 所有公共停泊处、所有港口建筑 |
| 游客停泊处 | Tourist Mooring | 港口（观光码头） | — | `133890` | 所有公共停泊处、所有港口建筑 |
| 飞船月台 | Airship Platform | 港口（飞船月台） | — | `962` | 所有港口建筑、所有飞船月台 |
| 煤矿 | Coal Mine | 矿场 / 采集场 | 1 张 | `1010304` | 所有山地矿山、所有旧世界矿场、所有生产建筑 等 4 个 |
| 石灰岩矿场 | Limestone Quarry | 矿场 / 采集场 | 8 张 | `1010309` | 所有旧世界矿场、所有生产建筑、所有矿山和水泥 |
| 矿坑 | Mineral Mine | 矿场 / 采集场 | — | `1010311` | 所有山地矿山、所有生产建筑、所有矿山和水泥 |
| 铁矿 | Iron Mine | 矿场 / 采集场 | 2 张 | `1010305` | 所有山地矿山、所有旧世界矿场、所有生产建筑 等 4 个 |
| 铜矿 | Copper Mine | 矿场 / 采集场 | — | `1010308` | 所有山地矿山、所有旧世界矿场、所有生产建筑 等 4 个 |
| 锌矿 | Zinc Mine | 矿场 / 采集场 | — | `1010307` | 所有山地矿山、所有旧世界矿场、所有生产建筑 等 4 个 |
| 陶土矿场 | Clay Pit | 矿场 / 采集场 | — | `100416` | 所有瓷土矿场、所有生产建筑 |
| 帆船造船厂 | Sailing Shipyard | 造船厂 | — | `1010520` | 所有帆船造船厂、所有港口建筑、所有造船厂 |
| 蒸汽船造船厂 | Steam Shipyard | 造船厂 | 6 张 | `1010521` | 所有港口建筑、所有造船厂 |
| 武器工厂 | Weapon Factory | 重工业 | 6 张 | `1010299` | 所有冶炼厂和铸造厂、所有生产建筑、所有重工业 |
| 汽车生产线 | Cab Assembly Line | 重工业 | 12 张 | `1010303` | 所有冶炼厂和铸造厂、所有生产建筑、所有生产线 等 4 个 |
| 炼钢厂 | Steelworks | 重工业 | 5 张 | `1010296` | 所有冶炼厂和铸造厂、所有生产建筑、所有重工业 等 4 个 |
| 重兵器工厂 | Heavy Weapons Factory | 重工业 | 8 张 | `1010301` | 所有冶炼厂和铸造厂、所有生产建筑、所有重工业 |
| 马达生产线 | Motor Assembly Line | 重工业 | 3 张 | `1010302` | 所有冶炼厂和铸造厂、所有生产建筑、所有生产线 等 4 个 |
| 高炉 | Furnace | 重工业 | 2 张 | `1010297` | 所有冶炼厂和铸造厂、所有生产建筑、所有重工业 等 4 个 |
| 黄铜冶炼厂 | Brass Smeltery | 重工业 | — | `1010282` | 所有冶炼厂和铸造厂、所有生产建筑、所有重工业 |
| 炭窑 | Charcoal Kiln | 重工业（自由区） | 1 张 | `1010298` | 所有冶炼厂和铸造厂、所有炭窑、所有生产建筑 等 4 个 |
| 纪念馆：乳脂松糕塔 | The Iron Tower: Trifle Tower | 餐厅（铁塔） | — | `133930` | 所有铁塔餐厅 |
| 纪念馆：探索年代 | The Iron Tower: Age of Exploration | 餐厅（铁塔） | — | `133932` | 所有铁塔餐厅 |
| 纪念馆：柑橘酱女士 | The Iron Tower: Lady Marmalade | 餐厅（铁塔） | — | `133931` | 所有铁塔餐厅 |
| 纪念馆：皇家奶油面包 | The Iron Tower: Brioche Royale | 餐厅（铁塔） | — | `133928` | 所有铁塔餐厅 |
| 纪念馆：风土龙虾 | The Iron Tower: Homard sur Lit de Terroir | 餐厅（铁塔） | — | `133933` | 所有铁塔餐厅 |
| 铁塔 | The Iron Tower | 餐厅（铁塔） | — | `132770` | 所有铁塔餐厅 |

#### 新世界（142 座）

| 中文名 | 英文名 | 类型 | 直接引用 | GUID | 所属目标组 |
|---|---|---|---|---|---|
| 农工住所 | Jornalero Residence | 住所 | 1 张 | `101254` | 所有住所、所有公共建筑、所有旧世界与新世界住所（学者住所除外） |
| 劳工住所 | Obrero Residence | 住所 | 3 张 | `101255` | 所有住所、所有公共建筑、所有投资人与劳工住所 等 4 个 |
| 庄园临时工区 | Hacienda Jornalero Quarters | 住所 | — | `24792` | 所有住所、所有公共建筑、所有旧世界与新世界住所（学者住所除外） |
| 庄园劳工区 | Hacienda Obrera Quarters | 住所 | — | `24793` | 所有住所、所有公共建筑、所有投资人与劳工住所 等 4 个 |
| 庄园艺术家区 | Hacienda Artista Quarters | 住所 | — | `6086` | 所有住所、所有公共建筑、所有旧世界与新世界住所（学者住所除外） |
| 艺术家住所 | Artista Residence | 住所 | — | `5405` | 所有住所、所有公共建筑、所有旧世界与新世界住所（学者住所除外） |
| 医院 | Hospital | 公共服务 | — | `101276` | 所有医院 |
| 城市医院 | City Hospital | 公共服务 | — | `6260` | 所有医院 |
| 小礼拜堂 | Chapel | 公共服务 | 6 张 | `101258` | 所有公共建筑、所有公共服务、所有教堂 |
| 拳击馆 | Boxing Arena | 公共服务 | — | `101259` | 所有公共建筑、所有公共服务 |
| 消防局 | Fire Department | 公共服务 | — | `6259` | 所有消防局 |
| 消防局 | Fire Station | 公共服务 | — | `101275` | 所有消防局 |
| 警察局 | Police Station | 公共服务 | — | `101274` | 所有警察局 |
| 警察总部 | Police Headquarters | 公共服务 | — | `6258` | 、所有警察局 |
| 市政厅 | Town Hall | 公共服务（工会） | — | `101285` | 所有市政厅 |
| 市场 | Marketplace | 公共服务（市场） | — | `101257` | 所有公共建筑、所有公共服务、所有市场 |
| 港务总管办公室 | Harbourmaster's Office | 公共服务（港务） | — | `101286` | 所有港口建筑 |
| 邮局 | Post Office | 公共服务（邮局） | — | `3761` | 所有新世界邮局和邮筒 |
| 邮筒 | Post Box | 公共服务（邮局） | — | `3661` | 所有新世界邮局和邮筒 |
| 兰花农场 | Orchid Farm | 农场 | 5 张 | `5814` | 所有作物农场、所有新世界作物农场、所有生产建筑 |
| 可可园 | Cocoa Plantation | 农场 | 8 张 | `1010332` | 所有作物农场、所有新世界作物农场、所有生产建筑 |
| 咖啡园 | Coffee Plantation | 农场 | 7 张 | `101251` | 所有作物农场、所有新世界作物农场、所有生产建筑 |
| 大蕉园 | Plantain Plantation | 农场 | 7 张 | `101263` | 所有作物农场、所有新世界作物农场、所有生产建筑 |
| 棉花园 | Cotton Plantation | 农场 | 8 张 | `1010331` | 所有作物农场、所有新世界作物农场、所有生产建筑 |
| 橡胶园 | Caoutchouc Plantation | 农场 | 7 张 | `1010333` | 所有作物农场、所有新世界作物农场、所有生产建筑 |
| 炼油厂 | Oil Refinery | 农场 | — | `1010561` | 所有冶炼厂和铸造厂、所有油井、所有生产建筑 |
| 烟草园 | Tobacco Plantation | 农场 | 8 张 | `1010330` | 所有作物农场、所有新世界作物农场、所有生产建筑 |
| 玉米农场 | Corn Farm | 农场 | 8 张 | `101270` | 所有作物农场、所有新世界作物农场、所有生产建筑 |
| 甘蔗园 | Sugar Cane Plantation | 农场 | 9 张 | `1010329` | 所有作物农场、所有新世界作物农场、所有生产建筑 |
| 药草花园 | Herb Garden | 农场 | 3 张 | `5463` | 所有作物农场、所有新世界作物农场、所有生产建筑 |
| 牛牧场 | Cattle Farm | 农场（可通电） | 1 张 | `101269` | 所有动物农场、所有牛牧场、所有生产建筑 |
| 羊驼牧场 | Alpaca Farm | 农场（可通电） | 2 张 | `101272` | 所有动物农场、所有生产建筑 |
| 美洲鸵农场 | Nandu Farm | 农场（可通电） | — | `5457` | 所有动物农场、所有生产建筑 |
| 庄园可可农场 | Hacienda Cocoa Farm | 农场（庄园） | 8 张 | `25009` | 所有作物农场、所有新世界作物农场、所有生产建筑 |
| 庄园咖啡农场 | Hacienda Coffee Farm | 农场（庄园） | 7 张 | `25005` | 所有作物农场、所有新世界作物农场、所有生产建筑 |
| 庄园土豆农场 | Hacienda Potato Farm | 农场（庄园） | 10 张 | `25019` | 所有作物农场、所有新世界作物农场、所有生产建筑 等 4 个 |
| 庄园橡胶园 | Hacienda Caoutchouc Plantation | 农场（庄园） | 7 张 | `25006` | 所有作物农场、所有新世界作物农场、所有生产建筑 |
| 庄园玉米农场 | Hacienda Corn Farm | 农场（庄园） | 7 张 | `25003` | 所有作物农场、所有新世界作物农场、所有生产建筑 |
| 庄园甘蔗农场 | Hacienda Sugar Cane Farm | 农场（庄园） | 9 张 | `24798` | 所有作物农场、所有新世界作物农场、所有生产建筑 |
| 庄园谷物农场 | Hacienda Grain Farm | 农场（庄园） | 9 张 | `25128` | 所有作物农场、所有新世界作物农场、所有生产建筑 等 4 个 |
| 庄园辛香料农场 | Hacienda Spice Farm | 农场（庄园） | 1 张 | `25020` | 所有作物农场、所有安贝沙作物农场、所有安贝沙作物农场（包含养蜂场） 等 5 个 |
| 伐木工人棚屋 | Lumberjack's Hut | 农牧场（自由区） | 2 张 | `101260` | 所有伐木工人棚屋、所有生产建筑 |
| 发电厂 | Power Station | 发电厂 | 4 张 | `5164` | — |
| 水坝 | Dam | 发电厂 | — | `6006` | 所有生产建筑 |
| 戏院 | Cinema | 增益建筑 | 10 张 | `6018` | 所有公共建筑、所有公共服务 |
| 森巴学校 | Samba School | 增益建筑 | — | `5840` | 所有公共建筑、所有公共服务 |
| 海滩 | Beach | 增益建筑 | — | `6264` | 所有公共建筑、所有公共服务 |
| 庄园肥料工作坊 | Hacienda Fertiliser Works | 增益建筑（文化） | 10 张 | `24805` | 所有生产建筑 |
| 传单打印机 | Pamphlet Printer | 多功能工厂 | — | `908` | 所有冶炼厂和铸造厂、所有生产建筑、所有重工业 |
| 军火工厂：灭火器 | Laboratory: Fire Extinguisher | 多功能工厂 | 3 张 | `6629` | 所有生产建筑 |
| 军火工厂：药物 | Laboratory: Medicine | 多功能工厂 | 5 张 | `6631` | 所有化学厂、所有生产建筑 |
| 军火工厂：警察装备 | Arsenal: Police Equipment | 多功能工厂 | 3 张 | `6630` | 可生产所有武器的多功能工厂、所有生产建筑 |
| 军火工厂：颜料 | Laboratory: Pigments | 多功能工厂 | 1 张 | `5462` | 所有化学厂、所有生产建筑 |
| 化学厂：乙醇 | Chemical Plant: Ethanol | 多功能工厂 | — | `135134` | 所有化学厂、所有新世界化学厂 |
| 化学厂：口香糖 | Chemical Plant: Chewing Gum | 多功能工厂 | 1 张 | `135185` | 所有化学厂、所有新世界化学厂 |
| 化学厂：底片卷 | Chemical Plant: Film Reels | 多功能工厂 | 4 张 | `5828` | 所有化学厂、所有新世界化学厂、所有生产建筑 |
| 化学厂：赛璐珞 | Chemical Plant: Celluloid | 多功能工厂 | — | `135224` | 所有化学厂、所有新世界化学厂 |
| 庄园兰姆酒工厂 | Hacienda Rum Distillery | 多功能工厂 | 7 张 | `24801` | 所有生产建筑、所有饮品生产 |
| 庄园制粥机 | Hacienda Atole Maker | 多功能工厂 | 1 张 | `25126` | 所有生产建筑、所有饮品生产 |
| 庄园啤酒酿造厂 | Hacienda Beer Brewery | 多功能工厂 | 7 张 | `25064` | 所有生产建筑、所有饮品生产 |
| 庄园烈酒酿酒厂 | Hacienda Schnapps Distillery | 多功能工厂 | 7 张 | `25350` | 所有生产建筑、所有饮品生产 |
| 庄园辣酱酿造厂 | Hacienda Hot Sauce Factory | 多功能工厂 | 1 张 | `25508` | 所有生产建筑、所有饮品生产 |
| 投水工厂 | Water Drop Factory | 多功能工厂 | — | `915` | 所有冶炼厂和铸造厂、所有生产建筑、所有重工业 |
| 水雷工厂 | Sea Mine Factory | 多功能工厂 | — | `907` | 可生产所有武器的多功能工厂、所有冶炼厂和铸造厂、所有生产建筑 等 4 个 |
| 炸弹工厂 | Bomb Factory | 多功能工厂 | — | `906` | 可生产所有武器的多功能工厂、所有冶炼厂和铸造厂、所有生产建筑 等 4 个 |
| 补给包工厂 | Care Package Factory | 多功能工厂 | — | `916` | 所有冶炼厂和铸造厂、所有生产建筑、所有重工业 |
| 冰激凌工厂 | Ice Cream Factory | 工厂 | 3 张 | `5459` | 所有生产建筑、所有食物生产 |
| 制玉米饼店 | Tortilla Maker | 工厂 | 5 张 | `101271` | 所有生产建筑、所有食物生产 |
| 制糖厂 | Sugar Refinery | 工厂 | 1 张 | `1010317` | 所有生产建筑、所有食物生产 |
| 咖啡烘焙厂 | Coffee Roaster | 工厂 | 7 张 | `101252` | 所有生产建筑、所有饮品生产 |
| 圆顶硬礼帽编织厂 | Bombín Weaver | 工厂 | 5 张 | `101273` | 所有生产建筑 |
| 巧克力工厂 | Chocolate Factory | 工厂 | 6 张 | `1010341` | 所有生产建筑、所有食物生产 |
| 摩托车工厂 | Scooter Factory | 工厂 | 8 张 | `5658` | 所有生产建筑、所有重工业 |
| 斗篷缝补厂 | Poncho Darner | 工厂 | 5 张 | `101266` | 所有成衣工厂、所有生产建筑 |
| 服装店 | Costume Shop | 工厂 | 7 张 | `5933` | 所有成衣工厂、所有生产建筑 |
| 朗姆酒工厂 | Rum Distillery | 工厂 | 8 张 | `1010340` | 所有生产建筑、所有饮品生产 |
| 棉纺织厂 | Cotton Mill | 工厂 | 1 张 | `1010318` | 所有成衣工厂、所有生产建筑 |
| 毛毡制造厂 | Felt Producer | 工厂 | 1 张 | `101415` | 所有生产建筑 |
| 炸大蕉饼店 | Fried Plantain Kitchen | 工厂 | 5 张 | `101264` | 所有生产建筑、所有食物生产 |
| 炸海鲜厨房 | Jalea Kitchen | 工厂 | 3 张 | `5458` | 所有生产建筑、所有食物生产 |
| 燃料站 | Fuel Station | 工厂 | — | `269840` | 所有生产建筑 |
| 珍珠养殖场 | Pearl Farm | 工厂 | 11 张 | `1010339` | 所有临海生产建筑、所有港口建筑、所有生产建筑 |
| 电扇工厂 | Fan Factory | 工厂 | 10 张 | `5862` | 所有生产建筑 |
| 砖块工厂 | Brick Factory | 工厂 | — | `101268` | 所有生产建筑、所有砖块工厂 |
| 硝石采石场 | Saltpetre Works | 工厂 | — | `101303` | 所有临海生产建筑、所有港口建筑、所有生产建筑 等 4 个 |
| 缆线工厂 | Cable Factory | 工厂 | 1 张 | `6279` | 所有生产建筑 |
| 缝纫机器工厂 | Sewing Machine Factory | 工厂 | 4 张 | `6083` | 所有生产建筑 |
| 船帆制造厂 | Sailmakers | 工厂 | — | `101265` | 所有成衣工厂、所有生产建筑 |
| 足球制造厂 | Ball Manufactory | 工厂 | 2 张 | `5879` | 所有成衣工厂、所有生产建筑 |
| 铝冶炼机 | Aluminium Smelter | 工厂 | 2 张 | `835` | 所有冶炼厂和铸造厂、所有生产建筑、所有重工业 |
| 锯木厂 | Sawmill | 工厂 | — | `101261` | 所有木工厂、所有生产建筑 |
| 镶嵌工作坊 | Marquetry Workshop | 工厂 | 1 张 | `101296` | 所有木工厂、所有生产建筑 |
| 雪茄工厂 | Cigar Factory | 工厂 | 9 张 | `1010342` | 所有生产建筑 |
| 香水混合机 | Perfume Mixer | 工厂 | 1 张 | `5657` | 所有生产建筑 |
| 马达装配厂 | Motor Assembly Plant | 工厂 | 7 张 | `5659` | 所有生产建筑、所有重工业 |
| 鱼油工厂 | Fish Oil Factory | 工厂 | — | `101262` | 所有临海生产建筑、所有渔场、所有港口建筑 等 4 个 |
| 鱿鱼养殖场 | Calamari Fishery | 工厂 | 1 张 | `7919` | 所有临海生产建筑、所有渔场、所有港口建筑 等 4 个 |
| 龙舌兰酒吧 | Mezcal Bar | 工厂 | 5 张 | `6594` | 所有生产建筑、所有饮品生产 |
| 动物园 | Zoo | 文化建筑（新世界） | — | `102282` | 所有动物园、所有文化建筑 |
| 博物馆 | Museum | 文化建筑（新世界） | — | `102283` | 所有博物馆、所有文化建筑 |
| 植物园 | Botanical Garden | 文化建筑（新世界） | — | `114141` | 所有文化建筑、所有植物园 |
| 果园：柑橘水果 | Orchard: Citrus | 果园（配方） | 1 张 | `133031` | 所有新世界果园、所有果园 |
| 果园：椰子油 | Orchard: Coconut Oil | 果园（配方） | — | `133004` | 所有新世界果园、所有果园 |
| 果园：樟脑油 | Orchard: Camphor Wax | 果园（配方） | — | `134614` | 所有新世界果园、所有果园 |
| 果园：肉桂 | Orchard: Cinnamon | 果园（配方） | — | `133030` | 所有新世界果园、所有果园 |
| 储油槽 | Oil Store | 港口 | — | `101330` | 所有港口建筑 |
| 库房 | Depot | 港口 | — | `101278` | 所有港口建筑 |
| 中型原油港口 | Medium Oil Harbour | 港口仓库 | — | `101405` | 所有港口建筑 |
| 中型贸易站 | Medium Trading Post | 港口仓库 | — | `101294` | 所有港口建筑、所有贸易站与栈桥 |
| 中型贸易站 | Medium Trading Post | 港口仓库 | — | `101291` | 所有港口建筑、所有贸易站与栈桥 |
| 大型原油港口 | Large Oil Harbour | 港口仓库 | — | `101406` | 所有港口建筑 |
| 大型贸易站 | Large Trading Post | 港口仓库 | — | `101292` | 所有港口建筑、所有贸易站与栈桥 |
| 大型贸易站 | Large Trading Post | 港口仓库 | — | `101295` | 所有港口建筑、所有贸易站与栈桥 |
| 小型原油港口 | Small Oil Harbour | 港口仓库 | — | `101329` | 所有港口建筑 |
| 小型贸易站 | Small Trading Post | 港口仓库 | — | `101293` | 所有港口建筑、所有贸易站与栈桥 |
| 小型贸易站 | Small Trading Post | 港口仓库 | — | `101290` | 所有港口建筑、所有贸易站与栈桥 |
| 豪华原油港口 | Grand Oil Harbour | 港口仓库 | — | `119281` | 所有港口建筑 |
| 反装甲炮 | Anti-Armour Gun | 港口防御工事 | — | `4797` | 所有港口建筑、所有防御炮塔 |
| 大贝蒂 | Big Betty | 港口防御工事 | — | `101571` | 所有港口建筑、所有防御炮塔 |
| 机枪 | Mounted Guns | 港口防御工事 | — | `101563` | 所有港口建筑、所有防御炮塔 |
| 火焰喷射塔 | Flame Tower | 港口防御工事 | — | `632` | 所有港口建筑、所有防御炮塔 |
| 炮塔 | Cannon Tower | 港口防御工事 | — | `101570` | 所有港口建筑、所有防御炮塔 |
| 防空炮台 | Flak Emplacement | 港口防御工事 | — | `742` | 所有港口建筑、所有防御炮塔 |
| 防空炮台 | Flak Emplacement | 港口防御工事 | — | `2968` | 所有港口建筑 |
| 高端栈桥 | Advanced Pier | 港口（栈桥·战役） | — | `125191` | 所有港口建筑、所有贸易站与栈桥 |
| 栈桥 | Pier | 港口（栈桥） | — | `101344` | 所有港口建筑、所有贸易站与栈桥 |
| 起重机修理厂 | Repair Crane | 港口（维修起重机） | — | `101573` | 所有港口建筑、所有维修起重机 |
| 公共停泊处 | Public Mooring | 港口（观光码头） | — | `102284` | 所有公共停泊处、所有港口建筑 |
| 飞船月台 | Airship Platform | 港口（飞船月台） | — | `963` | 所有港口建筑、所有飞船月台 |
| 牧场 | Pasture | 生产模块（可通电） | — | `8002` | 所有通电牧场 |
| 通电牧场 | Powered Pasture | 生产模块（可通电） | — | `8026` | 所有通电牧场 |
| 通电牧场 | Powered Pasture | 生产模块（可通电） | — | `8027` | 所有通电牧场 |
| 氦气开采机 | Helium Extractor | 矿场 / 采集场 | 3 张 | `1353` | 所有山地矿山、所有生产建筑、所有矿山和水泥 |
| 矿坑 | Mineral Mine | 矿场 / 采集场 | — | `1388` | 所有山地矿山、所有生产建筑、所有矿山和水泥 |
| 矿坑 | Mineral Mine | 矿场 / 采集场 | — | `1390` | 所有山地矿山、所有生产建筑、所有矿山和水泥 |
| 金矿 | Gold Mine | 矿场 / 采集场 | 1 张 | `101311` | 所有山地矿山、所有生产建筑、所有矿山和水泥 |
| 铝土矿场 | Bauxite Mine | 矿场 / 采集场 | 9 张 | `1308` | 所有山地矿山、所有生产建筑、所有矿山和水泥 |
| 陶土矿场 | Clay Pit | 矿场 / 采集场 | — | `101267` | 所有瓷土矿场、所有生产建筑 |
| 帆船造船厂 | Sailing Shipyard | 造船厂 | — | `101277` | 所有帆船造船厂、所有港口建筑、所有造船厂 |
| 高炉 | Furnace | 重工业 | 1 张 | `6080` | 所有冶炼厂和铸造厂、所有生产建筑、所有重工业 |
| 工业榨油机 | Industrial Oil Press | 重工业（自由区） | 6 张 | `1418` | 所有化学厂、所有新世界化学厂、所有生产建筑 等 4 个 |
| 炭窑 | Charcoal Kiln | 重工业（自由区） | 1 张 | `1345` | 所有炭窑、所有生产建筑 |

#### 安贝沙（57 座）

| 中文名 | 英文名 | 类型 | 直接引用 | GUID | 所属目标组 |
|---|---|---|---|---|---|
| 牧羊人住所 | Shepherd Residence | 住所 | — | `114436` | 所有住所、所有公共建筑、所有安贝沙住所 |
| 长老住所 | Elder Residence | 住所 | — | `114437` | 所有住所、所有公共建筑、所有安贝沙住所 |
| 修道院 | Monastery | 公共服务 | 3 张 | `114520` | 所有公共建筑、所有公共服务 |
| 医院 | Hospital | 公共服务 | — | `117668` | 所有医院 |
| 警察局 | Police Station | 公共服务 | — | `114508` | 所有警察局 |
| 音乐家广场 | Musicians' Court | 公共服务 | 2 张 | `114519` | 所有公共建筑、所有公共服务 |
| 消防局 | Fire Station | 公共服务（安贝沙） | — | `119892` | 所有消防局 |
| 市场 | Marketplace | 公共服务（市场） | — | `114518` | 所有公共建筑、所有公共服务、所有市场 |
| 港务总管办公室 | Harbourmaster's Office | 公共服务（港务） | — | `117860` | 所有港口建筑 |
| 亚麻农场 | Linseed Farm | 农场 | 1 张 | `114448` | 所有作物农场、所有安贝沙作物农场、所有安贝沙作物农场（包含养蜂场） 等 4 个 |
| 养蜂场 | Apiary | 农场 | 3 张 | `114453` | 所有作物农场、所有安贝沙作物农场（包含养蜂场）、所有生产建筑 |
| 山羊农场 | Goat Farm | 农场 | 2 张 | `114456` | 所有动物农场、所有生产建筑、所有饮品生产 |
| 木槿农场 | Hibiscus Farm | 农场 | 2 张 | `114447` | 所有作物农场、所有安贝沙作物农场、所有安贝沙作物农场（包含养蜂场） 等 4 个 |
| 木蓝农场 | Indigo Farm | 农场 | 2 张 | `114451` | 所有作物农场、所有安贝沙作物农场、所有安贝沙作物农场（包含养蜂场） 等 4 个 |
| 桑加牧场 | Sanga Farm | 农场 | 4 张 | `114439` | 所有动物农场、所有生产建筑 |
| 苔麸农场 | Teff Farm | 农场 | — | `114450` | 所有作物农场、所有安贝沙作物农场、所有安贝沙作物农场（包含养蜂场） 等 4 个 |
| 辛香料农场 | Spice Farm | 农场 | 1 张 | `114452` | 所有作物农场、所有安贝沙作物农场、所有安贝沙作物农场（包含养蜂场） 等 4 个 |
| 万扎伐木工 | Wanza Woodcutter | 农牧场（自由区） | 6 张 | `122963` | 所有伐木工人棚屋、所有生产建筑 |
| 亚麻磨坊 | Linen Mill | 工厂 | 1 张 | `114441` | 所有成衣工厂、所有生产建筑 |
| 壁毯织布机坊 | Tapestry Looms | 工厂 | 2 张 | `114469` | 所有成衣工厂、所有生产建筑 |
| 灯笼匠 | Lanternsmith | 工厂 | 7 张 | `114464` | 所有生产建筑 |
| 炖汤厨房 | Wat Kitchen | 工厂 | 1 张 | `114471` | 所有生产建筑、所有食物生产 |
| 烟斗工匠 | Pipe Maker | 工厂 | 3 张 | `114472` | 所有生产建筑 |
| 燃料站 | Fuel Station | 工厂 | — | `119028` | 所有生产建筑 |
| 画家 | Luminer | 工厂 | 4 张 | `114470` | 所有生产建筑 |
| 砖块风干房 | Brick Dry-House | 工厂 | — | `114467` | 所有生产建筑、所有砖块工厂 |
| 苔麸磨坊 | Teff Mill | 工厂 | 3 张 | `114459` | 所有生产建筑 |
| 茶厨 | Tea Spicer | 工厂 | 2 张 | `114468` | 所有生产建筑、所有饮品生产 |
| 蜡烛工坊 | Chandler | 工厂 | — | `114461` | 所有生产建筑 |
| 采盐场 | Salt Works | 工厂 | 2 张 | `114440` | 所有临海生产建筑、所有港口建筑、所有生产建筑 |
| 针织工坊 | Embroiderer | 工厂 | 2 张 | `114466` | 所有成衣工厂、所有生产建筑 |
| 陶瓷工作坊 | Ceramics Workshop | 工厂 | 4 张 | `118725` | 所有生产建筑 |
| 风干房 | Dry-House | 工厂 | 3 张 | `114444` | 所有生产建筑、所有食物生产 |
| 龙虾养殖场 | Lobster Fishery | 工厂 | 5 张 | `118729` | 所有临海生产建筑、所有渔场、所有港口建筑 等 4 个 |
| 储油槽 | Oil Store | 港口 | — | `119034` | 所有港口建筑 |
| 库房 | Depot | 港口 | — | `117870` | 所有港口建筑 |
| 中型原油港口 | Medium Oil Harbour | 港口仓库 | — | `119032` | 所有港口建筑 |
| 中型贸易站 | Medium Trading Post | 港口仓库 | — | `114627` | 所有港口建筑、所有贸易站与栈桥 |
| 中型贸易站 | Medium Trading Post | 港口仓库 | — | `114630` | 所有港口建筑、所有贸易站与栈桥 |
| 大型原油港口 | Large Oil Harbour | 港口仓库 | — | `119033` | 所有港口建筑 |
| 大型贸易站 | Large Trading Post | 港口仓库 | — | `114628` | 所有港口建筑、所有贸易站与栈桥 |
| 大型贸易站 | Large Trading Post | 港口仓库 | — | `114631` | 所有港口建筑、所有贸易站与栈桥 |
| 小型原油港口 | Small Oil Harbour | 港口仓库 | — | `119031` | 所有港口建筑 |
| 小型贸易站 | Small Trading Post | 港口仓库 | — | `114626` | 所有港口建筑、所有贸易站与栈桥 |
| 小型贸易站 | Small Trading Post | 港口仓库 | — | `114629` | 所有港口建筑、所有贸易站与栈桥 |
| 豪华原油港口 | Grand Oil Harbour | 港口仓库 | — | `270172` | 所有港口建筑 |
| 反装甲炮 | Anti-Armour Gun | 港口防御工事 | — | `4799` | 所有港口建筑、所有防御炮塔 |
| 机枪 | Mounted Guns | 港口防御工事 | — | `117861` | 所有港口建筑、所有防御炮塔 |
| 火焰喷射塔 | Flame Tower | 港口防御工事 | — | `823` | 所有港口建筑、所有防御炮塔 |
| 炮塔 | Cannon Tower | 港口防御工事 | — | `117863` | 所有港口建筑、所有防御炮塔 |
| 防空炮台 | Flak Emplacement | 港口防御工事 | — | `743` | 所有港口建筑、所有防御炮塔 |
| 高端栈桥 | Advanced Pier | 港口（栈桥·战役） | — | `125193` | 所有港口建筑、所有贸易站与栈桥 |
| 栈桥 | Pier | 港口（栈桥） | — | `117871` | 所有港口建筑、所有贸易站与栈桥 |
| 维修起重机 | Repair Crane | 港口（维修起重机） | — | `117864` | 所有港口建筑、所有维修起重机 |
| 抽水马达 | Water Pump | 灌溉 | 3 张 | `114544` | — |
| 造纸厂 | Paper Mill | 矿场 / 采集场 | 6 张 | `117744` | 所有生产建筑 |
| 陶土收集场 | Clay Collector | 矿场 / 采集场 | 5 张 | `117743` | 所有生产建筑 |

#### 北极（27 座）

| 中文名 | 英文名 | 类型 | 直接引用 | GUID | 所属目标组 |
|---|---|---|---|---|---|
| 技师庇护所 | Technician Shelter | 住所（北极） | 6 张 | `112652` | — |
| 探险家庇护所 | Explorer Shelter | 住所（北极） | 4 张 | `112091` | — |
| 消防救护站 | Ranger Station | 公共服务（北极） | 1 张 | `112669` | — |
| 邮局 | Post Office | 公共服务（邮局） | 1 张 | `4260` | — |
| 蓝色火焰喷射器浅水重炮舰 | Blue Flamethrower Monitor | 军舰 | — | `1537` | 所有船只 |
| 北极天然气矿场 | Arctic Gas Mine | 农场（北极） | 1 张 | `112690` | 所有北极生产建筑 |
| 哈士奇农场 | Husky Farm | 农场（北极） | 6 张 | `112682` | 所有北极生产建筑 |
| 鹅农场 | Goose Farm | 农场（北极） | 6 张 | `112676` | 所有北极生产建筑 |
| 一级狩猎小屋 | Prime Hunting Cabin | 农牧场（北极） | 1 张 | `116034` | 所有北极生产建筑 |
| 伐木工人棚屋 | Lumberjack's Hut | 农牧场（北极） | 7 张 | `114703` | 所有北极生产建筑 |
| 熊猎人 | Bear Hunting Cabin | 农牧场（北极） | 7 张 | `112673` | 所有北极生产建筑 |
| 驯鹿猎人 | Caribou Hunting Cabin | 农牧场（北极） | 7 张 | `112667` | 所有北极生产建筑 |
| 干肉饼工厂 | Pemmican Cookhouse | 工厂（北极） | 6 张 | `112668` | 所有北极生产建筑 |
| 油灯工厂 | Oil Lamp Factory | 工厂（北极） | 1 张 | `112679` | 所有北极生产建筑 |
| 海豹猎人 | Seal Hunting Docks | 工厂（北极） | 6 张 | `112674` | 所有北极生产建筑 |
| 犬雪橇工厂 | Husky Sled Factory | 工厂（北极） | 6 张 | `112680` | 所有北极生产建筑 |
| 睡袋工厂 | Sleeping Bag Factory | 工厂（北极） | 5 张 | `112675` | 所有北极生产建筑 |
| 连帽大衣工厂 | Parka Factory | 工厂（北极） | 5 张 | `112672` | 所有北极生产建筑 |
| 锯木厂 | Sawmill | 工厂（北极） | 3 张 | `114704` | 所有北极生产建筑 |
| 雪橇骨架工厂 | Sled Frame Factory | 工厂（北极） | 6 张 | `112681` | 所有北极生产建筑 |
| 鲸鱼猎人 | Whaling Station | 工厂（北极） | 6 张 | `112666` | 所有北极生产建筑 |
| 暖炉 | Heater | 暖炉 | 1 张 | `114751` | — |
| 反装甲炮 | Anti-Armour Gun | 港口防御工事 | — | `4798` | 所有港口建筑、所有防御炮塔 |
| 火焰喷射塔 | Flame Tower | 港口防御工事 | — | `824` | 所有港口建筑、所有防御炮塔 |
| 防空炮台 | Flak Emplacement | 港口防御工事 | — | `822` | 所有港口建筑、所有防御炮塔 |
| 深层金矿 | Deep Gold Mine | 矿场 / 采集场（北极） | 1 张 | `116029` | 所有北极生产建筑 |
| 炭窑 | Charcoal Kiln | 重工业（北极） | 1 张 | `114705` | 所有北极生产建筑、所有炭窑 |

#### 未标区域：船 / 港湾模块 / 各世界通用（62 座）

| 中文名 | 英文名 | 类型 | 直接引用 | GUID | 所属目标组 |
|---|---|---|---|---|---|
| 运输栈桥 | Commuter Pier | 公共服务（运输栈桥） | — | `101642` | 所有港口建筑 |
| 战斗巡洋舰 | Battle Cruiser | 军舰 | — | `100442` | 所有船只 |
| 护卫舰 | Frigate | 军舰 | — | `100439` | 所有船只 |
| 指挥舰 | Flagship | 军舰 | — | `101121` | 所有船只 |
| 浅水重炮舰 | Monitor | 军舰 | — | `100443` | 所有船只 |
| 火焰喷射器浅水重炮舰 | Flamethrower Monitor | 军舰 | — | `968` | 所有船只 |
| 炮艇 | Gunboat | 军舰 | — | `100437` | 所有船只 |
| 防空浅水重炮舰 | Flak Monitor | 军舰 | — | `720` | 所有船只 |
| 风帆战舰 | Ship-of-the-line | 军舰 | — | `100440` | 所有船只 |
| 家具店 | Furniture Store | 商业建筑（百货 / 药局 / 家具店） | — | `135099` | 所有购物中心 |
| 家具店：休闲椅 | Furniture Store: Lounge Seating | 商业建筑（百货 / 药局 / 家具店） | — | `135123` | 所有购物中心 |
| 家具店：写字桌 | Furniture Store: Writing Desks | 商业建筑（百货 / 药局 / 家具店） | — | `135120` | 所有购物中心 |
| 家具店：四帷柱床 | Furniture Store: Four-Poster Beds | 商业建筑（百货 / 药局 / 家具店） | — | `135122` | 所有购物中心 |
| 家具店：浴室屏风 | Furniture Store: Vanity Screens | 商业建筑（百货 / 药局 / 家具店） | — | `135121` | 所有购物中心 |
| 家具店：银行家台灯 | Furniture Store: Banker's Lamps | 商业建筑（百货 / 药局 / 家具店） | — | `135105` | 所有购物中心 |
| 百货公司 | Department Store | 商业建筑（百货 / 药局 / 家具店） | — | `135100` | 所有购物中心 |
| 百货公司：公事包 | Department Store: Briefcases | 商业建筑（百货 / 药局 / 家具店） | — | `135190` | 所有购物中心 |
| 百货公司：冰箱 | Department Store: Refrigerators | 商业建筑（百货 / 药局 / 家具店） | — | `135189` | 所有购物中心 |
| 百货公司：吸尘器 | Department Store: Vacuum Cleaners | 商业建筑（百货 / 药局 / 家具店） | — | `135188` | 所有购物中心 |
| 百货公司：烤面包机 | Department Store: Toasters | 商业建筑（百货 / 药局 / 家具店） | — | `135103` | 所有购物中心 |
| 百货公司：陶器 | Department Store: Crockery | 商业建筑（百货 / 药局 / 家具店） | — | `135187` | 所有购物中心 |
| 药局 | Drug Store | 商业建筑（百货 / 药局 / 家具店） | — | `134629` | 所有购物中心 |
| 药局：发油 | Drug Store: Pomade | 商业建筑（百货 / 药局 / 家具店） | — | `135194` | 所有购物中心 |
| 药局：口红 | Drug Store: Lipstick | 商业建筑（百货 / 药局 / 家具店） | — | `135192` | 所有购物中心 |
| 药局：洗涤剂 | Drug Store: Detergent | 商业建筑（百货 / 药局 / 家具店） | — | `135191` | 所有购物中心 |
| 药局：牙膏 | Drug Store: Toothpaste | 商业建筑（百货 / 药局 / 家具店） | — | `134631` | 所有购物中心 |
| 药局：面霜 | Drug Store: Face Cream | 商业建筑（百货 / 药局 / 家具店） | — | `135193` | 所有购物中心 |
| 出口办公室 | Exports Office | 港湾模块 | — | `601462` | 所有港口建筑 |
| 装货码头 | Loading Wharf | 港湾模块 | — | `131778` | 所有港口建筑 |
| 港湾主要码头 | Docklands Main Wharf | 港湾模块（主要码头） | — | `601470` | 所有港口建筑、所有贸易站与栈桥 |
| 库房 | Depot | 港湾模块（仓库） | — | `601463` | 所有港口建筑 |
| 栈桥 | Pier | 港湾模块（栈桥） | — | `601460` | 所有港口建筑、所有贸易站与栈桥 |
| 维修起重机 | Repair Crane | 港湾模块（维修） | — | `131777` | 所有港口建筑、所有维修起重机 |
| 港务总管 | Harbourmaster | 港湾模块（进口） | — | `601461` | 所有港口建筑 |
| 双桅纵帆船 | Schooner | 船 | — | `100438` | 所有船只 |
| 快速帆船 | Clipper | 船 | — | `100441` | 所有船只 |
| 油轮 | Oil Tanker | 船 | — | `100853` | 所有船只 |
| 货船 | Cargo Ship | 船 | — | `1010062` | 所有船只 |
| 大东方号 | The Great Eastern | 船（战役） | — | `118718` | 所有船只 |
| 鱼区 | Fish Shoals | 资源点 | 3 张 | `741` | — |
| 烈酒配方 | Schnapps Recipe | 配方 | 1 张 | `25351` | — |
| 咖啡厅 | Café | 餐厅 | — | `132782` | 所有餐厅（非纪念建筑） |
| 咖啡厅：丰裕之锥 | Cafe: Cone O'Copia | 餐厅 | — | `6138` | 所有餐厅（非纪念建筑） |
| 咖啡厅：芙蕾甜甜圈 | Cafe: Donut Fourré | 餐厅 | — | `132753` | 所有餐厅（非纪念建筑） |
| 咖啡厅：蝴蝶酥 | Cafe: Palmier Biscuit | 餐厅 | — | `133348` | 所有餐厅（非纪念建筑） |
| 咖啡厅：闪电泡芙 | Cafe: Eclair | 餐厅 | — | `133347` | 所有餐厅（非纪念建筑） |
| 咖啡厅：鞑靼鹿肉 | Cafe: Venison Tartare | 餐厅 | — | `133349` | 所有餐厅（非纪念建筑） |
| 咖啡厅：香蕉惊喜 | Cafe: Banana Surprise | 餐厅 | — | `133350` | 所有餐厅（非纪念建筑） |
| 酒吧 | Bar | 餐厅 | — | `132781` | 所有餐厅（非纪念建筑） |
| 酒吧：75 年蒙马特 | Bar: Montmartre '75' | 餐厅 | — | `133343` | 所有餐厅（非纪念建筑） |
| 酒吧：北极热红酒 | Bar: Arctic Glogg | 餐厅 | — | `133345` | 所有餐厅（非纪念建筑） |
| 酒吧：安贝沙晨曦 | Bar: Enbesa Sunrise | 餐厅 | — | `133346` | 所有餐厅（非纪念建筑） |
| 酒吧：德贵丽热带酒 | Bar: Daiquiri Tropic | 餐厅 | — | `132752` | 所有餐厅（非纪念建筑） |
| 酒吧：苦艾酒 | Bar: Absinthe | 餐厅 | — | `6137` | 所有餐厅（非纪念建筑） |
| 酒吧：黑色莫斯科大公国 | Bar: Black Muscovy | 餐厅 | — | `133342` | 所有餐厅（非纪念建筑） |
| 餐厅 | Restaurant | 餐厅 | — | `132780` | 所有餐厅（非纪念建筑） |
| 餐厅：大公炸肉排 | Restaurant: Archduke's Schnitzel | 餐厅 | — | `132747` | 所有餐厅（非纪念建筑） |
| 餐厅：恩潘纳达 | Restaurant: Empanadas | 餐厅 | — | `6136` | 所有餐厅（非纪念建筑） |
| 餐厅：斯特罗格夫红椒炖肉 | Restaurant: Stroggof Goulash | 餐厅 | — | `132750` | 所有餐厅（非纪念建筑） |
| 餐厅：炸鱼薯条 | Restaurant: Fish and Frites | 餐厅 | — | `133339` | 所有餐厅（非纪念建筑） |
| 餐厅：烟熏龙虾 | Restaurant: Lobster Cheminée | 餐厅 | — | `133341` | 所有餐厅（非纪念建筑） |
| 餐厅：酥皮鹿肉 | Restaurant: Venison en Croûte | 餐厅 | — | `133340` | 所有餐厅（非纪念建筑） |

### 8.3 区域 ↔ 当地商人

按上表的区域就能对号入座（商人的区域见第 5.1 节）：

| 区域 | 内部值 | 当地商人 |
|---|---|---|
| 旧世界 | `Moderate` | 布莱克、伊莱、卡希纳 |
| 新世界 | `Colony01` | 萨曼托 |
| 安贝沙 | `Africa` | 柯提马 |
| 北极 | `Arctic` | 库马克 |
| 崔老妮海角 / 打捞相关 | ——（无 `AssociatedRegions`） | 老奈特 |

> **目标组会跨区**：池 `125109`「所有安贝沙作物农场」除了 5 座安贝沙农场，还挂着新世界的
> 「庄园辛香料农场」（`25020`，`RecipeFarm`，香料在庄园里也能种），所以一张卡的作用区域
> 可以同时是「新世界 + 安贝沙」。`cards.md` 的用途列会如实写出两个地区；这类**生产卡**
> 在商人池里是**两家都挂**（柯提马 + 萨曼托），口径见 `mods/all-items-unlocked/README.md` 的规则 5+7。

