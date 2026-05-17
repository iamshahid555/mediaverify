from app.services.scraper import extract_article_content


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
            "source_domain": None,
        }

    if url:
        extracted = extract_article_content(url)
        return {
            "text": extracted["text"],
            "input_type": "url",
            "source_domain": extracted["domain"],
        }

    raise ValueError("Either a valid URL or non-empty text must be provided.")


def prepare_text(url: str | None, text: str | None) -> str:
    return prepare_content(url=url, text=text)["text"]
