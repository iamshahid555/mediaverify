import re


TRUSTED_DOMAIN_SCORES = {
    "reuters.com": 0.22,
    "apnews.com": 0.2,
    "bbc.com": 0.18,
    "bbc.co.uk": 0.18,
    "nytimes.com": 0.18,
    "washingtonpost.com": 0.18,
    "wsj.com": 0.18,
    "ft.com": 0.18,
    "theguardian.com": 0.18,
    "npr.org": 0.2,
    "abcnews.go.com": 0.18,
    "cbsnews.com": 0.18,
    "nbcnews.com": 0.18,
    "usatoday.com": 0.16,
    "aljazeera.com": 0.16,
    "bloomberg.com": 0.18,
    "politico.com": 0.14,
    "nasa.gov": 0.24,
    "cdc.gov": 0.24,
    "nih.gov": 0.22,
    "who.int": 0.24,
    "un.org": 0.18,
    "goal.com": 0.14,
    "espn.com": 0.16,
    "skysports.com": 0.16,
    "theathletic.com": 0.16,
}

LOW_TRUST_DOMAIN_SCORES = {
    "beforeitsnews.com": -0.3,
    "naturalnews.com": -0.26,
    "worldnewsdailyreport.com": -0.32,
    "infowars.com": -0.32,
}

SENSATIONAL_PATTERNS = [
    "shocking",
    "secret",
    "miracle",
    "hoax",
    "conspiracy",
    "cover-up",
    "they don't want you to know",
    "mainstream media won't tell you",
    "act now",
    "click here",
    "hidden truth",
]

EVIDENCE_PATTERNS = [
    "according to",
    "reported",
    "confirmed",
    "official",
    "authorities",
    "agency",
    "statement",
    "data",
    "study",
    "research",
    "documents",
    "court",
    "report",
]

AGENCY_PATTERNS = [
    "reuters",
    "associated press",
    "ap news",
    "bbc",
    "cdc",
    "nasa",
    "world health organization",
    "united nations",
]

ABSOLUTIST_PATTERN = re.compile(
    r"\b(always|never|nobody|everyone|completely|guaranteed|proves?|"
    r"undeniable|instantly)\b",
    re.IGNORECASE,
)
DATE_PATTERN = re.compile(
    r"\b(january|february|march|april|may|june|july|august|september|"
    r"october|november|december|\d{4})\b",
    re.IGNORECASE,
)
QUOTE_PATTERN = re.compile(r"\"[^\"]+\"")


def _count_pattern_hits(text: str, patterns: list[str]) -> int:
    normalized = text.lower()
    return sum(normalized.count(pattern) for pattern in patterns)


def _match_domain_score(source_domain: str | None) -> tuple[float, str | None]:
    if not source_domain:
        return 0.0, None

    domain = source_domain.lower()

    for trusted_domain, score in TRUSTED_DOMAIN_SCORES.items():
        if domain == trusted_domain or domain.endswith(f".{trusted_domain}"):
            return score, trusted_domain

    for low_trust_domain, score in LOW_TRUST_DOMAIN_SCORES.items():
        if domain == low_trust_domain or domain.endswith(f".{low_trust_domain}"):
            return score, low_trust_domain

    if domain.endswith(".gov") or domain.endswith(".edu"):
        return 0.18, domain

    return 0.0, None


