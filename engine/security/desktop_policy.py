from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from engine.agent.tools import PermissionPolicy


@dataclass
class DesktopPolicy:
    """Persisted desktop permission settings.

    Safe defaults deny network/browser/Git writes/pushes. Process and file
    control are enabled only through an explicit trusted mode.
    """
    autonomy: str = "ask"
    allow_files: bool = False
    allow_processes: bool = False
    allow_browser: bool = False
    allow_network: bool = False
    allow_git_write: bool = False
    allow_git_push: bool = False

    def validate(self) -> None:
        if self.autonomy not in {"ask", "trusted_workspace", "authorized_repo"}:
            raise ValueError("Unsupported autonomy mode")
        if self.allow_browser and not self.allow_network:
            raise ValueError("Browser access requires network access")
        if self.allow_git_push and self.autonomy != "authorized_repo":
            raise ValueError("Git push requires authorized_repo mode")
        if self.autonomy == "ask":
            self.allow_files = False
            self.allow_processes = False
            self.allow_git_write = False
            self.allow_git_push = False

    def tool_policy(self) -> PermissionPolicy:
        self.validate()
        return PermissionPolicy(
            allow_files=self.allow_files,
            allow_processes=self.allow_processes,
            allow_browser=self.allow_browser,
            allow_network=self.allow_network,
            allow_git_write=self.allow_git_write,
            allow_git_push=self.allow_git_push,
        )


class PolicyStore:
    def __init__(self, path: str | Path = "data/jelon_policy.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> DesktopPolicy:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            policy = DesktopPolicy(**{k: raw[k] for k in asdict(DesktopPolicy()).keys() if k in raw})
        except (FileNotFoundError, json.JSONDecodeError, TypeError):
            policy = DesktopPolicy()
        policy.validate()
        return policy

    def save(self, policy: DesktopPolicy) -> DesktopPolicy:
        policy.validate()
        temp = self.path.with_suffix(".tmp")
        temp.write_text(json.dumps(asdict(policy), indent=2), encoding="utf-8")
        os.replace(temp, self.path)
        return policy
