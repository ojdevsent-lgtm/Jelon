from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

class LearningStore:
    """Persistent local task, skill, and research knowledge store."""

    def __init__(self, path: str = "data/jelon_learning.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._save({"tasks": [], "skills": {}, "knowledge": []})

    def _load(self) -> dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, data: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def record_task(self, goal: str, status: str, summary: str) -> None:
        data = self._load()
        data.setdefault("tasks", []).append({
            "goal": goal, "status": status, "summary": summary,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        self._save(data)

    def save_skill(self, name: str, procedure: list[str], verified: bool = False) -> None:
        data = self._load()
        data.setdefault("skills", {})[name] = {
            "procedure": procedure, "verified": verified,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        self._save(data)

    def get_skill(self, name: str) -> dict[str, Any] | None:
        return self._load().get("skills", {}).get(name)

    def recent_tasks(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._load().get("tasks", [])[-limit:]

    def save_knowledge(
        self,
        topic: str,
        summary: str,
        sources: list[str],
        verified: bool = False,
        tested: bool = False,
        tags: list[str] | None = None,
    ) -> None:
        """Persist research-derived knowledge with explicit verification state."""
        data = self._load()
        data.setdefault("knowledge", []).append({
            "topic": topic,
            "summary": summary,
            "sources": sources,
            "verified": bool(verified),
            "tested": bool(tested),
            "tags": tags or [],
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        self._save(data)

    def search_knowledge(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Simple offline lexical retrieval; vector retrieval can replace this later."""
        terms = {term.lower() for term in query.split() if term.strip()}
        if not terms:
            return []
        scored = []
        for item in self._load().get("knowledge", []):
            haystack = " ".join([
                str(item.get("topic", "")),
                str(item.get("summary", "")),
                " ".join(item.get("tags", [])),
            ]).lower()
            score = sum(term in haystack for term in terms)
            if score:
                scored.append((score, item))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in scored[:limit]]