def _build_indicators(
    source_domain: str | None,
    matched_domain: str | None,
    domain_score: float,
    attribution_hits: int,
    evidence_hits: int,
    agency_hits: int,
    date_hits: int,
    quote_hits: int,
    sensational_hits: int,
    absolutist_hits: int,
    all_caps_hits: int,
) -> list[str]:
    signals: list[tuple[float, str]] = []

    if matched_domain and domain_score > 0:
        signals.append((
            abs(domain_score),
            f"Source signal: {matched_domain} carries a stronger reliability baseline than an unknown domain.",
        ))

    if matched_domain and domain_score < 0:
        signals.append((
            abs(domain_score),
            f"Risk signal: {matched_domain} has a weaker reliability baseline and needs stronger independent confirmation.",
        ))

    if source_domain and not matched_domain and domain_score == 0:
        signals.append((
            0.04,
            f"Source signal: {source_domain} is not yet in the source reference list, so the result relies more on article wording than source history.",
        ))

    if attribution_hits >= 2 or agency_hits >= 1:
        signals.append((
            0.12,
            "Attribution signal: the text includes reporting or institution-style attribution that is easier to verify.",
        ))

    if evidence_hits >= 2 or date_hits >= 1 or quote_hits >= 1:
        signals.append((
            0.1,
            "Verification signal: dates, quotes, or report-style wording make the claim more traceable.",
        ))

    if sensational_hits >= 1:
        signals.append((
            0.15,
            "Risk signal: the wording includes sensational or conspiratorial language often seen in misleading content.",
        ))

    if absolutist_hits >= 3:
        signals.append((
            0.08,
            "Risk signal: absolutist wording like 'all', 'never', or 'guaranteed' lowers credibility confidence.",
        ))

    if all_caps_hits >= 2:
        signals.append((
            0.06,
            "Risk signal: excessive all-caps emphasis suggests more emotional framing than standard reporting.",
        ))

    if not signals:
        signals.append((
            0.01,
            "Next check: confirm the publication date, named sources, and whether independent reporting matches the same claim.",
        ))

    signals.sort(key=lambda item: item[0], reverse=True)
    indicators = [text for _, text in signals[:3]]

    if not any(text.startswith("Next check:") for text in indicators):
        indicators.append(
            "Next check: confirm the publication date, named sources, and whether independent reporting matches the same claim."
        )

    return indicators[:4]


def analyze_text(text: str, source_domain: str | None = None) -> dict:
    """
    Run feature-based credibility analysis on extracted content.
    """

    normalized_text = re.sub(r"\s+", " ", text).strip()
    lowered_text = normalized_text.lower()
    word_count = len(normalized_text.split())

    domain_score, matched_domain = _match_domain_score(source_domain)
    attribution_hits = _count_pattern_hits(lowered_text, ["according to", "reported", "said", "confirmed", "stated"])
    evidence_hits = _count_pattern_hits(lowered_text, EVIDENCE_PATTERNS)
    agency_hits = _count_pattern_hits(lowered_text, AGENCY_PATTERNS)
    sensational_hits = _count_pattern_hits(lowered_text, SENSATIONAL_PATTERNS)
    absolutist_hits = len(ABSOLUTIST_PATTERN.findall(normalized_text))
    date_hits = len(DATE_PATTERN.findall(normalized_text))
    quote_hits = len(QUOTE_PATTERN.findall(normalized_text))
    exclamation_hits = normalized_text.count("!")
    all_caps_hits = sum(
        1
        for token in re.findall(r"\b[A-Z]{4,}\b", normalized_text)
        if token.isupper()
    )

    score = 0.5
    score += domain_score
    score += min(0.14, attribution_hits * 0.035)
    score += min(0.14, evidence_hits * 0.025)
    score += min(0.1, agency_hits * 0.05)
    score += min(0.06, date_hits * 0.02)
    score += min(0.04, quote_hits * 0.02)

    if word_count >= 120:
        score += 0.04
    elif word_count >= 35:
        score += 0.02

    if attribution_hits >= 1 and evidence_hits >= 2:
        score += 0.03

    score -= min(0.24, sensational_hits * 0.08)
    score -= min(0.08, absolutist_hits * 0.02)
    score -= min(0.06, exclamation_hits * 0.03)
    score -= min(0.06, all_caps_hits * 0.03)

    score = min(max(score, 0.05), 0.95)
    if score >= 0.62:
        credibility_label = "Likely Credible"
    elif score >= 0.45:
        credibility_label = "Needs Review"
    else:
        credibility_label = "Possibly Non-Credible"

    confidence = min(0.95, 0.52 + abs(score - 0.5) * 0.8)

    if credibility_label == "Needs Review":
        confidence = min(confidence, 0.68)

    indicators = _build_indicators(
        source_domain=source_domain,
        matched_domain=matched_domain,
        domain_score=domain_score,
        attribution_hits=attribution_hits,
        evidence_hits=evidence_hits,
        agency_hits=agency_hits,
        date_hits=date_hits,
        quote_hits=quote_hits,
        sensational_hits=sensational_hits,
        absolutist_hits=absolutist_hits,
        all_caps_hits=all_caps_hits,
    )

    return {
        "credibility_score": round(float(score), 4),
        "credibility_label": credibility_label,
        "raw_label": "FEATURE-BASED",
        "confidence": round(float(confidence), 4),
        "indicators": indicators,
    }
