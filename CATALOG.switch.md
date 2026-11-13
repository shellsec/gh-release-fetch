# Switch 独立清单

> 自动生成：`python tools/generate_switch_catalog_index.py`；修改 JSON 分片后重新生成。

与电脑端 `apps/`、移动端 `apps-mobile/` 分开维护。仅下载，不安装、不解压、不刷写。

共 **124 条**：**109 条可下载**、**15 条页面入口**。其中 5 条为固定 tag 的预发布版本。

目录收集自公开网络。条目提供用途和发布入口；作者信息以工具内显示及发布页为准。

逐项对照你提供的整合包组件，见 [组件对照表](apps-switch/COMPONENTS.md)。

## 使用入口

运行 `python lookup_app.py`，选择 **Switch**；也可直接搜索：

```bat
lookup_switch.bat 大气层
lookup_switch.bat 存档
lookup_switch.bat 投屏
python auto_update.py --apps-dir apps-switch --platform switch atmosphere-stable nx-firmware
python tools/run_saved_apps.py switch --apps-dir apps-switch
```

搜索后可下载、加入更新列表或打开项目页。条目默认关闭；显式指定 ID 可直接下载，启用后可批量更新。保存列表为 `saved_apps_switch.json`。

附件保留原文件名，保存到 `switch/<id>/`。NRO、OVL、NSP、BIN 载荷与固件压缩包都只下载，安装和复制到 SD 卡需按项目说明进行。

Windows 可直接打开根目录 lookup_app.exe，选择 Switch；相关 EXE 已同步重打包。BAT 在 Python 依赖齐全且源码存在时使用源码，否则使用 EXE。Switch 搜索目前以本地清单为准，未命中时通用 GitHub 补搜不支持 Switch 附件筛选。

## 分类概览

| 分类 | 条目数 |
|---|---|
| 系统基础 | 10 |
| 日常工具 | 29 |
| 在线视频 | 12 |
| 本地与家庭影音 | 4 |
| 游戏与串流 | 5 |
| 音乐 | 3 |
| 社交与阅读 | 5 |
| AI与自动化 | 4 |
| 云游戏与远程 | 5 |
| 文件与存档 | 11 |
| 游戏移植 | 13 |
| 主题与显示 | 4 |
| 悬浮插件 | 6 |
| 引导与维护载荷 | 6 |
| 芯片固件 | 3 |
| 配套资料与电脑工具 | 4 |

## 清单与下载规则

“可下载”表示已匹配公开发布附件，不表示已经过实机测试。核查日期、标签与文件名快照见 [release-check.json](apps-switch/release-check.json)。发布时间较早也不直接等于停更，兼容性需查看各项目说明。

