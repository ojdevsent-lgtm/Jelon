from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

class LearningStore:
    """Persistent local task/skill learning store.

    Stores observations and reusable procedures without modifying the model weights.
    """
    def __init__(self, path: str = "data/jelon_learning.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._save({"tasks": [], "skills": {}})

    def _load(self) -> dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, data: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def record_task(self, goal: str, status: str, summary: str) -> None:
        data = self._load()
        data["tasks"].append({
            "goal": goal, "status": status, "summary": summary,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        self._save(data)

    def save_skill(self, name: str, procedure: list[str], verified: bool = False) -> None:
        data = self._load()
        data["skills"][name] = {"procedure": procedure, "verified": verified}
        self._save(data)

    def get_skill(self, name: str) -> dict[str, Any] | None:
        return self._load()["skills"].get(name)

    def recent_tasks(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._load()["tasks"][-limit:]
