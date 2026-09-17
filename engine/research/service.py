"""Jelon research boundary.

Internet access is explicit: the agent may invoke a browser/research adapter only when the user authorizes network research.
"""
from dataclasses import dataclass

@dataclass
class ResearchResult:
    query: str
    sources: list[str]
    notes: str

class ResearchService:
    def search(self, query: str) -> ResearchResult:
        raise NotImplementedError("Attach the Playwright/browser adapter here; network access is not implicit.")
