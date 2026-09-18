from __future__ import annotations

from pathlib import Path

from .microphone import MicrophoneConfig, MicrophoneStream, ContinuousWakeListener
from .openwakeword import OpenWakeWordDetector
from .wake_word import WakeWordConfig
from .continuous import JelonVoiceRuntime
from .local_stt import WhisperCommandCapture, FasterWhisperSTT


def build_voice_runtime(
    agent,
    wake_model_path: str | Path,
    stt_model: str = "base",
    sensitivity: float = 0.5,
    tts=None,
):
    """Build Jelon's local continuous wake -> STT -> agent -> TTS runtime."""
    microphone = MicrophoneStream(MicrophoneConfig())
    detector = OpenWakeWordDetector(
        wake_model_path,
        config=WakeWordConfig(sensitivity=sensitivity),
    )
    stt = FasterWhisperSTT(stt_model)
    command_capture = WhisperCommandCapture.create(microphone, stt)
    listener = ContinuousWakeListener(microphone, detector, lambda: None)
    return JelonVoiceRuntime(listener, command_capture, agent, tts=tts)
