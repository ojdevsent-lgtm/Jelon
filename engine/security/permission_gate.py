from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from .desktop_policy import DesktopPolicy

@dataclass(frozen=True)
class AuthorizationResult:
    allowed: bool
    reason: str

class PermissionGate:
    """Central authorization boundary for potentially destructive operations."""
    def __init__(self, policy: DesktopPolicy | None = None):
        self.policy = policy or DesktopPolicy()

    def check(self, capability: str, arguments: dict[str, Any] | None = None) -> AuthorizationResult:
        args = arguments or {}
        if not self.policy.tool_policy().allows(capability):
            return AuthorizationResult(False, f"Permission denied: {capability}")
        if capability in {"allow_files", "allow_processes"}:
            target = args.get("path") or args.get("cwd")
            if target and not self._inside_workspace(target):
                return AuthorizationResult(False, "Path is outside the trusted workspace.")
        return AuthorizationResult(True, "Allowed")

    def _inside_workspace(self, target: str | Path) -> bool:
        try:
            workspace = Path(".").resolve()
            candidate = Path(target).expanduser().resolve()
            candidate.relative_to(workspace)
            return True
        except (OSError, ValueError):
            return False
