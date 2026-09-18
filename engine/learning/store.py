from __future__ import annotations

import json
import os
import tempfile
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
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return {"tasks": [], "skills": {}, "knowledge": []}

    def _save(self, data: dict[str, Any]) -> None:
        """Atomically persist memory so an interrupted write cannot corrupt it."""
        fd, temp_name = tempfile.mkstemp(prefix=".jelon-memory-", suffix=".tmp", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, self.path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

    def record_task(self, goal: str, status: str, summary: str) -> None:
        data = self._load()
        data.setdefault("tasks", []).append({
            "goal": goal,
            "status": status,
            "summary": summary,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        self._save(data)

    def save_skill(self, name: str, procedure: list[str], verified: bool = False) -> None:
        data = self._load()
        data.setdefault("skills", {})[name] = {
            "procedure": procedure,
            "verified": bool(verified),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self._save(data)

    def get_skill(self, name: str) -> dict[str, Any] | None:
        return self._load().get("skills", {}).get(name)

    def recent_tasks(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._load().get("tasks", [])[-max(0, limit):]

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
        item = {
            "topic": topic,
            "summary": summary,
            "sources": sources,
            "verified": bool(verified),
            "tested": bool(tested),
            "tags": tags or [],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        data.setdefault("knowledge", []).append(item)
        self._save(data)

    def search_knowledge(
        self,
        query: str,
        limit: int = 10,
        verified_only: bool = False,
    ) -> list[dict[str, Any]]:
        """Offline lexical retrieval with optional verification filtering."""
        terms = {term.lower() for term in query.split() if term.strip()}
        if not terms:
            return []
        scored = []
        for item in self._load().get("knowledge", []):
            if verified_only and not item.get("verified"):
                continue
            haystack = " ".join([
                str(item.get("topic", "")),
                str(item.get("summary", "")),
                " ".join(item.get("tags", [])),
            ]).lower()
            score = sum(term in haystack for term in terms)
            if score:
                scored.append((score, item))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in scored[:max(0, limit)]]

    def task_context(self, goal: str, limit: int = 5) -> dict[str, Any]:
        """Return relevant memory that can be injected into a future agent goal."""
        return {
            "recent_tasks": self.recent_tasks(limit),
            "relevant_knowledge": self.search_knowledge(goal, limit),
        }
