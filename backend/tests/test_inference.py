import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.inference import analyze_text  # noqa: E402


class InferenceTests(unittest.TestCase):
    def test_credible_reporting_style_scores_higher(self):
        text = (
            "According to Reuters, the health agency confirmed in its June 2026 report that vaccination rates "
            "increased after the campaign launch. Officials said updated clinic data and public statements would "
            "continue to be published each week for independent review."
        )

        result = analyze_text(text, source_domain="reuters.com")

        self.assertEqual(result["credibility_label"], "Likely Credible")
        self.assertGreaterEqual(result["credibility_score"], 0.6)
        self.assertTrue(any("Source signal" in indicator for indicator in result["indicators"]))

    def test_sensational_content_scores_lower(self):
        text = (
            "Shocking secret documents prove a miracle liquid instantly cures every illness and they do not want "
            "you to know the hidden truth. Mainstream media will never report it because the cover-up protects "
            "powerful companies from public outrage."
        )

        result = analyze_text(text)

        self.assertEqual(result["credibility_label"], "Possibly Non-Credible")
        self.assertLess(result["credibility_score"], 0.6)
        self.assertTrue(any("Risk signal" in indicator for indicator in result["indicators"]))


if __name__ == "__main__":
    unittest.main()
