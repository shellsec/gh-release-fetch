# Switch 独立清单

> 自动生成：`python tools/generate_switch_catalog_index.py`；修改 JSON 分片后重新生成。

与电脑端 `apps/`、移动端 `apps-mobile/` 分开维护。仅下载，不安装、不解压、不刷写。

共 **110 条**：**98 条可下载**、**12 条页面入口**。其中 5 条为固定 tag 的预发布版本。

逐项对照你提供的整合包组件，见 [组件对照表](apps-switch/COMPONENTS.md)。

## 使用入口

运行 `python lookup_app.py`，选择 **4：Switch**；也可直接搜索：

```bat
lookup_switch.bat 大气层
lookup_switch.bat 存档
lookup_switch.bat 投屏
python auto_update.py --apps-dir apps-switch --platform switch atmosphere-stable nx-firmware
python tools/run_saved_apps.py switch --apps-dir apps-switch
```

搜索后可下载、加入更新列表或打开项目页。条目默认关闭；显式指定 ID 可直接下载，启用后可批量更新。保存列表为 `saved_apps_switch.json`。

附件保留原文件名，保存到 `switch/<id>/`。NRO、OVL、NSP、BIN 载荷与固件压缩包都只下载，安装和复制到 SD 卡需按项目说明进行。

Windows 可直接打开根目录 lookup_app.exe，选择 4：Switch；相关 EXE 已同步重打包。BAT 在 Python 依赖齐全且源码存在时使用源码，否则使用 EXE。Switch 搜索目前以本地清单为准，未命中时通用 GitHub 补搜不支持 Switch 附件筛选。

## 分类概览

| 分类 | 条目数 |
|---|---|
| 系统基础 | 10 |
| 日常工具 | 26 |
| 在线视频 | 12 |
| 本地与家庭影音 | 3 |
| 游戏与串流 | 3 |
| 音乐 | 2 |
| 社交与阅读 | 5 |
| AI与自动化 | 4 |
| 云游戏与远程 | 5 |
| 文件与存档 | 11 |
| 游戏移植 | 7 |
| 主题与显示 | 4 |
| 悬浮插件 | 6 |
| 引导与维护载荷 | 6 |
| 芯片固件 | 3 |
| 配套资料与电脑工具 | 3 |

## 清单与下载规则

“可下载”表示已匹配公开发布附件，不表示已经过实机测试。核查日期、标签与文件名快照见 [release-check.json](apps-switch/release-check.json)。发布时间较早也不直接等于停更，兼容性需查看各项目说明。

