# PS5 独立清单

> 自动生成：`python tools/generate_ps5_catalog_index.py`。

共 **137 项**：**128 项有已核查下载附件**，**9 项为页面入口**。仅登记名称的 12 个项目未计入应用清单。

## 搜索与下载

运行 `python lookup_app.py`，选择 **PS5**，再输入关键词、选择结果和操作；也可直接运行 `lookup_ps5.bat`。

```bat
lookup_ps5.bat 模拟器
lookup_ps5.bat PS2
lookup_ps5.bat 播放器
lookup_ps5.bat FTP
python auto_update.py --apps-dir apps-ps5 --platform ps5 ftpsrv
python tools/run_saved_apps.py ps5 --apps-dir apps-ps5
```

下载保留原文件名，保存到 `ps5/<id>/`。默认条目关闭；可以显式指定 ID 下载，或在搜索结果中加入 `saved_apps_ps5.json` 更新列表。仅下载，不安装、不解压、不发送载荷。

Windows 可直接打开根目录 lookup_app.exe 选择 PS5；搜索、下载和保存列表 EXE 已同步重打包。BAT 在 Python 依赖齐全且源码存在时使用源码，否则使用 EXE。本地未命中时通用 GitHub 补搜尚不支持 PS5 附件筛选。

## 运行方式与版本

浏览器入口、HEN 环境、ELF 服务、websrv 应用、原生标题和电脑端 SDK 是不同内容。各条目的固件范围、权限、启动器、额外资源需分别查看作者说明；入口支持某版本，不表示本清单全部软件都支持该版本。本次未在 PS5 实机运行。

基础工具通常跟随作者最新稳定 Release；原生应用和需要配套的 websrv 包固定到核查标签，避免目录记录与实际附件不一致。带 beta/alpha/preview 的版本保持作者标记，不改称稳定版。

