from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

from .research_tool import ResearchPage, validate_public_url


@dataclass
class PlaywrightBrowser:
    """Small, lazy Playwright adapter used by ResearchTool.

    Playwright is imported only when the browser is actually started, so the
    Jelon core remains importable on machines without the optional dependency.
    """

    headless: bool = True
    search_engine: str = "https://www.google.com/search?q={query}"
    timeout_ms: int = 15000

    def __post_init__(self) -> None:
        self._playwright: Any = None
        self._browser: Any = None
        self._page: Any = None

    def _ensure_started(self) -> Any:
        if self._page is not None:
            return self._page
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise RuntimeError(
                "Playwright is not installed. Install the optional browser dependency."
            ) from exc

        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=self.headless)
        self._page = self._browser.new_page()
        self._page.set_default_timeout(self.timeout_ms)
        return self._page

    def open(self, url: str) -> ResearchPage:
        if not validate_public_url(url):
            raise ValueError("Only valid HTTP(S) public URLs are allowed.")
        page = self._ensure_started()
        page.goto(url, wait_until="domcontentloaded")
        title = page.title()
        text = page.locator("body").inner_text()
        return ResearchPage(url=page.url, title=title, text=text)

    def search(self, query: str) -> list[ResearchPage]:
        if not query.strip():
            return []
        url = self.search_engine.format(query=quote(query.strip()))
        return [self.open(url)]

    def close(self) -> None:
        if self._browser is not None:
            self._browser.close()
        if self._playwright is not None:
            self._playwright.stop()
        self._browser = None
        self._page = None
        self._playwright = None

    def __enter__(self) -> "PlaywrightBrowser":
        self._ensure_started()
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()
