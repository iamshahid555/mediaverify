import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.api.analyze import router  # noqa: E402


class AnalyzeApiTests(unittest.TestCase):
    def setUp(self):
        app = FastAPI()
        app.include_router(router)
        self.client = TestClient(app)

    @patch("app.api.analyze.save_analysis")
    @patch("app.api.analyze.analyze_text")
    @patch("app.api.analyze.prepare_content")
    def test_analyze_returns_structured_response(
        self,
        mock_prepare_content,
        mock_analyze_text,
        mock_save_analysis,
    ):
        mock_prepare_content.return_value = {
            "text": "According to a public health bulletin, local clinics reported a scheduled vaccine update.",
            "input_type": "text",
            "content_preview": "According to a public health bulletin, local clinics reported a scheduled vaccine update.",
            "source_url": None,
            "source_domain": None,
        }
        mock_analyze_text.return_value = {
            "credibility_score": 0.72,
            "credibility_label": "Likely Credible",
            "confidence": 0.83,
            "indicators": [
                "Attribution signal: the text includes reporting or institution-style attribution that is easier to verify.",
                "Next check: confirm the publication date, named sources, and whether independent reporting matches the same claim.",
            ],
        }

        response = self.client.post(
            "/analyze",
            json={
                "text": "According to a public health bulletin, local clinics reported a scheduled vaccine update."
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["credibility_label"], "Likely Credible")
        self.assertIn("confidence", response.json()["explanation"])
        mock_save_analysis.assert_called_once_with(
            input_type="text",
            credibility_score=0.72,
            credibility_label="Likely Credible",
            confidence=0.83,
            content_preview="According to a public health bulletin, local clinics reported a scheduled vaccine update.",
            source_url=None,
            source_domain=None,
        )

    @patch("app.api.analyze.prepare_content", side_effect=ValueError("Provided text is too short for analysis."))
    def test_analyze_returns_400_for_invalid_input(self, _mock_prepare_content):
        response = self.client.post("/analyze", json={"text": "Too short"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Provided text is too short for analysis.")

    def test_analyze_rejects_multiple_input_sources(self):
        response = self.client.post(
            "/analyze",
            json={
                "text": "According to the local authority, the scheduled maintenance will continue through the weekend for the central route.",
                "url": "https://example.com/article",
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("Provide exactly one", response.text)

    @patch("app.api.analyze.get_analysis_history")
    def test_history_returns_saved_records(self, mock_get_analysis_history):
        mock_get_analysis_history.return_value = [
            {
                "id": 1,
                "input_type": "url",
                "credibility_score": 0.68,
                "credibility_label": "Likely Credible",
                "confidence": 0.79,
                "content_preview": "A public agency released an updated flood warning for riverside districts.",
                "source_url": "https://example.com/flood-warning",
                "source_domain": "example.com",
                "created_at": "2026-05-24T10:00:00",
            }
        ]

        response = self.client.get("/history")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["history"][0]["source_domain"], "example.com")

    @patch("app.api.analyze.save_analysis")
    @patch("app.api.analyze.analyze_text")
    @patch("app.api.analyze.prepare_content")
    def test_analyze_supports_middle_review_label(
        self,
        mock_prepare_content,
        mock_analyze_text,
        mock_save_analysis,
    ):
        mock_prepare_content.return_value = {
            "text": "A sports report described a cup final result with match events and player performance highlights.",
            "input_type": "url",
            "content_preview": "A sports report described a cup final result with match events and player performance highlights.",
            "source_url": "https://goal.com/example",
            "source_domain": "goal.com",
        }
        mock_analyze_text.return_value = {
            "credibility_score": 0.56,
            "credibility_label": "Needs Review",
            "confidence": 0.61,
            "indicators": [
                "Source signal: goal.com carries a stronger reliability baseline than an unknown domain.",
                "Next check: confirm the publication date, named sources, and whether independent reporting matches the same claim.",
            ],
        }

        response = self.client.post(
            "/analyze",
            json={"url": "https://goal.com/example"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["credibility_label"], "Needs Review")
        mock_save_analysis.assert_called_once()


if __name__ == "__main__":
    unittest.main()
