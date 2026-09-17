from __future__ import annotations
from pathlib import Path
from .agent_controller import Observation

class FileTool:
    name = "files"
    description = "Read and write files inside an explicitly selected workspace."

    def __init__(self, permission_check):
        self.permission_check = permission_check

    def execute(self, arguments):
        if not self.permission_check("allow_files"):
            return Observation(False, "File access is disabled by policy.", {})
        root = Path(arguments.get("workspace", ".")).resolve()
        relative = Path(arguments.get("path", ""))
        target = (root / relative).resolve()
        if root not in target.parents and target != root:
            return Observation(False, "Path escapes the workspace.", {})
        action = arguments.get("action", "read")
        if action == "read":
            if not target.is_file():
                return Observation(False, "File does not exist.", {})
            return Observation(True, target.read_text(encoding="utf-8"), {"path": str(target)})
        if action == "write":
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(arguments.get("content", ""), encoding="utf-8")
            return Observation(True, "File written.", {"path": str(target)})
        return Observation(False, f"Unsupported file action: {action}", {})
