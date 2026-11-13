"""Bounded route probing and resumable, validated HTTP downloads."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import threading
import time
from urllib.parse import urlsplit

import requests

# Candidate services, not a promise of availability. Direct is always included.
ROUTES = (
    ("direct", ""), ("gh-proxy.com", "https://gh-proxy.com/"),
    ("ghfast.top", "https://ghfast.top/"), ("ghproxy.net", "https://ghproxy.net/"),
    ("gh.llkk.cc", "https://gh.llkk.cc/"),
    ("gh.api.99988866.xyz", "https://gh.api.99988866.xyz/"),
    ("cors.isteed.cc", "https://cors.isteed.cc/"),
    ("mirror.ghproxy.com", "https://mirror.ghproxy.com/"),
)
HEADERS = {"User-Agent": "GH-Release-Fetch", "Accept-Encoding": "identity"}
_route_cache = {}
_route_lock = threading.Lock()


class RangeUnavailable(ValueError):
    pass


class DownloadPaused(Exception):
    pass


def check_pause(cancelled):
    if cancelled and cancelled():
        raise DownloadPaused("已暂停，分片已保留")


def available_target(path):
    """Keep existing files and other tasks' partial downloads intact."""
    path = Path(path)
    candidate = path
    counter = 1
    while candidate.exists() or candidate.with_name(candidate.name + ".parts").exists():
        counter += 1
        candidate = path.with_name(f"{path.stem} ({counter}){path.suffix}")
    return candidate


def atomic_json(path, data):
    path = Path(path)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temp, path)


def probe(url):
    start = time.monotonic()
    with requests.get(url, headers={**HEADERS, "Range": "bytes=0-262143"},
                      stream=True, timeout=(4, 4)) as response:
        response.raise_for_status()
        if "text/html" in response.headers.get("Content-Type", "").lower():
            raise ValueError("线路返回网页")
        count = 0
        for chunk in response.iter_content(32768):
            count += len(chunk)
            if count >= 262144 or time.monotonic() - start >= 3:
                break
        if not count:
            raise ValueError("线路返回空文件")
    return count / max(time.monotonic() - start, .001)


def ranked_routes(url, route="auto", report=print):
    address = urlsplit(url)
    if address.query or address.username is not None:
        return [("direct", url)]
    candidates = [(name, prefix + url) for name, prefix in ROUTES]
    if route != "auto":
        return [next((item for item in candidates if item[0] == route), None)] if route in dict(ROUTES) else []
    with _route_lock:
        cached = _route_cache.get(address.hostname)
    if cached and time.monotonic() - cached[0] < 300:
        order = cached[1]
        return sorted(candidates, key=lambda item: order.index(item[0]))
    def check(item):
        name, target = item
        try:
            speed = probe(target)
            report(f"{name}: {speed / 1048576:.2f} MiB/s")
            return speed, item
        except (requests.RequestException, ValueError) as exc:
            report(f"{name}: 不可用 ({exc})")
            return -1, item
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(check, candidates))
    # Retain failed probes as last-resort candidates (e.g. transient failures).
    ordered = [item for _, item in sorted(results, key=lambda row: row[0], reverse=True)]
    if any(speed > 0 for speed, _ in results):
        with _route_lock:
            _route_cache[address.hostname] = (time.monotonic(), [name for name, _ in ordered])
    return ordered


def _range_info(response, start, end=None, total=None):
    match = re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)", response.headers.get("Content-Range", ""))
    if response.status_code != 206 or not match:
        raise ValueError("服务器未正确支持分段下载")
    a, b, size = map(int, match.groups())
    if a != start or (end is not None and b != end) or (total is not None and size != total):
        raise ValueError("服务器分段范围不一致")
    return size


