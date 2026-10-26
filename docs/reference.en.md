# Configuration and maintenance reference

[Back to the user guide](../README.md)

## Force a platform block

```bash
python auto_update.py --platform windows
python auto_update.py nodejs --platform windows
```

---

## TLS issues

```bash
python auto_update.py --insecure
```

Or in [`apps/root.json`](../apps/root.json): `"ssl_verify": false` (temporary).

---

## Mirrors and fallback

Order of operations (see [`auto_update.py`](../auto_update.py) for details): entry `releases_url` → on failure, `https://github.com/<owner>/<repo>/releases` → optional API. Optional root `release_page_mirrors` list for extra release-page hosts.

---

## Download directory and per-platform folders

`download_dir` in [`apps/root.json`](../apps/root.json) sets the root (e.g. `"."` or `"downloads"`).

If **`download_subdir_by_platform`** is `true` (default in this repo), files go under:

`{download_dir}/{windows|darwin|linux}/…`

Logs include **`[platform: …]`** and the resolved target directory. Large files via public proxies may be slow; the console shows **percent (with decimals) and MiB** to avoid a stuck “0%” display. Direct GitHub URLs are tried in the script’s mirror chain.

---

## Common app JSON fields

Required: `id`, `releases_url`, `repo_path`.

Useful optional fields: `enabled`, `installer_markers`, `download_names`, `download_url_templates`, `save_name`, `windows_installer`, `installer_extensions`, `process_name`, `kill_before_install`, `run_installer`, `url_hint`, `href_exclude_substrings`, `installer_markers_match_all`, `prefer_api_assets`, `version_tag_as_on_github`.

Human-oriented field glossary: `_说明` inside [`apps/root.json`](../apps/root.json) (keys starting with `_` are not consumed by the script).

Root keys: `download_dir`, `ssl_verify`, `download_subdir_by_platform`, `release_page_mirrors`, etc.

---

## Caveats

- Prefer **fully specified rules** before enabling many apps for cron; smoke-test single `id` first.
- Archives (7z/zip/tar, etc.) are **not** auto-extracted or opened with their associated app; after download the folder is opened in the file manager (Windows selects the file). exe/msi still auto-run when `run_installer` is true.
- Special cases (e.g. `nodejs`) may use extra official URLs — see script.
- **Unauthenticated GitHub API** rate limits can return 403; retry later, use a proxy, or wire a token into your environment for `requests` (not built into this repo).
- If **tag names and file names diverge** (e.g. `release-1.x` vs `1.x` in the asset), `{ver}` templates may need manual tuning.

---

## Common commands

```bash
pip install -r requirements.txt
python auto_update.py
python auto_update.py nodejs
python auto_update.py --platform windows
python auto_update.py --insecure
lookup_app.bat drawio
python lookup_app.py --no-prompt v2ray
```

```bat
search_soft_pages.bat
search_soft_pages.bat --stats
search_soft_pages.bat 7zip
```

---

## Logs and troubleshooting

- Log file: `update_log.txt`
- Saved release HTML: `github_page_<platform>_<app_id>.html` (e.g. `github_page_windows_obsidian.html`)
- On failure: check `releases_url`, fallbacks, markers / `download_url_templates` vs real asset names, TLS, API rate limits
- **`enabled`**: **batch** `auto_update.py` (no ids) only runs `enabled: true` rows; **lookup options 1/2** or **`auto_update.py <id>`** do **not** require `enabled`
- **Duplicate `id`**: same-platform duplicates fail merge; with `--platform windows` only **windows** shards load — duplicates on other platforms do not block that run. Remove stale rows from `99-未匹配-windows分片.json` if needed

---

## Maintenance scripts

### Daily use

| Goal | Command |
|------|---------|
| Fuzzy search GitHub catalog / saved list | `lookup_app.bat <keyword>` (§3) |
| Search Android APK / iOS App Store | `lookup_mobile.bat` / `lookup_ios.bat` |
| Search intro-page titles / open URLs | **`search_soft_pages.bat`** (no-arg interactive) |
| Search game pages (gamer520) | **`search_games.bat`** |
| Update from saved list | **`run_saved_apps.bat`** or `python tools/run_saved_apps.py` |
| Build Windows exe (no Python for daily use) | `powershell -File tools\build_exe.ps1` → copy `dist/exe/*.exe` to repo root |
| **Pack Release zip (one-click)** | **`pack_windows_release.bat`** or `tools\pack_windows_release.ps1` |
| Regenerate RECOMMENDED*.md | `python tools/generate_recommended_md.py` |
| Open local catalog page | **`open_catalog.bat`** ([`catalog.html`](../catalog.html)) |
| Regenerate [`catalog.html`](../catalog.html) | `python tools/generate_catalog_html.py` |
| Refresh [`CATALOG.md`](../CATALOG.md) | `python tools/generate_catalog_index.py` |

### enabled & layout

- Reset all `enabled` to `false`: **`reset_enabled_json.bat`** at repo root, or `python tools/reset_enabled_json.py` (`--dry-run` to preview; snapshot defaults to `tools/last_enabled_before_reset.json`)
- Restore `enabled` from snapshot: **`apply_enabled_snapshot.bat`** or `python tools/apply_enabled_snapshot.py`
- Split legacy `apps/darwin.json` / `apps/linux.json` into shard dirs: `python tools/split_darwin_linux_to_dirs.py` (backs up `*.json.bak`)
- Monolith vs `apps/` notes: [`apps/root.json`](../apps/root.json) → `_说明`

### Bulk catalog import (idempotent; do not re-run blindly)

| Script | Purpose |
|--------|---------|
| `tools/import_dayanzai_windows.py --apply` | Import open-source GitHub rows from dayanzai.me/windows |
| `tools/split_dayanzai_unmatched.py` | Move `99-未匹配` rows into category shards |
| `tools/sync_dayanzai_to_darwin_linux.py` | Mirror new Windows rows to darwin/linux |
| `tools/append_catalog_batch2.py` … `batch4.py` | Historical cross-platform batches |
| `tools/append_catalog_batch5.py` … `batch11.py` | AI IDE、截图/OCR、跨平台缺口等（见 [`CATALOG.md`](../CATALOG.md)） |

### Intro-page monitoring

See [`tools/soft_page_check/README.md`](../tools/soft_page_check/README.md). Common entry points: `monthly_check.bat`, `monthly_check_site.bat`, `open_changed_site.bat`, `refresh_urls.bat`, root `search_soft_pages.bat`, `fetch_github_on_changes.bat`.

---

*Former working title: **GithubWinDownTools** — renamed for clarity now that darwin/linux catalogs are first-class.*

