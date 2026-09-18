from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Protocol

class Tool(Protocol):
    name: str
    description: str
    def execute(self, arguments: dict[str, Any]) -> Any: ...

@dataclass
class PermissionPolicy:
    allow_files: bool = False
    allow_processes: bool = False
    allow_browser: bool = False
    allow_network: bool = False
    allow_git_push: bool = False

class ToolRegistry:
    def __init__(self, policy: PermissionPolicy | None = None):
        self.policy = policy or PermissionPolicy()
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return sorted(self._tools)
