from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

@dataclass
class ResearchPage:
    url: str
    title: str
    text: str
    source: str = "browser"

class ResearchTool:
    """Browser boundary for public research.

    The actual browser driver is injected so the core remains testable and
    does not require Playwright to be installed on every development machine.
    """

    name = "research"
    description = "Search and read public web pages when browser/network permissions are granted."
    capability = "allow_browser"

    def __init__(self, browser: Any, permission_check=None):
        self.browser = browser
        self.permission_check = permission_check or (lambda capability: True)

    def execute(self, arguments: dict[str, Any]):
        if not self.permission_check(self.capability):
            return {"success": False, "output": "Permission denied: allow_browser"}
        url = arguments.get("url")
        query = arguments.get("query")
        try:
            if query and hasattr(self.browser, "search"):
                pages = self.browser.search(str(query))
            elif url:
                pages = [self.browser.open(str(url))]
            else:
                return {"success": False, "output": "Provide a query or URL."}

            normalized = []
            for page in pages:
                if isinstance(page, dict):
                    item = page
                else:
                    item = {"url": getattr(page, "url", ""), "title": getattr(page, "title", ""), "text": getattr(page, "text", str(page))}
                normalized.append({
                    "url": item.get("url", ""),
                    "title": item.get("title", ""),
                    "text": item.get("text", "")[:12000],
                })
            return {"success": True, "output": f"Collected {len(normalized)} page(s).", "data": {"pages": normalized}}
        except Exception as exc:
            return {"success": False, "output": f"Research failed: {type(exc).__name__}: {exc}"}

def validate_public_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc) and not re.search(r"[
]", url)
