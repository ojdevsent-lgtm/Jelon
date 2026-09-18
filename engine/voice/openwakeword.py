from __future__ import annotations

from pathlib import Path

from .wake_word import WakeWordConfig, WakeWordDetector


class OpenWakeWordDetector(WakeWordDetector):
    """Local openWakeWord detector for a custom Jelon acoustic model."""

    def __init__(self, model_path: str | Path, config: WakeWordConfig | None = None):
        super().__init__(config)
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Jelon wake-word model not found: {self.model_path}")
        try:
            from openwakeword.model import Model
        except ImportError as exc:
            raise RuntimeError("openwakeword is required for acoustic wake detection.") from exc
        self._model = Model(wakeword_models=[str(self.model_path)], inference_framework="tflite")

    def detect(self, audio) -> bool:
        import numpy as np
        samples = np.asarray(audio).reshape(-1)
        if samples.dtype != np.int16:
            samples = samples.astype(np.int16)
        prediction = self._model.predict(samples)
        scores = prediction.values() if isinstance(prediction, dict) else [prediction]
        return any(float(score) >= self.config.sensitivity for score in scores)

    def reset(self):
        reset = getattr(self._model, "reset", None)
        if callable(reset):
            reset()
