#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""生成可本地打开的多平台分类展示页 catalog.html。"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from tools.app_list import CATALOGS, PLATFORMS
from tools.app_download import is_app_downloadable, resolve_open_page_url

OUT = os.path.join(ROOT, "catalog.html")
SHARD_RE = re.compile(r"^(\d+)-(.+)\.json$", re.UNICODE)
CHROME_DETAIL_RE = re.compile(r"https://chromewebstore\.google\.com/detail/(?:[^/?#]+/)?([a-p]{32})/?(?:[?#].*)?")


def collect() -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {p: [] for p in PLATFORMS}
    for _, directory, plat, _ in CATALOGS:
        plat_dir = os.path.join(ROOT, directory, plat)
        if not os.path.isdir(plat_dir):
            continue
        for name in sorted(os.listdir(plat_dir)):
            if not name.endswith(".json") or name.startswith("99-"):
                continue
            m = SHARD_RE.match(name)
            shard_cat = m.group(2) if m else name.replace(".json", "")
            with open(os.path.join(plat_dir, name), encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                continue
            for app in data:
                if not isinstance(app, dict) or not (app.get("id") or "").strip():
                    continue
                aliases = app.get("aliases") or []
                if isinstance(aliases, str):
                    aliases = [aliases]
                page = resolve_open_page_url(app)
                chrome_detail = CHROME_DETAIL_RE.fullmatch(app.get("chrome_store_url") or page)
                out[plat].append(
                    {
                        "id": (app.get("id") or "").strip(),
                        "intro": (app.get("简介") or "").strip(),
                        "cat": (app.get("分类") or "").strip() or shard_cat,
                        "subcategory": (app.get("子分类") or "").strip(),
                        "shard": name,
                        "repo": (app.get("repo_path") or "").strip(),
                        "url": page,
                        "chrome_id": chrome_detail[1] if chrome_detail else "",
                        "dl": is_app_downloadable(app),
                        "page": app.get("open_page_only") is True,
                        "aliases": [str(a) for a in aliases if str(a).strip()],
                    }
                )
    return out


HTML_TMPL = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="catalog-session" content="">
<title>GH Release Fetch · 分类目录</title>
<style>
:root {
  --bg: #0f1419;
  --panel: #1a222c;
  --panel2: #222c38;
  --line: #2e3a48;
  --text: #e7edf4;
  --muted: #8b9bb0;
  --accent: #5b9fd4;
  --ok: #3dba8b;
  --page: #d4a017;
}
* { box-sizing: border-box; }
html, body { margin: 0; background: var(--bg); color: var(--text); font: 15px/1.45 "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
header {
  padding: 20px 24px 12px;
  border-bottom: 1px solid var(--line);
  background: linear-gradient(180deg, #15202b, var(--bg));
  position: sticky; top: 0; z-index: 5;
}
h1 { margin: 0 0 6px; font-size: 22px; font-weight: 650; }
.sub { color: var(--muted); font-size: 13px; }
.toolbar { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; align-items: center; }
.plats button, .modes button {
  background: var(--panel); color: var(--text); border: 1px solid var(--line);
  border-radius: 999px; padding: 6px 14px; cursor: pointer; font: inherit;
}
.plats button.on, .modes button.on { background: var(--accent); color: #072033; border-color: var(--accent); font-weight: 600; }
input[type=search] {
  flex: 1; min-width: 220px; background: var(--panel); color: var(--text);
  border: 1px solid var(--line); border-radius: 8px; padding: 8px 12px; font: inherit;
}
.stats { color: var(--muted); font-size: 13px; }
.layout { display: grid; grid-template-columns: 220px 1fr; min-height: calc(100vh - 140px); }
nav {
  border-right: 1px solid var(--line); padding: 12px; overflow: auto; max-height: calc(100vh - 140px);
  position: sticky; top: 140px;
}
nav button {
  display: flex; justify-content: space-between; width: 100%;
  background: transparent; color: var(--text); border: 0; border-radius: 8px;
  padding: 7px 10px; cursor: pointer; font: inherit; text-align: left;
}
nav button:hover { background: var(--panel); }
nav button.on { background: var(--panel2); color: var(--accent); }
nav .n { color: var(--muted); font-size: 12px; }
main { padding: 16px 20px 40px; }
.cat-title { margin: 8px 0 12px; font-size: 18px; }
.batch { margin: 10px 0; color: var(--muted); font-size: 13px; }
.batch input { display: block; width: 100%; margin-top: 6px; }
.batch-choice { display: block; margin-top: 8px; font-size: 13px; }
#downloadLog { max-height: 18rem; overflow: auto; white-space: pre-wrap; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; }
.card {
  background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px;
}
.card h3 { margin: 0 0 4px; font-size: 15px; font-weight: 650; }
.meta { color: var(--muted); font-size: 12px; word-break: break-all; }
.intro { margin: 8px 0; color: #c5d0dc; font-size: 13px; min-height: 2.6em; }
.badge { display: inline-block; font-size: 11px; border-radius: 999px; padding: 2px 8px; margin-right: 6px; font-weight: 600; }
.badge.dl { background: rgba(61,186,139,.18); color: var(--ok); }
.badge.pg { background: rgba(212,160,23,.18); color: var(--page); }
.empty { color: var(--muted); padding: 40px 8px; }
footer { color: var(--muted); font-size: 12px; padding: 8px 24px 20px; }
@media (max-width: 800px) {
  .layout { grid-template-columns: 1fr; }
  nav { position: static; max-height: none; border-right: 0; border-bottom: 1px solid var(--line); display: flex; flex-wrap: wrap; gap: 6px; }
  nav button { width: auto; }
}
</style>
</head>
<body>
<header>
  <h1>开源与必备软件目录</h1>
  <div class="sub" id="downloadHint">通过 open_catalog.bat 打开可使用网页批量下载 · __DATE__</div>
  <div class="toolbar">
    <div class="plats" id="plats"></div>
    <div class="modes" id="modes"></div>
    <input type="search" id="q" placeholder="搜索名称、id、别名、分类…" autocomplete="off">
    <div class="stats" id="stats"></div>
  </div>
</header>
<div class="layout">
  <nav id="cats"></nav>
  <main>
    <h2 class="cat-title" id="catTitle"></h2>
    <label id="subcategoryFilter" hidden>用途 <select id="subcategory"></select></label>
    <div class="batch" id="downloadBatch" hidden>
      <button type="button" id="startBatch" hidden>批量下载</button>
      <button type="button" id="copyBatch">复制下载清单</button>
      <button type="button" id="clearBatch">清空选择</button>
      <span id="batchStatus" role="status"></span>
      <input id="batchList" aria-label="批量下载清单" readonly>
    </div>
    <p id="downloadStatus" role="status"></p>
    <pre id="downloadLog" hidden></pre>
    <div class="grid" id="grid"></div>
  </main>
</div>
<footer>lookup：<code>lookup_app.bat &lt;id&gt;</code> · 可下载项走 GitHub/CDN；「仅官网」选中后打开官方下载页。</footer>
<script id="data" type="application/json">__DATA__</script>
<script>
const DATA = JSON.parse(document.getElementById("data").textContent);
const PLATS = __PLATFORMS__;
const MODES = [["all","全部"],["dl","可下载"],["page","仅官网"]];
let plat = "windows", mode = "all", cat = "", subcategory = "", q = "";
const selectedItems = new Set();
const session = document.querySelector('meta[name="catalog-session"]').content;
const startBatch = document.getElementById("startBatch");
const downloadStatus = document.getElementById("downloadStatus");
const downloadLog = document.getElementById("downloadLog");
if (session) {
  startBatch.hidden = false;
  document.getElementById("copyBatch").hidden = true;
  document.getElementById("batchList").hidden = true;
  document.getElementById("downloadHint").textContent = "勾选多个平台的条目，再点「批量下载」。文件按平台保存。";
}

function renderDownloadBatch() {
  const count = selectedItems.size;
  document.getElementById("downloadBatch").hidden = !count;
  document.getElementById("batchList").value = [...selectedItems].join(" ");
  document.getElementById("batchStatus").textContent = session ? `已选 ${count} 项` : `已选 ${count} 项，复制后粘贴到菜单 15`;
}

function titleOf(row) {
  const intro = (row.intro || "").replace("（来源：dayanzai）","").trim();
  if (intro) {
    const head = intro.split(/[，,。]/)[0].trim();
    if (head.length >= 2 && head.length <= 48) return head;
  }
  return row.id.replaceAll("_", " ");
}
function rows() {
  const list = DATA[plat] || [];
  const qq = q.trim().toLowerCase();
  return list.filter(r => {
    if (mode === "dl" && !r.dl && !r.chrome_id) return false;
    if (mode === "page" && (!r.page || r.chrome_id)) return false;
    if (cat && r.cat !== cat) return false;
    if (subcategory && r.subcategory !== subcategory) return false;
    if (!qq) return true;
    const blob = [r.id, r.intro, r.cat, r.subcategory, r.repo, ...(r.aliases||[])].join(" ").toLowerCase();
    return blob.includes(qq);
  });
}
function catsOf(list) {
  const m = new Map();
  for (const r of list) m.set(r.cat, (m.get(r.cat)||0)+1);
  return [...m.entries()];
}
function render() {
  const all = DATA[plat] || [];
  const filtered = rows();
  document.getElementById("plats").innerHTML = PLATS.map(([k,l]) =>
    `<button class="${k===plat?"on":""}" data-p="${k}">${l} (${(DATA[k]||[]).length})</button>`
  ).join("");
  document.getElementById("modes").innerHTML = MODES.map(([k,l]) =>
    `<button class="${k===mode?"on":""}" data-m="${k}">${l}</button>`
  ).join("");
  const catCounts = catsOf((DATA[plat]||[]).filter(r => {
    if (mode === "dl" && !r.dl && !r.chrome_id) return false;
    if (mode === "page" && (!r.page || r.chrome_id)) return false;
    return true;
  }));
  const catTotal = catCounts.reduce((s, x) => s + x[1], 0);
  document.getElementById("cats").innerHTML =
    `<button class="${!cat?"on":""}" data-c="">全部分类<span class="n">${catTotal}</span></button>` +
    catCounts.map(([c,n]) => `<button class="${c===cat?"on":""}" data-c="${esc(c)}">${esc(c)}<span class="n">${n}</span></button>`).join("");
  document.getElementById("catTitle").textContent = cat || "全部分类";
  const subcategories = [...new Set(all.filter(r => r.cat === cat && r.subcategory)
    .map(r => r.subcategory))].sort((a, b) => a.localeCompare(b, "zh-CN"));
  const subcategorySelect = document.getElementById("subcategory");
  document.getElementById("subcategoryFilter").hidden = !subcategories.length;
  subcategorySelect.innerHTML = '<option value="">全部用途</option>' +
    subcategories.map(name => `<option value="${esc(name)}">${esc(name)}</option>`).join("");
  subcategorySelect.value = subcategory;
  document.getElementById("stats").textContent =
    `${PLATFORM_LABEL()} · 显示 ${filtered.length} / ${all.length}`;
  renderDownloadBatch();
  const grid = document.getElementById("grid");
  if (!filtered.length) {
    grid.innerHTML = `<div class="empty">没有匹配的条目</div>`;
    return;
  }
  grid.innerHTML = filtered.map(r => {
    const badge = r.chrome_id ? `<span class="badge dl">CRX</span>` :
      r.page ? `<span class="badge pg">仅官网</span>` :
      (r.dl ? `<span class="badge dl">可下载</span>` : `<span class="badge pg">仅页面</span>`);
    const repo = r.repo ? ` · ${r.repo}` : "";
    const link = /^https?:\/\//i.test(r.url) ? `<a href="${esc(r.url)}" target="_blank" rel="noopener">打开页面</a>` : "";
    const token = `catalog:${plat}/${encodeURIComponent(r.id)}`;
    const choice = r.chrome_id || r.dl ? "加入下载" : link ? "加入清单（打开页面）" : "";
    const checkbox = choice ? `<label class="batch-choice"><input type="checkbox" data-download="${esc(token)}"
      ${selectedItems.has(token) ? "checked" : ""}> ${choice}</label>` : "";
    return `<article class="card">
      <h3>${esc(titleOf(r))}</h3>
      <div class="meta">${badge}<code>${esc(r.id)}</code>${esc(repo)}</div>
      <div class="intro">${esc(r.intro || "（见仓库说明）")}</div>
      <div class="meta">${esc(r.cat)} · ${esc(r.subcategory || r.shard)} ${link ? "· "+link : ""}</div>
      ${checkbox}
    </article>`;
  }).join("");
}
function PLATFORM_LABEL(){ return Object.fromEntries(PLATS)[plat]; }
function esc(s){ return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

document.getElementById("plats").addEventListener("click", e => {
  const b = e.target.closest("button[data-p]"); if (!b) return; plat = b.dataset.p; cat = ""; subcategory = ""; render();
});
document.getElementById("modes").addEventListener("click", e => {
  const b = e.target.closest("button[data-m]"); if (!b) return; mode = b.dataset.m; render();
});
document.getElementById("cats").addEventListener("click", e => {
  const b = e.target.closest("button[data-c]"); if (!b) return; cat = b.dataset.c; subcategory = ""; render();
});
document.getElementById("subcategory").addEventListener("change", e => {
  subcategory = e.target.value;
  render();
});
document.getElementById("q").addEventListener("input", e => { q = e.target.value; render(); });
document.getElementById("grid").addEventListener("change", e => {
  const id = e.target.dataset.download;
  if (!id) return;
  if (e.target.checked) selectedItems.add(id);
  else selectedItems.delete(id);
  renderDownloadBatch();
});
document.getElementById("clearBatch").addEventListener("click", () => {
  selectedItems.clear();
  render();
});
document.getElementById("copyBatch").addEventListener("click", async () => {
  const list = document.getElementById("batchList");
  try {
    await navigator.clipboard.writeText(list.value);
    document.getElementById("batchStatus").textContent = "已复制，到菜单 15 粘贴下载清单";
  } catch {
    list.select();
    document.getElementById("batchStatus").textContent = "已选中文本，请手动复制后粘贴到菜单 15";
  }
});

async function downloadRequest(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {"X-Catalog-Session": session, ...options.headers},
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || "下载请求失败");
  return result;
}

startBatch.addEventListener("click", async () => {
  if (!selectedItems.size || startBatch.disabled) return;
  startBatch.disabled = true;
  downloadStatus.textContent = "正在提交下载清单…";
  downloadLog.textContent = "";
  downloadLog.hidden = false;
  try {
    const {job} = await downloadRequest("/api/download", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify([...selectedItems]),
    });
    downloadStatus.textContent = "正在处理选中的条目…";
    while (true) {
      const result = await downloadRequest(`/api/download/${job}`);
      downloadLog.textContent = result.lines.join("\n");
      downloadLog.scrollTop = downloadLog.scrollHeight;
      if (result.code !== null) {
        downloadStatus.textContent = result.code === 0 ? "批量下载已完成" : "部分条目处理失败，请查看下载日志";
        break;
      }
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  } catch (error) {
    downloadStatus.textContent = error.message;
  } finally {
    startBatch.disabled = false;
  }
});
render();
</script>
</body>
</html>
"""


def main() -> None:
    data = collect()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace(
        "</", "<\\/"
    )
    platforms = json.dumps([(plat, label) for label, _, plat, _ in CATALOGS], ensure_ascii=False)
    html = HTML_TMPL.replace("__DATE__", now).replace("__PLATFORMS__", platforms).replace("__DATA__", payload)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    counts = ", ".join("%s %d" % (p, len(data[p])) for p in PLATFORMS)
    print("Wrote", OUT, "(" + counts + ")")


if __name__ == "__main__":
    main()
