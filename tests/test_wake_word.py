import unittest
from engine.voice.wake_word import WakeWordConfig, TranscriptWakeWordDetector, WakeWordPipeline

class WakeWordTests(unittest.TestCase):
    def test_default_phrase_is_jelon(self):
        self.assertEqual(WakeWordConfig().phrase, "jelon")

    def test_transcript_detector_is_case_insensitive(self):
        detector = TranscriptWakeWordDetector()
        self.assertTrue(detector.detect_transcript("Hey JELON"))

    def test_pipeline_strips_wake_word(self):
        detector = TranscriptWakeWordDetector()
        calls = []
        pipeline = WakeWordPipeline(detector, None, lambda command: calls.append(command) or "ok")
        pipeline.detector.detect = lambda audio: detector.detect_transcript(audio)
        result = pipeline.process_audio("Jelon open my project")
        self.assertEqual(result, "ok")
        self.assertEqual(calls, ["open my project"])

if __name__ == "__main__":
    unittest.main()
