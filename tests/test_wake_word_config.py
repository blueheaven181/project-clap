import json
import tempfile
import unittest
from pathlib import Path

from src.wake_word_config import load_wake_word_selection


class WakeWordConfigTests(unittest.TestCase):
    def make_project(self, directory):
        project = Path(directory)
        production = project / "models" / "wake_words" / "hey_Clap.onnx"
        production.parent.mkdir(parents=True)
        production.write_bytes(b"production")
        return project, production

    def test_missing_config_uses_production(self):
        with tempfile.TemporaryDirectory() as directory:
            project, production = self.make_project(directory)
            result = load_wake_word_selection(project)
            self.assertEqual(result["model_path"], production)
            self.assertEqual(result["source"], "production")
            self.assertEqual(result["threshold"], 0.30)

    def test_enabled_candidate_is_selected(self):
        with tempfile.TemporaryDirectory() as directory:
            project, _ = self.make_project(directory)
            candidate = project / "candidate.onnx"
            candidate.write_bytes(b"candidate")
            config = project / "wake_word.local.json"
            config.write_text(json.dumps({
                "enabled": True,
                "model_path": str(candidate),
                "threshold": 0.30,
            }), encoding="utf-8")
            result = load_wake_word_selection(project, config)
            self.assertEqual(result["model_path"], candidate.resolve())
            self.assertEqual(result["source"], "local_candidate")

    def test_missing_candidate_falls_back_to_production(self):
        with tempfile.TemporaryDirectory() as directory:
            project, production = self.make_project(directory)
            config = project / "wake_word.local.json"
            config.write_text(json.dumps({
                "enabled": True,
                "model_path": "missing.onnx",
                "threshold": 0.30,
            }), encoding="utf-8")
            result = load_wake_word_selection(project, config)
            self.assertEqual(result["model_path"], production)
            self.assertIsNotNone(result["warning"])

    def test_lower_threshold_falls_back_to_production(self):
        with tempfile.TemporaryDirectory() as directory:
            project, production = self.make_project(directory)
            candidate = project / "candidate.onnx"
            candidate.write_bytes(b"candidate")
            config = project / "wake_word.local.json"
            config.write_text(json.dumps({
                "enabled": True,
                "model_path": str(candidate),
                "threshold": 0.10,
            }), encoding="utf-8")
            result = load_wake_word_selection(project, config)
            self.assertEqual(result["model_path"], production)
            self.assertEqual(result["threshold"], 0.30)


if __name__ == "__main__":
    unittest.main()
