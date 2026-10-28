**语言 / Language:** 中文 | [English](README.en.md)

# GH Release Fetch

按平台搜索软件、下载 GitHub Release 附件，并用个人更新列表重复获取所需软件。支持内置清单、自定义来源和独立的介绍页搜索。交互界面跟随系统显示语言（简体中文、繁体中文、English、日本語、한국어），未能识别时仍使用简体中文。

## 下载与加速下载

当前版本：**20261028** · [版本说明](https://github.com/shellsec/gh-release-fetch/releases/tag/20261028) · [最新 Release](https://github.com/shellsec/gh-release-fetch/releases/latest)

| 运行平台 | 加速下载（gh-proxy.com） | GitHub 原始下载 |
| --- | --- | --- |
| Windows x64 | [ZIP](https://gh-proxy.com/https://github.com/shellsec/gh-release-fetch/releases/download/20261028/gh-release-fetch-windows-6bd1991.zip) | [ZIP](https://github.com/shellsec/gh-release-fetch/releases/download/20261028/gh-release-fetch-windows-6bd1991.zip) |
| macOS ARM64 / Apple Silicon | [tar.gz](https://gh-proxy.com/https://github.com/shellsec/gh-release-fetch/releases/download/20261028/gh-release-fetch-6bd1991-macos-arm64.tar.gz) | [tar.gz](https://github.com/shellsec/gh-release-fetch/releases/download/20261028/gh-release-fetch-6bd1991-macos-arm64.tar.gz) |
| Linux x86_64 | [tar.gz](https://gh-proxy.com/https://github.com/shellsec/gh-release-fetch/releases/download/20261028/gh-release-fetch-6bd1991-linux-x86_64.tar.gz) | [tar.gz](https://github.com/shellsec/gh-release-fetch/releases/download/20261028/gh-release-fetch-6bd1991-linux-x86_64.tar.gz) |
| Linux ARM64 | [tar.gz](https://gh-proxy.com/https://github.com/shellsec/gh-release-fetch/releases/download/20261028/gh-release-fetch-6bd1991-linux-arm64.tar.gz) | [tar.gz](https://github.com/shellsec/gh-release-fetch/releases/download/20261028/gh-release-fetch-6bd1991-linux-arm64.tar.gz) |
| SHA256SUMS | [校验文件](https://gh-proxy.com/https://github.com/shellsec/gh-release-fetch/releases/download/20261028/SHA256SUMS) | [校验文件](https://github.com/shellsec/gh-release-fetch/releases/download/20261028/SHA256SUMS) |

安装包均基于 `6bd1991`，自带运行环境，无需另装 Python。加速入口不可用时，请使用原始下载。macOS 包未签名或公证；Linux 需要 glibc，不适用于 Alpine/musl，尚未实机验证。具体测试范围见版本说明。

已有完整 Windows 目录可从 Release 下载五个独立 EXE 替换升级；首次使用请下载并完整解压 ZIP，EXE 仍需要旁边的清单与数据目录。SHA256SUMS 覆盖四个安装包和五个 EXE。

## 快速开始

1. 下载适合**运行这套工具的电脑**的安装包，完整解压，保留包内清单和数据目录。
2. Windows 双击 `lookup_app.exe` 或 `lookup_app.bat`；macOS/Linux 在解压目录执行 `./lookup_app`。
3. 选择要搜索的平台，输入软件名或关键词。回车默认 Windows，最后一项可搜索全部清单。
4. 选择结果序号，再选择下载、加入更新列表或启用。

| 操作 | 用途 |
| --- | --- |
| 1：立刻下载 | 获取所选软件，无合适安装包时打开页面，不修改启用状态 |
| 2：加入并下载 | 保存到更新列表，并立即下载 |
| 3：加入列表 | 保存到更新列表，稍后统一下载 |
| 4：启用 | 设置 `enabled=true`，参与对应清单的批量处理 |
| 5：打开页面 | 打开官网或 GitHub Releases 页面 |

多选可输入 `1,3`，`a` 选全部，回车跳过。部分条目提供官网、商店或发布页入口，无法直接下载安装包。跨平台下载不会让目标软件在当前电脑上运行。

### 实际操作示例

以 Windows 搜索 UniClipboard 为例，输入部分名称也能匹配。以下省略完整时间戳、网络探测和下载地址，仅展示操作过程；版本号和结果数量以实际运行为准。

```text
用法: lookup_app [选项与关键词...]
示例: lookup_app drawio
      lookup_mobile.bat termux
      lookup_ios.bat 微信
直接下载: lookup_app -y --download drawio
打开页面: lookup_app chatbox --open

搜哪个清单?
  1 Windows       2 macOS          3 Linux
  4 Android       5 Android TV     6 iOS App Store
  7 Switch        8 PS4            9 PS5
 10 Vita         11 Xbox          12 Linux掌机
 13 自定义清单   14 搜全部清单
请选择 (1-14，回车=Windows，q=退出): 1
请输入关键词（回车=返回清单）: unicli

共 2 条匹配：
[1] windows  id=uniclipboard      enabled=否  [可下载]
    简介: UniClipboard（跨平台剪贴板同步与管理，Rust + Tauri）
[2] windows  id=uniclipboard_cli  enabled=否  [可下载]
    简介: UniClipboard CLI（Windows x64 zip）

请选择要操作的条目：
  输入序号（如 1 或 1,3）| a=全部 | b/回车=返回 | q=退出
> 1

请选择操作：
  1 = 立刻下载（无安装包则打开页面；不修改 enabled）
  2 = 加入更新列表并立刻下载
  3 = 加入更新列表 saved_apps_<平台>.json
  4 = 设为 enabled=true
  5 = 打开页面（官网 / GitHub Releases）
  b/回车 = 返回    q = 退出
> 1

[下载] 平台 windows：uniclipboard
找到最新版本: v1.5.0
下载进度: 100.0% (25.1/25.1 MiB)
安装包已下载: <程序目录>/windows/UniClipboard_1.5.0_x64-setup.exe
安装程序已启动
```

此示例条目配置了 `run_installer`，所以下载后启动安装程序；其它条目是否启动取决于各自配置。操作 1 不修改 `enabled`，即使结果显示“未启用”也能直接下载。

## 按平台搜索

工具的运行平台是 Windows、macOS、Linux；**清单平台**是要查找的软件或设备类型，两者可以不同。

| 菜单分类 | 清单目录 | 命令行平台值 |
| --- | --- | --- |
| Windows | `apps/windows/` | `windows` |
| macOS | `apps/darwin/` | `darwin` |
| Linux | `apps/linux/` | `linux` |
| Android | `apps-mobile/` | `android` |
| Android TV | `apps-tv/` | `android_tv` |
| iOS App Store | `apps-mobile/` | `ios` |
| Switch | `apps-switch/` | `switch` |
| PS4 | `apps-ps4/` | `ps4` |
| PS5 | `apps-ps5/` | `ps5` |
| Vita | `apps-vita/` | `vita` |
| Xbox | `apps-xbox/` | `xbox` |
| Linux 掌机 | `apps-handheld/` | `linux_handheld` |
| 自定义清单 | `apps-custom/` | 通过 `--custom` 管理 |
| 搜全部清单 | 上述平台及自定义清单 | `--all-catalogs` |

Windows 示例：

```bat
lookup_app.bat drawio
lookup_mobile.bat termux
lookup_app.bat --apps-dir apps-tv --platform android_tv 洛雪
lookup_app.bat --apps-dir apps-handheld --platform linux_handheld proton
lookup_app.bat --all-catalogs music
```

macOS/Linux 使用 `./lookup_app` 替换示例中的 `lookup_app.bat`。带关键词时可显式指定平台；无参数运行可从菜单选择。主机和掌机条目的固件、架构及安装要求以项目说明为准。

浏览清单：[桌面](CATALOG.md) · [移动端](CATALOG.mobile.md) · [Switch](CATALOG.switch.md) · [PS5](CATALOG.ps5.md) · [分类展示页](catalog.html)。

## 自定义清单

主菜单选择「自定义清单」，或运行 `lookup_app.bat --custom`（macOS/Linux：`./lookup_app --custom`）。

添加流程：**输入来源 → 识别附件 → 选择平台/架构/包类型 → 预览 → 仅保存或保存并下载**。

支持 `owner/repo`、GitHub 仓库或 Release 地址、HTTP(S) 下载直链，也可输入软件名查找候选项目。同一项目可选择多个附件；普通 APK 需确认 Android 手机或 Android TV，无法判断的压缩包需手动选择平台。

- GitHub 条目按所选附件规则跟随最新稳定 Release；命名变化时需重新识别附件。
- 普通直链按固定链接保存，不自动判断新版本。添加操作不会自动运行安装包。
- 支持搜索、修改名称/分类、重新识别、删除、批量添加、JSON 导入导出。
- 变更前自动备份，最多保留 20 次，可撤销最近修改；删除条目不会删除下载文件。
- 平台、架构和绿色版/安装版偏好会在成功添加后记住，可修改或清除。

个人条目、偏好和历史保存在 `apps-custom/`，发布包只附空模板。分享前请使用导出功能。

```bat
lookup_app.bat --custom-add https://github.com/shellsec/bolemusic
lookup_app.bat --custom-add https://example.org/app.exe --dry-run
```

## 更新列表与批量下载

搜索后选择操作 2 或 3，会按平台保存 `saved_apps_<平台>.json`。Windows 运行 `run_saved_apps.bat`；macOS/Linux 运行 `./run_saved_apps`，按提示选择或指定列表。

`auto_update` 不带应用 ID 时，只处理对应清单中 `enabled: true` 的条目；**明确指定 ID 时不要求启用**。首次使用建议从搜索入口开始。

下载位置由各清单 `root.json` 的 `download_dir` 等设置决定。安装包是否运行取决于条目的 `run_installer`；压缩包不会自动解压。批量处理前先检查所选条目的下载与安装设置。

## 介绍页与游戏频道搜索

`search_soft_pages.bat` / `search_soft_pages.exe` 搜索介绍页标题；`search_games.bat` / `search_games.exe` 搜索游戏频道。macOS/Linux 对应入口为 `./search_soft_pages` 和 `./search_games`。

这些是独立的页面索引，结果以打开链接为主，不属于「搜全部清单」的 GitHub 软件条目。索引刷新和监控见 [频道工具说明](tools/soft_page_check/README.md)。

## 常见问题

| 问题 | 处理方式 |
| --- | --- |
| Windows 启动时报 `CATALOGS` 导入错误 | 使用本页最新修复包，覆盖旧 EXE。新版内置模块不会被旁边的旧 `tools/*.py` 覆盖，可保留个人清单和配置。 |
| 只复制一个 EXE 后找不到清单 | 完整解压发布包，保留同级清单及数据目录。 |
| 没有更新列表或启用项 | 先运行 `lookup_app` 搜索，选择加入列表或启用，再运行批量入口。 |
| 下载失败、无合适附件 | 查看项目发布页、网络和附件命名规则；部分收录条目仅提供页面入口。 |
| 下载慢或加速入口不可用 | 尝试 GitHub 原始链接；应用下载也会按配置尝试备用来源。 |
| macOS 提示无法验证开发者 | 当前包未签名或公证；确认来源后，按系统安全设置提示处理。 |
| Linux 无法运行 | 确认 CPU 架构和 glibc 环境；此包不适用于 Alpine/musl。 |
| 想查看错误详情 | 在终端运行入口，查看程序目录的 `update_log.txt`；意外启动异常另写 `startup_error.log`，目录不可写时查看控制台输出。 |

清单并不包含所有软件，已收录项目也可能因上游变更失效。可通过自定义清单补充来源，或维护对应条目的匹配规则。

## 从源码运行与打包

源码使用 Python 3.10 或更新版本。发布包用户无需执行以下步骤。

```bash
git clone https://github.com/shellsec/gh-release-fetch.git
cd gh-release-fetch
python -m pip install -r requirements.txt
python lookup_app.py
```

常用命令：

```bash
python lookup_app.py --platform windows --no-prompt drawio
python lookup_app.py --all-catalogs --no-prompt music
python auto_update.py --platform windows drawio
python tools/run_saved_apps.py --help
```

Windows 打包运行 `pack_windows_release.bat`，输出位于 `dist/release/`。详见 [Windows 打包说明](release/windows/PACKAGING.md)。macOS/Linux 当前发布包采用自带 CPython 的便携目录格式，需完整保留运行时目录。

配置字段、镜像回退、下载目录、日志及维护脚本见 [配置与维护参考](docs/reference.zh-CN.md)。桌面全局配置见 [apps/root.json](apps/root.json)，同平台各 JSON 分片的应用 `id` 不可重复。

## 相关项目与支持

[AI 工具导航 aiv123.com](https://aiv123.com/) · [ofox.ai](https://ofox.io/x/aiv123) · [请我喝可乐 / 爱发电](https://ifdian.net/a/shellsec)

可选独立清单：[VibeCodingToolsDown](VibeCodingToolsDown/README.md) · [GiteeExploreHot](GiteeExploreHot/README.md)。它们不属于主菜单「搜全部清单」的默认范围。
