import contextlib
import importlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


class CustomCatalogTests(unittest.TestCase):
    def custom(self):
        self.assertIsNotNone(importlib.util.find_spec("tools.custom_catalog"), "custom catalog is not implemented")
        return importlib.import_module("tools.custom_catalog")

    def asset(self, name):
        return {"name": name, "browser_download_url": "https://github.com/acme/player/releases/download/v1.2.3/" + name}

    def test_parse_repository_release_proxy_and_fixed_sources(self):
        m = self.custom()
        self.assertEqual(m.parse_source("acme/player")["repo"], "acme/player")
        source = m.parse_source("https://gh-proxy.com/https://github.com/acme/player/releases/tag/v1.2.3")
        self.assertEqual((source["repo"], source["tag"]), ("acme/player", "v1.2.3"))
        source = m.parse_source("https://github.com/acme/player/releases/download/v1.2.3/player.apk")
        self.assertEqual((source["kind"], source["asset"]), ("github", "player.apk"))
        self.assertEqual(m.parse_source("https://example.org/player.apk")["kind"], "fixed")
        self.assertEqual(m.parse_source("VLC player")["kind"], "search")
        for bad in ("file:///tmp/a.exe", "https://github.com/acme/player/issues", "https://u:p@example.org/a.exe"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                m.parse_source(bad)

    def test_inference_excludes_junk_and_does_not_guess_apk_or_archive_platform(self):
        m = self.custom()
        assets = m.detect_assets([self.asset(n) for n in ["player-arm64.apk", "player.zip", "player-win-x64.exe", "player.dmg", "player.apk.sha256", "sources.zip", "player-debug.apk"]])
        self.assertEqual(len(assets), 4)
        apk = next(a for a in assets if a["name"].endswith(".apk"))
        self.assertEqual(apk["platforms"], ("android", "android_tv"))
        self.assertEqual(apk["architecture"], "ARM64")
        self.assertEqual(next(a for a in assets if a["name"] == "player.zip")["platforms"], ())
        self.assertEqual(m.detect_assets([self.asset("player-universal.apk")], "lx-music-tv")[0]["platforms"], ("android_tv",))

    def test_github_rule_follows_versions_without_crossing_architecture(self):
        m = self.custom()
        from auto_update import asset_targets_app
        entry = m.make_github_entry("acme/player", "v1.2.3", m.detect_assets([self.asset("player-v1.2.3-win-x64-green.7z")])[0], "windows", "Player", "音乐")
        self.assertTrue(asset_targets_app("player-v2.0.1-win-x64-green.7z", "https://example.org/player-v2.0.1-win-x64-green.7z", entry))
        for bad in ("player-v2.0.1-win-arm64-green.7z", "player-v2.0.1-win-x64-setup.exe", "player-v2.0.1-win-x64-green.7z.sig"):
            self.assertFalse(asset_targets_app(bad, "https://example.org/" + bad, entry))
        self.assertFalse(entry["run_installer"])
        self.assertNotIn("pinned_release_tag", entry)

    def test_fixed_link_resolves_without_fetching_release_pages(self):
        m = self.custom()
        from auto_update import check_latest_version
        entry = m.make_fixed_entry("https://example.org/player.apk?x=1", "android", "Player", "音乐")
        with patch("auto_update.request_release_page", side_effect=AssertionError("must not request release page")):
            self.assertEqual(check_latest_version(entry, "unused"), ("fixed", "https://example.org/player.apk?x=1"))
        from tools.app_download import is_app_downloadable, resolve_open_page_url
        self.assertTrue(is_app_downloadable(entry))
        self.assertEqual(resolve_open_page_url(entry), entry["fixed_download_url"])

    def test_duplicates_keep_enabled_and_other_owners_are_separate(self):
        m = self.custom()
        asset = m.detect_assets([self.asset("player-v1.2.3-win-x64.exe")])[0]
        first = m.make_github_entry("acme/player", "v1.2.3", asset, "windows", "Player", "工具")
        other = m.make_github_entry("other/player", "v1.2.3", asset, "windows", "Player", "工具")
        with tempfile.TemporaryDirectory() as td:
            m.save_entries(td, [("windows", first), ("windows", other)])
            rows = m.list_entries(td)
            self.assertEqual(len(rows), 2)
            m.edit_entry(td, "windows", first["id"], {"enabled": True})
            replacement = dict(first, 简介="New title")
            with self.assertRaises(ValueError):
                m.save_entries(td, [("windows", replacement)])
            m.save_entries(td, [("windows", replacement)], replace=True)
            updated = next(row["app"] for row in m.list_entries(td) if row["app"]["id"] == first["id"])
            self.assertTrue(updated["enabled"])
            self.assertEqual(updated["简介"], "New title")
            m.delete_entry(td, "windows", first["id"])
            self.assertEqual([row["app"]["repo_path"] for row in m.list_entries(td)], ["other/player"])

    def test_fixed_source_identity_does_not_depend_on_display_name(self):
        m = self.custom()
        first = m.make_fixed_entry("https://example.org/player.exe", "windows", "My Player", "工具")
        renamed = m.make_fixed_entry("https://example.org/player.exe", "windows", "Other display name", "音乐")
        self.assertEqual(first["id"], renamed["id"])

    def test_invalid_backup_does_not_erase_current_entries(self):
        m = self.custom()
        with tempfile.TemporaryDirectory() as td:
            app = m.make_fixed_entry("https://example.org/player.exe", "windows", "Player", "工具")
            m.save_entries(td, [("windows", app)])
            backups = Path(td, ".backups")
            (backups / "99999999999999999999999.json").write_text("{}", encoding="utf-8")
            with self.assertRaises(ValueError):
                m.undo_last_change(td)
            self.assertEqual(len(m.list_entries(td)), 1)

    def test_invalid_platform_and_corrupt_catalog_are_not_overwritten(self):
        m = self.custom()
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                m.save_entries(td, [("../outside", {"id": "a"})])
            p = Path(td, "windows", "11-自定义.json")
            p.parent.mkdir()
            p.write_text("broken", encoding="utf-8")
            with self.assertRaises(ValueError):
                m.save_entries(td, [("windows", {"id": "a"})])
            self.assertEqual(p.read_text(encoding="utf-8"), "broken")

    def test_cancel_preview_keeps_catalog_absent(self):
        m = self.custom()
        with tempfile.TemporaryDirectory() as td, patch("builtins.input", side_effect=["Player", "音乐", "0"]), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(m.run_add(td, source_text="https://example.org/player-win-x64.exe"), 0)
            self.assertEqual(list(Path(td).iterdir()), [])

    def test_save_only_does_not_download_and_apk_platform_choice_is_respected(self):
        m = self.custom()
        with tempfile.TemporaryDirectory() as td, patch("builtins.input", side_effect=["2", "Player TV", "音乐", "1"]), contextlib.redirect_stdout(io.StringIO()):
            download = unittest.mock.Mock()
            self.assertEqual(m.run_add(td, source_text="https://example.org/player.apk", download=download), 0)
            rows = m.list_entries(td)
            self.assertEqual([row["platform"] for row in rows], ["android_tv"])
            download.assert_not_called()

    def test_appimage_matching_is_case_insensitive_including_html_fallback(self):
        m = self.custom()
        from auto_update import asset_targets_app, href_allowed_for_app
        asset = m.detect_assets([self.asset("Player-1.2.3-x86_64.AppImage")])[0]
        entry = m.make_github_entry("acme/player", "v1.2.3", asset, "linux", "Player", "工具")
        self.assertTrue(asset_targets_app("Player-2.0.1-x86_64.AppImage", "https://example.org/Player-2.0.1-x86_64.AppImage", entry))
        self.assertFalse(href_allowed_for_app("https://example.org/Player-2.0.1-aarch64.AppImage", entry))

    def test_main_menu_custom_then_all_and_custom_search_are_integrated(self):
        m = self.custom()
        import sys
        import lookup_app
        with patch.object(sys, "argv", ["lookup_app.py"]), patch("builtins.input", side_effect=["13"]), contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(lookup_app.prompt_catalog_and_query())
            self.assertEqual(sys.argv[1:], ["--custom"])
        with tempfile.TemporaryDirectory() as td, contextlib.redirect_stdout(io.StringIO()):
            custom_dir = Path(td, "apps-custom")
            app = m.make_fixed_entry("https://example.org/unique.exe", "windows", "Unique Custom", "工具")
            m.save_entries(str(custom_dir), [("windows", app)])
            with patch.object(lookup_app, "SCRIPT_DIR", td), patch.object(lookup_app, "DEFAULT_APPS_DIR", str(custom_dir)), patch.object(lookup_app, "print_hits") as printed:
                self.assertEqual(lookup_app.main(["--all-catalogs", "--no-prompt", "Unique Custom"]), 0)
                self.assertEqual(printed.call_args.args[0][0]["id"], app["id"])

    def test_backup_undo_restores_deleted_entry(self):
        m = self.custom()
        with tempfile.TemporaryDirectory() as td:
            app = m.make_fixed_entry("https://example.org/player.exe", "windows", "Player", "工具")
            m.save_entries(td, [("windows", app)])
            m.delete_entry(td, "windows", app["id"])
            self.assertEqual(m.list_entries(td), [])
            self.assertTrue(m.undo_last_change(td))
            self.assertEqual(m.list_entries(td)[0]["id"], app["id"])

    def test_export_import_validates_entire_bundle_before_writing(self):
        m = self.custom()
        with tempfile.TemporaryDirectory() as td:
            source, dest = str(Path(td, "source")), str(Path(td, "dest"))
            app = m.make_fixed_entry("https://example.org/player.exe", "windows", "Player", "工具")
            m.save_entries(source, [("windows", app)])
            exported = m.export_entries(source)
            m.import_entries(dest, exported)
            self.assertEqual(m.list_entries(dest)[0]["id"], app["id"])
            exported["entries"].append({"platform": "../bad", "app": app})
            before = m.export_entries(dest)
            with self.assertRaises(ValueError):
                m.import_entries(dest, exported)
            self.assertEqual(m.export_entries(dest), before)

    def test_preferences_remember_platform_architecture_and_package_kind(self):
        m = self.custom()
        with tempfile.TemporaryDirectory() as td:
            m.save_preferences(td, {"platform": "windows", "architecture": "x64", "package_kind": "绿色/便携版"})
            prefs = m.load_preferences(td)
            self.assertEqual(prefs["architecture"], "x64")
            assets = m.detect_assets([self.asset("player-win-arm64.exe"), self.asset("player-win-x64-green.7z")])
            self.assertEqual(m.preferred_asset_indices(assets, prefs), [1])

    def test_batch_failure_does_not_save_earlier_previews(self):
        m = self.custom()
        inputs = ["https://example.org/player.exe", "file:///invalid.exe", "", "Player", "工具"]
        with tempfile.TemporaryDirectory() as td, patch("builtins.input", side_effect=inputs), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(m.run_batch(td), 1)
            self.assertEqual(list(Path(td).iterdir()), [])

    def test_cross_platform_source_edit_is_one_undo_step(self):
        m = self.custom()
        with tempfile.TemporaryDirectory() as td:
            app = m.make_fixed_entry("https://example.org/player.exe", "windows", "Player", "工具")
            m.save_entries(td, [("windows", app)])
            moved = m.make_fixed_entry("https://example.org/player.dmg", "darwin", "Player", "工具")
            moved["id"] = app["id"]
            m.save_entries(td, [("darwin", moved)], replace=True, remove_target=("windows", app["id"]))
            self.assertEqual([r["platform"] for r in m.list_entries(td)], ["darwin"])
            m.undo_last_change(td)
            self.assertEqual([r["platform"] for r in m.list_entries(td)], ["windows"])

    def test_missing_github_variant_reports_actionable_reason(self):
        m = self.custom()
        from auto_update import fetch_release_via_api
        entry = m.make_github_entry("acme/player", "v1.2.3", m.detect_assets([self.asset("player-1.2.3-win-x64.exe")])[0], "windows", "Player", "工具")
        with patch("auto_update.requests.get") as get:
            get.return_value.json.return_value = {"tag_name": "v2.0.0", "assets": [self.asset("player-2.0.0-win-arm64.exe")]}
            with self.assertRaisesRegex(RuntimeError, "重新识别"):
                fetch_release_via_api(entry)

    def test_github_multi_platform_import_and_save_download_callback(self):
        m = self.custom()
        repo = {"full_name": "acme/player", "name": "Player"}
        assets = m.detect_assets([self.asset("player-v1.2.3-win-x64.exe"), self.asset("player-v1.2.3-arm64.dmg")])
        with tempfile.TemporaryDirectory() as td, patch.object(m, "inspect_github", return_value=(repo, "v1.2.3", assets)), patch("builtins.input", side_effect=["a", "Player", "音乐", "2"]), contextlib.redirect_stdout(io.StringIO()):
            download = unittest.mock.Mock(return_value=0)
            self.assertEqual(m.run_add(td, source_text="acme/player", download=download), 0)
            self.assertEqual({r["platform"] for r in m.list_entries(td)}, {"windows", "darwin"})
            self.assertEqual(len(download.call_args.args[0]), 2)

    def test_partial_custom_download_is_not_reported_as_success(self):
        import requests
        from auto_update import download_installer
        m = self.custom()
        app = m.make_fixed_entry("https://example.org/player.exe", "windows", "Player", "工具")
        def interrupted(*args, **kwargs):
            yield b"x" * 1500
            raise requests.ConnectionError("connection interrupted")
        with tempfile.TemporaryDirectory() as td, patch("auto_update.requests.get") as get:
            get.return_value.headers = {"content-length": "3000"}
            get.return_value.iter_content.side_effect = interrupted
            target = str(Path(td, "player.exe"))
            with self.assertRaisesRegex(RuntimeError, "网络连接"):
                download_installer("fixed", app["fixed_download_url"], app, target, max_retries=1)
            self.assertFalse(Path(target).exists())

    def test_import_drops_execution_flags_and_unsafe_paths(self):
        m = self.custom()
        with tempfile.TemporaryDirectory() as td:
            app = m.make_fixed_entry("https://example.org/player.exe", "windows", "Player", "工具")
            app.update(run_installer=True, kill_before_install=True, process_name="explorer", save_subdir="../../escape")
            m.import_entries(td, {"format": "gh-release-fetch-custom-v1", "entries": [{"platform": "windows", "app": app}]})
            saved = m.list_entries(td)[0]["app"]
            self.assertFalse(saved["run_installer"])
            self.assertEqual(saved["save_subdir"], saved["id"])
            self.assertNotIn("kill_before_install", saved)

    def test_custom_ipa_can_be_downloaded_while_store_entries_still_open_pages(self):
        import lookup_app
        hits = [{"id": "custom_ipa", "platform": "ios", "apps_dir": "apps-custom", "downloadable": True}]
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(lookup_app.run_download_now(hits, "apps-custom", True), 0)
        self.assertIn("--platform ios", output.getvalue())

    def test_fixed_url_downloads_through_real_updater_without_running_package(self):
        import http.server
        import threading
        from auto_update import update_one
        m = self.custom()
        payload = b"test package, never execute\n" * 100
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            def log_message(self, *args):
                pass
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as td, patch("auto_update.run_installer") as install, patch("auto_update.reveal_in_file_manager"), contextlib.redirect_stdout(io.StringIO()):
                url = "http://127.0.0.1:%d/package.exe" % server.server_port
                app = m.make_fixed_entry(url, "windows", "Fixture", "工具")
                self.assertEqual(update_one(app, td, platform_key="windows", cfg={"download_subdir_by_platform": True}), 0)
                target = Path(td, "windows", app["save_subdir"], "package.exe")
                self.assertEqual(target.read_bytes(), payload)
                install.assert_not_called()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


    def test_nested_menu_returns_to_caller_and_direct_zero_exits(self):
        m = self.custom()
        seen = []

        def search(query):
            seen.append(query)
            return 7

        with tempfile.TemporaryDirectory() as td, patch("builtins.input", side_effect=["1", "vlc"]), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(m.run_menu(td, search=search, download=lambda rows: 0), 7)
        self.assertEqual(seen, ["vlc"])
        seen.clear()
        with tempfile.TemporaryDirectory() as td, patch("builtins.input", side_effect=["0"]), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(m.run_menu(td, search=search, download=lambda rows: 0), 0)
        for token in ("0", "b", "返回", "back"):
            seen.clear()
            with tempfile.TemporaryDirectory() as td, patch("builtins.input", side_effect=["1", "", "9", token]), contextlib.redirect_stdout(io.StringIO()) as output:
                result = m.run_menu(td, search=search, download=lambda rows: 0, nested=True)
            self.assertIs(result, m.MENU_BACK)
            self.assertEqual(seen, [])
            self.assertIn("无效选择。", output.getvalue())
        with tempfile.TemporaryDirectory() as td, patch("builtins.input", side_effect=["1", "vlc"]), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(m.run_menu(td, search=lambda query: m.MENU_QUIT, download=lambda rows: 0, nested=True), 0)


if __name__ == "__main__":
    unittest.main()
