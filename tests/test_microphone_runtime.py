import unittest

from engine.voice.microphone import ContinuousWakeListener, MicrophoneConfig


class FakeMicrophone:
    def __init__(self, blocks):
        self.blocks = iter(blocks)
        self.started = False
        self.stopped = False

    def start(self):
        self.started = True

    def read(self, timeout=None):
        block = next(self.blocks)
        return block

    def stop(self):
        self.stopped = True


class FakeDetector:
    def detect(self, block):
        return block == "wake"


class MicrophoneRuntimeTests(unittest.TestCase):
    def test_config_matches_openwakeword_audio(self):
        self.assertEqual(MicrophoneConfig().sample_rate, 16000)
        self.assertEqual(MicrophoneConfig().channels, 1)
        self.assertEqual(MicrophoneConfig().dtype, "int16")

    def test_listener_dispatches_wake(self):
        microphone = FakeMicrophone(["noise", "wake"])
        events = []
        listener = ContinuousWakeListener(microphone, FakeDetector(), lambda: events.append("wake"))
        with self.assertRaises(StopIteration):
            listener.run_forever()
        self.assertEqual(events, ["wake"])
        self.assertTrue(microphone.started)
        self.assertTrue(microphone.stopped)


if __name__ == "__main__":
    unittest.main()
