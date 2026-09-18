from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Protocol

class Tool(Protocol):
    name: str; description: str; capability: str
    def execute(self, arguments: dict[str, Any]) -> Any: ...

@dataclass
class PermissionPolicy:
    allow_files: bool = False; allow_processes: bool = False; allow_browser: bool = False
    allow_network: bool = False; allow_git_write: bool = False; allow_git_push: bool = False
    def allows(self, capability: str) -> bool: return bool(getattr(self, capability, False))

class ToolRegistry:
    def __init__(self, policy=None): self.policy = policy or PermissionPolicy(); self._tools = {}
    def register(self, tool):
        if not getattr(tool, "name", None): raise ValueError("Tool must define a non-empty name.")
        self._tools[tool.name] = tool
    def get(self, name): return self._tools.get(name)
    def names(self): return sorted(self._tools)
    def describe(self):
        return [{"name": n, "description": str(getattr(self._tools[n], "description", "")), "capability": str(getattr(self._tools[n], "capability", ""))} for n in self.names()]
    def execute(self, name, arguments):
        tool = self.get(name)
        if tool is None: return {"success": False, "output": f"Unknown tool: {name}"}
        capability = getattr(tool, "capability", "")
        if capability and not self.policy.allows(capability): return {"success": False, "output": f"Permission denied: {capability}"}
        try: return tool.execute(arguments)
        except Exception as exc: return {"success": False, "output": f"{type(exc).__name__}: {exc}"}