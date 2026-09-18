"""Local model interfaces for Jelon."""

from .local_model import EchoBackend, InferenceBackend, LocalModel
from .llama_cpp_backend import LlamaCppBackend

__all__ = ["EchoBackend", "InferenceBackend", "LocalModel", "LlamaCppBackend"]
