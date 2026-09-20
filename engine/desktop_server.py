from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from engine.agent.agent_controller import AgentController, Goal
from engine.agent.tools import PermissionPolicy, ToolRegistry
from engine.computer.agent_tool import WindowsComputerTool
from engine.computer.windows import WindowsComputerAdapter
from engine.learning.store import LearningStore
from engine.security.desktop_policy import DesktopPolicy, PolicyStore


class DesktopServer:
    """JSONL host for the Jelon Windows desktop application.

    Computer control is disabled by default. The desktop UI must explicitly
    authorize trusted-workspace computer control before the Windows tool is
    exposed to the agent.
    """

    def __init__(self):
        self.policy_store = PolicyStore(os.getenv("JELON_POLICY_PATH", "data/jelon_policy.json"))
        self.policy = self.policy_store.load()
        self.store = LearningStore(os.getenv("JELON_MEMORY_PATH", "data/jelon_learning.json"))
        self.agent = None
        self.registry = ToolRegistry(self.policy.tool_policy())
        self._register_platform_tools()

    def _register_platform_tools(self) -> None:
        if sys.platform == "win32":
            self.registry.register(WindowsComputerTool(WindowsComputerAdapter()))

    def _rebuild_agent(self) -> None:
        self.registry.policy = self.policy.tool_policy()
        self.agent = None

    def _status(self, text: str):
        return {
            "type": "status",
            "text": text,
            "autonomy": self.policy.autonomy,
            "computer_control": bool(
                self.policy.allow_processes and self.policy.autonomy in {"trusted_workspace", "authorized_repo"}
            ),
            "tools": self.registry.names(),
        }

    def _ensure_agent(self):
        if self.agent is not None:
            return self.agent
        model_path = os.getenv("JELON_MODEL_PATH", "").strip()
        if not model_path:
            return None
        from engine.model.local_model import LocalModel
        model = LocalModel(model_path)
        self.agent = AgentController(model, self.registry, self.store)
        return self.agent

    def _set_policy(self, message: dict):
        if "computer_control" in message:
            enabled = bool(message.get("computer_control"))
            if enabled:
                self.policy = DesktopPolicy(
                    autonomy="trusted_workspace",
                    allow_processes=True,
                    allow_files=True,
                    allow_browser=self.policy.allow_browser,
                    allow_network=self.policy.allow_network,
                    allow_git_write=False,
                    allow_git_push=False,
                )
            else:
                self.policy = DesktopPolicy(
                    autonomy="ask",
                    allow_files=False,
                    allow_processes=False,
                    allow_browser=False,
                    allow_network=False,
                    allow_git_write=False,
                    allow_git_push=False,
                )
        else:
            requested = dict(
                autonomy=str(message.get("autonomy", self.policy.autonomy)),
                allow_files=bool(message.get("allow_files", self.policy.allow_files)),
                allow_processes=bool(message.get("allow_processes", self.policy.allow_processes)),
                allow_browser=bool(message.get("allow_browser", self.policy.allow_browser)),
                allow_network=bool(message.get("allow_network", self.policy.allow_network)),
                allow_git_write=bool(message.get("allow_git_write", self.policy.allow_git_write)),
                allow_git_push=bool(message.get("allow_git_push", self.policy.allow_git_push)),
            )
            self.policy = DesktopPolicy(**requested)

        self.policy_store.save(self.policy)
        self._rebuild_agent()
        return self._status(
            "Computer control enabled • trusted workspace"
            if self.policy.allow_processes
            else "Computer control disabled"
        )

    def handle(self, message: dict):
        kind = str(message.get("type", "")).strip().lower()

        if kind == "status":
            model = os.getenv("JELON_MODEL_PATH", "").strip()
            suffix = "local model configured" if model else "local model not configured"
            return self._status(f"Core online • {suffix}")

        if kind == "policy.set":
            try:
                return self._set_policy(message)
            except Exception as exc:
                return {"type": "error", "text": f"Policy update failed: {type(exc).__name__}: {exc}"}

        if kind == "goal":
            text = str(message.get("text", "")).strip()
            if not text:
                return {"type": "error", "text": "Goal is empty."}
            agent = self._ensure_agent()
            if agent is None:
                return {
                    "type": "result",
                    "status": "blocked",
                    "text": "Jelon core is running, but no local model is configured. Set JELON_MODEL_PATH to a compatible local model before executing AI goals.",
                }
            try:
                result = agent.run(Goal(text, self.store.task_context(text)))
                return {
                    "type": "result",
                    "text": result.summary,
                    "status": result.status,
                    "attempts": result.attempts,
                    "observations": [o.output for o in result.observations[-8:]],
                }
            except Exception as exc:
                return {"type": "error", "text": f"{type(exc).__name__}: {exc}"}

        if kind == "shutdown":
            return {"type": "status", "text": "Core shutting down", "_shutdown": True}

        return {"type": "error", "text": f"Unknown message type: {kind or '<empty>'}"}

    def run(self):
        print(json.dumps(self._status("Core online"), ensure_ascii=False), flush=True)
        for line in sys.stdin:
            try:
                message = json.loads(line)
                if not isinstance(message, dict):
                    raise ValueError("message must be a JSON object")
                response = self.handle(message)
                shutdown = bool(response.pop("_shutdown", False))
                print(json.dumps(response, ensure_ascii=False), flush=True)
                if shutdown:
                    break
            except Exception as exc:
                print(json.dumps({"type": "error", "text": f"{type(exc).__name__}: {exc}"}), flush=True)


if __name__ == "__main__":
    DesktopServer().run()
