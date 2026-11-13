"""Optional, build-time stable release discovery for curated upstream repositories.

Only explicit platform/architecture installer names are offered. A source page
is always available; unknown archives and ambiguous architectures are omitted.
"""
import json
import os
import re
import urllib.request
from datetime import datetime, timezone

from .catalog import safe_url


def classify_asset(name):
    n = name.lower()
    if any(s in n for s in ('debug', 'symbols', 'unsigned', 'source', 'nightly', 'beta', 'portable')):
        return None
    if not n.endswith(('.exe', '.msi', '.dmg', '.appimage', '.deb', '.rpm', '.apk')):
        return None
    if n.endswith(('.exe', '.msi')):
        platform = 'windows'
    elif n.endswith('.dmg'):
        platform = 'darwin'
    elif n.endswith('.apk'):
        platform = 'android'
    else:
        platform = 'linux'
    if any(s in n for s in ('arm64', 'aarch64', 'arm64-v8a')):
        arch = 'arm64'
    elif any(s in n for s in ('x86_64', 'x86-64', 'x64', 'amd64')):
        arch = 'x64'
    elif 'universal' in n:
        arch = 'universal'
    elif re.search(r'(?:^|[-_.])(x86|i386|i686|win32|ia32)(?:[-_.]|$)', n):
        arch = 'x86'
    elif 'armeabi-v7a' in n:
        arch = 'armv7'
    else:
        return None
    return platform, arch


def refresh(products, cache_path):
    records = {}
    if cache_path.exists():
        records = json.loads(cache_path.read_text(encoding='utf-8'))
    errors = []
    now = datetime.now(timezone.utc).isoformat(timespec='seconds')
    for p in products:
        repo = p.get('repo', '')
        if not p['featured'] or not re.fullmatch(r'[\w.-]+/[\w.-]+', repo):
            continue
        headers = {'Accept':'application/vnd.github+json', 'User-Agent':'GH-Release-Fetch-Website'}
        token = os.environ.get('GITHUB_TOKEN')
        if token:
            headers['Authorization'] = f'Bearer {token}'
        request = urllib.request.Request(f'https://api.github.com/repos/{repo}/releases/latest', headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                release = json.load(response)
            if release.get('draft') or release.get('prerelease'):
                raise ValueError('not a stable release')
            assets = []
            for asset in release.get('assets', []):
                match = classify_asset(asset.get('name', ''))
                url = safe_url(asset.get('browser_download_url', ''))
                if not match or not url or not url.startswith(f'https://github.com/{repo}/releases/download/'):
                    continue
                platform, arch = match
                if platform not in p['platforms']:
                    continue
                assets.append(dict(platform=platform, arch=arch, name=asset['name'], url=url, size=asset.get('size',0)))
            records[p['id']] = dict(version=release.get('tag_name',''), fetched=now, assets=assets)
        except Exception as exc:
            # Never print request headers or tokens. A stale record is not published as current.
            records.pop(p['id'], None)
            errors.append(f"{p['id']}: {type(exc).__name__}")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    return records, errors
