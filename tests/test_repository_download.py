import contextlib
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
from pathlib import Path
import re
import tempfile
import threading
import unittest
from unittest.mock import patch
import zipfile

import requests

import lookup_app
from tools import download_engine as engine
from tools import repository_download as repo


DATA = bytes(range(256)) * 20480


class DownloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                cls.seen.append((self.path, self.headers.get("Range"), self.headers.get("If-Range")))
                if self.path == "/html":
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"<html>proxy error</html>")
                    return
                data = DATA
                header = self.headers.get("Range")
                start, end = 0, len(data) - 1
                ranged = header and self.path != "/stream" and not (self.path == "/range-change" and header != "bytes=0-0")
                if self.path == "/416" and header and header != "bytes=0-0":
                    self.send_response(416)
                    self.end_headers()
                    return
                if ranged:
                    start, end = map(int, re.fullmatch(r"bytes=(\d+)-(\d+)", header).groups())
                self.send_response(206 if ranged else 200)
                self.send_header("Content-Length", str(end - start + 1))
                self.send_header("ETag", cls.etag)
                if ranged:
                    self.send_header("Content-Range", f"bytes {start}-{end}/{len(data)}")
                self.end_headers()
                try:
                    self.wfile.write(data[start:end + 1])
                except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
                    pass
        cls.seen = []
        cls.etag = '"v1"'
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.seen.clear()
        type(self).etag = '"v1"'

    def test_parallel_download_chinese_path_and_digest(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "中文目录" / "代码.zip"
            engine.download_url(self.base + "/file", target, digest=hashlib.sha256(DATA).hexdigest(), report=lambda x: None)
            self.assertEqual(target.read_bytes(), DATA)
            self.assertFalse(target.with_name(target.name + ".parts").exists())
            self.assertEqual(len([x for x in self.seen if x[1] != "bytes=0-0"]), 4)

    def seed(self, target, url, etag='"v1"'):
        work = target.with_name(target.name + ".parts")
        work.mkdir()
        engine.atomic_json(work / "state.json", dict(url=url, total=len(DATA), etag=etag, count=1))
        (work / "0.part").write_bytes(DATA[:65536])

    def test_resume_uses_if_range(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "source.zip"
            url = self.base + "/file"
            self.seed(target, url)
            engine.download_url(url, target, threads=1, report=lambda x: None)
            self.assertEqual(target.read_bytes(), DATA)
            self.assertIn(("/file", f"bytes=65536-{len(DATA)-1}", '"v1"'), self.seen)

    def test_resource_change_discards_partial(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "source.zip"
            url = self.base + "/file"
            self.seed(target, url, etag='"old"')
            engine.download_url(url, target, threads=1, report=lambda x: None)
            self.assertEqual(target.read_bytes(), DATA)
            self.assertIn(("/file", f"bytes=0-{len(DATA)-1}", '"v1"'), self.seen)

    def test_no_range_falls_back_to_one_stream(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "file"
            engine.download_url(self.base + "/stream", target, report=lambda x: None)
            self.assertEqual(target.read_bytes(), DATA)
            self.assertIn(("/stream", None, None), self.seen)

    def test_bad_digest_never_publishes(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "file"
            with self.assertRaisesRegex(ValueError, "SHA256"):
                engine.download_url(self.base + "/file", target, digest="0" * 64, report=lambda x: None)
            self.assertFalse(target.exists())
            self.assertFalse(list(target.with_name("file.parts").glob("*.part")))

    def test_200_and_416_during_download_restart_as_stream(self):
        for path in ("/range-change", "/416"):
            with self.subTest(path=path), tempfile.TemporaryDirectory() as td:
                target = Path(td) / "file"
                engine.download_url(self.base + path, target, report=lambda x: None)
                self.assertEqual(target.read_bytes(), DATA)
                self.assertIn((path, None, None), self.seen)

    def test_html_never_publishes(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "file"
            with self.assertRaisesRegex(ValueError, "网页"):
                engine.download_url(self.base + "/html", target, report=lambda x: None)
            self.assertFalse(target.exists())

    def test_interruption_preserves_progress(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "file"
            url = self.base + "/file"
            self.seed(target, url)
            original = requests.get
            def interrupted(*args, **kwargs):
                if kwargs.get("headers", {}).get("Range") != "bytes=0-0":
                    raise requests.ConnectionError("断网")
                return original(*args, **kwargs)
            with patch.object(engine.requests, "get", side_effect=interrupted):
                with self.assertRaises(requests.ConnectionError):
                    engine.download_url(url, target, threads=1, report=lambda x: None)
            engine.download_url(url, target, threads=1, report=lambda x: None)
            self.assertEqual(target.read_bytes(), DATA)


class RepositoryTests(unittest.TestCase):
    def test_chrome_store_inputs_and_dispatch(self):
        item = "cnjifjpddelmedmihgijeibhnjfabmlf"
        page = f"https://chromewebstore.google.com/detail/{item}"
        source = f"https://chromewebstore.google.com/detail/obsidian-web-clipper/{item}?hl=zh-CN"
        self.assertEqual(repo.chrome_store.extension_id(source), item)
        self.assertEqual(repo.chrome_store.extension_id(f"https://chrome.google.com/webstore/detail/{item}"), item)
        for invalid in ("https://chromewebstore.google.com/category/extensions",
                        f"https://example.com@chromewebstore.google.com/detail/{item}"):
            with self.assertRaises(ValueError):
                repo.chrome_store.extension_id(invalid)
        with patch("builtins.input", side_effect=[source, "1"]), patch.object(repo.webbrowser, "open") as launch:
            self.assertEqual(repo.run(), 0)
            launch.assert_called_once_with(page)
        with tempfile.TemporaryDirectory() as folder, patch.object(repo.chrome_store, "download_crx") as download:
            target = Path(folder) / "扩展.crx"
            download.return_value = target
            self.assertEqual(lookup_app.main(["--repository", item, "--no-prompt",
                                             "--output", str(target), "--threads", "2"]), 0)
            download.assert_called_once_with(item, target, threads=2)

    def test_chrome_rejects_redirect_outside_google(self):
        response = requests.Response()
        response.status_code = 302
        response.headers["Location"] = "https://googleusercontent.com.example.org/file.crx"
        with patch.object(repo.chrome_store.requests, "get", return_value=response) as get:
            response._content_consumed = True
            with self.assertRaisesRegex(ValueError, "Google"):
                repo.chrome_store.google_get(repo.chrome_store.UPDATE, headers={"If-Range": "etag"})
            get.assert_called_once_with(repo.chrome_store.UPDATE, headers={}, allow_redirects=False)

    def test_addresses_and_unicode_refs(self):
        self.assertEqual(repo.parse_repository("owner/repo.git")["repo"], "owner/repo")
        parsed = repo.parse_repository("https://github.com/owner/repo/tree/feature/%E4%B8%AD%E6%96%87")
        self.assertEqual(parsed["ref"], "feature/中文")
        self.assertEqual(parsed["kind"], "source")
        parsed = repo.parse_repository("https://github.com/o/r/releases/download/v1/a%20b.zip")
        self.assertEqual(parsed["asset"], "a b.zip")
        for source in ("https://evil.com/o/r", "https://github.com@evil.com/o/r", "o/..", "https://github.com/o/r/blob/main/a"):
            with self.assertRaises(ValueError):
                repo.parse_repository(source)

    def test_tree_branch_with_slash_and_directory(self):
        def get(path):
            if path.endswith("feature%2Fx"):
                return {"sha": "a" * 40}
            response = requests.Response()
            response.status_code = 404
            raise requests.HTTPError(response=response)
        with patch.object(repo, "api", side_effect=get):
            self.assertEqual(repo.resolve_commit("o/r", "feature/x/src", True), ("a" * 40, "feature/x"))

    def test_dry_run_does_not_network_or_write(self):
        with tempfile.TemporaryDirectory() as td, patch.object(repo, "api") as api, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(repo.run(source="o/r", kind="source", base_dir=td, dry_run=True, interactive=False), 0)
            api.assert_not_called()
            self.assertEqual(list(Path(td).iterdir()), [])

    def test_menu_15_dispatches_repository(self):
        import sys
        with patch.object(sys, "argv", ["lookup_app.py"]), patch("builtins.input", return_value="15"), contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(lookup_app.prompt_catalog_and_query())
            self.assertEqual(sys.argv[1:], ["--repository"])
        with patch.object(repo, "run", return_value=0) as run:
            self.assertEqual(lookup_app.main(["--repository", "o/r", "--repo-kind", "source", "--no-prompt"]), 0)
            self.assertFalse(run.call_args.kwargs["interactive"])

    def test_back_and_quit_remain_distinct(self):
        with patch("builtins.input", return_value="b"), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(repo.run(), 0)
        with patch("builtins.input", return_value="q"):
            self.assertIs(repo.run(), repo.MENU_QUIT)
        with patch.object(repo, "run", return_value=repo.MENU_QUIT):
            self.assertIs(lookup_app._dispatch(["--repository"], menu_mode=True), lookup_app._QUIT)

    def test_source_end_to_end_records_commit_and_extracts_unicode(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "源码.zip"
            def fetch(url, destination, **kwargs):
                self.assertIn("a" * 40, url)
                with zipfile.ZipFile(destination, "w") as archive:
                    archive.writestr("项目/README.md", "中文正常")
                kwargs["validator"](destination)
                return Path(destination)
            with patch.object(repo, "api", side_effect=[{"full_name": "o/r", "default_branch": "main"}, {"sha": "a" * 40}]), patch.object(repo, "download", side_effect=fetch), contextlib.redirect_stdout(io.StringIO()):
                code = repo.run(source="o/r", kind="source", output=str(target), extract=True, base_dir=td, interactive=False)
            self.assertEqual(code, 0)
            self.assertEqual((target.with_suffix("") / "项目/README.md").read_text(encoding="utf-8"), "中文正常")
            task = json.loads((Path(td) / "repository_downloads/repository_tasks.json").read_text(encoding="utf-8"))[0]
            self.assertEqual(task["commit"], "a" * 40)
            self.assertEqual(task["status"], "completed")

    def test_release_digest_forwarded(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "tool.zip"
            with patch.object(repo, "api", side_effect=[{"full_name": "o/r", "default_branch": "main"}, {"tag_name": "v1", "assets": [{"name": "tool.zip", "size": 123, "browser_download_url": "https://github.com/o/r/releases/download/v1/tool.zip", "digest": "sha256:" + "a" * 64}]}]), patch.object(repo, "download", return_value=target) as download, contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(repo.run(source="o/r", kind="release", output=str(target), interactive=False, base_dir=td), 0)
            self.assertEqual(download.call_args.kwargs["digest"], "sha256:" + "a" * 64)

    def test_source_completion_opens_directory_and_keeps_zip(self):
        for selection in ("", "2"):
            with self.subTest(selection=selection), tempfile.TemporaryDirectory() as td:
                target = Path(td) / "源码.zip"

                def fetch(url, destination, **kwargs):
                    with zipfile.ZipFile(destination, "w") as archive:
                        archive.writestr("项目/README.md", "中文正常")
                    return destination

                output = io.StringIO()
                metadata = [{"full_name": "o/r", "default_branch": "main"}, {"sha": "a" * 40}]
                with patch.object(repo, "api", side_effect=metadata), \
                        patch.object(repo, "download", side_effect=fetch), \
                        patch.object(repo, "finish_action") as finish, \
                        patch("builtins.input", side_effect=["", "", "", "", selection]), \
                        contextlib.redirect_stdout(output):
                    self.assertEqual(repo.run(source="o/r", kind="source", output=str(target), base_dir=td), 0)
                expected = target.with_suffix("") / "项目" if selection else target
                finish.assert_called_once_with(1, expected, Path(td) / "repository_downloads")
                self.assertTrue(target.is_file())
                self.assertNotIn("保留 ZIP", output.getvalue())

    def test_zip_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "evil.zip"
            with zipfile.ZipFile(target, "w") as archive:
                archive.writestr("../escape", "bad")
            with self.assertRaisesRegex(ValueError, "不安全"):
                repo.extract_zip(target)
            self.assertFalse(target.with_suffix("").exists())

    def test_git_clone_branch_and_missing_git(self):
        with tempfile.TemporaryDirectory() as td, patch.object(repo.shutil, "which", return_value="git"), patch.object(repo.subprocess, "check_output", return_value="sha refs/heads/feature/x"), patch.object(repo.subprocess, "run") as run:
            repo.clone("o/r", Path(td) / "project", ref="feature/x", shallow=True, submodules=True, lfs=True)
            commands = [x.args[0] for x in run.call_args_list]
            self.assertTrue(any("--branch" in x and "--depth" in x for x in commands))
            self.assertTrue(any("submodule" in x for x in commands))
            self.assertTrue(any(x[-2:] == ["lfs", "pull"] for x in commands))
        with patch.object(repo.shutil, "which", return_value=None):
            with self.assertRaisesRegex(ValueError, "未找到 Git"):
                repo.clone("o/r", "unused")

    def test_git_update_rejects_dirty_tree(self):
        with patch.object(repo.subprocess, "check_output", side_effect=["https://github.com/o/r.git", " M README"]), patch.object(repo.subprocess, "run") as run:
            with self.assertRaisesRegex(ValueError, "本地改动"):
                repo.update_git(".", "o/r")
            run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