### 系统基础

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `atmosphere-stable` — [Atmosphere 大气层稳定整合包](https://github.com/rumla3434/Atmosphere-stable/releases) | .7z | 整合包与官方 Atmosphere 本体是不同选择；保留整合包原目录结构。 |
| `nx-firmware` — [Switch 系统离线升级固件](https://github.com/rumla3434/NX_Firmware/releases) | .rar | 仅提供离线固件下载；刷写与下载分开，兼容性查看发布说明。 |
| `atmosphere` — [Atmosphere 自定义固件](https://github.com/Atmosphere-NX/Atmosphere/releases) | .zip | 压缩包不含单独发布的 fusee.bin；使用 fusee 启动时需从同一发布页另取对应载荷。Daybreak 随 Atmosphere 提供。 |
| `hekate` — [Hekate 引导、NAND 备份与 emuMMC](https://github.com/CTCaer/hekate/releases) | .zip | 选择含 Nyx 的完整 ZIP；保留 bootloader 目录，备份和 emuMMC 操作需在设备端进行。 |
| `nx-hbmenu` — [自制程序菜单](https://github.com/switchbrew/nx-hbmenu/releases) | .zip | Atmosphere 整合环境通常已包含 hbmenu，无需重复覆盖。 |
| `hekate-easyworld` — [Hekate easyworld 汉化版](https://github.com/easyworld/hekate/releases) | .zip | 默认下载简体中文 _sc.zip 完整包；繁体 _tc.zip 在同一发布页。汉化与官方原版是替代选择，使用前核对 Nyx/Hekate 版本。 |
| `hekate-zdm` — [Hekate zdm 汉化版](https://github.com/zdm65477730/hekate/releases) | .bin | 独立 nyx.bin 汉化文件，手动放到 SD:/bootloader/sys/。本次 latest 标签为 v6.5.3-CN，不能据此认定兼容 Hekate 6.5.4。 |
| `sys-patch` — [sys-patch 系统模块](https://github.com/impeeza/sys-patch/releases) | .zip | 系统模块套件；按压缩包实际目录部署。与 IPS 签名补丁是不同方案，兼容性查看对应发布说明。 |
| `sigpatch-scripts` — [签名补丁制作脚本与补丁数据库](https://github.com/borntohonk/Switch-Ghidra-Guides/blob/master/scripts/make_patches.py) | 页面入口 | 电脑端 Python 制作脚本入口，需自行准备运行环境；此条只打开脚本，不自动执行。 |
| `sigpatch-downloads` — [Sigpatch 签名补丁发布讨论](https://gbatemp.net/threads/sigpatches-for-atmosphere-hekate-fss0-fusee-package3.571543/) | 页面入口 | 论坛附件手动下载；按帖内说明核对系统与 Atmosphere 版本。 |

### 日常工具

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `jksv` — [存档备份和还原](https://github.com/J-D-K/JKSV/releases) | .nro | 仅下载主机端文件；放置路径、资源依赖及启动方式见项目说明。 |
| `sys-clk` — [频率调节](https://github.com/retronx-team/sys-clk/releases) | .zip | 完整保留压缩包中的 SD 卡目录布局，具体依赖与启动方式见项目说明。 |
| `missioncontrol` — [第三方手柄连接](https://github.com/ndeadly/MissionControl/releases) | .zip | 完整保留压缩包中的 SD 卡目录布局，具体依赖与启动方式见项目说明。 |
| `ftpd` — [FTP 无线传文件](https://github.com/mtheall/ftpd/releases) | .nro | 仅下载主机端文件；放置路径、资源依赖及启动方式见项目说明。 |
| `tesla-menu` — [游戏内悬浮菜单（配合 nx-ovlloader）](https://github.com/WerWolv/Tesla-Menu/releases) | .zip | 原版 Tesla 菜单，配合 nx-ovlloader；与 Ultrahand 同属菜单方案，安装前按各项目说明选择。 |
| `nx-ovlloader` — [悬浮菜单加载器（配合 Tesla-Menu）](https://github.com/WerWolv/nx-ovlloader/releases) | .zip | 悬浮插件加载器；菜单与插件的系统兼容性以对应项目说明为准。 |
| `nx-shell` — [文件管理器](https://github.com/joel16/NX-Shell/releases) | .nro | 仅下载主机端文件；放置路径、资源依赖及启动方式见项目说明。 |
| `edizon` — [存档编辑与金手指工具](https://github.com/WerWolv/EdiZon/releases) | .nro | 仅下载主机端文件；放置路径、资源依赖及启动方式见项目说明。 |
| `homeguard` — [HOME 键控制工具](https://github.com/Aster145/HomeGuard/releases/tag/v0.1.1) | .zip；预发布固定 `v0.1.1` | 预发布固定版本；先阅读 README 的启动与限制说明，后续版本需人工复核 tag。 |
| `dbi` — [DBI 文件管理与 USB/MTP 工具](https://github.com/rashevskyv/dbi/releases) | .nro | 只下载主机端 DBI.nro；dbi.config 及电脑端后端程序可从同一发布页按需获取。 |
| `hb-appstore` — [Homebrew App Store 自制应用商店](https://github.com/fortheusers/hb-appstore/releases) | .zip | 下载 switch-extracttosd.zip，包含完整资源；不下载 Wii U 文件。 |
| `aio-switch-updater` — [AIO Switch Updater 系统组件更新工具](https://github.com/HamletDuFromage/aio-switch-updater/releases) | .zip | 完整保留压缩包中的 SD 卡目录布局，具体依赖与启动方式见项目说明。 |
| `ultrahand-overlay` — [Ultrahand 悬浮菜单与脚本工具](https://github.com/ppkantorski/Ultrahand-Overlay/releases) | .zip | 选择 sdout.zip 完整 SD 布局包；依赖与放置方式见项目说明，勿只复制 ovlmenu.ovl 而漏掉资源。 |
| `emuiibo` — [emuiibo 虚拟 amiibo 系统模块](https://github.com/XorTroll/emuiibo/releases) | .zip | ZIP 为 Switch 系统模块；桌面端 emuiigen.jar 不属于本条下载内容。 |
| `sys-con` — [sys-con USB 有线手柄支持模块](https://github.com/cathery/sys-con/releases) | .zip | 旧版 USB 手柄模块；使用前核对当前系统与 Atmosphere 兼容性，不代表支持所有手柄。 |
| `fastcfwswitch` — [fastCFWswitch 启动载荷切换悬浮插件](https://github.com/Hartie95/fastCFWswitch/releases) | .zip | 悬浮插件，需要配置目标 payload 路径。 |
| `awoo-installer` — [Awoo Installer 主机端安装工具](https://github.com/Huntereb/Awoo-Installer/releases) | .zip | 主机端 ZIP；电脑端配套工具见 ns-usbloader，不将电脑程序复制为 NRO。 |
| `ascent-toolbox` — [Ascent Toolbox 系统模块管理](https://github.com/exploitz86/Ascent-Toolbox/releases) | .nro | Ascent Toolbox，与 DeepSea 分支分开收录；按对应项目确认设备和重启支持。 |
| `deepsea-toolbox` — [DeepSea Toolbox 深海工具箱](https://github.com/Team-Neptune/DeepSea-Toolbox/releases) | .nro | 原 DeepSea 分支；实际发布文件名为 DeepSeaToolbox.nro，不与 Ascent 版本混写。 |
| `edizon-se` — [EdiZon SE 存档与金手指工具](https://github.com/tomvita/EdiZon-SE/releases) | .zip | 选择 edizon.zip 标准包；同页 EdiZon_alt.zip 是另一版本，使用差异以项目说明为准。 |
| `linkalho` — [Linkalho 离线账号关联工具](https://github.com/impeeza/linkalho/releases) | .zip | 离线账号关联工具；功能与当前系统支持范围查看项目说明。 |
| `nx-activity-log-zdm` — [游戏游玩时间记录汉化版](https://github.com/zdm65477730/NX-Activity-Log/releases) | .nro | 游玩时间记录工具汉化分支；主机端 NRO。 |
| `sphaira` — [Sphaira 自制菜单与文件管理](https://github.com/ITotalJustice/sphaira/releases) | .zip | 完整 ZIP；按 README 确认替换 hbmenu.nro 的方式与功能，保留所需资源。 |
| `switch-time` — [Switch Time 网络校时工具](https://github.com/3096/switch-time/releases) | .nro | 网络校时 NRO；联网条件与系统设置要求查看 README。 |
| `tencent-switcher-gui` — [Tencent Switcher GUI 系统区域切换](https://github.com/CaiMiao/Tencent-switcher-GUI/releases) | .nro | 系统区域切换工具；本次 latest 标签为 0.1.1，未将用户参考 0.1.2 写成已核实版本。 |
| `tinwoo` — [TinWoo 主机端安装工具](https://github.com/mrdude2478/Tinwoo-Release/releases) | .zip | 主机端完整 ZIP；使用方式与前端要求查看发布说明。 |

### 在线视频

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `wiliwili` — [B 站客户端](https://github.com/xfangfang/wiliwili/releases) | .zip | 完整保留压缩包中的 SD 卡目录布局，具体依赖与启动方式见项目说明。 |
| `switch-newpipe` — [YouTube 客户端](https://github.com/mirusu400/switch-newpipe/releases) | .nro | 仅下载主机端文件；放置路径、资源依赖及启动方式见项目说明。 |
| `switch-hongguo` — [红果短剧客户端](https://github.com/ZYP-INre/switch-hongguo/releases) | .nro | 仅下载主机端文件；放置路径、资源依赖及启动方式见项目说明。 |
| `switchtvbox` — [影视客户端](https://github.com/lGuann/SwitchTVBox/releases) | .zip | 完整保留压缩包中的 SD 卡目录布局，具体依赖与启动方式见项目说明。 |
| `tikzen` — [视频客户端](https://github.com/lGuann/Tikzen/releases) | .zip | 完整保留压缩包中的 SD 卡目录布局，具体依赖与启动方式见项目说明。 |
| `hongguo-switch` — [红果短剧客户端](https://github.com/dongrez1990-cloud/hongguo-switch/releases) | .nsp | 仅下载主机端文件；放置路径、资源依赖及启动方式见项目说明。 |
| `streamfin` — [流媒体客户端](https://github.com/scamNscoot/StreamFin/releases) | .nro | 仅下载主机端文件；放置路径、资源依赖及启动方式见项目说明。 |
| `stremnx` — [流媒体客户端](https://github.com/denpingus/StremNX/releases) | .nro | 仅下载主机端文件；放置路径、资源依赖及启动方式见项目说明。 |
| `twinx` — [Twitch 直播客户端](https://github.com/DomazinUS/twiNX/releases) | .zip | 完整保留压缩包中的 SD 卡目录布局，具体依赖与启动方式见项目说明。 |
| `ytb-player` — [YouTube 客户端](https://github.com/murat303/ytb-player/releases) | .nro | 仅下载主机端文件；放置路径、资源依赖及启动方式见项目说明。 |
| `nxtube` — [NxTube：YouTube App 补丁介绍](https://www.gamebrew.org/wiki/NxTube_Switch) | 页面入口 | 仅提供补丁介绍页面；补丁版本与官方 YouTube App 的兼容性以项目说明为准。 |
| `youtube-switch` — [YouTube 官方 Switch App](https://www.nintendo.com/us/store/products/youtube-switch/) | 页面入口 | 官方商店分发，不是 GitHub Release；安装要求以任天堂商店说明为准。 |

### 本地与家庭影音

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `switchfin` — [Jellyfin / Emby 客户端](https://github.com/dragonflylee/switchfin/releases) | .nro | 仅下载主机端文件；放置路径、资源依赖及启动方式见项目说明。 |
| `nxmp` — [本地及网络视频播放器](https://github.com/proconsule/nxmp/releases) | .zip | 完整保留压缩包中的 SD 卡目录布局，具体依赖与启动方式见项目说明。 |
| `nx-cast` — [DLNA / AirPlay 投屏与 IPTV](https://github.com/Ode1l/NX-Cast/releases) | .zip | 使用 NX-Cast-sdmc.zip，保留目录结构复制到 SD 根目录；hbmenu 启动，手机和 Switch 连同一局域网，具体投屏能力以 README 为准。 |

### 游戏与串流

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `retroarch` — [模拟器前端](https://www.retroarch.com/?page=platforms) | 页面入口 | 该 GitHub 最新 Release 只有源码包；Switch 构建从官方平台下载页获取。 |
| `moonlight-switch` — [电脑游戏和画面串流](https://github.com/XITRIX/Moonlight-Switch/releases) | .nro | 仅下载主机端文件；放置路径、资源依赖及启动方式见项目说明。 |
| `corkdeck` — [实验性 Windows 游戏运行项目](https://github.com/plv890/CorkDeck/releases) | .zip | 实验性 Windows 游戏运行环境；所需游戏数据需自行准备，兼容性以项目说明为准。 |

### 音乐

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `switify` — [Spotify 客户端](https://github.com/DomazinUS/Switify/releases) | .zip | 完整保留压缩包中的 SD 卡目录布局，具体依赖与启动方式见项目说明。 |
| `nasswitch` — [NAS 音乐播放](https://github.com/hlhlhl231/nasswitch/releases) | .zip | 完整保留压缩包中的 SD 卡目录布局，具体依赖与启动方式见项目说明。 |

### 社交与阅读

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `telegramnx` — [Telegram 客户端](https://github.com/CostelaCNX/TelegramNX/releases) | .zip | 完整保留压缩包中的 SD 卡目录布局，具体依赖与启动方式见项目说明。 |
| `sporegram` — [Telegram 客户端](https://github.com/fungalspores/sporegram/releases) | .nro | 仅下载主机端文件；放置路径、资源依赖及启动方式见项目说明。 |
| `qq-for-switch` — [实验性 QQ 客户端](https://github.com/shuiwen879867/QQ-for-Switch/releases) | .nro | 仅下载主机端文件；放置路径、资源依赖及启动方式见项目说明。 |
| `koreader-switch` — [实验性电子书阅读器移植](https://github.com/miikearthur/KOReader-Switch/releases) | .nro | 实验性移植；提供 NRO 不等于已验证实机全部功能，兼容性与启动方式以项目说明为准。 |
| `switch-dit` — [Reddit 客户端](https://github.com/mena-works/switch-dit/releases) | .zip | 完整保留压缩包中的 SD 卡目录布局，具体依赖与启动方式见项目说明。 |

### AI与自动化

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `switch-dsh-client` — [DeepSeek AI 聊天](https://github.com/ArakiW/switch-dsh-client/releases) | .nro | 仅下载主机端文件；放置路径、资源依赖及启动方式见项目说明。 |
| `nxcourier` — [局域网控制、状态读取与截图](https://github.com/granule256/nxcourier) | 页面入口 | 已有 Release 标签但没有附件；需按 README 自行构建或配置电脑端工具。 |
| `claude-code-switch` — [AI 聊天客户端](https://github.com/CommunityPokeOrg/claude-code-switch/releases) | .nro | 仅下载主机端文件；放置路径、资源依赖及启动方式见项目说明。 |
| `chatnx` — [AI 聊天客户端](https://github.com/Jonathan8520/ChatNX/releases) | .nro | 仅下载主机端文件；放置路径、资源依赖及启动方式见项目说明。 |

### 云游戏与远程

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `uuremote-ns` — [UU 远程客户端](https://github.com/Antman2023/UURemote-ns/releases/tag/v0.1.6) | .zip；预发布固定 `v0.1.6` | 预发布固定版本；下载 Switch 完整 ZIP，配对和服务要求见 README，后续版本需人工复核 tag。 |
| `opennow-switch` — [GeForce NOW 云游戏客户端](https://github.com/OpenCloudGaming/OpenNOW-Switch/releases) | .zip | 完整保留压缩包中的 SD 卡目录布局，具体依赖与启动方式见项目说明。 |
| `zerodroid` — [Boosteroid 云游戏客户端](https://github.com/elzerdodata/ZERODROID/releases) | .nro | 仅下载主机端文件；放置路径、资源依赖及启动方式见项目说明。 |
| `halyard` — [Shadow 云电脑客户端](https://github.com/Wasabules/Halyard/releases) | .nro | 仅下载主机端文件；放置路径、资源依赖及启动方式见项目说明。 |
| `nsteamlink` — [Steam 远程串流](https://github.com/kxn/nsteamlink/releases) | .nro | 仅下载主机端文件；放置路径、资源依赖及启动方式见项目说明。 |

### 文件与存档

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `locals-nx` — [LocalSend 无线传文件](https://github.com/z3lc/LocalS-NX/releases) | .zip | 完整保留压缩包中的 SD 卡目录布局，具体依赖与启动方式见项目说明。 |
| `minfs` — [通过浏览器管理 SD 卡](https://github.com/minbbb/minFS/releases) | .zip | 完整保留压缩包中的 SD 卡目录布局，具体依赖与启动方式见项目说明。 |
| `switchsavesync` — [存档同步到 Google Drive](https://github.com/NspxMiguel/SwitchSaveSync/releases) | .ovl | 发布物为 .ovl 插件，另需 overlay 环境及 Google Drive 授权配置；详见项目说明。 |
| `pkhex-nx` — [宝可梦存档编辑](https://github.com/cbreezy210/PKHeX-NX/releases/tag/v0.9.5-beta) | .zip；预发布固定 `v0.9.5-beta` | Beta 固定版本，下载包含应用与资源的标准 ZIP；按发布说明用完整内存模式启动，后续版本需人工复核 tag。 |
| `nxshare` — [通过网页浏览及下载相册截图和视频](https://github.com/musebrot1/NXShare/releases) | .nro | 仅下载主机端文件；放置路径、资源依赖及启动方式见项目说明。 |
| `checkpoint` — [Checkpoint 存档备份与还原](https://github.com/BernardoGiordano/Checkpoint/releases) | .nro | 只选择 Switch 的 Checkpoint.nro，排除 3DS 文件与调试 ELF。 |
| `nxdumptool` — [NXDumpTool 自有游戏与内容导出](https://github.com/DarkMatterCore/nxdumptool/releases) | .nro | 仅下载主机端文件；放置路径、资源依赖及启动方式见项目说明。 |
| `goldleaf` — [Goldleaf 文件与内容管理](https://github.com/XorTroll/Goldleaf/releases) | .nro | 仅下载主机端文件；放置路径、资源依赖及启动方式见项目说明。 |
| `dbipatcher` — [DBI 补丁与翻译发行包](https://github.com/rashevskyv/DBIPatcher/releases) | .nro | 配套 dbi-translation-zhcn；必须使用同一发布版本的 DBI.nro 与翻译文件。 |
| `n-xplorer` — [N-Xplorer 文本编辑与文件管理](https://github.com/Craftyawesome/N-Xplorer/releases/tag/0.7.1-crash-fix) | .nro；预发布固定 `0.7.1-crash-fix` | 当前仅发现预发布 N-Xplorer.nro，固定到已核查 tag，后续需人工更新。 |
| `dbi-translation-zhcn` — [DBI 简体中文翻译文件](https://github.com/rashevskyv/DBIPatcher/releases) | .bin | 下载 translation_zhcn.bin，手动重命名为 translation.bin，与本清单 dbipatcher 的同一发布版本 DBI.nro 放入同一个 SD 卡文件夹；不要混用其他版本的 DBI。 |

### 游戏移植

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `touhou-switch` — [东方系列移植（自备游戏文件）](https://github.com/saekaze/touhou-switch) | 页面入口 | 当前未发现公开 Release；查看仓库构建说明，游戏数据需自备。 |
| `sh3-nx` — [寂静岭 3 移植（自备游戏文件）](https://github.com/cutarev/sh3-nx/releases) | .nro | 只提供移植程序，游戏数据需按项目说明自行准备。 |
| `zomboid-switch` — [僵尸毁灭工程移植（自备游戏文件）](https://github.com/etonedemid/zomboid-switch) | 页面入口 | 当前未发现公开 Release；查看仓库说明，游戏数据需自备。 |
| `sms-switch` — [超级马里奥阳光移植（自备游戏文件）](https://github.com/chasem-dev/sms-switch/releases/tag/v0.3.0) | .zip；预发布固定 `v0.3.0` | 预发布固定版本，选择 sms-switch.zip；需要自备游戏数据，后续版本需人工复核 tag。 |
| `megamanx-nx` — [洛克人 X 移植（自备游戏文件）](https://github.com/Thorhax/MegaManX-NX/releases) | .zip | 优先完整 ZIP；所需游戏资源按项目说明准备。 |
| `ikemen-nx` — [兼容 MUGEN 的格斗游戏引擎](https://github.com/juanp9180-cmyk/ikemen-nx/releases) | .zip | 优先 sd.zip 完整包；不要只取辅助 nxconfig.nro 而遗漏主程序与资源。 |
| `portnx` — [游戏移植项目浏览工具](https://github.com/CostelaCNX/PortNX/releases) | .zip | 用于浏览移植项目；各游戏的数据与使用要求以对应项目说明为准。 |

### 主题与显示

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `nxthemes-installer` — [NXThemes Installer Switch 主题安装器](https://github.com/exelix11/SwitchThemeInjector/releases) | .nro | 仅下载主机端 NRO，不下载电脑端 NxThemeTool.zip；主题需与当前系统适配。 |
| `fizeau` — [Fizeau 屏幕色温与色彩调节](https://github.com/averne/Fizeau/releases) | .zip | 完整保留压缩包中的 SD 卡目录布局，具体依赖与启动方式见项目说明。 |
| `status-monitor-overlay` — [Status Monitor 性能与硬件状态悬浮窗](https://github.com/masagrator/Status-Monitor-Overlay/releases) | .zip | 悬浮窗需兼容的菜单与 overlay 加载器。 |
| `fpslocker` — [FPSLocker 帧率控制悬浮插件](https://github.com/masagrator/FPSLocker/releases) | .ovl | 悬浮插件需配套环境及游戏设置；操作要求查看项目说明。 |

### 悬浮插件

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `nx-ovlloader-zdm` — [nx-ovlloader 汉化分支](https://github.com/zdm65477730/nx-ovlloader/releases) | .zip | 汉化分支的 overlay 加载器；按 ZIP 目录放置，与所选菜单及当前系统版本配套。 |
| `ultrahand-zdm` — [Ultrahand 汉化菜单](https://github.com/zdm65477730/Ultrahand-Overlay/releases) | .zip | 汉化分支完整菜单包；与原版 Tesla/Ultrahand 是替代选择，避免同时覆盖同名菜单文件。 |
| `ovl-sysmodules-zdm` — [系统模块管理悬浮插件](https://github.com/zdm65477730/ovl-sysmodules/releases) | .zip | 系统模块开关悬浮插件；需要 overlay 加载器与菜单。 |
| `edizon-overlay-zdm` — [EdiZon 汉化金手指悬浮插件](https://github.com/zdm65477730/EdiZon-Overlay/releases) | .zip | 下载 EdiZon.zip 套件；NRO/OVL 以压缩包实际内容为准，不把单独的 overlay 描述成独立 NRO。 |
| `sys-clk-zdm` — [sys-clk 汉化超频套件](https://github.com/zdm65477730/sys-clk/releases) | .zip | 下载 sys-clk.zip 主机端套件；需要模块与菜单配套，支持频率以设备和项目说明为准。 |
| `status-monitor-zdm` — [Status Monitor 汉化监控悬浮插件](https://github.com/zdm65477730/Status-Monitor-Overlay/releases) | .zip | 下载 StatusMonitor.zip；退出快捷键和资源依赖以所下载分支说明为准。 |

### 引导与维护载荷

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `commonproblemresolver` — [主题与插件启动故障排查载荷](https://github.com/zdm65477730/CommonProblemResolver/releases) | .bin | Hekate 下运行的维护载荷；.bin 放入 SD:/bootloader/payloads/。功能及支持机型查看发布说明。 |
| `lockpick-rcm` — [Lockpick RCM 主机密钥导出载荷](https://github.com/impeeza/Lockpick_RCMDecScots/releases) | .zip | 选择 _Hekate.zip 版本；解压后按包内说明放置载荷，导出文件位置以项目说明为准。 |
| `tegraexplorer-ext` — [TegraExplorer Ext 文件管理载荷](https://github.com/sthetix/TegraExplorer-Ext/releases) | .zip | Hekate 下运行的文件管理载荷包；保留包内目录结构，额外 TE 脚本按项目说明放置。 |
| `hwfly-toolbox` — [HWFLY 工具箱载荷](https://github.com/hwfly-nx/hwfly-toolbox/releases) | .bin | HWFLY 工具箱 .bin，放入 bootloader/payloads/；仅用于与项目匹配的芯片，不执行刷写。 |
| `downgradefixer` — [系统降级故障修复载荷](https://github.com/sthetix/DowngradeFixer/releases) | .zip | Hekate 下运行的故障修复载荷包；具体可修复问题与系统条件查看项目说明，不自动运行。 |
| `warmboot-extractor` — [Mariko Warmboot 补丁提取载荷](https://github.com/sthetix/Warmboot-Extractor/releases) | .zip | Warmboot 提取载荷包；适用机型和提取前提查看 README，不将它视为全机型通用。 |

### 芯片固件

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `hwfly-firmware` — [HWFLY 固件与 SDLoader](https://github.com/hwfly-nx/firmware/releases) | .zip | 完整固件 ZIP；按硬件版本与 README 选择其中的 firmware/SDLoader 文件，下载不会改名或刷写。 |
| `picofly-firmwares` — [Picofly 固件与工具箱](https://github.com/Ansem-SoD/Picofly/tree/main/Firmwares) | 页面入口 | 固件保存在仓库 Firmwares/，没有稳定 Release；保留目录页面入口，手动选择对应硬件文件。 |
| `picofly-usk` — [Picofly USK 固件项目](https://github.com/rehius/usk/releases) | .bin | 下载主机更新用 update.bin；同页 firmware.uf2 是另一分发形式，硬件与升级方式以项目说明为准。 |

### 配套资料与电脑工具

| ID / 项目 | 下载内容 | 使用说明 |
|---|---|---|
| `ips-patch-creator` — [IPS Patch Creator 补丁制作工具](https://gbatemp.net/download/ips-patch-creator.39133/) | 页面入口 | 电脑端制作工具页面；不作为 Switch NRO 下载或执行。 |
| `sigpatch-database` — [Switch Ghidra 签名补丁数据库](https://github.com/borntohonk/Switch-Ghidra-Guides/tree/master/patch_database) | 页面入口 | 仓库中的补丁数据库目录，手动查阅与选择。 |
| `ns-usbloader` — [NS-USBloader 电脑端传输工具](https://github.com/developersu/ns-usbloader/releases) | 页面入口 | 电脑端配套 Awoo 等主机应用；在发布页选择本机系统及 Java 版本对应文件，不复制到 Switch 作为 NRO。 |

## 后续维护

在 `apps-switch/switch/` 中维护分类 JSON 数组，ID 在 Switch 平台内必须唯一。名称和中文搜索词填入 `aliases`；资源或插件依赖写入 `使用说明`。

下载规则应匹配 Switch 的发布附件，排除电脑端、3DS、Wii U、源码、校验文件和调试包。有完整 SD 布局包时优先完整包，避免遗漏资源；禁止只凭扩展名选多平台附件。

预发布项目通过 `pinned_release_tag` 固定到已核查版本，后续需人工复核并更新标签。普通条目仍动态解析最新稳定 Release。

页面入口说明具体原因：无公开 Release、Release 无附件、官方外部分发或商店分发。确认新包后再补规则，不把源码包当作主机程序。

更新分片与核查快照后运行 `python tools/generate_switch_catalog_index.py` 刷新本页。
