# 更新日志

## 20261113-desktop（2026-11-13）

- Windows 单 EXE 内置运行环境、平台清单和网页目录。桌面菜单可切换简体中文和 English，并保存语言偏好。
- 平台目录支持分类、搜索和批量下载。链接加速下载支持 GitHub 发布附件、仓库源码、Git 克隆、直链和 Chrome 原版 CRX。
- 下载队列支持暂停、续传、重试和直接打开已完成的文件。可分别清理下载文件和日志。
- 自定义清单支持从粘贴文本提取来源、预览并去重导入。下载历史可重下原附件或获取最新版。
- 在线清单可独立更新并校验，个人数据存放在 `%LOCALAPPDATA%\GHReleaseFetch`。
- 更新中英文 README，加入主界面截图和 Windows 下载链接。

## 20261113-single-exe（2026-11-13）

- Windows 发行包只包含 `GHReleaseFetch.exe`。原有批处理入口统一调用这一程序。
- 窗口标题显示 `GH Release Fetch - github.com/shellsec/gh-release-fetch`，顶部「GitHub」入口可直接打开项目仓库。

## 20261113-gui-r4（2026-11-13）

- 单 EXE 内置平台目录、网页目录和搜索索引。个人数据保存在 `%LOCALAPPDATA%\GHReleaseFetch`。
- 平台目录、链接下载、我的清单、下载历史共用下载队列，新增资讯和游戏搜索入口。
- 官方清单首次启动后台检查，之后每隔七天检查，也可手动更新。独立目录包支持自适应线路和 SHA-256 校验。

## 20261113-gui-r2（2026-11-13）

- 平台树添加图标，更新图形版 EXE 图标和表格样式。
- 软件右键支持立即下载、打开官网或商店。下载队列右键可打开目录、复制保存路径或查看任务日志。
- 增加明确的批量下载按钮，支持导入旧版个人更新清单。保存位置、队列结果和下载日志可跨重启保留。

## 20261113-gui（2026-11-13）

- 新增 Windows 图形便携版，双击 `GHReleaseFetch.exe` 打开，内置运行环境。
- 平台和分类浏览、关键词搜索、跨平台多选、网页批量下载及官方页面入口可从图形界面使用。
- 下载队列保存任务状态，支持暂停、继续和重试。平台附件、仓库发布包、源码 ZIP 和 Chrome CRX 共用分片下载引擎。
- 仓库入口支持选择发布附件、源码 ZIP、解压、Git 克隆、下载线路和连接数。Chrome 原版 CRX 仍走 Google 官方地址。

## 20261112-platform-catalog（2026-11-12）

- 菜单 1–12 与网页批量下载目录共新增 68 条。Windows、macOS、Linux 各 7 条，Android 9 条，Android TV 与 iOS 各 3 条，Switch 5 条，PS4 11 条，PS5 6 条，Vita 3 条，Xbox 4 条，Linux 掌机 3 条。新增条目按平台与用途浏览，使用官方发布附件或 App Store 页面。
- GitHub 开源 Chrome 扩展列表扩充至 56 款，补充 Consent-O-Matic、SimpleLogin、LeechBlock NG、JSON Formatter、Joplin Web Clipper 等。Bitwarden、Tampermonkey、Dark Reader 等热门条目增加 Chrome 商店 CRX 入口。
- GitHub 开源 Chrome 扩展列表从 19 款扩充到 42 款，新增隐私防护、密码安全、截图录屏、网页测试等用途，并收录 OpenCapture。
- 菜单 1–12 的平台入口可输入 `V` 按分类浏览，支持多选下载或打开官方页面。菜单 15 也使用 `V`，原按键 `l` 仍可用。
- 菜单 15 的「浏览可下载列表」按用途提供 GitHub 开源 Chrome 扩展和 Chrome 商店 CRX 两类入口。普通 GitHub 仓库可直接输入地址。

## 20261112-two-exe-icon（2026-11-12）

- Windows 主程序和下载器换用新的多尺寸图标。

