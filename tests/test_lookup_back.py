import contextlib
import io
import sys
import tempfile
import unittest
from unittest.mock import patch

import lookup_app


HIT = {
    "score": 100,
    "platform": "windows",
    "path": "windows/01.json",
    "abspath": "x",
    "apps_dir": "apps",
    "shard": "01.json",
    "shard_category": "工具",
    "id": "drawio",
    "分类": "工具",
    "enabled": False,
    "简介": "demo",
    "repo_path": "jgraph/drawio",
    "downloadable": True,
    "open_page_url": "",
}


class LookupBackTests(unittest.TestCase):
    def test_choose_back_skip_and_reprompt_invalid(self):
        hits = [{"id": "a"}, {"id": "b"}]
        for token in ("b", "B", "0", "back", "返回", ""):
            with patch("builtins.input", return_value=token):
                self.assertIs(lookup_app.prompt_choose_hits(hits), lookup_app._BACK)
        for token in ("q", "Q"):
            with patch("builtins.input", return_value=token):
                self.assertIs(lookup_app.prompt_choose_hits(hits), lookup_app._QUIT)
        with patch("builtins.input", return_value="2,1"):
            self.assertEqual([h["id"] for h in lookup_app.prompt_choose_hits(hits)], ["a", "b"])
        with patch("builtins.input", side_effect=["9", "x", "a"]):
            self.assertEqual(lookup_app.prompt_choose_hits(hits), hits)

    def test_action_back_returns_to_item_list(self):
        with patch("builtins.input", side_effect=["1", "b", "q"]), patch.object(lookup_app, "print_hits") as printed:
            self.assertIs(lookup_app.run_interactive([HIT], "apps", True), lookup_app._QUIT)
        printed.assert_called_once()
        with patch("builtins.input", side_effect=["1", "", "q"]), patch.object(lookup_app, "print_hits") as printed:
            self.assertIs(lookup_app.run_interactive([HIT], "apps", True), lookup_app._QUIT)
        printed.assert_called_once()
        with patch("builtins.input", side_effect=["nope", "b"]):
            self.assertEqual(lookup_app.prompt_action_mode(), "back")
        with patch("builtins.input", return_value=""):
            self.assertEqual(lookup_app.prompt_action_mode(), "back")
        with patch("builtins.input", return_value="q"):
            self.assertEqual(lookup_app.prompt_action_mode(), "quit")

    def test_keyword_enter_back_or_exit(self):
        with patch("builtins.input", return_value=""):
            self.assertIs(lookup_app._prompt_next_query(True), lookup_app._BACK)
            self.assertIsNone(lookup_app._prompt_next_query(False))
        with patch("builtins.input", return_value="other app"):
            self.assertEqual(lookup_app._prompt_next_query(False), ["other", "app"])

    def test_cli_back_searches_again(self):
        queries = []

        def fake_search(apps_dir, query, min_score=40):
            queries.append(query)
            return [HIT]

        with tempfile.TemporaryDirectory() as td, \
                patch.object(lookup_app, "search_apps", side_effect=fake_search), \
                patch("builtins.input", side_effect=["b", "other", "q"]), \
                contextlib.redirect_stdout(io.StringIO()):
            code = lookup_app.main(["--apps-dir", td, "drawio"])
        self.assertEqual(code, 0)
        self.assertEqual(queries, ["drawio", "other"])

    def test_menu_back_returns_to_catalog(self):
        state = {"n": 0}

        def catalog():
            state["n"] += 1
            if state["n"] == 1:
                sys.argv[:] = ["lookup_app.py", "--apps-dir", td, "drawio"]
                return True
            return False

        with tempfile.TemporaryDirectory() as td, \
                patch.object(sys, "argv", ["lookup_app.py"]), \
                patch.object(lookup_app, "prompt_catalog_and_query", side_effect=catalog), \
                patch.object(lookup_app, "search_apps", return_value=[HIT]), \
                patch("builtins.input", side_effect=["b", ""]), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(lookup_app.main(), 0)
        self.assertEqual(state["n"], 2)

    def test_enter_on_items_returns_to_keyword(self):
        queries = []

        def fake_search(apps_dir, query, min_score=40):
            queries.append(query)
            return [HIT]

        pending = ["", ""]

        def fake_input(prompt=""):
            if not pending:
                raise AssertionError("unexpected prompt")
            return pending.pop(0)

        with tempfile.TemporaryDirectory() as td, \
                patch.object(lookup_app, "search_apps", side_effect=fake_search), \
                patch("builtins.input", side_effect=fake_input), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(lookup_app.main(["--apps-dir", td, "drawio"]), 0)
        self.assertEqual(queries, ["drawio"])
        self.assertEqual(pending, [])

    def test_action_and_download_return_to_item_list(self):
        pending = ["1", "4", "q"]

        def fake_input(prompt=""):
            if not pending:
                raise AssertionError("unexpected prompt")
            return pending.pop(0)

        with tempfile.TemporaryDirectory() as td, \
                patch.object(lookup_app, "search_apps", return_value=[HIT]), \
                patch("builtins.input", side_effect=fake_input), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(lookup_app.main(["--apps-dir", td, "--dry-run", "drawio"]), 0)
        self.assertEqual(pending, [])

        pending = ["1", "q"]

        def fake_input_download(prompt=""):
            if not pending:
                raise AssertionError("unexpected prompt")
            return pending.pop(0)

        with tempfile.TemporaryDirectory() as td, \
                patch.object(lookup_app, "search_apps", return_value=[HIT]), \
                patch.object(lookup_app, "run_download_now", return_value=3) as downloaded, \
                patch("builtins.input", side_effect=fake_input_download), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(lookup_app.main(["--apps-dir", td, "--download", "drawio"]), 0)
        downloaded.assert_called_once()
        self.assertEqual(pending, [])

    def test_one_shot_flags_do_not_loop(self):
        with tempfile.TemporaryDirectory() as td, \
                patch.object(lookup_app, "search_apps", return_value=[HIT]), \
                patch("builtins.input", side_effect=AssertionError("should not prompt")), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(lookup_app.main(["--apps-dir", td, "--yes", "--dry-run", "--no-save-prompt", "drawio"]), 0)
            self.assertEqual(lookup_app.main(["--apps-dir", td, "--no-prompt", "drawio"]), 0)
            self.assertEqual(lookup_app.main(["--apps-dir", td, "-y", "--download", "--dry-run", "drawio"]), 0)
            self.assertEqual(lookup_app.main(["--apps-dir", td, "--open", "--dry-run", "drawio"]), 1)

    def test_catalog_empty_keyword_and_invalid_stay_open(self):
        pending = ["99", "1", "", "q"]

        def fake_input(prompt=""):
            if not pending:
                raise AssertionError("unexpected prompt")
            return pending.pop(0)

        with patch.object(sys, "argv", ["lookup_app.py"]), \
                patch("builtins.input", side_effect=fake_input), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertFalse(lookup_app.prompt_catalog_and_query())
        self.assertEqual(pending, [])

    def test_github_suggest_returns_to_keyword_unless_one_shot(self):
        queries = []

        def fake_search(apps_dir, query, min_score=40):
            queries.append(query)
            return []

        pending = ["other", ""]

        def fake_input(prompt=""):
            if not pending:
                raise AssertionError("unexpected prompt")
            return pending.pop(0)

        with tempfile.TemporaryDirectory() as td, \
                patch.object(lookup_app, "search_apps", side_effect=fake_search), \
                patch("tools.lookup_github_suggest.run_github_suggest", return_value=2), \
                patch("builtins.input", side_effect=fake_input), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(lookup_app.main(["--apps-dir", td, "drawio"]), 0)
        self.assertEqual(queries, ["drawio", "other"])
        self.assertEqual(pending, [])

        with tempfile.TemporaryDirectory() as td, \
                patch.object(lookup_app, "search_apps", return_value=[]), \
                patch("tools.lookup_github_suggest.run_github_suggest", return_value=2) as suggest, \
                patch("builtins.input", side_effect=AssertionError("should not prompt")), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(lookup_app.main(["--apps-dir", td, "--dry-run", "missing"]), 2)
            self.assertEqual(lookup_app.main(["--apps-dir", td, "--no-prompt", "missing"]), 2)
        self.assertEqual(suggest.call_count, 2)

    def test_menu_github_and_custom_return_to_catalog(self):
        state = {"n": 0}

        def catalog():
            state["n"] += 1
            if state["n"] == 1:
                sys.argv[:] = ["lookup_app.py", "--apps-dir", td, "missing"]
                return True
            return False

        with tempfile.TemporaryDirectory() as td, \
                patch.object(sys, "argv", ["lookup_app.py"]), \
                patch.object(lookup_app, "prompt_catalog_and_query", side_effect=catalog), \
                patch.object(lookup_app, "search_apps", return_value=[]), \
                patch("tools.lookup_github_suggest.run_github_suggest", return_value=0), \
                patch("builtins.input", side_effect=[""]), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(lookup_app.main(), 0)
        self.assertEqual(state["n"], 2)

        state["n"] = 0

        def catalog_custom():
            state["n"] += 1
            if state["n"] == 1:
                sys.argv[:] = ["lookup_app.py", "--custom"]
                return True
            return False

        pending = ["0"]

        def fake_input(prompt=""):
            if not pending:
                raise AssertionError("unexpected prompt")
            return pending.pop(0)

        with patch.object(sys, "argv", ["lookup_app.py"]), \
                patch.object(lookup_app, "prompt_catalog_and_query", side_effect=catalog_custom), \
                patch("builtins.input", side_effect=fake_input), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(lookup_app.main(), 0)
        self.assertEqual(state["n"], 2)
        self.assertEqual(pending, [])

        pending = ["0"]
        with patch("builtins.input", side_effect=fake_input), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(lookup_app.main(["--custom"]), 0)
        self.assertEqual(pending, [])


if __name__ == "__main__":
    unittest.main()
