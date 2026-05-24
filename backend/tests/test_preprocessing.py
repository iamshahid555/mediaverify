import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.preprocessing import prepare_content  # noqa: E402


class PreprocessingTests(unittest.TestCase):
    def test_prepare_content_rejects_short_text(self):
        with self.assertRaisesRegex(ValueError, "too short"):
            prepare_content(url=None, text="Short text")

    @patch("app.services.preprocessing.extract_article_content")
    def test_prepare_content_returns_url_metadata(self, mock_extract_article_content):
        mock_extract_article_content.return_value = {
            "text": (
                "According to a city report, the transport authority increased weekday service after monitoring "
                "passenger demand and reviewing six months of delay data across the central route."
            ),
            "domain": "city.example",
        }

        result = prepare_content(
            url="https://city.example/transport/service-update",
            text=None,
        )

        self.assertEqual(result["input_type"], "url")
        self.assertEqual(result["source_url"], "https://city.example/transport/service-update")
        self.assertEqual(result["source_domain"], "city.example")
        self.assertTrue(result["content_preview"].startswith("According to a city report"))


if __name__ == "__main__":
    unittest.main()
