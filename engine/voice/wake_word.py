from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable


@dataclass(frozen=True)
class WakeWordConfig:
    phrase: str = "jelon"
    sensitivity: float = 0.5

    def __post_init__(self):
        if not self.phrase.strip():
            raise ValueError("Wake phrase must not be empty.")
        if not 0.0 <= self.sensitivity <= 1.0:
            raise ValueError("Sensitivity must be between 0 and 1.")


class WakeWordDetector:
    """Local wake-word boundary.

    A real detector can be injected later (Porcupine, openWakeWord, or a
    custom local model). The detector never sends audio to a cloud service.
    """

    def __init__(self, config: WakeWordConfig | None = None):
        self.config = config or WakeWordConfig()

    def detect(self, audio) -> bool:
        raise NotImplementedError(
            "No local wake-word engine is installed. Inject a detector backend."
        )


class TranscriptWakeWordDetector:
    """Deterministic fallback for tests and microphone pipelines.

    This is not an acoustic detector: it checks text produced by local STT.
    """

    def __init__(self, config: WakeWordConfig | None = None):
        self.config = config or WakeWordConfig()

    def detect_transcript(self, transcript: str) -> bool:
        phrase = self.config.phrase.casefold().strip()
        words = transcript.casefold().split()
        return phrase in words


class WakeWordPipeline:
    """Routes audio to the agent only after the wake phrase is detected."""

    def __init__(
        self,
        detector: object,
        stt: object,
        command_handler: Callable[[str], object],
        config: WakeWordConfig | None = None,
    ):
        self.detector = detector
        self.stt = stt
        self.command_handler = command_handler
        self.config = config or WakeWordConfig()

    def process_audio(self, audio):
        if not self.detector.detect(audio):
            return None
        transcript = self.stt.transcribe(audio)
        command = self._remove_wake_phrase(transcript)
        if not command:
            return {"wake": True, "command": "", "status": "listening"}
        return self.command_handler(command)

    def _remove_wake_phrase(self, transcript: str) -> str:
        phrase = self.config.phrase.casefold()
        words = transcript.split()
        kept = []
        removed = False
        for word in words:
            clean = word.strip(".,!?;:'\"()[]{}")
            if not removed and clean.casefold() == phrase:
                removed = True
                continue
            kept.append(word)
        return " ".join(kept).strip()
