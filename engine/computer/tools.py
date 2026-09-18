from __future__ import annotations
from pathlib import Path
from typing import Any

class ComputerTool:
    """Safe computer-tool boundary; concrete OS adapters can be injected."""
    def __init__(self, adapter: Any, permission_check):
        self.adapter = adapter
        self.permission_check = permission_check

    def execute(self, action: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if not self.permission_check("allow_processes"):
            return {"success": False, "output": "Permission denied: allow_processes"}
        method = getattr(self.adapter, action, None)
        if method is None:
            return {"success": False, "output": f"Unsupported computer action: {action}"}
        try:
            return {"success": True, "output": str(method(**arguments))}
        except Exception as exc:
            return {"success": False, "output": f"{type(exc).__name__}: {exc}"}
