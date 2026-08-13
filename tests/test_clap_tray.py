import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from unittest.mock import MagicMock


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_FOLDER / "src"))

import clap_tray


class ClapTrayTests(unittest.TestCase):
    @patch("clap_tray.sys.frozen", True, create=True)
    def test_packaged_modes_relaunch_same_executable(self):
        self.assertEqual(
            [sys.executable, "--listener"], clap_tray.listener_command()
        )
        self.assertEqual(
            [sys.executable, "--orb", "--live"],
            clap_tray.orb_command(live=True),
        )

    def test_controller_prevents_duplicate_owned_listener(self):
        process = MagicMock()
        process.poll.return_value = None
        popen = MagicMock(return_value=process)
        controller = clap_tray.ClapController(popen=popen)
        with patch.object(clap_tray, "LOG_FOLDER", Path("data/private/test-logs")):
            with patch("pathlib.Path.open", MagicMock()):
                self.assertTrue(controller.start())
                self.assertFalse(controller.start())
        popen.assert_called_once()

    @patch("presence_state.stop_presence_window")
    def test_controller_stop_terminates_listener_and_orb(self, stop_orb):
        process = MagicMock()
        process.poll.return_value = None
        controller = clap_tray.ClapController()
        controller.process = process
        self.assertTrue(controller.stop())
        process.terminate.assert_called_once_with()
        stop_orb.assert_called_once_with()

    def test_icon_is_generated_in_memory(self):
        image = clap_tray.create_tray_image()
        self.assertEqual((64, 64), image.size)
        self.assertEqual("RGBA", image.mode)

    def test_preview_menu_labels_lifecycle_controls_as_disabled(self):
        menu = clap_tray.preview_menu()
        rendered = str(menu)
        self.assertIn("Status: Preview only", rendered)
        self.assertIn("Open Floating Orb", rendered)
        self.assertIn("Start listening", rendered)
        self.assertIn("Exit Preview", rendered)

    @patch("presence_state.stop_presence_window")
    def test_application_menu_offers_show_and_hide_orb(self, _stop):
        controller = MagicMock()
        controller.is_running.return_value = True
        icon = MagicMock()
        rendered = str(clap_tray.application_menu(controller, icon))
        self.assertIn("Show Orb", rendered)
        self.assertIn("Hide Orb", rendered)

    @patch("clap_tray.subprocess.Popen")
    def test_open_orb_launches_only_visual_preview(self, popen):
        clap_tray.open_orb()
        arguments = popen.call_args.args[0]
        self.assertIn("clap_floating_orb_preview.py", arguments[-2])
        self.assertEqual("--live", arguments[-1])
        self.assertNotIn("clap_detector.py", " ".join(arguments))


if __name__ == "__main__":
    unittest.main()
