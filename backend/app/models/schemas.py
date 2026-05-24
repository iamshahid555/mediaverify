import re
from typing import List, Optional

from pydantic import BaseModel, HttpUrl, field_validator, model_validator

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


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


class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 2:
            raise ValueError("Enter a full name with at least 2 characters.")
        return cleaned

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if not EMAIL_PATTERN.match(cleaned):
            raise ValueError("Provide a valid email address.")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        return value


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if not EMAIL_PATTERN.match(cleaned):
            raise ValueError("Provide a valid email address.")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not value:
            raise ValueError("Password is required.")
        return value


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    created_at: str


class AuthResponse(BaseModel):
    token: str
    user: UserResponse


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


class MessageResponse(BaseModel):
    message: str
