from __future__ import annotations


class LocalTTS:
    """Local text-to-speech adapter using the operating system speech engine."""

    def __init__(self, rate: int = 175, volume: float = 1.0, voice: str | None = None):
        try:
            import pyttsx3
        except ImportError as exc:
            raise RuntimeError("pyttsx3 is required for local TTS.") from exc
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", int(rate))
        self.engine.setProperty("volume", max(0.0, min(1.0, float(volume))))
        if voice:
            self.set_voice(voice)

    def voices(self):
        return list(self.engine.getProperty("voices") or [])

    def set_voice(self, voice: str):
        for item in self.voices():
            if str(getattr(item, "id", "")) == voice or str(getattr(item, "name", "")) == voice:
                self.engine.setProperty("voice", item.id)
                return
        raise ValueError(f"Voice not found: {voice}")

    def speak(self, text: str) -> str:
        message = str(text).strip()
        if not message:
            return ""
        self.engine.say(message)
        self.engine.runAndWait()
        return message

    def stop(self):
        self.engine.stop()
