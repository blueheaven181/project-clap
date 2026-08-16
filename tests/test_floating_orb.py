import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC))

import clap_floating_orb_preview as floating


class FakeCreateMutex:
    restype = None

    def __init__(self, handle=42):
        self.handle = handle

    def __call__(self, *_args):
        return self.handle


class FakeKernel32:
    def __init__(self, last_error):
        self.CreateMutexW = FakeCreateMutex()
        self.last_error = last_error
        self.closed = []

    def GetLastError(self):
        return self.last_error

    def CloseHandle(self, handle):
        self.closed.append(handle)


class FloatingOrbTests(unittest.TestCase):
    def test_standby_is_smaller_and_active_states_show_status(self):
        self.assertEqual((0.72, False), floating.target_presentation("standby"))
        for state in ("listening", "thinking", "speaking"):
            self.assertEqual((1.0, True), floating.target_presentation(state))

    def test_standby_status_reveals_for_hover_or_recent_change(self):
        self.assertTrue(floating.should_show_status("standby", 3.0, True))
        self.assertTrue(floating.should_show_status("standby", 1.0, False))
        self.assertFalse(floating.should_show_status("standby", 3.0, False))
        self.assertTrue(floating.should_show_status("listening", 30.0, False))

    @patch("clap_floating_orb_preview.sys.platform", "win32")
    def test_first_orb_is_allowed(self):
        kernel = FakeKernel32(0)
        self.assertTrue(floating.acquire_orb_instance(kernel))
        self.assertEqual([], kernel.closed)

    @patch("clap_floating_orb_preview.sys.platform", "win32")
    def test_duplicate_orb_is_rejected(self):
        kernel = FakeKernel32(183)
        self.assertFalse(floating.acquire_orb_instance(kernel))
        self.assertEqual([42], kernel.closed)


if __name__ == "__main__":
    unittest.main()
