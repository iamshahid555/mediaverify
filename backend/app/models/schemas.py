from typing import List, Optional

from pydantic import BaseModel, HttpUrl, model_validator


class AnalyzeRequest(BaseModel):
    """
    Request schema for analyzing news content.
    The user can provide either a URL or raw text.
    """
    url: Optional[HttpUrl] = None
    text: Optional[str] = None

    @model_validator(mode="after")
    def validate_input_source(self):
        has_url = self.url is not None
        has_text = bool(self.text and self.text.strip())

        if has_url == has_text:
            raise ValueError("Provide exactly one of 'url' or 'text'.")

        if self.text is not None:
            self.text = self.text.strip()

        return self


class HistoryItem(BaseModel):
    id: int
    input_type: str
    credibility_score: float
    credibility_label: str
    confidence: float
    content_preview: Optional[str] = None
    source_url: Optional[str] = None
    source_domain: Optional[str] = None
    created_at: str


class Explanation(BaseModel):
    """
    Human-readable explanation for the credibility result.
    """
    label: str
    confidence: float
    indicators: List[str]


class AnalyzeResponse(BaseModel):
    """
    Response schema returned after analysis.
    """
    credibility_score: float
    credibility_label: str
    explanation: Explanation


class HistoryResponse(BaseModel):
    history: List[HistoryItem]
