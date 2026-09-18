from __future__ import annotations
from typing import Any

class VoicePipeline:
    """Injectable local STT -> agent -> TTS pipeline."""
    def __init__(self, stt: Any, agent: Any, tts: Any):
        self.stt, self.agent, self.tts = stt, agent, tts

    def process_audio(self, audio: Any) -> Any:
        text = self.stt.transcribe(audio)
        result = self.agent.run(text)
        return self.tts.speak(getattr(result, "summary", str(result)))
