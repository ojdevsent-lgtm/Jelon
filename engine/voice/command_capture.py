from __future__ import annotations


class LocalSTTCommandCapture:
    """Adapter for a local STT implementation."""

    def __init__(self, recorder, transcribe_recording):
        self.recorder = recorder
        self.transcribe_recording = transcribe_recording

    def __call__(self) -> str:
        audio = self.recorder()
        return self.transcribe_recording(audio)
