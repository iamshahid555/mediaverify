from app.services.scraper import extract_article_content


PREVIEW_LENGTH = 180


def _build_preview(text: str, limit: int = PREVIEW_LENGTH) -> str:
    compact_text = " ".join(text.split())
    if len(compact_text) <= limit:
        return compact_text

    return f"{compact_text[: limit - 3].rstrip()}..."


def prepare_content(url: str | None, text: str | None) -> dict:
    """
    Return normalized content plus source metadata for downstream analysis.
    """

    if text:
        cleaned_text = text.strip()
        if len(cleaned_text) < 50:
            raise ValueError("Provided text is too short for analysis.")

        return {
            "text": cleaned_text,
            "input_type": "text",
            "content_preview": _build_preview(cleaned_text),
            "source_url": None,
            "source_domain": None,
        }

    if url:
        extracted = extract_article_content(url)
        return {
            "text": extracted["text"],
            "input_type": "url",
            "content_preview": _build_preview(extracted["text"]),
            "source_url": url,
            "source_domain": extracted["domain"],
        }

    raise ValueError("Either a valid URL or non-empty text must be provided.")


def prepare_text(url: str | None, text: str | None) -> str:
    return prepare_content(url=url, text=text)["text"]
