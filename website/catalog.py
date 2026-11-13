"""Normalize public catalog fields; never export runtime config or personal lists."""
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

from .content import CATEGORIES, FEATURED, PLATFORMS

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    'windows': 'apps/windows', 'darwin': 'apps/darwin', 'linux': 'apps/linux',
    'android': 'apps-mobile/android', 'ios': 'apps-mobile/ios',
    'android_tv': 'apps-tv/android_tv', 'linux_handheld': 'apps-handheld/linux_handheld',
    'switch': 'apps-switch', 'ps4': 'apps-ps4', 'ps5': 'apps-ps5',
    'vita': 'apps-vita', 'xbox': 'apps-xbox',
}


def safe_url(value):
    if not isinstance(value, str) or any(ord(c) < 32 for c in value) or '\\' in value:
        return ''
    try:
        parsed = urlsplit(value)
        if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password:
            return ''
        return value
    except ValueError:
        return ''


def source_url(row):
    for field in ('open_page_url', 'releases_url', 'homepage', 'url'):
        url = safe_url(row.get(field, ''))
        if url:
            return url.replace('https://bgithub.xyz/', 'https://github.com/')
    repo = row.get('repo_path', '')
    if re.fullmatch(r'[\w.-]+/[\w.-]+', repo):
        return f'https://github.com/{repo}/releases'
    return ''


def category_for(label):
    for id, _, _, _, old, _ in CATEGORIES:
        if label in old:
            return id
    return 'more'


def slug(value):
    # Raw IDs may be Chinese. UTF-8 hex is deterministic and URL safe.
    return re.sub(r'[^a-z0-9_-]', lambda m: m[0].encode().hex(), value.lower())


def collect(root=ROOT):
    featured = {p['id']: p for p in FEATURED}
    aliases = {a.lower(): p['id'] for p in FEATURED for a in [p['id'], *p['aliases']]}
    aliases.update({'bitwarden_desktop':'bitwarden', 'bitwarden_android':'bitwarden', 'bitwarden_ios':'bitwarden'})
    products = {}
    for platform, directory in SOURCES.items():
        for path in sorted((root / directory).rglob('*.json')):
            if path.name == 'root.json' or (path.name.startswith('99-') and platform != 'ios'):
                continue
            data = json.loads(path.read_text(encoding='utf-8-sig'))
            if not isinstance(data, list):
                continue
            for row in data:
                if not isinstance(row, dict) or not isinstance(row.get('id'), str):
                    continue
                raw_id = row['id'].strip()
                if not raw_id:
                    continue
                id = aliases.get(raw_id.lower(), slug(raw_id))
                editorial = featured.get(id)
                if editorial and platform not in editorial['supported']:
                    continue
                intro = str(row.get('简介', '')).strip()
                if any(s in intro for s in ('未提供 Linux', '仅 Windows', '不提供 Linux')) and platform == 'linux':
                    continue
                url = source_url(row)
                if not url:
                    continue
                item = products.setdefault(id, dict(id=id, name=raw_id.replace('_',' '),
                    summary=intro or f'{raw_id} 的项目与获取入口。', category=category_for(row.get('分类', '')),
                    aliases=[], platforms={}, featured=False, reason='', audience='', note=''))
                extra = row.get('aliases', [])
                if isinstance(extra, str):
                    extra = [extra]
                item['aliases'] = sorted(set(item['aliases'] + [raw_id] + [str(a) for a in extra]))
                target = dict(url=url, kind='store' if urlsplit(url).hostname in ('apps.apple.com','play.google.com') else 'release' if '/releases' in url else 'website')
                if platform not in item['platforms'] or target['kind'] == 'store':
                    item['platforms'][platform] = target
    for id, p in featured.items():
        item = products.setdefault(id, dict(id=id, platforms={}, aliases=[]))
        item.update({k:p[k] for k in ('name','category','summary','reason','audience','note','repo')})
        item.update(featured=True, official=safe_url(p['url']))
        item['aliases'] = sorted(set(item['aliases'] + p['aliases']))
        # Explicit editorial support, including tools missing from the old catalog.
        for platform in p['supported']:
            existing = item['platforms'].get(platform, {})
            if existing.get('kind') == 'store':
                continue
            item['platforms'][platform] = dict(url=safe_url(p['url']), kind='website')
    return sorted(products.values(), key=lambda p:(not p['featured'], p['name'].casefold()))
