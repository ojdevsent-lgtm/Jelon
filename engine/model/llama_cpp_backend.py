from __future__ import annotations

from pathlib import Path
from typing import Any

class LlamaCppBackend:
    """Optional local GGUF inference backend using llama-cpp-python."""

    def __init__(self, **model_kwargs: Any):
        self.model_kwargs = model_kwargs
        self._llm: Any = None

    def load(self, model_path: Path) -> None:
        try:
            from llama_cpp import Llama
        except ImportError as exc:
            raise RuntimeError(
                "llama-cpp-python is not installed. Install it to use GGUF inference."
            ) from exc
        self._llm = Llama(model_path=str(model_path), **self.model_kwargs)

    def generate(self, prompt: str, **kwargs: Any) -> str:
        if self._llm is None:
            raise RuntimeError("Llama.cpp backend is not loaded.")
        params = {"max_tokens": 512, "temperature": 0.2}
        params.update(kwargs)
        result = self._llm(prompt, **params)
        choices = result.get("choices", [])
        if not choices:
            return ""
        return str(choices[0].get("text", "")).strip()

    def unload(self) -> None:
        self._llm = None
