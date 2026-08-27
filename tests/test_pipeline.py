"""Tests for the pure parts of the pipeline.

Same convention as the lunchUncle repo: functions that do IO are left alone,
functions that shape data are tested. No network, no keys, no fixtures.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline import integrity  # noqa: E402
from pipeline.fetch import collapse, extract_text  # noqa: E402
from pipeline.translate import parse_hokkien  # noqa: E402
from pipeline.whitelist import NotWhitelisted, check, is_allowed  # noqa: E402


class TestWhitelist(unittest.TestCase):
    def test_allows_whitelisted_hosts_and_subdomains(self):
        for url in ("https://www.moneysense.gov.sg/articles/x",
                    "https://cpf.gov.sg/member",
                    "https://www.mas.gov.sg/news"):
            self.assertTrue(is_allowed(url), url)

    def test_blocks_the_open_web(self):
        with self.assertRaises(NotWhitelisted):
            check("https://example.com/money")

    def test_blocks_lookalike_suffix_attack(self):
        # The guardrail is worthless if this passes.
        with self.assertRaises(NotWhitelisted):
            check("https://moneysense.gov.sg.evil.com/page")

    def test_blocks_plain_http(self):
        with self.assertRaises(NotWhitelisted):
            check("http://moneysense.gov.sg/page")


class TestExtractText(unittest.TestCase):
    def test_drops_script_and_style_content(self):
        html = "<p>Keep this</p><script>var secret = 1;</script><style>p{color:red}</style>"
        text = extract_text(html)
        self.assertIn("Keep this", text)
        self.assertNotIn("secret", text)
        self.assertNotIn("color", text)

    def test_block_tags_become_line_breaks(self):
        self.assertEqual(extract_text("<p>One</p><p>Two</p>"), "One\nTwo")

    def test_collapse_normalises_whitespace(self):
        self.assertEqual(collapse("  a   b  \n\n\n  c  "), "a b\nc")


class TestIntegrity(unittest.TestCase):
    def test_normalise_strips_currency_and_separators(self):
        for raw in ("S$1,000", "$1000", "1,000", "1000"):
            self.assertEqual(integrity.normalise(raw), "1000", raw)

    def test_normalise_trims_trailing_zeros(self):
        self.assertEqual(integrity.normalise("3.50"), "3.5")
        self.assertEqual(integrity.normalise("3.0"), "3")

    def test_extract_finds_money_percentages_and_ages(self):
        found = integrity.extract_figures("Pay S$1,200 at 4.5% from age 65.")
        self.assertEqual(found, {"1200", "4.5%", "65"})

    def test_passes_when_every_figure_survives(self):
        result = integrity.check("You get S$1,200 at age 65.",
                                 ("Chinese", "你在65岁拿到1,200元。"))
        self.assertTrue(result["ok"], result)

    def test_flags_a_figure_that_changed(self):
        # The exact failure this module exists to catch.
        result = integrity.check("You get S$1,200 at age 65.",
                                 ("Chinese", "你在65岁拿到1,300元。"))
        self.assertFalse(result["ok"])
        self.assertIn("1200", result["missing"]["Chinese"])

    def test_flags_a_figure_that_vanished(self):
        result = integrity.check("Payouts start at age 65.",
                                 ("Hokkien", "開始領錢。"))
        self.assertFalse(result["ok"])
        self.assertIn("65", result["missing"]["Hokkien"])

    def test_han_numerals_are_not_false_positives(self):
        # 一千 is 1000 written differently, not a dropped figure.
        result = integrity.check("You get $1000.", ("Chinese", "你拿到一千元。"))
        self.assertTrue(result["ok"], result)

    def test_empty_translation_reports_everything_missing(self):
        result = integrity.check("You get $500 at 65.", ("Hokkien", ""))
        self.assertFalse(result["ok"])
        self.assertEqual(set(result["missing"]["Hokkien"]), {"500", "65"})

    def test_report_is_readable_on_success_and_failure(self):
        ok = integrity.check("Pay $50.", ("Chinese", "付50元。"))
        self.assertIn("survived", integrity.format_report(ok))

        bad = integrity.check("Pay $50.", ("Chinese", "付60元。"))
        self.assertIn("MISMATCH", integrity.format_report(bad))
        self.assertIn("Do not publish", integrity.format_report(bad))


class TestParseHokkien(unittest.TestCase):
    def test_parses_plain_json(self):
        got = parse_hokkien('{"han": "這馬", "tailo": "tsit-ma2", "register_notes": "n"}')
        self.assertEqual(got["han"], "這馬")
        self.assertEqual(got["tailo"], "tsit-ma2")
        self.assertFalse(got["parse_failed"])

    def test_parses_json_in_a_fenced_block(self):
        got = parse_hokkien('```json\n{"han": "這馬", "tailo": "tsit-ma2"}\n```')
        self.assertEqual(got["han"], "這馬")
        self.assertFalse(got["parse_failed"])

    def test_falls_back_to_raw_text_rather_than_losing_a_translation(self):
        got = parse_hokkien("這馬無啥物錢")
        self.assertEqual(got["han"], "這馬無啥物錢")
        self.assertTrue(got["parse_failed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
