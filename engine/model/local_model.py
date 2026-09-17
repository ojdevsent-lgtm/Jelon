from __future__ import annotations
from pathlib import Path

class LocalModel:
    """Adapter for a local inference runtime. No cloud API is required."""
    def __init__(self, model_path: str | None = None):
        self.model_path = Path(model_path) if model_path else None
        self.loaded = False

    def load(self) -> None:
        if self.model_path and not self.model_path.exists():
            raise FileNotFoundError(self.model_path)
        # Runtime integration is deliberately isolated here so the agent does not depend on a vendor API.
        self.loaded = True

    def generate(self, prompt: str) -> str:
        if not self.loaded:
            self.load()
        return "LOCAL_MODEL_RESPONSE_REQUIRED: connect a supported local inference backend."
