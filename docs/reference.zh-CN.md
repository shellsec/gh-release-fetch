# 配置与维护参考

[返回使用说明](../README.zh-CN.md)

## 指定平台读取

即使当前不是该系统，也可强制读取某个平台块：

```bash
python auto_update.py --platform windows
python auto_update.py --platform darwin
python auto_update.py --platform linux
```

与指定 `id` 组合：

```bash
python auto_update.py nodejs --platform windows
```

---

## HTTPS 证书问题

临时关闭证书校验：

```bash
python auto_update.py --insecure
```

或在 [`apps/root.json`](../apps/root.json) 根级设置：

```json
"ssl_verify": false
```

注意：关闭证书校验有安全风险，证书恢复正常后建议改回 `true`。

---

## 发布页镜像与自适应回退

脚本对发布页抓取采用自适应策略：

- 先访问应用条目里的 `releases_url`
- 若镜像返回 403、5xx 或不可访问，自动回退到 `https://github.com/<owner>/<repo>/releases`
- 若页面能打开但未解析到合适安装包，会继续尝试 GitHub API
- 若页面标题不是可靠版本号，会优先从发布链接中的 tag 提取版本
- 若页面版本与 API `latest` 不一致，会按页面识别到的 tag 请求对应版本的 API

可在 [`apps/root.json`](../apps/root.json) 根级增加可选配置：

```json
"release_page_mirrors": [
  "https://github.com",
  "https://你的自建镜像域名"
]
```

脚本会按顺序尝试这些发布页来源（具体以 `auto_update.py` 实现为准）。

---

## 下载目录与平台子目录

默认下载根目录由 [`apps/root.json`](../apps/root.json) 中的 `download_dir` 控制（例如 `"."` 或 `"downloads"`）。

当根级 **`download_subdir_by_platform` 为 `true`**（本仓库默认开启）时，实际保存路径为：

`{download_dir}/{windows|darwin|linux}/…`

便于在同一台机器上交叉执行 `--platform windows` / `darwin` / `linux` 时，安装包按系统类型分文件夹存放。日志中会标注 **`[平台: …]`** 与完整目标路径。压缩包下完后会打开该目录（Windows 选中文件）；exe/msi 仍按 `run_installer` 启动安装程序。

大文件经公共下载镜像（如 `gh-proxy.com` 等）时可能较慢；控制台会显示 **百分比（含小数）与已下/总大小（MiB）**，避免长时间停在「0%」的错觉。直连 GitHub 的备用 URL 会按脚本逻辑依次尝试。

若希望所有平台文件仍落在同一目录，可在 [`apps/root.json`](../apps/root.json) 中将 `download_subdir_by_platform` 设为 `false`。

---

## apps 常用字段

每条应用至少需要：

- `id`
- `releases_url`
- `repo_path`

常见可选字段：

- `enabled`：是否参与批量处理
- `installer_markers`：在发布页里识别安装包链接的关键字
- `download_names`：兜底拼接下载地址时使用的文件名模板（`{ver}` 为去掉 `v` 的版本号）
- `download_url_templates`：自定义备用下载地址模板，支持 `{ver}`（保留 `v`）与 `{ver_plain}`（去掉 `v`）
- `save_name`：本地保存文件名模板
- `windows_installer`：Windows 安装包模式（与 `installer_extensions` 等配合）
- `installer_extensions`：如 `.exe`、`.msi`
- `process_name`：安装前要结束的进程名（Windows）
- `kill_before_install`：安装前是否先结束进程
- `run_installer`：是否下载完成后自动启动安装程序（exe/msi）；压缩包始终只打开下载目录
- `url_hint`：页面兜底搜索时使用的关键字
- `href_exclude_substrings`：排除不需要的链接
- `installer_markers_match_all`：要求多个关键字同时命中
- `prefer_api_assets`：优先从 GitHub API 资产列表中选包（适合附件很多的仓库或 tag 无 `v` 前缀等场景）
- `version_tag_as_on_github`：`true` 时不强行给版本号加 `v`（适用于 tag 为 `0.11.7` 这类仓库）

更完整的字段说明见 [`apps/root.json`](../apps/root.json) 内 `_说明` 对象（仅供人阅读，脚本不使用以下划线开头的键）。

**`apps/root.json` 根级（非单条应用）常用**：`download_dir`、`ssl_verify`、`download_subdir_by_platform`（`true` 时下载落在 `download_dir/<windows|darwin|linux>/`）、`release_page_mirrors` 等。

---

## 当前需要注意

- 想 **立即稳定使用**，请优先启用 **已带完整匹配规则** 的条目（Windows 侧多数常用软件已配 `installer_markers` / `download_names` / `save_name` 等，但仍建议先对单个 `id` 试跑再批量定时）。
- 想让某条 **目录型/占位** 条目真正可自动下载，需补全 `installer_markers`、`download_names`、`save_name` 等。
- 下载结果为 **压缩包**（7z/zip/tar 等）时，脚本 **不会** 自动解压，也不会用关联程序打开压缩包本身，而是打开下载目录（Windows 会选中该文件）。exe/msi 仍可按 `run_installer` 自动运行安装程序。
- 个别条目（如 `nodejs`）含特殊逻辑：可能结合 `nodejs.org` 等官方地址，以脚本为准。
- **GitHub API 有未认证请求频率限制**；短时间对大量 `prefer_api_assets` 条目连跑可能触发 403，可隔段时间重试、配置网络代理，或为请求配置 GitHub 令牌（需自行在环境中使 `requests` 生效，本仓库不内置令牌逻辑）。
- 若某软件 **tag 与资产文件名规则不一致**（例如 tag 为 `release-1.x` 而包名为 `1.x`），可能无法仅靠 `{ver}` 模板拼对，需改配置或等脚本扩展；这类情况在 README 中无法穷举，以实际日志为准。

