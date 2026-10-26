import contextlib
import io
import os
from pathlib import Path
import shutil
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools import ghrf_runtime as runtime

ROOT = Path(__file__).resolve().parents[1]
EXES = ("lookup_app", "auto_update", "run_saved_apps", "search_soft_pages", "search_games")
BATS = ("lookup_app", "lookup_mobile", "lookup_ios", "lookup_switch", "lookup_ps5", "run_saved_apps", "search_soft_pages", "search_games", "run_update")


class CliStartupTests(unittest.TestCase):
    def runner(self):
        self.assertTrue(hasattr(runtime, "run_cli"), "shared CLI startup/error handling is missing")
        return runtime.run_cli

    def test_double_click_failure_keeps_error_visible(self):
        runner = self.runner()
        with patch.object(sys, "argv", ["run_saved_apps.exe"]), patch.object(runtime, "owns_console_window", return_value=True), patch("builtins.input", return_value="") as prompt:
            self.assertEqual(runner(lambda: 1), 1)
            prompt.assert_called_once()

    def test_command_line_failure_does_not_block_automation(self):
        runner = self.runner()
        with patch.object(runtime, "owns_console_window", return_value=False), patch("builtins.input", side_effect=AssertionError("must not pause")):
            self.assertEqual(runner(lambda: 1), 1)

    def test_uncaught_failure_reports_traceback_and_diagnostic_file(self):
        runner = self.runner()
        def broken():
            raise RuntimeError("startup fixture error")
        with tempfile.TemporaryDirectory() as td, patch.object(runtime, "repo_root", return_value=td), patch.object(runtime, "owns_console_window", return_value=False), contextlib.redirect_stderr(io.StringIO()) as output:
            self.assertEqual(runner(broken), 1)
            self.assertIn("startup fixture error", output.getvalue())
            self.assertIn("startup fixture error", Path(td, "startup_error.log").read_text(encoding="utf-8"))

    def test_help_exit_is_preserved_without_pause(self):
        runner = self.runner()
        def help_exit():
            raise SystemExit(0)
        with patch.object(runtime, "owns_console_window", return_value=True), patch("builtins.input", side_effect=AssertionError("help must not pause")):
            self.assertEqual(runner(help_exit), 0)

    def test_updater_import_survives_unwritable_log_directory(self):
        with patch("logging.FileHandler", side_effect=PermissionError("read-only application folder")):
            runpy.run_path(str(ROOT / "auto_update.py"), run_name="startup_import_test")

    @unittest.skipUnless(os.name == "nt", "Windows console ownership")
    def test_onefile_parent_and_child_are_one_interactive_application(self):
        self.assertTrue(hasattr(runtime, "console_image_paths"), "onefile parent/child ownership detection is missing")
        executable = str(ROOT / "run_saved_apps.exe")
        with patch.object(sys, "frozen", True, create=True), patch.object(sys, "executable", executable), patch.object(sys.stdin, "isatty", return_value=True), patch.object(runtime, "console_image_paths", return_value=[executable, executable]):
            self.assertTrue(runtime.owns_console_window())
        with patch.object(sys, "frozen", True, create=True), patch.object(sys, "executable", executable), patch.object(sys.stdin, "isatty", return_value=True), patch.object(runtime, "console_image_paths", return_value=[executable, executable, "C:\\Windows\\System32\\cmd.exe"]):
            self.assertFalse(runtime.owns_console_window())