def download_url(url, destination, *, threads=4, digest=None, validator=None, report=print,
                 request=None, min_parallel_size=4 * 1048576, cancelled=None, _stream=False,
                 work_dir=None):
    """Resume only against the same URL, size and strong ETag; never mix routes."""
    check_pause(cancelled)
    request = request or requests.get
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    work = Path(work_dir) if work_dir else destination.with_name(destination.name + ".parts")
    work.mkdir(parents=True, exist_ok=True)
    meta_path = work / "state.json"
    with request(url, headers=HEADERS if _stream else {**HEADERS, "Range": "bytes=0-0"},
                      stream=True, timeout=(8, 20)) as response:
        response.raise_for_status()
        if "text/html" in response.headers.get("Content-Type", "").lower():
            raise ValueError("下载地址返回了网页")
        ranged = response.status_code == 206 and not _stream
        total = _range_info(response, 0, 0) if ranged else int(response.headers.get("Content-Length", 0))
        etag = response.headers.get("ETag", "")
    strong = bool(etag and not etag.startswith("W/"))
    count = min(max(1, threads), 8, total) if ranged and total >= min_parallel_size else 1
    state = dict(url=url, total=total, etag=etag, count=count)
    old = None
    try:
        old = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        pass
    resume = ranged and strong and old == state
    if not resume:
        for part in work.glob("*.part"):
            part.unlink()
    atomic_json(meta_path, state)
    report(f"下载：{count} 连接；" + ("恢复已有进度" if resume else "新任务"))
    progress_lock = threading.Lock()
    progress = {"parts": [0] * count, "last": 0.0}
    if resume:
        for index in range(count):
            part = work / f"{index}.part"
            progress["parts"][index] = part.stat().st_size if part.exists() else 0
    started = time.monotonic()
    resumed_bytes = sum(progress["parts"])

    def transfer(index):
        start = total * index // count
        end = total * (index + 1) // count - 1
        part = work / f"{index}.part"
        offset = part.stat().st_size if resume and part.exists() else 0
        length = end - start + 1
        if ranged and offset == length:
            return part
        if ranged and offset > length:
            part.unlink()
            offset = 0
        error = None
        for attempt in range(3):
            check_pause(cancelled)
            # Persisted bytes are trusted only when guarded by a strong validator.
            offset = part.stat().st_size if ranged and strong and part.exists() else 0
            if ranged and offset == length:
                return part
            headers = dict(HEADERS)
            if ranged:
                headers["Range"] = f"bytes={start + offset}-{end}"
                if strong:
                    headers["If-Range"] = etag
            try:
                with request(url, headers=headers, stream=True, timeout=(8, 20)) as response:
                    if ranged and response.status_code in (200, 416):
                        raise RangeUnavailable("分段能力已变化，改用单连接重新下载")
                    response.raise_for_status()
                    if "text/html" in response.headers.get("Content-Type", "").lower():
                        raise ValueError("下载地址返回网页")
                    if ranged:
                        _range_info(response, start + offset, end, total)
                        if strong and response.headers.get("ETag") != etag:
                            raise ValueError("文件已变化，请重新下载")
                    with part.open("ab" if offset else "wb") as output:
                        for chunk in response.iter_content(65536):
                            check_pause(cancelled)
                            output.write(chunk)
                            with progress_lock:
                                progress["parts"][index] = output.tell()
                                now = time.monotonic()
                                if now - progress["last"] >= .5:
                                    done = sum(progress["parts"]) / 1048576
                                    size = f" / {total / 1048576:.2f}" if total else ""
                                    speed = max(0, done - resumed_bytes / 1048576) / max(now - started, .01)
                                    report(f"下载进度：{done:.2f}{size} MiB，{speed:.2f} MiB/s")
                                    progress["last"] = now
                if total and part.stat().st_size != length:
                    raise requests.ConnectionError("文件长度不完整")
                return part
            except requests.RequestException as exc:
                error = exc
        raise error

    try:
        with ThreadPoolExecutor(max_workers=count) as pool:
            parts = list(pool.map(transfer, range(count)))
    except RangeUnavailable as exc:
        report(str(exc))
        return download_url(url, destination, threads=1, digest=digest,
                            validator=validator, report=report, request=request,
                            min_parallel_size=min_parallel_size, cancelled=cancelled, _stream=True,
                            work_dir=work)
    assembled = work / "assembled"
    sha = hashlib.sha256()
    with assembled.open("wb") as output:
        for part in parts:
            with part.open("rb") as source:
                while chunk := source.read(1048576):
                    check_pause(cancelled)
                    sha.update(chunk)
                    output.write(chunk)
    if not assembled.stat().st_size:
        raise ValueError("空文件")
    if digest and sha.hexdigest() != digest.removeprefix("sha256:").lower():
        # A bad completed part must not be reused indefinitely.
        for part in parts:
            part.unlink()
        raise ValueError("SHA256 校验失败，已清理损坏分片")
    if validator:
        try:
            validator(assembled)
        except (ValueError, OSError) as exc:
            for part in parts:
                part.unlink()
            raise ValueError(f"文件内容校验失败：{exc}") from exc
    check_pause(cancelled)
    os.replace(assembled, destination)
    for part in parts:
        part.unlink()
    meta_path.unlink()
    if not any(work.iterdir()):
        work.rmdir()
    return destination


def download(url, destination, *, route="auto", threads=4, digest=None, validator=None, report=print,
             cancelled=None):
    failures = []
    destination = Path(destination)
    primary = destination.with_name(destination.name + ".parts")
    previous = None
    if route == "auto":
        state = primary / "state.json"
        try:
            previous = json.loads(state.read_text(encoding="utf-8"))["url"]
        except (OSError, ValueError, KeyError, TypeError):
            previous = None
    preferred = next(((name, previous) for name, prefix in ROUTES if prefix + url == previous), None)

    def candidates():
        if preferred:
            yield preferred
        check_pause(cancelled)
        yield from (item for item in ranked_routes(url, route, report) if item != preferred)

    if route != "auto" and route not in dict(ROUTES):
        raise ValueError("未知线路")
    for name, target in candidates():
        check_pause(cancelled)
        report(f"使用线路：{name}")
        try:
            work = primary if not previous or target == previous else primary / ("route-" + name)
            result = download_url(target, destination, threads=threads, digest=digest, validator=validator,
                                  report=report, cancelled=cancelled, work_dir=work)
            return result
        except (requests.RequestException, ValueError) as exc:
            if (primary / "state.json").exists():
                previous = previous or target
            failures.append(f"{name}: {exc}")
            report(f"线路失败，保留任务：{exc}")
    raise RuntimeError("所有线路下载失败；可重新执行继续。\n" + "\n".join(failures))