社区应用由 [PS5 Homebrew Catalog](https://github.com/darkxex/ps5-homebrew-catalog) 发现，下载仍来自各作者的 GitHub Release。已逐项核对附件名；源码包、已缺失附件保留页面入口。目录提供的 SHA256 仅作上游记录，本工具当前没有以实际下载字节验证这些摘要。

原生 RetroArch、websrv 的 RetroArch 前端/核心、websrv 内置 RetroArch 包属于不同分发，不要将其解压布局混用。模拟器的 BIOS、游戏数据、部分运行库由用户按作者说明准备。

## 分类概览

| 分类 | 项目数 |
|---|---|
| 系统环境 | 4 |
| 载荷与网络服务 | 3 |
| 文件与存档 | 2 |
| 开发与Linux | 4 |
| 补充模拟器与应用 | 4 |
| 商店客户端 | 2 |
| 模拟器 | 15 |
| 影音与直播 | 15 |
| 音乐 | 6 |
| 串流与云游戏 | 6 |
| 工具与个性化 | 11 |
| AI | 3 |
| 游戏移植 | 30 |
| 自制游戏 | 1 |
| 测试工具 | 5 |
| websrv模拟器 | 10 |
| websrv游戏移植 | 9 |
| websrv应用 | 7 |

## 相同 Title ID 的不同项目

以下条目报告了相同 Title ID，不能据此认为可以同时安装；请核对作者说明。

| Title ID | 条目 |
|---|---|
| PPSA99058 | overdrive, overdrive-community |
| PPSA99350 | ytps5, native-ppsa99350 |

## 系统环境

| ID / 项目 | 运行方式 / 下载 | 说明 |
|---|---|---|
| `relapse-exploit` — [Relapse PS5 入口项目](https://github.com/ntfargo/Relapse-Exploit) | 浏览器入口/源码；页面入口 | 浏览器入口/自托管源码，保留项目页面；不把整个源码仓库当作主机安装包。 固件：项目 README 列出 7.00–13.60；其范围不等于各载荷与应用的范围。 |
| `etahen` — [etaHEN 官方自制运行环境](https://github.com/etaHEN/etaHEN/releases) | ELF/载荷；.bin | 官方分发；不能把第三方新版分支的支持范围套用于本条。 固件：按项目 README 与当前发布说明核对。 |
| `etahen-community-11-13` — [etaHEN 11.00–13.60 第三方移植](https://github.com/GronedWaffel/etahen-11.00-13.60/releases) | ELF/载荷；.elf | 非官方分支，与官方 etaHEN 分开维护；需要匹配的入口和 ELF 加载环境，稳定性查看发布说明。 固件：作者标示 11.00–13.60；具体依赖与硬件测试范围以分支 README 为准。 |
| `onionhen` — [OnionHEN 社区运行环境](https://github.com/aydencharles/onionHEN/releases) | ELF/载荷；.elf | 与 etaHEN 为不同环境选择，不自动同时加载。 固件：按项目 README 与当前发布说明核对。 |

## 载荷与网络服务

| ID / 项目 | 运行方式 / 下载 | 说明 |
|---|---|---|
| `elfldr` — [ELF Loader PS5 载荷加载器](https://github.com/ps5-payload-dev/elfldr/releases) | ELF/载荷；.elf | 选择 PS5 ELF 加载器，供其他载荷使用。 固件：按项目 README 与当前发布说明核对。 |
| `ftpsrv` — [PS5 FTP 文件传输服务](https://github.com/ps5-payload-dev/ftpsrv/releases) | ELF/载荷；.elf | 选择常规 ftpsrv-ps5.elf；同页 PS4 与 install 变体不混用。 固件：按项目 README 与当前发布说明核对。 |
| `websrv` — [PS5 网页服务与 Homebrew Launcher](https://github.com/ps5-payload-dev/websrv/releases) | ELF/载荷；.elf | websrv ZIP 应用需要此类环境；不要将 websrv 包、原生标题和 PS4 PKG 视为同一种包。 固件：按项目 README 与当前发布说明核对。 |

## 文件与存档

| ID / 项目 | 运行方式 / 下载 | 说明 |
|---|---|---|
| `itemzflow` — [Itemzflow 应用管理](https://github.com/LightningMods/Itemzflow) | 应用/外部分发；页面入口 | 本次最新 Release 未提供附件；仓库包含 PS4/PS5 相关内容，保留作者页面并按其说明选择 PS5 分发。 固件：按项目 README 与当前发布说明核对。 |
| `apollo-ps5` — [Apollo PS5 存档工具项目](https://github.com/bucanero/apollo-ps5) | 源码项目；页面入口 | 本次未发现稳定 Release；保留源码页面，不表示已经提供可安装 PS5 包。 固件：按项目 README 与当前发布说明核对。 |

## 开发与Linux

| ID / 项目 | 运行方式 / 下载 | 说明 |
|---|---|---|
| `ps5-payload-sdk` — [PS5 Payload SDK 电脑端开发工具](https://github.com/ps5-payload-dev/sdk/releases) | 电脑端 SDK；.zip | 运行在电脑的开发 SDK，不是复制到主机直接运行的应用。 固件：按项目 README 与当前发布说明核对。 |
| `ps5-linux-loader` — [PS5 Linux 启动载荷](https://github.com/ps5-linux/ps5-linux-loader/releases) | ELF/载荷；.elf | 需要对应固件和外部存储等前置条件；按项目 README 配置，本工具只下载。 固件：仅作者 README 列出的 Phat/Slim 机型及 3.00–7.61 内具体版本；不是整个区间通用，也不继承 Relapse 支持范围。 |
| `ps5-linux-image` — [PS5 Linux 镜像构建项目](https://github.com/ps5-linux/ps5-linux-image) | 电脑端镜像构建；页面入口 | 本次 Release 无可下载镜像附件；保留构建项目页面。 固件：仅作者 README 列出的 Phat/Slim 机型及 3.00–7.61 内具体版本；不是整个区间通用，也不继承 Relapse 支持范围。 |
| `ps5-linux-tools` — [PS5 Linux 配套工具](https://github.com/ps5-linux/ps5-linux-tools) | Linux 工具源码；页面入口 | 源码工具项目，需在相应 Linux 环境按 README 构建使用。 固件：仅作者 README 列出的 Phat/Slim 机型及 3.00–7.61 内具体版本；不是整个区间通用，也不继承 Relapse 支持范围。 |

## 补充模拟器与应用

| ID / 项目 | 运行方式 / 下载 | 说明 |
|---|---|---|
| `psp5` — [PSP5 原生 PSP 模拟器](https://github.com/tsuramatsu1/psp5/releases/tag/v1.000.100) | 原生标题；.zip；固定 v1.000.100 | 基于 PPSSPP；所需游戏数据和兼容性查看作者说明。 固件：按项目 README 与当前发布说明核对。 |
| `retroarch-websrv-engine` — [RetroArch websrv 前端与资源](https://github.com/avoidik/ps5-retroarch/releases/tag/v1.0.1) | websrv 应用；.zip；固定 v1.0.1 | 与 retroarch-websrv-cores 配套；这是 websrv 布局，与 native RetroArch 标题分开。 固件：按项目 README 与当前发布说明核对。 |
| `retroarch-websrv-cores` — [RetroArch websrv 模拟器核心](https://github.com/avoidik/ps5-retroarch/releases/tag/v1.0.1) | websrv 资源；.zip；固定 v1.0.1 | 需匹配的 RetroArch websrv 前端；BIOS 与游戏数据按核心说明准备。 固件：按项目 README 与当前发布说明核对。 |
| `ytps5` — [ytps5 YouTube 客户端](https://github.com/haasele/ytps5/releases/tag/01.000.005) | 原生标题；.zip；固定 01.000.005 | 原生标题包；与其他项目是否使用同一 Title ID 需核对，安装前看作者 README。 固件：按项目 README 与当前发布说明核对。 |

## 商店客户端

| ID / 项目 | 运行方式 / 下载 | 说明 |
|---|---|---|
| `overdrive` — [Overdrive 原发布仓库客户端](https://github.com/overdriveps5/overdrive-releases/releases) | 商店客户端 / exFAT 标题；.zip | 当前发布仓库 README 指定的 exFAT ZIP 包；客户端与服务可用性分别确认，部署依赖按仓库说明核对。 固件：按对应分支 README 核对入口、自制运行环境和镜像加载支持，不沿用其他商店的要求。 |
| `overdrive-community` — [Overdrive MyLuxy 社区重建客户端](https://github.com/MyLuxy/overdrive/releases) | 商店客户端 / exFAT 标题；.exfat | 第三方重建分支；裸 exFAT 镜像，不是 ZIP，勿更改扩展名。ShadowMount+ 等前置环境查看该分支 README。与原发布版使用同一 Title ID，是替代版本。 固件：按对应分支 README 核对入口、自制运行环境和镜像加载支持，不沿用其他商店的要求。 |

## 模拟器

| ID / 项目 | 运行方式 / 下载 | 说明 |
|---|---|---|
| `native-ppsa06464` — [PS64（PS5 模拟器）](https://github.com/dantaipan/PS64/releases/tag/01.000.000) | 原生标题；.zip；固定 01.000.000 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa68091` — [Ruffle Flash（PS5 模拟器）](https://github.com/ZiZc3/Ruffle-Flash-PS5/releases/tag/1.2.0) | 原生标题；.zip；固定 1.2.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa92280` — [Capy Mobile（PS5 模拟器）](https://github.com/khalifa007/CapyMobile/releases/tag/v0.5.0) | 原生标题；.zip；固定 v0.5.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa97358` — [XPSemu（PS5 模拟器）](https://github.com/ZiZc3/XPSemu/releases/tag/Alpha-2.1) | 原生标题；.zip；固定 Alpha-2.1 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa97510` — [PSXS5（PS5 模拟器）](https://github.com/SynoPiia/PSXS5/releases/tag/v2.2.0) | 原生标题；.zip；固定 v2.2.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa98510` — [SwanStationPS5（PS5 模拟器）](https://github.com/darkxex/SwanStationPS5/releases/tag/1.4.2) | 原生标题；.zip；固定 1.4.2 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99008` — [ProsperoEden（PS5 模拟器）](https://github.com/blackbearreloaded/ProsperoEden) | 原生标题；页面入口 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。目录记录的附件当前未核实可用，保留作者页面入口。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99142` — [Seedee5（PS5 模拟器）](https://github.com/mortaljinx/Seedee5/releases/tag/v1.21) | 原生标题；.zip；固定 v1.21 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99169` — [RetroArch（PS5 模拟器）](https://github.com/mihawk-99/PS5_RetroArch/releases/tag/v3.0.0-beta-3) | 原生标题；.zip；固定 v3.0.0-beta-3 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99203` — [PS5SX2（PS5 模拟器）](https://github.com/Swordpdf/PS5SX2/releases/tag/vk-285-171) | 原生标题；.zip；固定 vk-285-171 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99247` — [PSFlyCast（PS5 模拟器）](https://github.com/Press5elect/PSFlycast/releases/tag/v1.2.0) | 原生标题；.zip；固定 v1.2.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99248` — [PSSwanStation（PS5 模拟器）](https://github.com/Press5elect/PSSwanStation/releases/tag/build24) | 原生标题；.zip；固定 build24 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99360` — [PS5CEMU-HAR（PS5 模拟器）](https://github.com/premohq/PS5CEMU-HAR/releases/tag/v4.0.1) | 原生标题；.zip；固定 v4.0.1 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99764` — [Porpoise（PS5 模拟器）](https://github.com/elripalda/Porpoise-Dolphin-Emulator-for-PS5/releases/tag/v3.0) | 原生标题；.zip；固定 v3.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99808` — [PICO-8 for PS5（PS5 模拟器）](https://github.com/RafaelNGP/pico8-ps5/releases/tag/v0.1.2) | 原生标题；.zip；固定 v0.1.2 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |

## 影音与直播

| ID / 项目 | 运行方式 / 下载 | 说明 |
|---|---|---|
| `native-ppsa74126` — [Stremio Plus（PS5 影音与直播）](https://github.com/LoZazaMastro/Stremio-Plus/releases/tag/0.5.11) | 原生标题；.zip；固定 0.5.11 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa77711` — [Stremio（PS5 影音与直播）](https://github.com/Sp9nky/unofficial-stremio-ps5-port/releases/tag/v1.2) | 原生标题；.ffpfsc；固定 v1.2 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa85300` — [VLC（PS5 影音与直播）](https://github.com/ZiZc3/VLC/releases/tag/v0.4.6) | 原生标题；.zip；固定 v0.4.6 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99003` — [ProsperoTV（PS5 影音与直播）](https://github.com/ThatGuyKalvin/ProsperoTV/releases/tag/01.000.080) | 原生标题；.zip；固定 01.000.080 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99015` — [Media Player Classic PS5（PS5 影音与直播）](https://github.com/MisterTemaki/MediaPlayerClassicPS5/releases/tag/v1.2.3) | 原生标题；.zip；固定 v1.2.3 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99039` — [EVO Player（PS5 影音与直播）](https://github.com/sainsaji/EVO-PLAYER-PS5/releases/tag/v0.12.0) | 原生标题；.zip；固定 v0.12.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99141` — [Mortalfin（PS5 影音与直播）](https://github.com/mortaljinx/mortalfin/releases/tag/1.0.0-beta.5) | 原生标题；.zip；固定 1.0.0-beta.5 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99288` — [Nuvio Max'd（PS5 影音与直播）](https://github.com/HandshakeHackin/Nuvio-maxd-releases/releases/tag/v0.5.34-native-experimental) | 原生标题；.zip；固定 v0.5.34-native-experimental | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99420` — [PS5MC（PS5 影音与直播）](https://github.com/VivaLaVent/PS5MC/releases/tag/1.2) | 原生标题；.zip；固定 1.2 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99474` — [Twispero（PS5 影音与直播）](https://github.com/unicxrn/twispero/releases/tag/v1.0.0) | 原生标题；.zip；固定 v1.0.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99505` — [Jelly5（PS5 影音与直播）](https://github.com/02dnot/Jelly5/releases/tag/v0.7.0) | 原生标题；.zip；固定 v0.7.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99515` — [Emby5（PS5 影音与直播）](https://github.com/bornaradusin/Emby5/releases/tag/1.2.5) | 原生标题；.zip；固定 1.2.5 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99520` — [Régie5（PS5 影音与直播）](https://github.com/viviandsx/regie5/releases/tag/v0.7.0) | 原生标题；.zip；固定 v0.7.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99991` — [YouTube Max’d（PS5 影音与直播）](https://github.com/HandshakeHackin/youtube-maxd/releases/tag/v1.3.0-preview.1) | 原生标题；.zip；固定 v1.3.0-preview.1 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99997` — [Nuvio PS5（PS5 影音与直播）](https://github.com/bilawalriaz/nuvio-ps5-homebrew/releases/tag/v0.1.0-alpha.7) | 原生标题；.zip；固定 v0.1.0-alpha.7 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |

## 音乐

| ID / 项目 | 运行方式 / 下载 | 说明 |
|---|---|---|
| `native-ppsa01153` — [OliSe Player（PS5 音乐）](https://github.com/Marice/OliSePlayer/releases/tag/02.001.000) | 原生标题；.zip；固定 02.001.000 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa17641` — [SymphonyStation5（PS5 音乐）](https://github.com/TsvetomirGT/SymphonyStation5/releases/tag/v0.1.0) | 原生标题；.zip；固定 v0.1.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa47770` — [Afterglow（PS5 音乐）](https://github.com/DevvNirvana/afterglow/releases/tag/01.000.006) | 原生标题；.zip；固定 01.000.006 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa98427` — [CD Player（PS5 音乐）](https://github.com/LoZazaMastro/CD-Player/releases/tag/v1.1.1) | 原生标题；.zip；固定 v1.1.1 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99061` — [Spot5（PS5 音乐）](https://github.com/abhi245y/spot5/releases/tag/v1.1.0) | 原生标题；.zip；固定 v1.1.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `bolemusic_ps5` — [波乐音乐（ps5；平台支持与安装方式见项目说明）](https://github.com/shellsec/bolemusic/releases) | ；页面入口 |  固件：查看作者说明。 |

## 串流与云游戏

| ID / 项目 | 运行方式 / 下载 | 说明 |
|---|---|---|
| `native-ppsa39410` — [VITA5（PS5 串流与云游戏）](https://github.com/StonedModder/VITA5/releases/tag/v1.0.0) | 原生标题；.zip；固定 v1.0.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99002` — [ProsperoLight（PS5 串流与云游戏）](https://github.com/LedyBacer/ProsperoLight/releases/tag/01.000.110) | 原生标题；.zip；固定 01.000.110 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99082` — [OpenNOW PS5 - Prototype（PS5 串流与云游戏）](https://github.com/Portablelle/OpenNOW-PS5/releases/tag/0.1) | 原生标题；.zip；固定 0.1 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99350` — [Steam Remote Play（PS5 串流与云游戏）](https://github.com/jmelovich/Steam-Link-PS5/releases/tag/v1.0.0) | 原生标题；.zip；固定 v1.0.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99600` — [Cloud Play（PS5 串流与云游戏）](https://github.com/tertiumndatur/ps5-cloud-play/releases/tag/v1.0.0) | 原生标题；.zip；固定 v1.0.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99810` — [PSBox Cloud Gaming（PS5 串流与云游戏）](https://github.com/RafaelNGP/xbox-cloud-gaming-ps5/releases/tag/v1.3.0) | 原生标题；.zip；固定 v1.3.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |

## 工具与个性化

| ID / 项目 | 运行方式 / 下载 | 说明 |
|---|---|---|
| `native-ppsa69426` — [Signal Companion（PS5 工具与个性化）](https://github.com/Marice/ps5-signal-companion/releases/tag/v00.003.000) | 原生标题；.zip；固定 v00.003.000 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa75837` — [Jewel Case（PS5 工具与个性化）](https://github.com/SkaRift/JewelCase/releases/tag/v1.1) | 原生标题；.zip；固定 v1.1 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa76677` — [RommPS（PS5 工具与个性化）](https://github.com/s0liton/RommPS/releases/tag/v1.2.1) | 原生标题；.zip；固定 v1.2.1 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa90210` — [Prospero Themes（PS5 工具与个性化）](https://github.com/Darkatek7/ProsperoThemes/releases/tag/01.000.008) | 原生标题；.zip；固定 01.000.008 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99000` — [ProsperoStore（PS5 工具与个性化）](https://github.com/darkxex/ProsperoStore/releases/tag/v1.000.101) | 原生标题；.zip；固定 v1.000.101 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99030` — [Forever Launcher（PS5 工具与个性化）](https://github.com/bizkut/ps5-forever/releases/tag/01.000.014) | 原生标题；.zip；固定 01.000.014 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99109` — [Prospero Explorer（PS5 工具与个性化）](https://github.com/SvenGDK/Prospero-Explorer/releases/tag/v1.0) | 原生标题；.zip；固定 v1.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99110` — [Prospero Multi Tools（PS5 工具与个性化）](https://github.com/SvenGDK/Prospero-Multi-Tools/releases/tag/v1) | 原生标题；.zip；固定 v1 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99773` — [PShare（PS5 工具与个性化）](https://github.com/StonedModder/PShare/releases/tag/1.0) | 原生标题；.zip；固定 1.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99930` — [Forwarder Manager（PS5 工具与个性化）](https://github.com/heydemoura/ps5-forwarder-manager/releases/tag/00.001.004) | 原生标题；.zip；固定 00.001.004 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99995` — [Prospero Win（PS5 工具与个性化）](https://github.com/mpereiraesaa/prospero-win/releases/tag/v0.2.0) | 原生标题；.zip；固定 v0.2.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |

## AI

| ID / 项目 | 运行方式 / 下载 | 说明 |
|---|---|---|
| `native-ppsa99004` — [ProsperoAI（PS5 AI）](https://github.com/blackbearreloaded/ProsperoAI) | 原生标题；页面入口 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。目录记录的附件当前未核实可用，保留作者页面入口。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99575` — [PS5LM（PS5 AI）](https://github.com/cobanov/PS5LM/releases/tag/v0.9.0) | 原生标题；.zip；固定 v0.9.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99581` — [PS5LM Plus（PS5 AI）](https://github.com/abhi245y/PS5LM-Plus/releases/tag/v0.8.4) | 原生标题；.zip；固定 v0.8.4 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |

## 游戏移植

| ID / 项目 | 运行方式 / 下载 | 说明 |
|---|---|---|
| `native-ppsa19111` — [XashPS5（PS5 游戏移植）](https://github.com/GordonProsperoMan/xash3d-ps5/releases/tag/v1.3) | 原生标题；.zip；固定 v1.3 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa47402` — [Syobon Action（PS5 游戏移植）](https://github.com/kvaps/syobon-action-ps5/releases/tag/01.001.000) | 原生标题；.zip；固定 01.001.000 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa59322` — [ccleste（PS5 游戏移植）](https://github.com/darkxex/PS5_Celeste/releases/tag/1.00) | 原生标题；.zip；固定 1.00 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa69421` — [SuperTuxKart（PS5 游戏移植）](https://github.com/Marice/stk-ps5/releases/tag/00.001.000) | 原生标题；.zip；固定 00.001.000 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa69423` — [Rush 2 Recompiled（PS5 游戏移植）](https://github.com/Marice/rush2-ps5/releases/tag/v00.003.000) | 原生标题；.zip；固定 v00.003.000 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa69424` — [Wave Race 64 Recompiled（PS5 游戏移植）](https://github.com/Marice/wave-race-64-ps5/releases/tag/v00.001.000) | 原生标题；.zip；固定 v00.001.000 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa74207` — [The Simpsons Game（PS5 游戏移植）](https://github.com/LoZazaMastro/TheSimpsonsGame-PS5-Builder) | 原生标题；页面入口 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。目录链接是源码/构建器包，保留作者页面，不作为主机可运行程序下载。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa94002` — [Raptor: Call of the Shadows (PS5)（PS5 游戏移植）](https://github.com/ChaDea1/RaptorPS5/releases/tag/v1.0.0-rc.2) | 原生标题；.zip；固定 v1.0.0-rc.2 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa98001` — [PokeMMO Prospero（PS5 游戏移植）](https://github.com/Shabbypenguin/PokeMMO-Prospero/releases/tag/v1.0.2) | 原生标题；.zip；固定 v1.0.2 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa98511` — [ReKHCoM（PS5 游戏移植）](https://github.com/darkxex/ReKHCom-PS5/releases/tag/ps5-v1.0.6) | 原生标题；.zip；固定 ps5-v1.0.6 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99010` — [vkQuake（PS5 游戏移植）](https://github.com/mihawk-99/PS5_vkQuake/releases/tag/1.0) | 原生标题；.zip；固定 1.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99300` — [Spider-Man: Edge of Time（PS5 游戏移植）](https://github.com/KongaTime/PS5_EdgeOfTimeTitle/releases/tag/V.1.1.1) | 原生标题；.zip；固定 V.1.1.1 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99303` — [Quake3e（PS5 游戏移植）](https://github.com/griches/PS5_Quake3e/releases/tag/v1.2.0) | 原生标题；.zip；固定 v1.2.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99305` — [Dusklight（PS5 游戏移植）](https://github.com/griches/PS5_Dusklight/releases/tag/v1.0.0) | 原生标题；.zip；固定 v1.0.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99309` — [Wind Waker（PS5 游戏移植）](https://github.com/griches/PS5_SwitchWaker/releases/tag/v1.0.3) | 原生标题；.zip；固定 v1.0.3 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99310` — [Mario 64（PS5 游戏移植）](https://github.com/griches/PS5_Ghostship/releases/tag/v1.0.1) | 原生标题；.zip；固定 v1.0.1 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99312` — [Super Mario Sunshine（PS5 游戏移植）](https://github.com/griches/PS5_Sunshine/releases/tag/v0.10.0) | 原生标题；.zip；固定 v0.10.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99313` — [Doom 3 BFG（PS5 游戏移植）](https://github.com/griches/PS5_Doom3/releases/tag/v1.0) | 原生标题；.zip；固定 v1.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99314` — [Eternal Darkness（PS5 游戏移植）](https://github.com/griches/PS5_EternalDarkness/releases/tag/v0.9.3) | 原生标题；.zip；固定 v0.9.3 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99320` — [Ship of Harkinian (Vulkan)（PS5 游戏移植）](https://github.com/damiantw/PS5_Shipwright/releases/tag/01.000.000) | 原生标题；.zip；固定 01.000.000 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99403` — [NFS Black Box（PS5 游戏移植）](https://github.com/lavavex/nfs-blackbox-ps5/releases/tag/01.000.000) | 原生标题；.zip；固定 01.000.000 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99620` — [Ship of Harkinian (Ocarina of Time)（PS5 游戏移植）](https://github.com/mshivam019/oot64-ps5/releases/tag/v1.2.0) | 原生标题；.zip；固定 v1.2.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99621` — [2 Ship 2 Harkinian (Majora's Mask)（PS5 游戏移植）](https://github.com/mshivam019/tmm64-ps5/releases/tag/v1.1.0) | 原生标题；.zip；固定 v1.1.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99630` — [Morrowind (OpenMW)（PS5 游戏移植）](https://github.com/mshivam019/morrowind-ps5/releases/tag/v1.0.1) | 原生标题；.zip；固定 v1.0.1 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99640` — [Twilight Princess (Dusklight)（PS5 游戏移植）](https://github.com/mshivam019/dusklight-ps5/releases/tag/ps5-v0.1.0) | 原生标题；.zip；固定 ps5-v0.1.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99641` — [Wind Waker HD（PS5 游戏移植）](https://github.com/mshivam019/ww-ps5/releases/tag/ps5-v0.1.2) | 原生标题；.zip；固定 ps5-v0.1.2 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99660` — [Animal Crossing for PS5（PS5 游戏移植）](https://github.com/mshivam019/ac-ps5/releases/tag/v1.0.0) | 原生标题；.zip；固定 v1.0.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99666` — [DOOM Native Port（PS5 游戏移植）](https://github.com/lowbit/ps5-doom/releases/tag/v1.1.1) | 原生标题；.zip；固定 v1.1.1 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99670` — [Link’s Awakening for PS5（PS5 游戏移植）](https://github.com/mshivam019/la-ps5/releases/tag/v0.1.0) | 原生标题；.zip；固定 v0.1.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99728` — [OpenRCT2 Native Port（PS5 游戏移植）](https://github.com/lowbit/ps5-openrct2/releases/tag/v1.0.0) | 原生标题；.zip；固定 v1.0.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。所需 BIOS、游戏或商业运行库需按作者说明自行准备。 固件：按作者 README 与发布说明核对，未统一核定。 |

## 自制游戏

| ID / 项目 | 运行方式 / 下载 | 说明 |
|---|---|---|
| `native-ppsa28319` — [Middle Ages Ping Pong（PS5 自制游戏）](https://github.com/STL1te/MedievalTennis/releases/tag/01.000.000) | 原生标题；.zip；固定 01.000.000 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |

## 测试工具

| ID / 项目 | 运行方式 / 下载 | 说明 |
|---|---|---|
| `native-ppsa69420` — [ScreenTester5（PS5 测试工具）](https://github.com/Marice/ScreenTester5/releases/tag/01.000.000) | 原生标题；.zip；固定 01.000.000 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa98766` — [DriftCheck（PS5 测试工具）](https://github.com/felipemelchior/driftcheck5/releases/tag/01.000.000) | 原生标题；.zip；固定 01.000.000 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99051` — [Surround Sound Studio（PS5 测试工具）](https://github.com/sainsaji/PS5-Audio-Passthrough-Research/releases/tag/01.000.003) | 原生标题；.zip；固定 01.000.003 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99510` — [GyroAim（PS5 测试工具）](https://github.com/jmelovich/ps5-gyroaim/releases/tag/v1.0.2) | 原生标题；.zip；固定 v1.0.2 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |
| `native-ppsa99920` — [Prospero Vibrate（PS5 测试工具）](https://github.com/SvenGDK/Prospero-Vibrate/releases/tag/v1.0) | 原生标题；.zip；固定 v1.0 | 原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。 固件：按作者 README 与发布说明核对，未统一核定。 |

## websrv模拟器

| ID / 项目 | 运行方式 / 下载 | 说明 |
|---|---|---|
| `websrv-fbneo` — [FBNeo（websrv 包）](https://github.com/ps5-payload-dev/websrv/releases/tag/v0.34) | websrv 应用；.zip；固定 v0.34 | 作者 websrv Release 中的独立应用包；按其 Homebrew Launcher 布局部署，游戏/BIOS/资源依赖按项目说明自行准备。 固件：按项目 README 与当前发布说明核对。 |
| `websrv-lakesnes` — [LakeSnes（websrv 包）](https://github.com/ps5-payload-dev/websrv/releases/tag/v0.34) | websrv 应用；.zip；固定 v0.34 | 作者 websrv Release 中的独立应用包；按其 Homebrew Launcher 布局部署，游戏/BIOS/资源依赖按项目说明自行准备。 固件：按项目 README 与当前发布说明核对。 |
| `websrv-mednafen` — [Mednafen（websrv 包）](https://github.com/ps5-payload-dev/websrv/releases/tag/v0.34) | websrv 应用；.zip；固定 v0.34 | 作者 websrv Release 中的独立应用包；按其 Homebrew Launcher 布局部署，游戏/BIOS/资源依赖按项目说明自行准备。 固件：按项目 README 与当前发布说明核对。 |
| `websrv-pfbneo-7-1-ps5` — [pfbneo-7.1_ps5（websrv 包）](https://github.com/ps5-payload-dev/websrv/releases/tag/v0.34) | websrv 应用；.zip；固定 v0.34 | 作者 websrv Release 中的独立应用包；按其 Homebrew Launcher 布局部署，游戏/BIOS/资源依赖按项目说明自行准备。 固件：按项目 README 与当前发布说明核对。 |
| `websrv-pgba-7-1-ps5` — [pgba-7.1_ps5（websrv 包）](https://github.com/ps5-payload-dev/websrv/releases/tag/v0.34) | websrv 应用；.zip；固定 v0.34 | 作者 websrv Release 中的独立应用包；按其 Homebrew Launcher 布局部署，游戏/BIOS/资源依赖按项目说明自行准备。 固件：按项目 README 与当前发布说明核对。 |
| `websrv-pgen-7-1-ps5` — [pgen-7.1_ps5（websrv 包）](https://github.com/ps5-payload-dev/websrv/releases/tag/v0.34) | websrv 应用；.zip；固定 v0.34 | 作者 websrv Release 中的独立应用包；按其 Homebrew Launcher 布局部署，游戏/BIOS/资源依赖按项目说明自行准备。 固件：按项目 README 与当前发布说明核对。 |
| `websrv-pnes-7-1-ps5` — [pnes-7.1_ps5（websrv 包）](https://github.com/ps5-payload-dev/websrv/releases/tag/v0.34) | websrv 应用；.zip；固定 v0.34 | 作者 websrv Release 中的独立应用包；按其 Homebrew Launcher 布局部署，游戏/BIOS/资源依赖按项目说明自行准备。 固件：按项目 README 与当前发布说明核对。 |
| `websrv-psnes-7-1-ps5` — [psnes-7.1_ps5（websrv 包）](https://github.com/ps5-payload-dev/websrv/releases/tag/v0.34) | websrv 应用；.zip；固定 v0.34 | 作者 websrv Release 中的独立应用包；按其 Homebrew Launcher 布局部署，游戏/BIOS/资源依赖按项目说明自行准备。 固件：按项目 README 与当前发布说明核对。 |
| `websrv-retroarch` — [RetroArch（websrv 包）](https://github.com/ps5-payload-dev/websrv/releases/tag/v0.34) | websrv 应用；.zip；固定 v0.34 | 作者 websrv Release 中的独立应用包；按其 Homebrew Launcher 布局部署，游戏/BIOS/资源依赖按项目说明自行准备。 固件：按项目 README 与当前发布说明核对。 |
| `websrv-scummvm` — [ScummVM（websrv 包）](https://github.com/ps5-payload-dev/websrv/releases/tag/v0.34) | websrv 应用；.zip；固定 v0.34 | 作者 websrv Release 中的独立应用包；按其 Homebrew Launcher 布局部署，游戏/BIOS/资源依赖按项目说明自行准备。 固件：按项目 README 与当前发布说明核对。 |

## websrv游戏移植

| ID / 项目 | 运行方式 / 下载 | 说明 |
|---|---|---|
| `websrv-crispydoom` — [CrispyDoom（websrv 包）](https://github.com/ps5-payload-dev/websrv/releases/tag/v0.34) | websrv 应用；.zip；固定 v0.34 | 作者 websrv Release 中的独立应用包；按其 Homebrew Launcher 布局部署，游戏/BIOS/资源依赖按项目说明自行准备。 固件：按项目 README 与当前发布说明核对。 |
| `websrv-devilutionx` — [DevilutionX（websrv 包）](https://github.com/ps5-payload-dev/websrv/releases/tag/v0.34) | websrv 应用；.zip；固定 v0.34 | 作者 websrv Release 中的独立应用包；按其 Homebrew Launcher 布局部署，游戏/BIOS/资源依赖按项目说明自行准备。 固件：按项目 README 与当前发布说明核对。 |
| `websrv-eduke32` — [EDuke32（websrv 包）](https://github.com/ps5-payload-dev/websrv/releases/tag/v0.34) | websrv 应用；.zip；固定 v0.34 | 作者 websrv Release 中的独立应用包；按其 Homebrew Launcher 布局部署，游戏/BIOS/资源依赖按项目说明自行准备。 固件：按项目 README 与当前发布说明核对。 |
| `websrv-mari0` — [Mari0（websrv 包）](https://github.com/ps5-payload-dev/websrv/releases/tag/v0.34) | websrv 应用；.zip；固定 v0.34 | 作者 websrv Release 中的独立应用包；按其 Homebrew Launcher 布局部署，游戏/BIOS/资源依赖按项目说明自行准备。 固件：按项目 README 与当前发布说明核对。 |
| `websrv-omnispeak` — [Omnispeak（websrv 包）](https://github.com/ps5-payload-dev/websrv/releases/tag/v0.34) | websrv 应用；.zip；固定 v0.34 | 作者 websrv Release 中的独立应用包；按其 Homebrew Launcher 布局部署，游戏/BIOS/资源依赖按项目说明自行准备。 固件：按项目 README 与当前发布说明核对。 |
| `websrv-openjazz` — [OpenJazz（websrv 包）](https://github.com/ps5-payload-dev/websrv/releases/tag/v0.34) | websrv 应用；.zip；固定 v0.34 | 作者 websrv Release 中的独立应用包；按其 Homebrew Launcher 布局部署，游戏/BIOS/资源依赖按项目说明自行准备。 固件：按项目 README 与当前发布说明核对。 |
| `websrv-vvvvvv` — [VVVVVV（websrv 包）](https://github.com/ps5-payload-dev/websrv/releases/tag/v0.34) | websrv 应用；.zip；固定 v0.34 | 作者 websrv Release 中的独立应用包；按其 Homebrew Launcher 布局部署，游戏/BIOS/资源依赖按项目说明自行准备。 固件：按项目 README 与当前发布说明核对。 |
| `websrv-wolf4sdl` — [Wolf4SDL（websrv 包）](https://github.com/ps5-payload-dev/websrv/releases/tag/v0.34) | websrv 应用；.zip；固定 v0.34 | 作者 websrv Release 中的独立应用包；按其 Homebrew Launcher 布局部署，游戏/BIOS/资源依赖按项目说明自行准备。 固件：按项目 README 与当前发布说明核对。 |
| `websrv-yquake2` — [YQuake2（websrv 包）](https://github.com/ps5-payload-dev/websrv/releases/tag/v0.34) | websrv 应用；.zip；固定 v0.34 | 作者 websrv Release 中的独立应用包；按其 Homebrew Launcher 布局部署，游戏/BIOS/资源依赖按项目说明自行准备。 固件：按项目 README 与当前发布说明核对。 |

## websrv应用

| ID / 项目 | 运行方式 / 下载 | 说明 |
|---|---|---|
| `websrv-ffplay` — [FFplay（websrv 包）](https://github.com/ps5-payload-dev/websrv/releases/tag/v0.34) | websrv 应用；.zip；固定 v0.34 | 作者 websrv Release 中的独立应用包；按其 Homebrew Launcher 布局部署，游戏/BIOS/资源依赖按项目说明自行准备。 固件：按项目 README 与当前发布说明核对。 |
| `websrv-linkdev` — [LinkDev（websrv 包）](https://github.com/ps5-payload-dev/websrv/releases/tag/v0.34) | websrv 应用；.zip；固定 v0.34 | 作者 websrv Release 中的独立应用包；按其 Homebrew Launcher 布局部署，游戏/BIOS/资源依赖按项目说明自行准备。 固件：按项目 README 与当前发布说明核对。 |
| `websrv-offact` — [OffAct（websrv 包）](https://github.com/ps5-payload-dev/websrv/releases/tag/v0.34) | websrv 应用；.zip；固定 v0.34 | 作者 websrv Release 中的独立应用包；按其 Homebrew Launcher 布局部署，游戏/BIOS/资源依赖按项目说明自行准备。 固件：按项目 README 与当前发布说明核对。 |
| `websrv-pkginstall` — [PKGInstall（websrv 包）](https://github.com/ps5-payload-dev/websrv/releases/tag/v0.34) | websrv 应用；.zip；固定 v0.34 | 作者 websrv Release 中的独立应用包；按其 Homebrew Launcher 布局部署，游戏/BIOS/资源依赖按项目说明自行准备。 固件：按项目 README 与当前发布说明核对。 |
| `websrv-sverigesradio` — [SverigesRadio（websrv 包）](https://github.com/ps5-payload-dev/websrv/releases/tag/v0.34) | websrv 应用；.zip；固定 v0.34 | 作者 websrv Release 中的独立应用包；按其 Homebrew Launcher 布局部署，游戏/BIOS/资源依赖按项目说明自行准备。 固件：按项目 README 与当前发布说明核对。 |
| `websrv-svtplay` — [SVTplay（websrv 包）](https://github.com/ps5-payload-dev/websrv/releases/tag/v0.34) | websrv 应用；.zip；固定 v0.34 | 作者 websrv Release 中的独立应用包；按其 Homebrew Launcher 布局部署，游戏/BIOS/资源依赖按项目说明自行准备。 固件：按项目 README 与当前发布说明核对。 |
| `websrv-tvheadend` — [TVHeadend（websrv 包）](https://github.com/ps5-payload-dev/websrv/releases/tag/v0.34) | websrv 应用；.zip；固定 v0.34 | 作者 websrv Release 中的独立应用包；按其 Homebrew Launcher 布局部署，游戏/BIOS/资源依赖按项目说明自行准备。 固件：按项目 README 与当前发布说明核对。 |

## 维护与核查

核心工具的核查记录见 [release-check.json](apps-ps5/release-check.json)，社区应用作者链接和附件核查见 [community-source.json](apps-ps5/community-source.json)。

```bat
python tools/import_ps5_community_catalog.py --refresh
python tools/generate_ps5_catalog_index.py
```

不带 --refresh 时只从本地快照重建社区分片。导入器保留同一 ID 的 enabled 状态，生成的 10–19 号分片由脚本维护；自定义条目放在其他分片以免被刷新覆盖。核查暂时失败时不覆盖已有快照。

待关注但未发布的名称见 [unpublished.json](apps-ps5/unpublished.json)，不会把这些登记项当成已经存在的下载包。
