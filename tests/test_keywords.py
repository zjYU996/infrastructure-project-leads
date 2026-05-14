from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from project_leads.keywords import detect_project_type, relevance_level


class KeywordTests(unittest.TestCase):
    def test_bridge_tender_is_high_relevance(self) -> None:
        level, matches = relevance_level("Steel bridge EPC tender for a new viaduct")

        self.assertEqual(level, "High")
        self.assertGreaterEqual(len(matches), 3)

    def test_chinese_keywords_are_supported(self) -> None:
        level, _ = relevance_level("港口码头钢结构采购招标公告")

        self.assertEqual(level, "High")
        self.assertEqual(detect_project_type("港口码头钢结构采购招标公告"), "Steel Structure / 钢结构")

    def test_unrelated_text_has_no_relevance(self) -> None:
        level, matches = relevance_level("Annual report and investor update")

        self.assertIsNone(level)
        self.assertEqual(matches, [])


if __name__ == "__main__":
    unittest.main()