## 20261112-two-exe（2026-11-12）

- Windows 便携包只需 `lookup_app.exe` 和 `auto_update.exe`，无需安装 Python。
- 个人更新清单、软件资讯和游戏页面搜索统一由 `lookup_app.exe` 提供。原有 `run_saved_apps.bat`、`search_soft_pages.bat` 和 `search_games.bat` 保留，主菜单 16、17、18 可直接进入。
- `open_catalog.bat` 继续打开可勾选并批量下载的网页目录，平台附件由 `auto_update.exe` 下载，Chrome CRX 由主程序从 Google 获取。

## 20261112-web-batch（2026-11-12）

Windows 便携包收录 12 个平台的目录。双击 `open_catalog.bat` 后，可在同一网页跨平台勾选条目并直接批量下载。下载调用现有下载器，附件按平台保存到 `catalog_downloads/`，官方页面条目在浏览器打开。

浏览器扩展目录覆盖 23 种用途，Windows 有 83 条，macOS 和 Linux 各有 81 条。菜单 15 支持 Chrome 商店链接或扩展 ID，原版 CRX 可从 Google 下载并续传。下列记录汇总了上一版之后的新增与调整。

- Windows 和 macOS 的游戏分类新增 NX2Apple，分别匹配 Windows x64 构建器和 Apple Silicon 启动器的正式发布附件。
  v1.3.0 的两个 ZIP 均已完整下载，逐文件通过 ZIP 完整性检查，SHA-256 与 GitHub 发布附件记录一致。
- 本地分类目录新增「批量下载」按钮。通过 `open_catalog.bat` 或 `--serve-catalog` 启动后可在网页提交选中项，并查看下载日志和结果。
- 分类展示页支持全部 12 个平台的复选框。菜单 15 可接收跨平台清单，按平台保存附件，Chrome 扩展保存为 CRX，页面条目打开官方入口。
- 浏览器扩展支持多选下载。分类展示页可勾选 Chrome 商店扩展并复制清单，菜单 15 接收多个链接或 ID，搜索结果也可按编号批量下载 CRX。
- 浏览器扩展新增「二维码」用途，收录 ZenQR、QR Lite 和 Offline QR Code Generator。
- 浏览器扩展再新增 32 款，补齐无障碍检查、网页测试、标签管理、协作与反馈、语言学习和辅助阅读等用途。
- 菜单 15 支持 Chrome 商店扩展详情链接和扩展 ID，可打开商店安装或从 Google 下载原版 CRX，支持分段并发和断点续传。
- 浏览器扩展再新增 12 款，包括 Refined GitHub、Tampermonkey、SponsorBlock、KeePassXC-Browser 和 Firefox Multi-Account Containers。
- 浏览器扩展新增 32 款，覆盖开发调试、隐私防护、广告拦截、办公翻译、学习科研、阅读研究、截图录屏、设计与样式、AI 助手、密码安全、笔记剪藏、视频增强、下载与嗅探、效率工具、新标签页和代理与网络。分类展示页支持按用途筛选，新增条目打开官方获取页面。
- Windows、macOS 和 Linux 新增「浏览器扩展」分类。GitHub Accelerator 提供 Chrome／Edge ZIP 和 Firefox XPI 下载入口。FlowPick 和沉浸式翻译的现有扩展条目归入新分类。
- Windows、macOS 和 Linux 的 AI 分类新增 Tokei，用于查看 AI 工具的用量和费用。支持下载 Windows x64 安装包、macOS 通用 DMG 和 Linux amd64 DEB。
- Switch 游戏与串流新增 tico 模拟器前端。当前核查的正式版为 0.8.0，可下载官方 `tico.nro`。
- Switch 配套资料与电脑工具新增 SCCM Switch Toolbox 官方发布页入口，用于在 Windows 上备份、恢复和迁移 Switch SD 卡及 emuMMC。

## 20261109-multiplatform（2026-11-09）

本次补充 12 个平台的 80 条记录。新增项默认关闭批量更新，可在对应平台清单搜索并单独获取。收录范围为 2026-10-09 至 2026-11-09 的正式发布。

