import contextlib
import io
import os
import re
import unittest
from unittest.mock import patch

import lookup_app
from tools.custom_catalog import run_menu
from tools.ui_lang import STRINGS, SUPPORTED, detect_language, resolve_tag, t

_SPEC = re.compile(r"%(?:%|[-+0 #]*\d*(?:\.\d+)?[a-zA-Z])")


class UiLangTests(unittest.TestCase):
    def test_every_language_has_the_same_placeholders(self):
        base = {key: _SPEC.findall(value) for key, value in STRINGS["zh-CN"].items()}
        for lang in SUPPORTED:
            self.assertEqual(set(STRINGS[lang]), set(base), lang)
            for key, specs in base.items():
                self.assertEqual(_SPEC.findall(STRINGS[lang][key]), specs, "%s %s" % (lang, key))

    def test_detect_exact_primary_and_fallback(self):
        self.assertEqual(resolve_tag("zh-TW"), "zh-TW")
        self.assertEqual(resolve_tag("zh_CN.UTF-8"), "zh-CN")
        self.assertEqual(resolve_tag("zh"), "zh-CN")
        self.assertEqual(resolve_tag("zh-HK"), "zh-CN")
        self.assertEqual(resolve_tag("zh-Hant-TW"), "zh-TW")
        self.assertEqual(resolve_tag("ja_JP.UTF-8"), "ja")
        self.assertEqual(resolve_tag("ko-KR"), "ko")
        self.assertEqual(resolve_tag("en_US.UTF-8"), "en")
        self.assertEqual(resolve_tag("fr_FR"), "en")
        self.assertIsNone(resolve_tag(""))
        self.assertIsNone(resolve_tag("C"))
        self.assertIsNone(resolve_tag("POSIX"))
        self.assertEqual(detect_language({"GH_RELEASE_FETCH_LANG": "en"}, win_langid=2052), "en")
        self.assertEqual(detect_language({"GH_RELEASE_FETCH_LANG": "zh-TW"}, win_langid=2052), "zh-TW")
        self.assertEqual(detect_language({"GH_RELEASE_FETCH_LANG": "de"}, win_langid=2052), "en")
        self.assertEqual(detect_language({"LC_ALL": "ja_JP.UTF-8", "LANG": "en"}, win_langid=2052), "ja")
        self.assertEqual(detect_language({"LANG": "en_US.UTF-8"}, win_langid=2052), "en")
        self.assertEqual(detect_language({}, win_langid=1028), "zh-TW")
        self.assertEqual(detect_language({}, win_langid=1041), "ja")
        self.assertEqual(detect_language({}, win_langid=1042), "ko")
        self.assertEqual(detect_language({}, win_langid=1033), "en")
        self.assertEqual(detect_language({}, win_langid=2052), "zh-CN")
        self.assertEqual(detect_language({}, win_langid=1031), "en")
        self.assertEqual(detect_language({}, win_langid=0), "zh-CN")
        self.assertEqual(detect_language({}, win_langid=None), "zh-CN")
        self.assertEqual(detect_language({"LANG": "C"}, win_langid=0), "zh-CN")

    def test_missing_key_uses_existing_chinese(self):
        STRINGS["zh-CN"]["_probe"] = "中文原文"
        try:
            with patch.dict(os.environ, {"GH_RELEASE_FETCH_LANG": "en"}):
                self.assertEqual(t("_probe"), "中文原文")
            with patch.dict(os.environ, {"GH_RELEASE_FETCH_LANG": "ja"}):
                self.assertEqual(t("choose.title"), "操作する項目を選んでください:")
        finally:
            del STRINGS["zh-CN"]["_probe"]

    def test_choose_prompt_follows_chinese_and_english(self):
        hits = [{"id": "a"}, {"id": "b"}]
        buf = io.StringIO()
        with patch.dict(os.environ, {"GH_RELEASE_FETCH_LANG": "zh-CN"}), \
                patch("builtins.input", return_value="b"), \
                contextlib.redirect_stdout(buf):
            self.assertIs(lookup_app.prompt_choose_hits(hits), lookup_app._BACK)
        text = buf.getvalue()
        self.assertIn("请选择要操作的条目", text)
        self.assertIn("b/回车=返回", text)
        self.assertIn("q=退出", text)

        buf = io.StringIO()
        with patch.dict(os.environ, {"GH_RELEASE_FETCH_LANG": "en"}), \
                patch("builtins.input", return_value="q"), \
                contextlib.redirect_stdout(buf):
            self.assertIs(lookup_app.prompt_choose_hits(hits), lookup_app._QUIT)
        text = buf.getvalue()
        self.assertIn("Select entries:", text)
        self.assertIn("b/Enter=back", text)
        self.assertIn("q=quit", text)
        self.assertNotIn("请选择", text)

    def test_custom_menu_english_keeps_quit_key(self):
        buf = io.StringIO()
        with patch.dict(os.environ, {"GH_RELEASE_FETCH_LANG": "en"}), \
                patch("builtins.input", return_value="q"), \
                contextlib.redirect_stdout(buf):
            self.assertEqual(run_menu("unused", search=lambda query: 0, download=lambda rows: 0), 0)
        text = buf.getvalue()
        self.assertIn("Custom apps", text)
        self.assertIn("q  quit", text)
        self.assertNotIn("自定义软件", text)


if __name__ == "__main__":
    unittest.main()
