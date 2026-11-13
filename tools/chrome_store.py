"""Chrome Web Store input and Google-hosted CRX downloads."""
from pathlib import Path
import re
import struct
from urllib.parse import urlencode, urljoin, urlsplit
import zipfile

import requests

from tools.download_engine import download_url


STORE = "https://chromewebstore.google.com"
UPDATE = "https://clients2.google.com/service/update2/crx"
EXTENSION_ID = re.compile(r"[a-p]{32}", re.ASCII)


def extension_id(source):
    """Return None for other sources and reject invalid Chrome Store links."""
    if EXTENSION_ID.fullmatch(source):
        return source
    url = urlsplit(source)
    legacy = url.hostname == "chrome.google.com" and url.path.startswith("/webstore")
    if url.hostname != "chromewebstore.google.com" and not legacy:
        return None
    path = url.path.removeprefix("/webstore") if legacy else url.path
    match = re.fullmatch(r"/detail/(?:[^/]+/)?([a-p]{32})/?", path)
    if url.scheme != "https" or url.netloc.lower() != url.hostname or not match:
        raise ValueError("请粘贴 Chrome 商店扩展详情页链接或 32 位扩展 ID")
    return match[1]


def store_url(item):
    return f"{STORE}/detail/{item}"


def update_url(item):
    # Chrome protocol compatibility version for requesting a CRX3 package.
    return UPDATE + "?" + urlencode({
        "response": "redirect", "prodversion": "157.0.8103.78",
        "acceptformat": "crx3", "x": f"id={item}&uc",
    })


def google_get(url, **kwargs):
    # Google's CRX CDN ignores Range when If-Range carries its ETag.
    # The engine compares the returned ETag and byte range before writing.
    headers = dict(kwargs.pop("headers", {}))
    headers.pop("If-Range", None)
    for _ in range(6):
        parsed = urlsplit(url)
        host = parsed.hostname or ""
        if (parsed.scheme != "https" or parsed.netloc.lower() != host
                or not host.endswith((".google.com", ".googleusercontent.com", ".gstatic.com"))):
            raise ValueError("Chrome 下载跳转地址不属于 Google")
        response = requests.get(url, headers=headers, allow_redirects=False, **kwargs)
        if response.is_redirect:
            with response:
                url = urljoin(url, response.headers["Location"])
            continue
        if response.status_code in (204, 404):
            response.close()
            raise ValueError("Google 未提供可下载的 CRX，请检查扩展 ID 或打开商店详情页")
        return response
    raise ValueError("Chrome 下载跳转次数过多")


def validate_crx(path):
    with path.open("rb") as file:
        header = file.read(12)
        if len(header) != 12:
            raise ValueError("CRX 文件头不完整")
        magic, version, header_size = struct.unpack("<4sII", header)
        if magic != b"Cr24" or version != 3 or not header_size:
            raise ValueError("文件不是 CRX3")
        file.seek(header_size, 1)
        if file.read(4) != b"PK\x03\x04":
            raise ValueError("CRX3 缺少扩展内容")
    try:
        with zipfile.ZipFile(path) as archive:
            if "manifest.json" not in archive.namelist() or archive.testzip() is not None:
                raise ValueError("CRX3 扩展内容不完整")
    except zipfile.BadZipFile as exc:
        raise ValueError("CRX3 扩展内容损坏") from exc


def download_crx(item, target, *, threads=4, report=print, cancelled=None):
    target = Path(target)
    if target.suffix.lower() != ".crx":
        raise ValueError("请使用 .crx 文件名")
    if target.exists():
        raise ValueError(f"目标已存在，请换一个路径：{target}")
    return download_url(update_url(item), target, threads=threads, validator=validate_crx,
                        report=report, cancelled=cancelled,
                        request=google_get, min_parallel_size=256 * 1024)