| 平台 | 新增 | 分类与项目 |
| --- | ---: | --- |
| Windows | 8 | AI · LokalBot；下载 · Grabline、Firelink；工具 · Kensaku；笔记 · Hubble.md；终端 · psmux；音视频 · MediaMTX；数据库 · based |
| macOS | 8 | AI · LokalBot；下载 · Grabline、Firelink；工具 · Kensaku；效率 · Hop；笔记 · Hubble.md；音视频 · MediaMTX；数据库 · based |
| Linux | 7 | AI · LokalBot；下载 · Grabline、Firelink；工具 · Kensaku；笔记 · Hubble.md；音视频 · MediaMTX；数据库 · based |
| Android | 9 | AI · LokalBot；工具 · Fossify File Manager、Translate You；效率 · Mindwtr、Smartspacer；网络 · Whisper RSS、Feeder；远程与协作 · Side Screen；音视频 · Switch Frame Tap |
| iOS | 7 | 备份 · Proton Drive；安全 · 2FAS Auth；网络与通讯 · NetNewsWire、Ice Cubes、Mlem、Monal；远程与协作 · KDE Connect |
| Android TV | 7 | 桌面与启动器 · Aerial TV、Lounge、RustTV Launcher、Luncher；多媒体 · Wholphin、Vega、Switch Frame Tap |
| Switch | 3 | 日常工具 · SaltyNX；游戏与串流 · Switch Frame Tap；游戏移植 · SwitchWaker |
| PS4 | 5 | 系统与文件 · PS MTP Explorer、Apollo Save Tool；开发与教育 · Scratch Everywhere；多媒体 · JTPlay、TVHP |
| PS5 | 6 | 载荷与网络服务 · PS5 Exporter、PS5 Tailscale；文件与存档 · PS5Save；工具与个性化 · PrefBar、PS5 TabShifter、PoorDS4 |
| Vita | 5 | 应用管理 · PSVitaAlive、VitaForge；实用工具 · VitaFlightRadar；开发与教育 · Scratch Everywhere；游戏移植 · VectorVita |
| Xbox | 3 | 系统工具 · X-Files UWP、Game Vault；开发与教育 · Scratch Everywhere |
| Linux 掌机 | 12 | 系统与插件 · Loadout、PowerDeck、XR Gaming、Achievement Customizer、EGPU Buddy、FSR4Injector；兼容层 · GE-Proton；串流 · chiaki-ng；游戏库与启动器 · Heronite、Heroic Games Launcher、Steam ROM Manager、NonSteamLaunchers |
| **合计** | **80** | **71 条直接下载，9 条官方页面入口** |

同一平台按项目 ID 和仓库去重。跨平台构建保留在各自入口，例如 Switch Frame Tap 的主机端与接收端。iOS 使用 App Store，Monal 指向美国区。初代 Xbox 的 Scratch Everywhere 为 ISO/XBE 包，X-Files UWP 和 Game Vault 面向 Dev Mode。掌机的架构、配套插件和硬件要求见条目说明。

### 下载与操作

- 主菜单 **15 仓库下载**接受 `owner/repo` 和 GitHub 地址，可以获取 Release 附件、源码 ZIP 或 Git 克隆。个人更新清单顺延到 **16**。
- 仓库附件和源码 ZIP 可在 8 条候选线路中测速选线。服务器支持分段时最多使用 8 个连接，资源校验匹配时可续传。切换线路时从头下载以避免混用分片。
- 源码 ZIP 下载后自动保留，回车打开下载目录，也可解压到同名目录并打开。仓库入口输入 `h` 可查看记录、恢复可续传任务或更新已克隆仓库。
- GitHub API 限流时，可从官方发布页的附件列表解析下载链接。

### 便携包

Windows x64 用户可完整解压 ZIP 后运行 `lookup_app.bat`。新增平台条目依赖同包内的 JSON 清单，升级时请保留个人清单和下载记录，并使用新包的程序与清单。
