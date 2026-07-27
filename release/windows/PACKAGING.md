# Windows 发布包说明

面向 **GitHub Releases** 上传的 Windows 便携 zip（含 exe，无需 Python）。

## 生成

在仓库根目录 **一键**（编译 exe → 复制到根目录 → 打 zip）：

```bat
pack_windows_release.bat
```

指定版本号（传给打包脚本，写入 `VERSION.txt` 与 zip 文件名）：

```bat
pack_windows_release.bat -Version 1.0.0
```

或分步 / 仅用 PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File tools\build_exe.ps1
Copy-Item dist\exe\*.exe .
powershell -ExecutionPolicy Bypass -File tools\pack_windows_release.ps1 -SkipBuild
```

完整打包（脚本内会先编译 exe，再复制、再打 zip）：

```powershell
powershell -ExecutionPolicy Bypass -File tools\pack_windows_release.ps1
```

## 输出

| 路径 | 说明 |
|------|------|
| `dist/release/gh-release-fetch-windows-<版本>/` | 解压后的目录结构（可本地试跑） |
| `dist/release/gh-release-fetch-windows-<版本>.zip` | **上传到 Release 的文件** |

未指定 `-Version` 时，版本名取自 `git describe --tags`，否则用当天日期 `yyyyMMdd`。

## zip 内容

- 5 个 exe + 5 个 bat（lookup / saved / search_soft / search_games / update）
- `apps/`、`apps-mobile/`
- `tools/soft_page_check/`（`history`、`list` 等，供 search_soft_pages / search_games）
- `README.txt`、`VERSION.txt`、`saved_apps_windows.example.json`
- `CATALOG.md`、`RECOMMENDED.zh-CN.md` 等导读（可选阅读）
- `VibeCodingToolsDown/dist/vibecoding/manifest.json`（Cursor / VS Code / Trae / VirtualBox 等 manifest 解析用的本地 snapshot）

不含 Python 源码与维护脚本（含 `VibeCodingToolsDown/scripts/build_manifest.py`；因此便携包**不会**在下载前联网刷新 manifest，需靠打包时写入的 snapshot。完整仓库或自带 scripts 时可由 `refresh_manifest_before_resolve` 自动刷新）。`monthly_check` 等请用完整仓库。

## Release 上传建议

1. 创建 GitHub Release，打 tag（如 `v1.0.0`）
2. 附件上传 `gh-release-fetch-windows-v1.0.0.zip`
3. 说明中写：解压即用，`lookup_app.bat` 搜软件下载
