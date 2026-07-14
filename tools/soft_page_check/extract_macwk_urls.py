#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""从 macwk.com /soft/all/pN 分页抓取 Mac 软件详情页 URL（全量约 174 条）。"""
from __future__ import annotations

import argparse
import html as html_lib
import re
import ssl
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
OUT = HERE / "list" / "macwk_urls.txt"
OUT_LIST = HERE / "list" / "macwk_list.txt"

BASE = "https://www.macwk.com"
LISTING_BASE = f"{BASE}/soft/all"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
TIMEOUT = 25
CTX = ssl.create_default_context()
PAGE_SLEEP = 0.5
MIN_NEW_PER_PAGE = 5

HREF_PAT = re.compile(r"""href\s*=\s*['"]([^'"]+)['"]""", re.I)
CARD_PAT = re.compile(
    r"""href\s*=\s*['"](/soft/[^'"]+)['"][^>]*class\s*=\s*['"]macwk-app\b[^'"]*['"]"""
    r""".*?macwk-app__body--title[^>]*>.*?<span>([^<]+)</span>""",
    re.I | re.S,
)
SOFT_PATH = re.compile(r"^/soft/([^/]+)$")


def fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=TIMEOUT, context=CTX) as resp:
        return resp.read().decode(resp.headers.get_content_charset() or "utf-8", errors="replace")


def listing_url(page: int) -> str:
    return f"{LISTING_BASE}/p{max(1, page)}"


def normalize_soft_url(href: str) -> str | None:
    u = urljoin(BASE + "/", href.split("#")[0].strip())
    parsed = urlparse(u)
    if parsed.netloc.lower() not in ("www.macwk.com", "macwk.com"):
        return None
    m = SOFT_PATH.match(parsed.path or "")
    if not m:
        return None
    slug = m.group(1).lower()
    if slug in ("all",):
        return None
    return f"{BASE}/soft/{slug}"


def clean_title(raw: str) -> str:
    return html_lib.unescape(re.sub(r"\s+", " ", raw)).strip()


def extract_from_listing(html: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for href, raw_title in CARD_PAT.findall(html):
        url = normalize_soft_url(href)
        if not url:
            continue
        title = clean_title(raw_title)
        if title:
            found[url] = title
    if found:
        return found
    for href in HREF_PAT.findall(html):
        url = normalize_soft_url(href)
        if url:
            found.setdefault(url, "")
    return found


def crawl(max_pages: int, min_new: int) -> tuple[dict[str, str], int]:
    found: dict[str, str] = {}
    last_page = 0
    for page in range(1, max(1, max_pages) + 1):
        url = listing_url(page)
        try:
            html = fetch(url)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            print(f"  [warn] {url} -> {exc}", file=sys.stderr)
            break
        batch = extract_from_listing(html)
        new_urls = 0
        for url, title in batch.items():
            if url not in found:
                found[url] = title
                new_urls += 1
            elif title and not found.get(url):
                found[url] = title
        titled = sum(1 for t in found.values() if t)
        print(f"  page {page}: +{new_urls} url (累计 {len(found)}, 有标题 {titled})")
        last_page = page
        if page > 1 and new_urls < min_new:
            print(f"  本页新增 {new_urls} < {min_new}，停止翻页")
            break
        if page < max_pages:
            time.sleep(PAGE_SLEEP)
    return found, last_page


def main() -> None:
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass

    ap = argparse.ArgumentParser(description="抓取 macwk.com 全部软件列表 URL")
    ap.add_argument("--max-pages", type=int, default=20, help="最多翻页数（默认 20，遇空页自动停）")
    ap.add_argument(
        "--min-new",
        type=int,
        default=MIN_NEW_PER_PAGE,
        help=f"单页新增少于此数则停止（默认 {MIN_NEW_PER_PAGE}）",
    )
    args = ap.parse_args()

    print(f"抓取 {LISTING_BASE}/p1 … p{args.max_pages}")
    items, pages_done = crawl(args.max_pages, args.min_new)
    urls = sorted(items.keys())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "# macwk.com Mac 软件（extract_macwk_urls.py 生成）",
        f"# pages=1..{pages_done} count={len(urls)}",
        "# 列表: https://www.macwk.com/soft/all/p1",
        "# 标题见 macwk_list.txt",
    ]
    OUT.write_text("\n".join(header + [""] + urls) + ("\n" if urls else ""), encoding="utf-8")
    list_lines = [f"{items[u] or '(列表页无标题)'}\t{u}" for u in urls]
    list_header = [
        "# title<TAB>url — search_pages 搜索用（列表页标题，非逐页 fetch）",
        f"# pages=1..{pages_done} count={len(list_lines)}",
    ]
    OUT_LIST.write_text(
        "\n".join(list_header + [""] + list_lines) + ("\n" if list_lines else ""),
        encoding="utf-8",
    )
    print(f"已写入 {len(urls)} 条 -> {OUT}")
    print(f"已写入 {len(list_lines)} 条 -> {OUT_LIST}")


if __name__ == "__main__":
    main()
