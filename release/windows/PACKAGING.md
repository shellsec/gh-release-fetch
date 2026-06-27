# Windows 发布包说明

面向 **GitHub Releases** 上传的 Windows 便携 zip（含 exe，无需 Python）。

## 生成

在仓库根目录：

```powershell
powershell -ExecutionPolicy Bypass -File tools\pack_windows_release.ps1
```

指定版本号（写入 `VERSION.txt` 与 zip 文件名）：

```powershell
powershell -ExecutionPolicy Bypass -File tools\pack_windows_release.ps1 -Version 1.0.0
```

已打过 exe、只重新打包目录：

```powershell
powershell -ExecutionPolicy Bypass -File tools\pack_windows_release.ps1 -SkipBuild
```

## 输出

| 路径 | 说明 |
|------|------|
| `dist/release/gh-release-fetch-windows-<版本>/` | 解压后的目录结构（可本地试跑） |
| `dist/release/gh-release-fetch-windows-<版本>.zip` | **上传到 Release 的文件** |

未指定 `-Version` 时，版本名取自 `git describe --tags`，否则用当天日期 `yyyyMMdd`。

## zip 内容

- 4 个 exe + 4 个 bat（lookup / saved / search / update）
- `apps/`、`apps-mobile/`
- `tools/soft_page_check/`（`history`、`list` 等，供 search_soft_pages）
- `README.txt`、`VERSION.txt`、`saved_apps_windows.example.json`
- `CATALOG.md`、`RECOMMENDED.zh-CN.md` 等导读（可选阅读）

不含 Python 源码与维护脚本（`monthly_check` 等请用完整仓库）。

## Release 上传建议

1. 创建 GitHub Release，打 tag（如 `v1.0.0`）
2. 附件上传 `gh-release-fetch-windows-v1.0.0.zip`
3. 说明中写：解压即用，`lookup_app.bat` 搜软件下载
