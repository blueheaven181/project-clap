import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from src import presence_state


class PresenceStateTests(unittest.TestCase):
    @patch("src.presence_state.socket.socket")
    def test_valid_state_is_stored_and_sent_locally(self, socket_class):
        channel = MagicMock()
        socket_class.return_value.__enter__.return_value = channel

        presence_state.set_presence_state("listening")

        self.assertEqual("listening", presence_state.get_presence_state())
        channel.sendto.assert_called_once_with(
            b"listening",
            (presence_state.HOST, presence_state.PORT),
        )

    def test_invalid_state_is_rejected(self):
        with self.assertRaises(ValueError):
            presence_state.set_presence_state("executing_command")

    @patch("src.presence_state.subprocess.Popen")
    def test_visualizer_launch_is_separate_and_live(self, popen):
        with patch.object(
            presence_state, "CONFIG_PATH", Path("missing-presence-config.json")
        ):
            presence_state.start_presence_window()
            arguments = popen.call_args.args[0]
            self.assertEqual("--live", arguments[-1])
            self.assertIn("clap_presence_preview.py", arguments[-2])

    @patch("src.presence_state.subprocess.Popen")
    def test_floating_visualizer_is_selected_by_local_config(self, popen):
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "presence.json"
            config_path.write_text(
                json.dumps({"mode": "floating"}), encoding="utf-8"
            )
            with patch.object(presence_state, "CONFIG_PATH", config_path):
                presence_state.start_presence_window()
        arguments = popen.call_args.args[0]
        self.assertIn("clap_floating_orb_preview.py", arguments[-2])
        self.assertEqual("--live", arguments[-1])


if __name__ == "__main__":
    unittest.main()
