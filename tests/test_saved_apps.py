import contextlib
import io
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import run_saved_apps
from tools.app_list import load_list, save_hits_by_platform


class SavedAppsTests(unittest.TestCase):
    def test_import_successful_history_and_remove_from_list(self):
        hit = {"platform": "windows", "id": "good", "path": "windows/01.json", "downloadable": True}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "update_log.txt").write_text(
                " - INFO - === [good] 开始 === [平台: windows]\n"
                " - INFO - [good] 安装包已下载: good.zip\n"
                " - INFO - === [failed] 开始 === [平台: windows]\n"
                " - ERROR - [failed] 失败: timed out\n",
                encoding="utf-8",
            )
            with patch.object(run_saved_apps, "SCRIPT_DIR", directory), \
                    patch("lookup_app.search_apps", return_value=[hit, dict(hit, id="failed")]) as search, \
                    patch("lookup_app.print_hits"), \
                    patch("builtins.input", side_effect=["i", "a", "q"]), \
                    contextlib.redirect_stdout(io.StringIO()):
                search.side_effect = lambda source, *a, **k: search.return_value if Path(source).name == "apps" else []
                self.assertEqual(run_saved_apps.main(["--manage"]), 0)
            path = root / "saved_apps_windows.json"
            self.assertEqual([row["id"] for row in load_list(path)["items"]], ["good"])
            with patch.object(run_saved_apps, "SCRIPT_DIR", directory), \
                    patch("builtins.input", side_effect=["1", "1", "y", "q"]), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(run_saved_apps.main(["--manage"]), 0)
            self.assertEqual(load_list(path)["count"], 0)

    def test_batch_uses_one_folder_and_opens_once_after_partial_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            hit = {"id": "demo", "path": "01.json"}
            save_hits_by_platform(directory, [dict(hit, platform=p) for p in ("windows", "linux")], str(root / "apps"))
            folders = []

            def updater(command, **kwargs):
                folder = Path(command[command.index("--batch-download-dir") + 1])
                folders.append(folder)
                platform = command[command.index("--platform") + 1]
                if platform == "windows":
                    (folder / "demo.zip").touch()
                return subprocess.CompletedProcess(command, int(platform == "linux"))

            with patch.object(run_saved_apps, "SCRIPT_DIR", directory), \
                    patch.object(run_saved_apps, "resolve_auto_update_argv", side_effect=lambda root, args: args), \
                    patch.object(run_saved_apps.subprocess, "run", side_effect=updater), \
                    patch.object(run_saved_apps.subprocess, "Popen") as opener, \
                    patch("builtins.input", side_effect=["a", "q"]), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(run_saved_apps.main(["--manage"]), 1)
            self.assertEqual(len(folders), 2)
            self.assertEqual(folders[0], folders[1])
            self.assertEqual(opener.call_args.args[0][1], str(folders[0]))
            self.assertEqual(opener.call_count, 1)