---

## 常见命令

```bash
pip install -r requirements.txt
python auto_update.py
python auto_update.py nodejs
python auto_update.py --platform windows
python auto_update.py --insecure
```

查找应用（不写盘）：

```bat
lookup_app.bat drawio
python lookup_app.py --no-prompt v2ray
search_soft_pages.bat
search_soft_pages.bat --stats
search_soft_pages.bat 7zip
```

---

## 日志与排错

- 运行日志：`update_log.txt`
- 各应用抓取到的发布页 HTML：`github_page_<platform>_<app_id>.html`（例如 `github_page_windows_obsidian.html`）
- 下载失败时优先检查：`releases_url` 是否可访问、是否已回退到官方页或 API、`installer_markers` / `download_names` / `download_url_templates` 是否仍与真实资产一致、网络与证书、是否命中 GitHub API 限流
- **`enabled`**：**批量** `python auto_update.py`（不带 id）只处理 `enabled: true`；**lookup 选 1/2** 或 **`auto_update.py <id>` 指定 id 时不要求 enabled**
- **`重复的 id`**：同一平台多个分片出现相同 `id` 时会报错；`auto_update --platform windows` 仅合并 **windows** 分片，其它平台的重复 id **不会挡住** 本次 Windows 下载。检查 `99-未匹配-windows分片.json` 是否与正式分片重复

---

## 维护工具（可选）

### 日常使用

| 目的 | 命令 |
|------|------|
| GitHub 清单模糊查找 / 加入更新列表 | `lookup_app.bat <关键词>`（见 §3） |
| 搜 Android APK / iOS 商店 | `lookup_mobile.bat` / `lookup_ios.bat` |
| 介绍页标题搜索 / 打开链接 | **`search_soft_pages.bat`**（无参数可交互输入） |
| 游戏页标题搜索（gamer520） | **`search_games.bat`** |
| 按列表一键更新 | **`run_saved_apps.bat`** 或 `python tools/run_saved_apps.py` |
| Windows 无 Python 打包 exe | `powershell -File tools\build_exe.ps1` → 复制 `dist/exe/*.exe` 到仓库根 |
| 刷新推荐导读 Markdown | `python tools/generate_recommended_md.py` |
| 打开分类展示页 | **`open_catalog.bat`**（[`catalog.html`](../catalog.html)） |
| 刷新分类展示页 [`catalog.html`](../catalog.html) | `python tools/generate_catalog_html.py` |
| 刷新 [`CATALOG.md`](../CATALOG.md) | `python tools/generate_catalog_index.py` |
| 刷新 [`CATALOG.mobile.md`](../CATALOG.mobile.md) | `python tools/generate_mobile_catalog_index.py` |

### enabled 与清单维护

- 将所有应用 JSON 中的 `enabled` 写回 `false`：项目根 **`reset_enabled_json.bat`** 或 `python tools/reset_enabled_json.py`（可加 `--dry-run` 预览；快照默认 `tools/last_enabled_before_reset.json`）
- 按快照恢复 `enabled`：项目根 **`apply_enabled_snapshot.bat`** 或 `python tools/apply_enabled_snapshot.py`
- 将 `apps/darwin.json`、`apps/linux.json` 按 windows 分片名拆到 `apps/darwin/`、`apps/linux/`：`python tools/split_darwin_linux_to_dirs.py`（会备份原单文件为 `*.json.bak`）
- 单文件与 `apps/` 目录的拆分与恢复说明见 [`apps/root.json`](../apps/root.json) 内 `_说明`

### 批量扩充收录（幂等脚本，勿重复执行）

| 脚本 | 用途 |
|------|------|
| `tools/import_dayanzai_windows.py --apply` | 从大眼仔旭 Windows 专区抓取开源 GitHub 项 |
| `tools/split_dayanzai_unmatched.py` | 将 `99-未匹配` 分片拆到各分类 |
| `tools/sync_dayanzai_to_darwin_linux.py` | Windows 新条目同步到 darwin/linux |
| `tools/append_catalog_batch5.py` … `batch11.py` | AI IDE、截图/OCR、跨平台缺口等（见 [`CATALOG.md`](../CATALOG.md)） |
| `tools/append_mobile_catalog_batch1.py` | 首批 Android APK + iOS App Store 占位（见 [`CATALOG.mobile.md`](../CATALOG.mobile.md)） |
| `tools/append_mobile_catalog_batch2.py` | v2rayNG、SmsForwarder（Android） |
| `tools/append_mobile_catalog_batch3.py` | 按桌面 30 分类大补 Android（约 +65 条） |
| `tools/append_mobile_catalog_batch4.py` | NipaPlay-Reload、NextPlayer、mpv-android（Android） |
| `tools/append_mobile_catalog_batch5.py` | Android 薄分类大补 + iOS App Store 占位扩展 |
| `tools/append_mobile_catalog_batch6.py` | Android / iOS 尽量全覆盖（batch5 后再 +77） |
| `tools/append_catalog_batch21.py` | macOS 装机必备官网/网页占位（对齐 Android） |
| `tools/append_mobile_catalog_batch9.py` | iOS 装机必备 App Store 占位（对齐 Android） |
| `tools/append_catalog_batch2.py` ~ `batch4.py` | 历史批处理（跨平台常用软件） |

### 介绍页监控（soft_page_check）

详见 [`tools/soft_page_check/README.md`](../tools/soft_page_check/README.md)。常用：`monthly_check.bat`、`monthly_check_site.bat`、`open_changed_site.bat`、`refresh_urls.bat`、`search_soft_pages.bat`（根目录）、`fetch_github_on_changes.bat`。
