from __future__ import annotations

import queue
import threading
from dataclasses import dataclass


@dataclass(frozen=True)
class MicrophoneConfig:
    sample_rate: int = 16000
    channels: int = 1
    block_size: int = 1280
    dtype: str = "int16"


class MicrophoneStream:
    """Continuous local microphone PCM stream using sounddevice."""

    def __init__(self, config: MicrophoneConfig | None = None):
        self.config = config or MicrophoneConfig()
        self._queue: queue.Queue = queue.Queue()
        self._stream = None

    def _callback(self, indata, frames, time_info, status):
        self._queue.put(indata.copy())

    def start(self):
        try:
            import sounddevice as sd
        except ImportError as exc:
            raise RuntimeError("sounddevice is required for microphone streaming.") from exc
        if self._stream is not None:
            return
        self._stream = sd.InputStream(
            samplerate=self.config.sample_rate,
            channels=self.config.channels,
            blocksize=self.config.block_size,
            dtype=self.config.dtype,
            callback=self._callback,
        )
        self._stream.start()

    def read(self, timeout: float | None = None):
        return self._queue.get(timeout=timeout)

    def stop(self):
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None


class ContinuousWakeListener:
    """Runs the microphone continuously and dispatches wake events."""

    def __init__(self, microphone, detector, on_wake):
        self.microphone = microphone
        self.detector = detector
        self.on_wake = on_wake
        self._stop = threading.Event()

    def run_forever(self):
        self._stop.clear()
        self.microphone.start()
        try:
            while not self._stop.is_set():
                try:
                    block = self.microphone.read(timeout=0.5)
                except queue.Empty:
                    continue
                if self.detector.detect(block):
                    self.on_wake()
        finally:
            self.microphone.stop()

    def stop(self):
        self._stop.set()
