from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import json

@dataclass
class Skill:
    name: str
    description: str = ""
    procedures: list[str] = field(default_factory=list)
    source: str = "local"
    verified: bool = False

class SkillRegistry:
    def __init__(self, root: str = "skills"):
        self.root = Path(root)
        self.skills: dict[str, Skill] = {}

    def discover(self) -> list[Skill]:
        self.skills.clear()
        if not self.root.exists():
            return []
        for path in self.root.glob("*/skill.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                skill = Skill(
                    name=data.get("name", path.parent.name),
                    description=data.get("description", ""),
                    procedures=data.get("procedures", []),
                    source=data.get("source", "local"),
                    verified=bool(data.get("verified", False)),
                )
                self.skills[skill.name] = skill
            except (OSError, ValueError):
                continue
        return list(self.skills.values())

    def get(self, name: str) -> Skill | None:
        return self.skills.get(name)
