from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from engine.agent.agent_controller import AgentController, Goal
from engine.agent.tools import PermissionPolicy, ToolRegistry
from engine.learning.store import LearningStore


class DesktopServer:
    """JSONL host process used by the Windows desktop shell.

    The transport is intentionally small: one JSON object per input/output line.
    This keeps the desktop UI independent from the Python implementation and
    makes the transport replaceable for the packaged build.
    """

    def __init__(self):
        self.registry = ToolRegistry(PermissionPolicy())
        self.store = LearningStore(os.getenv("JELON_MEMORY_PATH", "data/jelon_learning.json"))
        self.agent = None

    def _status(self, text: str):
        return {"type": "status", "text": text}

    def _ensure_agent(self):
        if self.agent is not None:
            return self.agent
        model_path = os.getenv("JELON_MODEL_PATH", "").strip()
        if not model_path:
            return None
        try:
            from engine.model.local_model import LocalModel
            model = LocalModel(model_path)
            self.agent = AgentController(model, self.registry, self.store)
            return self.agent
        except Exception:
            return None

    def handle(self, message: dict):
        kind = str(message.get("type", "")).strip().lower()
        if kind == "status":
            model = os.getenv("JELON_MODEL_PATH", "").strip()
            if model:
                return self._status("Core online • local model configured")
            return self._status("Core online • local model not configured")

        if kind == "goal":
            text = str(message.get("text", "")).strip()
            if not text:
                return {"type": "error", "text": "Goal is empty."}
            agent = self._ensure_agent()
            if agent is None:
                return {
                    "type": "result",
                    "text": "Jelon core is running, but no local model is configured yet. Set JELON_MODEL_PATH to a compatible local model file before executing AI goals.",
                }
            try:
                result = agent.run(Goal(text, self.store.task_context(text)))
                return {
                    "type": "result",
                    "text": result.summary,
                    "status": result.status,
                    "attempts": result.attempts,
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
