from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol


class InferenceBackend(Protocol):
    """Minimal interface for any local model runtime."""

    def load(self, model_path: Path) -> None: ...
    def generate(self, prompt: str, **kwargs: Any) -> str: ...
    def unload(self) -> None: ...


class LocalModel:
    """Provider-independent local inference facade.

    No cloud API is required. A concrete backend (for example llama.cpp,
    ONNX Runtime, or another local engine) is injected by the host.
    """

    def __init__(
        self,
        model_path: str | None = None,
        backend: InferenceBackend | None = None,
    ):
        self.model_path = Path(model_path) if model_path else None
        self.backend = backend
        self.loaded = False

    def load(self) -> None:
        if self.model_path is None:
            raise ValueError("A local model_path is required before inference.")
        if not self.model_path.exists():
            raise FileNotFoundError(self.model_path)
        if self.backend is None:
            raise RuntimeError(
                "No local inference backend configured. "
                "Inject a backend such as llama.cpp or ONNX Runtime."
            )
        self.backend.load(self.model_path)
        self.loaded = True

    def generate(self, prompt: str, **kwargs: Any) -> str:
        if not prompt.strip():
            raise ValueError("Prompt must not be empty.")
        if not self.loaded:
            self.load()
        result = self.backend.generate(prompt, **kwargs)
        if not isinstance(result, str):
            raise TypeError("Inference backend must return text.")
        return result

    def unload(self) -> None:
        if self.backend is not None and self.loaded:
            self.backend.unload()
        self.loaded = False


class EchoBackend:
    """Tiny deterministic backend for tests and development.

    It is not an AI model and must never be presented as one.
    """

    def load(self, model_path: Path) -> None:
        self.model_path = model_path

    def generate(self, prompt: str, **kwargs: Any) -> str:
        return prompt

    def unload(self) -> None:
        pass
