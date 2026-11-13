import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from datetime import datetime, timezone

from website.catalog import collect, safe_url
from website.downloads import classify_asset, refresh
from website.build import build


class CatalogTests(unittest.TestCase):
    def test_url_policy(self):
        for value in ('javascript:alert(1)', '//evil.test', 'https://user:pass@example.com', 'https://example.com/\nfoo'):
            self.assertEqual(safe_url(value), '')
        self.assertEqual(safe_url('https://example.com/a'), 'https://example.com/a')

    def test_products_merge_platforms_without_inventing_support(self):
        products = collect()
        local = next(p for p in products if p['id'] == 'localsend')
        self.assertTrue({'windows', 'darwin', 'linux', 'android', 'ios'} <= set(local['platforms']))
        self.assertEqual(local['platforms']['ios']['kind'], 'store')
        self.assertIn('apps.apple.com/', local['platforms']['ios']['url'])
        power = next(p for p in products if p['id'] == 'powertoys')
        self.assertEqual(set(power['platforms']), {'windows'})
        self.assertFalse(any(p['id'] == 'pixpin' and 'linux' in p['platforms'] for p in products))
        self.assertEqual(len({p['id'] for p in products}), len(products))


class DownloadTests(unittest.TestCase):
    def test_asset_platform_architecture_and_noise(self):
        self.assertEqual(classify_asset('LocalSend-1.17.0-windows-x86-64.exe'), ('windows', 'x64'))
        self.assertEqual(classify_asset('LocalSend-1.17.0-macos-universal.dmg'), ('darwin', 'universal'))
        self.assertEqual(classify_asset('LocalSend-1.17.0-linux-arm64.deb'), ('linux', 'arm64'))
        self.assertEqual(classify_asset('LocalSend-1.17.0-android-arm64-v8a.apk'), ('android', 'arm64'))
        for name in ('source.zip', 'app-windows-x64.exe.sha256', 'app-linux-x64-debug.tar.gz', 'app-windows-x64.exe.blockmap', 'app-unsigned.apk'):
            self.assertIsNone(classify_asset(name))
        self.assertIsNone(classify_asset('app.zip'))

    def test_failed_refresh_removes_old_direct_download(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'downloads.json'
            path.write_text(json.dumps({'localsend': {'version':'old','assets':[]}}),encoding='utf-8')
            product = {'id':'localsend','repo':'localsend/localsend','featured':True,'platforms':{'windows':{}}}
            with patch('website.downloads.urllib.request.urlopen', side_effect=OSError('offline')):
                records, errors = refresh([product],path)
            self.assertNotIn('localsend', records)
            self.assertEqual(len(errors),1)

    def test_refresh_rejects_prerelease_and_foreign_assets(self):
        import io
        product = {'id':'example','repo':'team/app','featured':True,'platforms':{'windows':{}}}
        release = {'tag_name':'v1','assets':[
            {'name':'app-windows-x64.exe','browser_download_url':'https://github.com/team/app/releases/download/v1/app-windows-x64.exe'},
            {'name':'app-windows-arm64.exe','browser_download_url':'https://other.example.com/file.exe'},
            {'name':'app-linux-x64.deb','browser_download_url':'https://github.com/team/app/releases/download/v1/app-linux-x64.deb'},
        ]}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'downloads.json'
            with patch('website.downloads.urllib.request.urlopen',return_value=io.BytesIO(json.dumps(release).encode())):
                records, errors = refresh([product],path)
            self.assertFalse(errors)
            self.assertEqual(len(records['example']['assets']),1)
            release['prerelease']=True
            with patch('website.downloads.urllib.request.urlopen',return_value=io.BytesIO(json.dumps(release).encode())):
                records, errors = refresh([product],path)
            self.assertNotIn('example',records)


class BuildTests(unittest.TestCase):
    def test_static_content_subpath_seo_and_internal_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            build(out, 'https://tools.example.com/software')
            home = (out / 'index.html').read_text(encoding='utf-8')
            detail = (out / 'app/localsend/index.html').read_text(encoding='utf-8')
            self.assertIn('LocalSend', home)
            self.assertIn('https://tools.example.com/software/app/localsend/', detail)
            self.assertIn('SoftwareApplication', detail)
            self.assertIn('下载与传输', detail)
            self.assertNotIn('aggregateRating', detail)
            self.assertTrue((out / 'platform/ios/index.html').exists())
            self.assertTrue((out / 'category/office/index.html').exists())
            self.assertTrue((out / 'collections/new-pc/index.html').exists())
            self.assertIn('noindex', (out / 'search/index.html').read_text(encoding='utf-8'))
            self.assertIn('/software/sitemap.xml', (out / 'robots.txt').read_text(encoding='utf-8'))
            self.assertIn('/software/assets/style.css', home)
            data = json.loads((out / 'assets/catalog.json').read_text(encoding='utf-8'))
            self.assertGreater(len(data['products']), 100)
            import re
            import xml.etree.ElementTree as ET
            titles = []
            for page in out.rglob('*.html'):
                document = page.read_text(encoding='utf-8')
                if 'content="index,follow"' in document:
                    titles.append(re.search(r'<title>(.*?)</title>', document).group(1))
                    self.assertEqual(document.count('<h1>'), 1, page)
                    self.assertIn('<meta name="description"', document)
                    self.assertIn('rel="canonical"', document)
                    for schema in re.findall(r'<script type="application/ld\+json">(.*?)</script>', document):
                        self.assertEqual(json.loads(schema)['@context'], 'https://schema.org')
                for href in re.findall(r'(?:href|src)="(/software/[^"?#]*)', document):
                    target = out / href.removeprefix('/software/')
                    self.assertTrue(target.exists(), f'{page}: {href}')
            self.assertEqual(len(titles), len(set(titles)))
            self.assertEqual(len(ET.parse(out/'sitemap.xml').getroot()), len(titles))

    def test_preview_has_no_fake_canonical_or_sitemap(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            build(out, '')
            self.assertNotIn('rel="canonical"', (out / 'index.html').read_text(encoding='utf-8'))
            self.assertFalse((out / 'sitemap.xml').exists())

    def test_download_snapshot_expires_and_xss_is_escaped(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            record = {'localsend':{'version':'<script>bad</script>','fetched':datetime.now(timezone.utc).isoformat(), 'assets':[{'platform':'windows','arch':'x64','name':'app-x64.exe','url':'https://github.com/localsend/localsend/releases/download/v1/app.exe'}]}}
            cache = out/'downloads.json'
            cache.write_text(json.dumps(record),encoding='utf-8')
            build(out)
            detail = (out/'app/localsend/index.html').read_text(encoding='utf-8')
            self.assertIn('app-x64.exe',detail)
            self.assertNotIn('<script>bad</script>',detail)
            record['localsend']['fetched']='2000-01-01T00:00:00+00:00'
            cache.write_text(json.dumps(record),encoding='utf-8')
            build(out)
            self.assertNotIn('app-x64.exe',(out/'app/localsend/index.html').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
