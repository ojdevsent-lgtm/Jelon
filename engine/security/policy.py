from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class AutonomyPolicy:
    mode: str = "ask"
    workspace: Path = Path(".")
    allow_network: bool = False
    allow_browser: bool = False
    allow_git_write: bool = False
    allow_git_push: bool = False

    def permits(self, capability: str) -> bool:
        if capability in {"allow_files", "allow_processes"}:
            return self.mode in {"trusted_workspace", "authorized_repo"}
        if capability == "allow_browser":
            return self.allow_browser and self.allow_network
        if capability == "allow_network":
            return self.allow_network
        if capability == "allow_git_write":
            return self.allow_git_write and self.mode in {"trusted_workspace", "authorized_repo"}
        if capability == "allow_git_push":
            return self.allow_git_push and self.mode == "authorized_repo"
        return False
