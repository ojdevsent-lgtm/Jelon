from __future__ import annotations
import subprocess
from .agent_controller import Observation

class GitTool:
    name = "git"
    description = "Inspect or modify a local Git workspace under Jelon permissions."

    def __init__(self, permission_check):
        self.permission_check = permission_check

    def execute(self, arguments):
        action = arguments.get("action", "status")
        cwd = arguments.get("cwd")
        commands = {
            "status": ["git", "status", "--short", "--branch"],
            "diff": ["git", "diff", "--"],
            "log": ["git", "log", "-5", "--oneline"],
            "pull": ["git", "pull", "--ff-only"],
            "commit": ["git", "commit", "-am", arguments.get("message", "Jelon update")],
            "push": ["git", "push"],
        }
        if action in {"commit", "push"} and not self.permission_check("allow_git_write"):
            return Observation(False, "Git write is disabled by policy.", {})
        if action == "push" and not self.permission_check("allow_git_push"):
            return Observation(False, "Git push is disabled by policy.", {})
        command = commands.get(action)
        if command is None:
            return Observation(False, f"Unsupported git action: {action}", {})
        p = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=120)
        return Observation(p.returncode == 0, (p.stdout or "") + (p.stderr or ""), {"returncode": p.returncode})
