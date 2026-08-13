import json
import tempfile
import unittest
from pathlib import Path

from src.speech_voice_config import (
    DEFAULT_RATE,
    DEFAULT_VOICE,
    load_speech_voice_config,
)


class SpeechVoiceConfigTests(unittest.TestCase):
    def test_missing_config_uses_default(self):
        with tempfile.TemporaryDirectory() as directory:
            result = load_speech_voice_config(Path(directory) / "missing.json")
        self.assertEqual(DEFAULT_VOICE, result["voice"])
        self.assertEqual(DEFAULT_RATE, result["rate"])
        self.assertEqual("default", result["source"])

    def test_enabled_valid_voice_is_selected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "voice.json"
            path.write_text(json.dumps({
                "enabled": True,
                "voice": "en-US-AvaNeural",
                "rate": "+2%",
            }), encoding="utf-8")
            result = load_speech_voice_config(path)
        self.assertEqual("en-US-AvaNeural", result["voice"])
        self.assertEqual("+2%", result["rate"])
        self.assertEqual("local", result["source"])

    def test_invalid_voice_falls_back(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "voice.json"
            path.write_text(json.dumps({
                "enabled": True,
                "voice": "not-a-voice",
                "rate": "+2%",
            }), encoding="utf-8")
            result = load_speech_voice_config(path)
        self.assertEqual(DEFAULT_VOICE, result["voice"])
        self.assertIsNotNone(result["warning"])

    def test_out_of_range_rate_falls_back(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "voice.json"
            path.write_text(json.dumps({
                "enabled": True,
                "voice": "en-US-AvaNeural",
                "rate": "+80%",
            }), encoding="utf-8")
            result = load_speech_voice_config(path)
        self.assertEqual(DEFAULT_RATE, result["rate"])
        self.assertIsNotNone(result["warning"])


if __name__ == "__main__":
    unittest.main()
