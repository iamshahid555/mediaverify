from pydantic import BaseModel, HttpUrl
from typing import Optional, List


class AnalyzeRequest(BaseModel):
    """
    Request schema for analyzing news content.
    The user can provide either a URL or raw text.
    """
    url: Optional[HttpUrl] = None
    text: Optional[str] = None


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