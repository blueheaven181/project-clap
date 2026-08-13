import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from microphone_config import select_named_microphone, select_sounddevice_input


class MicrophoneSelectionTests(unittest.TestCase):
    def test_sounddevice_prefers_named_usable_input(self):
        devices = [
            {"name": "Remote Audio", "max_input_channels": 0},
            {"name": "USB microphone", "max_input_channels": 1},
            {"name": "Microphone (fifine Microphone)", "max_input_channels": 1},
        ]
        self.assertEqual(select_sounddevice_input(devices), 2)

    def test_sounddevice_falls_back_to_first_usable_input(self):
        devices = [
            {"name": "Output", "max_input_channels": 0},
            {"name": "Available microphone", "max_input_channels": 1},
        ]
        self.assertEqual(select_sounddevice_input(devices), 1)

    def test_speech_recognition_prefers_named_microphone(self):
        names = ["Remote Audio", "Microphone (fifine Microphone)"]
        self.assertEqual(select_named_microphone(names), 1)

    def test_speech_recognition_can_use_library_default_as_fallback(self):
        self.assertIsNone(select_named_microphone(["Remote Audio"]))


if __name__ == "__main__":
    unittest.main()
