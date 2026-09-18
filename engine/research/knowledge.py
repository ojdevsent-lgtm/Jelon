from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from engine.learning.store import LearningStore


@dataclass
class VerifiedKnowledge:
    topic: str
    summary: str
    sources: list[str]
    tags: list[str]
    verified: bool = False
    tested: bool = False


class ResearchKnowledgePipeline:
    """Turns browser results into explicitly verified local knowledge.

    Extraction is intentionally injected so the pipeline can use a local model
    later without coupling storage to a specific inference runtime.
    """

    def __init__(
        self,
        store: LearningStore,
        extractor: Callable[[str, list[dict[str, Any]]], dict[str, Any]] | None = None,
    ):
        self.store = store
        self.extractor = extractor or self._default_extractor

    def ingest(
        self,
        topic: str,
        pages: list[dict[str, Any]],
        tested: bool = False,
    ) -> VerifiedKnowledge:
        usable = [
            page for page in pages
            if page.get("url") and page.get("text")
        ]
        extracted = self.extractor(topic, usable)
        sources = [
            str(page["url"]) for page in usable
            if str(page["url"]).startswith(("http://", "https://"))
        ]
        knowledge = VerifiedKnowledge(
            topic=topic,
            summary=str(extracted.get("summary", "")),
            sources=sources,
            tags=[str(tag) for tag in extracted.get("tags", [])],
            verified=bool(sources) and bool(extracted.get("summary")),
            tested=tested,
        )
        self.store.save_knowledge(
            knowledge.topic,
            knowledge.summary,
            knowledge.sources,
            verified=knowledge.verified,
            tested=knowledge.tested,
            tags=knowledge.tags,
        )
        return knowledge

    @staticmethod
    def _default_extractor(topic: str, pages: list[dict[str, Any]]) -> dict[str, Any]:
        # Conservative fallback: no claim is marked verified without a source.
        snippets = []
        for page in pages[:5]:
            text = " ".join(str(page.get("text", "")).split())
            if text:
                snippets.append(text[:1500])
        summary = " ".join(snippets)
        return {"summary": summary[:6000], "tags": [topic] if topic else []}
