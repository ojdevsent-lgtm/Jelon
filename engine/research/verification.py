from __future__ import annotations
from urllib.parse import urlparse


def valid_sources(pages: list[dict]) -> list[str]:
    result = []
    for page in pages:
        url = str(page.get("url", ""))
        parsed = urlparse(url)
        if parsed.scheme in {"http", "https"} and parsed.netloc:
            result.append(url)
    return result


def verify_research(pages: list[dict], minimum_sources: int = 1) -> bool:
    """Conservative verification: source presence is required; testing is separate."""
    return len(valid_sources(pages)) >= minimum_sources