@unittest.skipUnless(os.name == "nt" and all((ROOT / "dist/exe" / (name + ".exe")).exists() for name in EXES), "requires Windows test executables")
class PortableBatTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(dir=ROOT / "build")
        cls.stage = Path(cls.temp.name)
        for name in BATS:
            shutil.copy2(ROOT / (name + ".bat"), cls.stage / (name + ".bat"))
        for name in EXES:
            shutil.copy2(ROOT / "dist/exe" / (name + ".exe"), cls.stage / (name + ".exe"))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_all_shortcuts_use_exe_when_python_exists_but_sources_do_not(self):
        env = dict(os.environ)
        env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + str(Path(os.environ["SystemRoot"], "System32"))
        for name in BATS:
            with self.subTest(entry=name):
                result = subprocess.run(["cmd.exe", "/d", "/c", str(self.stage / (name + ".bat")), "--help"], cwd=self.stage, env=env, input=b"\n", capture_output=True, timeout=20)
                self.assertEqual(result.returncode, 0, (name, result.stdout[-500:], result.stderr[-500:]))
                self.assertIn(b"usage:", result.stdout.lower())

    def test_portable_shortcuts_do_not_probe_python_or_store_aliases(self):
        shim = self.stage / "python.cmd"
        marker = self.stage / "python-probe.txt"
        shim.write_bytes(b'@echo off\r\necho probed>"%~dp0python-probe.txt"\r\nexit /b 88\r\n')
        try:
            for name in BATS:
                with self.subTest(entry=name):
                    result = subprocess.run(["cmd.exe", "/d", "/c", str(self.stage / (name + ".bat")), "--help"], cwd=self.stage, input=b"\n", capture_output=True, timeout=20)
                    self.assertEqual(result.returncode, 0, (name, result.stderr[-300:]))
                    self.assertFalse(marker.exists(), name)
        finally:
            shim.unlink()
            if marker.exists():
                marker.unlink()

    def test_frozen_apps_ignore_legacy_python_modules_next_to_executables(self):
        legacy = self.stage / "tools"
        legacy.mkdir(exist_ok=True)
        (legacy / "__init__.py").write_text("", encoding="utf-8")
        shutil.copy2(ROOT / "tools/ghrf_runtime.py", legacy / "ghrf_runtime.py")
        shutil.copy2(ROOT / "tools/app_download.py", legacy / "app_download.py")
        (legacy / "app_list.py").write_text("PLATFORMS = ('windows',)\n# Legacy version without CATALOGS\n", encoding="utf-8")
        channel = legacy / "soft_page_check"
        channel.mkdir(exist_ok=True)
        for name in ("list_scopes", "gamer520_live_search", "search_pages"):
            (channel / (name + ".py")).write_text("raise RuntimeError('legacy external module loaded')\n", encoding="utf-8")
        try:
            for name in EXES:
                with self.subTest(entry=name):
                    result = subprocess.run([str(self.stage / (name + ".exe")), "--help"], cwd=self.stage, capture_output=True, timeout=20)
                    self.assertEqual(result.returncode, 0, (name, result.stderr[-1800:]))
                    self.assertIn(b"usage:", result.stdout.lower())
        finally:
            shutil.rmtree(legacy)

    def test_real_onefile_double_click_keeps_configuration_errors_visible(self):
        (self.stage / "apps").mkdir(exist_ok=True)
        (self.stage / "apps" / "root.json").write_text('{"platform_keys":["windows"]}', encoding="utf-8")
        shell = shutil.which("pwsh") or shutil.which("powershell")
        script = '''
$probe = Start-Process -FilePath $env:STARTUP_TEST_EXE -WorkingDirectory $env:STARTUP_TEST_DIR -WindowStyle Hidden -PassThru
try {
    if ($probe.WaitForExit(5000)) { exit 2 }
    Write-Output 'ERROR_WINDOW_REMAINS_OPEN'
} finally {
    if (-not $probe.HasExited) { $probe.Kill($true); $probe.WaitForExit() }
}
'''
        for name in ("run_saved_apps", "auto_update"):
            with self.subTest(entry=name):
                env = dict(os.environ, STARTUP_TEST_EXE=str(self.stage / (name + ".exe")), STARTUP_TEST_DIR=str(self.stage))
                env.pop("GH_RELEASE_FETCH_NO_PAUSE", None)
                result = subprocess.run([shell, "-NoProfile", "-Command", script], env=env, capture_output=True, timeout=20)
                self.assertEqual(result.returncode, 0, (name, result.stderr))
                self.assertIn(b"ERROR_WINDOW_REMAINS_OPEN", result.stdout)


if __name__ == "__main__":
    unittest.main()
