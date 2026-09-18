from __future__ import annotations

from typing import Any


class WindowsComputerTool:
    """Agent-facing wrapper for WindowsComputerAdapter."""

    name = "windows_computer"
    description = "Control the Windows desktop: launch/open, mouse, keys, hotkeys, and text input."
    capability = "allow_processes"

    def __init__(self, adapter):
        self.adapter = adapter

    def execute(self, arguments: dict[str, Any]):
        action = str(arguments.get("action", "")).strip()
        payload = arguments.get("arguments") or {}
        if not action:
            return {"success": False, "output": "Missing computer action."}
        return {"success": True, "output": str(getattr(self.adapter, action)(**payload))}