### 系统基础

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `atmosphere-stable` — [获取配好组件的 Atmosphere 整合包](https://github.com/rumla3434/Atmosphere-stable/releases) | .7z | 整合包与官方 Atmosphere 本体是不同选择；保留整合包原目录结构。 |
| `nx-firmware` — [下载 Switch 系统离线更新包](https://github.com/rumla3434/NX_Firmware/releases) | .rar | 仅提供离线固件下载；刷写与下载分开，兼容性查看发布说明。 |
| `atmosphere` — [运行 Switch 自制应用和系统模块](https://github.com/Atmosphere-NX/Atmosphere/releases) | .zip | 压缩包不含单独发布的 fusee.bin；使用 fusee 启动时需从同一发布页另取对应载荷。Daybreak 随 Atmosphere 提供。 |
| `hekate` — [选择启动环境、备份 NAND 和管理 emuMMC](https://github.com/CTCaer/hekate/releases) | .zip | 选择含 Nyx 的完整 ZIP；保留 bootloader 目录，备份和 emuMMC 操作需在设备端进行。 |
| `nx-hbmenu` — [浏览并启动 SD 卡上的自制应用](https://github.com/switchbrew/nx-hbmenu/releases) | .zip | Atmosphere 整合环境通常已包含 hbmenu，无需重复覆盖。 |
| `hekate-easyworld` — [用中文操作 Hekate 启动菜单和 Nyx 工具](https://github.com/easyworld/hekate/releases) | .zip | 默认下载简体中文 _sc.zip 完整包；繁体 _tc.zip 在同一发布页。汉化与官方原版是替代选择，使用前核对 Nyx/Hekate 版本。 |
| `hekate-zdm` — [给 Hekate 的 Nyx 界面换上 zdm 中文版](https://github.com/zdm65477730/hekate/releases) | .bin | 独立 nyx.bin 汉化文件，手动放到 SD:/bootloader/sys/。本次 latest 标签为 v6.5.3-CN，不能据此认定兼容 Hekate 6.5.4。 |
| `sys-patch` — [在系统运行时应用 sys-patch 支持的补丁](https://github.com/impeeza/sys-patch/releases) | .zip | 系统模块套件；按压缩包实际目录部署。与 IPS 签名补丁是不同方案，兼容性查看对应发布说明。 |
| `sigpatch-scripts` — [在电脑上生成签名补丁](https://github.com/borntohonk/Switch-Ghidra-Guides/blob/master/scripts/make_patches.py) | 页面入口 | 电脑端 Python 制作脚本入口，需自行准备运行环境；此条只打开脚本，不自动执行。 |
| `sigpatch-downloads` — [查找与系统版本匹配的签名补丁](https://gbatemp.net/threads/sigpatches-for-atmosphere-hekate-fss0-fusee-package3.571543/) | 页面入口 | 论坛附件手动下载；按帖内说明核对系统与 Atmosphere 版本。 |

### 日常工具

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `jksv` — [把游戏存档备份到 SD 卡，或从备份还原](https://github.com/J-D-K/JKSV/releases) | .nro | 下载 JKSV.nro。建议在还原前先备份当前存档。 |
| `sys-clk` — [为不同游戏设置 CPU、GPU 和内存频率](https://github.com/retronx-team/sys-clk/releases) | .zip | 下载 Switch 版压缩包。解压时保留包内目录，依赖见项目说明。 |
| `missioncontrol` — [连接第三方蓝牙手柄](https://github.com/ndeadly/MissionControl/releases) | .zip | 下载 Switch 版压缩包。解压时保留包内目录，依赖见项目说明。 |
| `ftpd` — [用手机或电脑通过 FTP 读写 SD 卡文件](https://github.com/mtheall/ftpd/releases) | .nro | 在 Switch 上打开 FTP 服务，再用手机或电脑连接屏幕上显示的地址。 |
| `tesla-menu` — [在游戏中打开悬浮菜单和插件](https://github.com/WerWolv/Tesla-Menu/releases) | .zip | 原版 Tesla 菜单，配合 nx-ovlloader；与 Ultrahand 同属菜单方案，安装前按各项目说明选择。 |
| `nx-ovlloader` — [加载 Tesla 等悬浮菜单所需的插件](https://github.com/WerWolv/nx-ovlloader/releases) | .zip | 悬浮插件加载器；菜单与插件的系统兼容性以对应项目说明为准。 |
| `nx-shell` — [在 Switch 上浏览和整理 SD 卡文件](https://github.com/joel16/NX-Shell/releases) | .nro | 下载独立 NRO。可以在 hbmenu 中打开。 |
| `edizon` — [备份、还原或编辑游戏存档](https://github.com/WerWolv/EdiZon/releases) | .nro | 下载 Switch 版文件。放置位置和依赖见项目说明。 |
| `homeguard` — [管理 HOME 菜单的保护设置](https://github.com/Aster145/HomeGuard/releases/tag/v0.1.1) | .zip；预发布固定 `v0.1.1` | 预发布固定版本；先阅读 README 的启动与限制说明，后续版本需人工复核 tag。 |
| `dbi` — [通过 USB 或 MTP 在电脑和 Switch 之间传文件](https://github.com/rashevskyv/dbi/releases) | .nro | 此条目只下载 DBI.nro。需要配置文件或电脑端工具时，可从同一发布页获取。 |
| `hb-appstore` — [在 Switch 上查找、下载和更新自制应用](https://github.com/fortheusers/hb-appstore/releases) | .zip | 下载 switch-extracttosd.zip，包含完整资源；不下载 Wii U 文件。 |
| `aio-switch-updater` — [下载自制系统、固件和相关更新包](https://github.com/HamletDuFromage/aio-switch-updater/releases) | .zip | 下载 Switch 版压缩包。解压时保留包内目录，依赖见项目说明。 |
| `ultrahand-overlay` — [在游戏内打开悬浮工具和运行脚本](https://github.com/ppkantorski/Ultrahand-Overlay/releases) | .zip | 选择 sdout.zip 完整 SD 布局包；依赖与放置方式见项目说明，勿只复制 ovlmenu.ovl 而漏掉资源。 |
| `emuiibo` — [用虚拟 amiibo 代替实体 amiibo](https://github.com/XorTroll/emuiibo/releases) | .zip | ZIP 为 Switch 系统模块；桌面端 emuiigen.jar 不属于本条下载内容。 |
| `sys-con` — [用 USB 连接兼容的第三方手柄](https://github.com/cathery/sys-con/releases) | .zip | 旧版 USB 手柄模块；使用前核对当前系统与 Atmosphere 兼容性，不代表支持所有手柄。 |
| `fastcfwswitch` — [从悬浮菜单选择载荷并重启](https://github.com/Hartie95/fastCFWswitch/releases) | .zip | 悬浮插件，需要配置目标 payload 路径。 |
| `awoo-installer` — [在 Switch 上使用 Awoo 安装工具](https://github.com/Huntereb/Awoo-Installer/releases) | .zip | 主机端 ZIP；电脑端配套工具见 ns-usbloader，不将电脑程序复制为 NRO。 |
| `ascent-toolbox` — [查看和切换系统模块](https://github.com/exploitz86/Ascent-Toolbox/releases) | .nro | Ascent Toolbox，与 DeepSea 分支分开收录；按对应项目确认设备和重启支持。 |
| `deepsea-toolbox` — [管理 DeepSea 环境中的系统模块](https://github.com/Team-Neptune/DeepSea-Toolbox/releases) | .nro | 原 DeepSea 分支；实际发布文件名为 DeepSeaToolbox.nro，不与 Ascent 版本混写。 |
| `edizon-se` — [在游戏运行时查找和修改数值](https://github.com/tomvita/EdiZon-SE/releases) | .zip | 选择 edizon.zip 标准包；同页 EdiZon_alt.zip 是另一版本，使用差异以项目说明为准。 |
| `linkalho` — [管理主机上的本地账号关联](https://github.com/impeeza/linkalho/releases) | .zip | 离线账号关联工具；功能与当前系统支持范围查看项目说明。 |
| `nx-activity-log-zdm` — [用中文查看各游戏的游玩时长](https://github.com/zdm65477730/NX-Activity-Log/releases) | .nro | 游玩时间记录工具汉化分支；主机端 NRO。 |
| `sphaira` — [在一个菜单里启动自制应用、浏览文件和找工具](https://github.com/ITotalJustice/sphaira/releases) | .zip | 完整 ZIP；按 README 确认替换 hbmenu.nro 的方式与功能，保留所需资源。 |
| `switch-time` — [联网校准 Switch 的系统时间](https://github.com/3096/switch-time/releases) | .nro | 下载校时 NRO。使用前请确认 Switch 已联网。 |
| `tencent-switcher-gui` — [在 Switch 上切换系统区域](https://github.com/CaiMiao/Tencent-switcher-GUI/releases) | .nro | 下载当前公开 Release。可切换的区域和使用条件以项目说明为准。 |
| `tinwoo` — [在 Switch 上使用 TinWoo 安装工具](https://github.com/mrdude2478/Tinwoo-Release/releases) | .zip | 主机端完整 ZIP；使用方式与前端要求查看发布说明。 |
| `saltynx` — [SaltyNX（FPSLocker 等工具使用的 Switch 系统模块）](https://github.com/masagrator/SaltyNX/releases/latest) | .zip | 作者要求固件 10.0.0 起及官方 Atmosphère 环境；选标准 ZIP，联机游戏使用前查阅作者限制。 |
| `simplemodmanager` — [在 Switch 上启用、停用和整理游戏模组](https://github.com/nadrino/SimpleModManager/releases) | .nro | 下载图形版 NRO。模组目录和兼容性见项目说明。 |
| `homebrew-details` — [查看、整理和启动 SD 卡上的自制应用](https://github.com/Chrscool8/Homebrew-Details/releases) | 页面入口 | 从发布页选择 Switch 版，按页面说明放置附件。 |

### 在线视频

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `wiliwili` — [在 Switch 上浏览和播放哔哩哔哩视频](https://github.com/xfangfang/wiliwili/releases) | .zip | 下载 Switch 版压缩包，按项目说明保留包内目录。 |
| `switch-newpipe` — [在 Switch 上浏览和播放 YouTube 视频](https://github.com/mirusu400/switch-newpipe/releases) | .nro | 下载 Switch 版文件。放置位置和依赖见项目说明。 |
| `switch-hongguo` — [在 Switch 上浏览红果短剧](https://github.com/ZYP-INre/switch-hongguo/releases) | .nro | 下载 Switch 版文件。放置位置和依赖见项目说明。 |
| `switchtvbox` — [在 Switch 上浏览和播放影视内容](https://github.com/lGuann/SwitchTVBox/releases) | .zip | 下载 Switch 版压缩包。解压时保留包内目录，依赖见项目说明。 |
| `tikzen` — [在 Switch 上浏览短视频](https://github.com/lGuann/Tikzen/releases) | .zip | 下载 Switch 版压缩包。解压时保留包内目录，依赖见项目说明。 |
| `hongguo-switch` — [用另一款 Switch 客户端浏览红果短剧](https://github.com/dongrez1990-cloud/hongguo-switch/releases) | .nsp | 下载 Switch 版文件。放置位置和依赖见项目说明。 |
| `streamfin` — [在 Switch 上浏览和播放网络媒体](https://github.com/scamNscoot/StreamFin/releases) | .nro | 下载 Switch 版文件。放置位置和依赖见项目说明。 |
| `stremnx` — [在 Switch 上使用 Stremio 观看网络媒体](https://github.com/denpingus/StremNX/releases) | .nro | 下载 Switch 版文件。放置位置和依赖见项目说明。 |
| `twinx` — [在 Switch 上观看 Twitch 直播](https://github.com/DomazinUS/twiNX/releases) | .zip | 下载 Switch 版压缩包。解压时保留包内目录，依赖见项目说明。 |
| `ytb-player` — [用自制播放器观看 YouTube 视频](https://github.com/murat303/ytb-player/releases) | .nro | 下载 Switch 版文件。放置位置和依赖见项目说明。 |
| `nxtube` — [给 Switch 官方 YouTube 应用加上网页增强功能](https://www.gamebrew.org/wiki/NxTube_Switch) | 页面入口 | 仅提供补丁介绍页面；补丁版本与官方 YouTube App 的兼容性以项目说明为准。 |
| `youtube-switch` — [使用任天堂商店分发的 YouTube 应用](https://www.nintendo.com/us/store/products/youtube-switch/) | 页面入口 | 官方商店分发，不是 GitHub Release；安装要求以任天堂商店说明为准。 |

### 本地与家庭影音

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `switchfin` — [播放 Jellyfin 或 Emby 服务器里的影音](https://github.com/dragonflylee/switchfin/releases) | .nro | 下载 Switch 版文件。放置位置和依赖见项目说明。 |
| `nxmp` — [播放 SD 卡、本地存储或网络中的影音](https://github.com/proconsule/nxmp/releases) | .zip | 下载 Switch 版压缩包。解压时保留包内目录，依赖见项目说明。 |
| `nx-cast` — [接收手机投屏或播放 IPTV 播放列表](https://github.com/Ode1l/NX-Cast/releases) | .zip | 下载 NX-Cast-sdmc.zip，保留目录结构。投屏时把手机和 Switch 连到同一局域网。 |
| `switchwave` — [在 Switch 上硬解播放本地视频或网络共享里的影音](https://github.com/averne/SwitchWave/releases) | 页面入口 | 下载完整压缩包后，按项目说明将内容合并到 SD 卡。 |

### 游戏与串流

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `retroarch` — [在 Switch 上管理和启动不同平台的模拟器核心](https://www.retroarch.com/?page=platforms) | 页面入口 | 该 GitHub 最新 Release 只有源码包；Switch 构建从官方平台下载页获取。 |
| `moonlight-switch` — [把电脑游戏的画面和声音串流到 Switch](https://github.com/XITRIX/Moonlight-Switch/releases) | .nro | 下载 Switch 版文件。放置位置和依赖见项目说明。 |
| `corkdeck` — [尝试在 Switch 上运行部分 Windows 游戏](https://github.com/plv890/CorkDeck/releases) | .zip | 实验性 Windows 游戏运行环境；所需游戏数据需自行准备，兼容性以项目说明为准。 |
| `switch_frame_tap` — [Switch Frame Tap（通过 USB 或网络传送 Switch 画面与声音）](https://github.com/TomasUribe/switch-frame-tap/releases/latest) | .zip | 需 Atmosphère 与对应接收端；此处为 Switch 端包。 |
| `tico` — [tico（Switch 模拟器前端，集中管理游戏库与模拟器模块）](https://github.com/ticohq/tico/releases/latest) | .nro | 需要 Atmosphère 和 Homebrew Menu。下载 tico.nro 后放到 SD 卡的 /switch/tico/。0.8.0 起模拟器模块需在 tico Store 另行安装。升级前按作者说明备份存档。 |

### 音乐

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `switify` — [在 Switch 上浏览和播放 Spotify 音乐](https://github.com/DomazinUS/Switify/releases) | .zip | 下载 Switch 版压缩包。解压时保留包内目录，依赖见项目说明。 |
| `nasswitch` — [播放 NAS 里保存的音乐](https://github.com/hlhlhl231/nasswitch/releases) | .zip | 下载 Switch 版压缩包。解压时保留包内目录，依赖见项目说明。 |
| `bolemusic_switch` — [在 Switch 上使用波乐音乐](https://github.com/shellsec/bolemusic/releases) | .nro | 查看项目说明。 |

### 社交与阅读

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `telegramnx` — [在 Switch 上使用 Telegram](https://github.com/CostelaCNX/TelegramNX/releases) | .zip | 下载 Switch 版压缩包。解压时保留包内目录，依赖见项目说明。 |
| `sporegram` — [用另一款 Switch 客户端访问 Telegram](https://github.com/fungalspores/sporegram/releases) | .nro | 下载 Switch 版文件。放置位置和依赖见项目说明。 |
| `qq-for-switch` — [尝试在 Switch 上使用 QQ](https://github.com/shuiwen879867/QQ-for-Switch/releases) | .nro | 下载 Switch 版文件。放置位置和依赖见项目说明。 |
| `koreader-switch` — [在 Switch 上阅读电子书](https://github.com/miikearthur/KOReader-Switch/releases) | .nro | 实验性移植；提供 NRO 不等于已验证实机全部功能，兼容性与启动方式以项目说明为准。 |
| `switch-dit` — [在 Switch 上浏览 Reddit 帖子](https://github.com/mena-works/switch-dit/releases) | .zip | 下载 Switch 版压缩包。解压时保留包内目录，依赖见项目说明。 |

### AI与自动化

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `switch-dsh-client` — [在 Switch 上与 DeepSeek 对话](https://github.com/ArakiW/switch-dsh-client/releases) | .nro | 下载 Switch 版文件。放置位置和依赖见项目说明。 |
| `nxcourier` — [远程控制 Switch 并查看主机状态和截图](https://github.com/granule256/nxcourier) | 页面入口 | 已有 Release 标签但没有附件；需按 README 自行构建或配置电脑端工具。 |
| `claude-code-switch` — [在 Switch 上使用 Claude Code](https://github.com/CommunityPokeOrg/claude-code-switch/releases) | .nro | 下载 Switch 版文件。放置位置和依赖见项目说明。 |
| `chatnx` — [在 Switch 上使用 AI 聊天工具](https://github.com/Jonathan8520/ChatNX/releases) | .nro | 下载 Switch 版文件。放置位置和依赖见项目说明。 |

### 云游戏与远程

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `uuremote-ns` — [用 Switch 连接 UU 远程服务](https://github.com/Antman2023/UURemote-ns/releases/tag/v0.1.6) | .zip；预发布固定 `v0.1.6` | 预发布固定版本；下载 Switch 完整 ZIP，配对和服务要求见 README，后续版本需人工复核 tag。 |
| `opennow-switch` — [在 Switch 上连接 GeForce NOW 玩云游戏](https://github.com/OpenCloudGaming/OpenNOW-Switch/releases) | .zip | 下载 Switch 版压缩包。解压时保留包内目录，依赖见项目说明。 |
| `zerodroid` — [在 Switch 上连接 Boosteroid 玩云游戏](https://github.com/elzerdodata/ZERODROID/releases) | .nro | 下载 Switch 版文件。放置位置和依赖见项目说明。 |
| `halyard` — [用 Switch 连接 Shadow 云电脑](https://github.com/Wasabules/Halyard/releases) | .nro | 下载 Switch 版文件。放置位置和依赖见项目说明。 |
| `nsteamlink` — [把 Steam 游戏从电脑串流到 Switch](https://github.com/kxn/nsteamlink/releases) | .nro | 下载 Switch 版文件。放置位置和依赖见项目说明。 |

### 文件与存档

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `locals-nx` — [用 LocalSend 和同一局域网里的设备互传文件](https://github.com/z3lc/LocalS-NX/releases) | .zip | 下载 Switch 版后，和运行 LocalSend 的手机或电脑连接同一局域网。 |
| `minfs` — [用手机或电脑浏览器访问 Switch 的 SD 卡](https://github.com/minbbb/minFS/releases) | .zip | 下载 Switch 版压缩包。解压时保留包内目录，依赖见项目说明。 |
| `switchsavesync` — [把游戏存档同步到 Google Drive](https://github.com/NspxMiguel/SwitchSaveSync/releases) | .ovl | 发布物为 .ovl 插件，另需 overlay 环境及 Google Drive 授权配置；详见项目说明。 |
| `pkhex-nx` — [在 Switch 上编辑宝可梦存档](https://github.com/cbreezy210/PKHeX-NX/releases/tag/v0.9.5-beta) | .zip；预发布固定 `v0.9.5-beta` | Beta 固定版本，下载包含应用与资源的标准 ZIP；按发布说明用完整内存模式启动，后续版本需人工复核 tag。 |
| `nxshare` — [用浏览器查看和下载 Switch 相册里的截图与视频](https://github.com/musebrot1/NXShare/releases) | .nro | 在 Switch 启动工具后，用手机或电脑打开它显示的地址。 |
| `checkpoint` — [备份或还原 Switch 游戏存档](https://github.com/BernardoGiordano/Checkpoint/releases) | .nro | 下载 Switch 版 Checkpoint.nro。已有存档可以先备份，再进行还原。 |
| `nxdumptool` — [导出自己主机上的游戏卡带或已安装内容](https://github.com/DarkMatterCore/nxdumptool/releases) | .nro | 下载 Switch 版文件。放置位置和依赖见项目说明。 |
| `goldleaf` — [在 Switch 上浏览文件和管理已安装内容](https://github.com/XorTroll/Goldleaf/releases) | .nro | 下载 Switch 版文件。放置位置和依赖见项目说明。 |
| `dbipatcher` — [使用支持外部语言文件的 DBI](https://github.com/rashevskyv/DBIPatcher/releases) | .nro | 配套 dbi-translation-zhcn；必须使用同一发布版本的 DBI.nro 与翻译文件。 |
| `n-xplorer` — [在 Switch 上整理文件并编辑文本](https://github.com/Craftyawesome/N-Xplorer/releases/tag/0.7.1-crash-fix) | .nro；预发布固定 `0.7.1-crash-fix` | 当前仅发现预发布 N-Xplorer.nro，固定到已核查 tag，后续需人工更新。 |
| `dbi-translation-zhcn` — [给兼容版本的 DBI 加上简体中文](https://github.com/rashevskyv/DBIPatcher/releases) | .bin | 将 translation_zhcn.bin 改名为 translation.bin，与本目录 dbipatcher 对应的 DBI.nro 放在同一文件夹。 |

### 游戏移植

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `touhou-switch` — [在 Switch 上运行东方系列移植版](https://github.com/saekaze/touhou-switch) | 页面入口 | 当前未发现公开 Release；查看仓库构建说明，游戏数据需自备。 |
| `sh3-nx` — [在 Switch 上运行《寂静岭 3》移植版](https://github.com/cutarev/sh3-nx/releases) | .nro | 只提供移植程序，游戏数据需按项目说明自行准备。 |
| `zomboid-switch` — [在 Switch 上运行《僵尸毁灭工程》移植版](https://github.com/etonedemid/zomboid-switch) | 页面入口 | 当前未发现公开 Release；查看仓库说明，游戏数据需自备。 |
| `sms-switch` — [在 Switch 上运行《超级马力欧阳光》移植版](https://github.com/chasem-dev/sms-switch/releases/tag/v0.3.0) | .zip；预发布固定 `v0.3.0` | 预发布固定版本，选择 sms-switch.zip；需要自备游戏数据，后续版本需人工复核 tag。 |
| `megamanx-nx` — [在 Switch 上运行《洛克人 X》移植版](https://github.com/Thorhax/MegaManX-NX/releases) | .zip | 优先完整 ZIP；所需游戏资源按项目说明准备。 |
| `ikemen-nx` — [在 Switch 上运行兼容 MUGEN 的格斗引擎](https://github.com/juanp9180-cmyk/ikemen-nx/releases) | .zip | 优先 sd.zip 完整包；不要只取辅助 nxconfig.nro 而遗漏主程序与资源。 |
| `portnx` — [查找 Switch 游戏移植项目](https://github.com/CostelaCNX/PortNX/releases) | .zip | 用于浏览移植项目；各游戏的数据与使用要求以对应项目说明为准。 |
| `switchwaker` — [SwitchWaker（GameCube《风之杖》的 Switch 原生移植）](https://github.com/centollOS/SwitchWaker/releases/latest) | .zip | 需 Atmosphère 和 hbmenu；此条下载美版构建，需自备 GZLE01 revision 0 镜像；欧版附件见作者发布页。 |
| `oracles_project_nx` — [The Oracles Project NX（塞尔达传说 Oracles 移植）](https://github.com/toniisound/the-oracles-project-nx/releases/latest) | .nro | 需支持自制应用的 Switch，自备项目要求的美版 ROM。 |
| `touhou12_switch` — [东方星莲船 Switch 移植（TH12）](https://github.com/saekaze/th12-switch/releases/latest) | .nro | 需支持自制应用的 Switch，自备原版游戏资源。 |
| `openmohaa_nx` — [OpenMoHAA NX（荣誉勋章：联合袭击引擎移植）](https://github.com/NaGaa95/openmohaa_nx/releases/latest) | .nro | 需支持自制应用的 Switch，自备原版游戏数据。 |
| `mega_man_w_switch` — [Mega Man W（Switch 同人平台动作游戏）](https://github.com/Vroccolli/mega-man-w-switch-homebrew/releases/latest) | .zip | 需支持自制应用的 Switch，按发行说明复制到 SD 卡。 |
| `horizon_nx` — [Horizon NX（用 Rust 实现的 Switch 版 Minecraft）](https://github.com/JohnUzoka/horizon-nx/releases/latest) | .zip | 需支持自制应用的 Switch。 |

### 主题与显示

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `nxthemes-installer` — [安装或更换 Switch 的 HOME 菜单主题](https://github.com/exelix11/SwitchThemeInjector/releases) | .nro | 仅下载主机端 NRO，不下载电脑端 NxThemeTool.zip；主题需与当前系统适配。 |
| `fizeau` — [调节屏幕的色温和色彩](https://github.com/averne/Fizeau/releases) | .zip | 下载 Switch 版压缩包。解压时保留包内目录，依赖见项目说明。 |
| `status-monitor-overlay` — [在游戏中查看帧率、温度和硬件状态](https://github.com/masagrator/Status-Monitor-Overlay/releases) | .zip | 悬浮窗需兼容的菜单与 overlay 加载器。 |
| `fpslocker` — [在游戏中调整支持的帧率设置](https://github.com/masagrator/FPSLocker/releases) | .ovl | 悬浮插件需配套环境及游戏设置；操作要求查看项目说明。 |

### 悬浮插件

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `nx-ovlloader-zdm` — [加载 zdm 分支支持的悬浮菜单插件](https://github.com/zdm65477730/nx-ovlloader/releases) | .zip | 汉化分支的 overlay 加载器；按 ZIP 目录放置，与所选菜单及当前系统版本配套。 |
| `ultrahand-zdm` — [用中文悬浮菜单打开插件和运行脚本](https://github.com/zdm65477730/Ultrahand-Overlay/releases) | .zip | 汉化分支完整菜单包；与原版 Tesla/Ultrahand 是替代选择，避免同时覆盖同名菜单文件。 |
| `ovl-sysmodules-zdm` — [在中文悬浮菜单里启用或停用系统模块](https://github.com/zdm65477730/ovl-sysmodules/releases) | .zip | 系统模块开关悬浮插件；需要 overlay 加载器与菜单。 |
| `edizon-overlay-zdm` — [在中文悬浮界面中管理金手指和修改数值](https://github.com/zdm65477730/EdiZon-Overlay/releases) | .zip | 下载 EdiZon.zip 套件；NRO/OVL 以压缩包实际内容为准，不把单独的 overlay 描述成独立 NRO。 |
| `sys-clk-zdm` — [用中文界面调整游戏运行频率](https://github.com/zdm65477730/sys-clk/releases) | .zip | 下载 sys-clk.zip 主机端套件；需要模块与菜单配套，支持频率以设备和项目说明为准。 |
| `status-monitor-zdm` — [在中文悬浮界面中查看帧率和硬件状态](https://github.com/zdm65477730/Status-Monitor-Overlay/releases) | .zip | 下载 StatusMonitor.zip；退出快捷键和资源依赖以所下载分支说明为准。 |

### 引导与维护载荷

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `commonproblemresolver` — [通过 Hekate 启动排查工具，处理常见启动问题](https://github.com/zdm65477730/CommonProblemResolver/releases) | .bin | Hekate 下运行的维护载荷；.bin 放入 SD:/bootloader/payloads/。功能及支持机型查看发布说明。 |
| `lockpick-rcm` — [从自己的 Switch 导出主机密钥](https://github.com/impeeza/Lockpick_RCMDecScots/releases) | .zip | 选择 _Hekate.zip 版本；解压后按包内说明放置载荷，导出文件位置以项目说明为准。 |
| `tegraexplorer-ext` — [在系统启动前浏览文件和运行维护脚本](https://github.com/sthetix/TegraExplorer-Ext/releases) | .zip | Hekate 下运行的文件管理载荷包；保留包内目录结构，额外 TE 脚本按项目说明放置。 |
| `hwfly-toolbox` — [使用 HWFLY 芯片的维护工具](https://github.com/hwfly-nx/hwfly-toolbox/releases) | .bin | HWFLY 工具箱 .bin，放入 bootloader/payloads/；仅用于与项目匹配的芯片，不执行刷写。 |
| `downgradefixer` — [尝试修复系统降级后的启动故障](https://github.com/sthetix/DowngradeFixer/releases) | .zip | Hekate 下运行的故障修复载荷包；具体可修复问题与系统条件查看项目说明，不自动运行。 |
| `warmboot-extractor` — [从兼容的 Mariko 主机提取 Warmboot 组件](https://github.com/sthetix/Warmboot-Extractor/releases) | .zip | Warmboot 提取载荷包；适用机型和提取前提查看 README，不将它视为全机型通用。 |

### 芯片固件

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `hwfly-firmware` — [获取对应 HWFLY 芯片的固件和 SDLoader](https://github.com/hwfly-nx/firmware/releases) | .zip | 完整固件 ZIP；按硬件版本与 README 选择其中的 firmware/SDLoader 文件，下载不会改名或刷写。 |
| `picofly-firmwares` — [查找与 Picofly 芯片型号对应的固件](https://github.com/Ansem-SoD/Picofly/tree/main/Firmwares) | 页面入口 | 固件保存在仓库 Firmwares/，没有稳定 Release；保留目录页面入口，手动选择对应硬件文件。 |
| `picofly-usk` — [获取 Picofly USK 固件更新文件](https://github.com/rehius/usk/releases) | .bin | 下载主机更新用 update.bin；同页 firmware.uf2 是另一分发形式，硬件与升级方式以项目说明为准。 |

### 配套资料与电脑工具

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `ips-patch-creator` — [在电脑上制作 IPS 补丁](https://gbatemp.net/download/ips-patch-creator.39133/) | 页面入口 | 电脑端制作工具页面；不作为 Switch NRO 下载或执行。 |
| `sigpatch-database` — [查找供 Ghidra 分析使用的签名补丁资料](https://github.com/borntohonk/Switch-Ghidra-Guides/tree/master/patch_database) | 页面入口 | 仓库中的补丁数据库目录，手动查阅与选择。 |
| `ns-usbloader` — [从电脑通过 USB 或网络向 Switch 发送文件](https://github.com/developersu/ns-usbloader/releases) | 页面入口 | 电脑端配套 Awoo 等主机应用；在发布页选择本机系统及 Java 版本对应文件，不复制到 Switch 作为 NRO。 |
| `sccm-switch-toolbox` — [在 Windows 上备份、恢复和迁移 Switch SD 卡及 emuMMC](https://github.com/SocalConsoleModding/Switch-Toolbox/releases) | 页面入口 | 在官方发布页下载 SCCM_Switch_Toolbox.exe，在 Windows 电脑上运行。 |

## 后续维护

在 `apps-switch/switch/` 中维护分类 JSON 数组，ID 在 Switch 平台内必须唯一。名称和中文搜索词填入 `aliases`；资源或插件依赖写入 `使用说明`。

下载规则应匹配 Switch 的发布附件，排除电脑端、3DS、Wii U、源码、校验文件和调试包。有完整 SD 布局包时优先完整包，避免遗漏资源；禁止只凭扩展名选多平台附件。

预发布项目通过 `pinned_release_tag` 固定到已核查版本，后续需人工复核并更新标签。普通条目仍动态解析最新稳定 Release。

页面入口说明具体原因：无公开 Release、Release 无附件、官方外部分发或商店分发。确认新包后再补规则，不把源码包当作主机程序。

更新分片与核查快照后运行 `python tools/generate_switch_catalog_index.py` 刷新本页。
