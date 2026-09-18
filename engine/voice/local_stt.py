from __future__ import annotations

import time

from .microphone import MicrophoneStream
from .command_capture import LocalSTTCommandCapture


class SilenceCommandRecorder:
    """Record a spoken command from a shared microphone stream."""

    def __init__(self, microphone: MicrophoneStream, silence_seconds: float = 1.0, max_seconds: float = 15.0, threshold: int = 700):
        self.microphone = microphone
        self.silence_seconds = silence_seconds
        self.max_seconds = max_seconds
        self.threshold = threshold

    def __call__(self):
        import numpy as np

        blocks = []
        started = False
        last_voice = time.monotonic()
        started_at = time.monotonic()
        was_running = getattr(self.microphone, "running", False)
        self.microphone.start()
        if hasattr(self.microphone, "clear_pending"):
            self.microphone.clear_pending()
        try:
            while time.monotonic() - started_at < self.max_seconds:
                block = self.microphone.read(timeout=1.0)
                samples = np.asarray(block).reshape(-1).astype(np.int16)
                rms = float(np.sqrt(np.mean(samples.astype(np.float32) ** 2)))
                if rms >= self.threshold:
                    started = True
                    last_voice = time.monotonic()
                if started:
                    blocks.append(samples.copy())
                    if time.monotonic() - last_voice >= self.silence_seconds:
                        break
        finally:
            if not was_running:
                self.microphone.stop()
        return np.concatenate(blocks) if blocks else np.zeros(0, dtype=np.int16)


class FasterWhisperSTT:
    """Local Whisper-compatible STT adapter."""

    def __init__(self, model_size: str = "base", device: str = "cpu", compute_type: str = "int8"):
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise RuntimeError("faster-whisper is required for local STT.") from exc
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe(self, audio):
        import numpy as np
        samples = np.asarray(audio).reshape(-1).astype(np.float32) / 32768.0
        segments, _ = self.model.transcribe(samples, beam_size=1)
        return " ".join(segment.text.strip() for segment in segments).strip()


class WhisperCommandCapture(LocalSTTCommandCapture):
    """Convenience local command capture using silence detection + STT."""

    @classmethod
    def create(cls, microphone: MicrophoneStream, stt: FasterWhisperSTT):
        recorder = SilenceCommandRecorder(microphone)
        return cls(recorder, stt.transcribe)
