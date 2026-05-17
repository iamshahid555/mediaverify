import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


ARTICLE_SELECTORS = (
    "article",
    "main",
    "[role='main']",
    ".article-body",
    ".story-body",
    ".caas-body",
    ".entry-content",
    ".post-content",
    "#articleBody",
)


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _paragraphs_from_node(node) -> list[str]:
    paragraphs: list[str] = []

    for paragraph in node.find_all("p"):
        text = _normalize_text(paragraph.get_text(" ", strip=True))
        if len(text) >= 60 and len(text.split()) >= 10:
            paragraphs.append(text)

    return paragraphs


def _select_article_text(soup: BeautifulSoup) -> str:
    candidate_paragraph_sets: list[list[str]] = []
    seen_nodes: set[int] = set()

    for selector in ARTICLE_SELECTORS:
        for node in soup.select(selector):
            node_id = id(node)
            if node_id in seen_nodes:
                continue

            seen_nodes.add(node_id)
            paragraphs = _paragraphs_from_node(node)
            if paragraphs:
                candidate_paragraph_sets.append(paragraphs)

    if not candidate_paragraph_sets:
        paragraphs = _paragraphs_from_node(soup)
        if paragraphs:
            candidate_paragraph_sets.append(paragraphs)

    if not candidate_paragraph_sets:
        return _normalize_text(soup.get_text(separator=" ", strip=True))

    candidate_paragraph_sets.sort(
        key=lambda paragraphs: sum(len(paragraph) for paragraph in paragraphs),
        reverse=True,
    )
    return " ".join(candidate_paragraph_sets[0])


def extract_article_content(url: str, timeout: int = 10) -> dict:
    """
    Fetch and extract likely article-body text from a URL.
    """

    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": "MediaVerify/1.0 (+https://example.com)"
            }
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ValueError(f"Failed to fetch URL content: {exc}")

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup([
        "script", "style", "noscript", "header", "footer", "aside", "nav",
        "form", "button", "svg"
    ]):
        tag.decompose()

    article_text = _select_article_text(soup)
    domain = urlparse(url).netloc.lower().removeprefix("www.")

    if not article_text or len(article_text) < 200:
        raise ValueError("Extracted article text is too short or empty.")

    return {
        "text": article_text,
        "domain": domain,
    }


def extract_article_text(url: str, timeout: int = 10) -> str:
    return extract_article_content(url, timeout=timeout)["text"]
