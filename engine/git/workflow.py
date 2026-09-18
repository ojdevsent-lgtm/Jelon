from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any

@dataclass
class GitWorkflow:
    runner: Any
    permission_check: Any

    def inspect(self, path: str = ".") -> Any:
        return self.runner.run(["status", "--short"], cwd=Path(path))

    def test(self, command: list[str], cwd: str = ".") -> Any:
        return self.runner.run(command, cwd=Path(cwd))

    def commit(self, message: str, cwd: str = ".") -> Any:
        if not self.permission_check("allow_git_write"):
            return {"success": False, "output": "Permission denied: allow_git_write"}
        return self.runner.run(["commit", "-am", message], cwd=Path(cwd))

    def push(self, remote: str = "origin", branch: str = "HEAD", cwd: str = ".") -> Any:
        if not self.permission_check("allow_git_push"):
            return {"success": False, "output": "Permission denied: allow_git_push"}
        return self.runner.run(["push", remote, branch], cwd=Path(cwd))
