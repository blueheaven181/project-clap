import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

import single_instance


class FakeCreateMutex:
    restype = None

    def __init__(self, handle):
        self.handle = handle

    def __call__(self, _attributes, _owner, _name):
        return self.handle


class FakeKernel32:
    def __init__(self, last_error, handle=42):
        self.CreateMutexW = FakeCreateMutex(handle)
        self.last_error = last_error
        self.closed = []

    def GetLastError(self):
        return self.last_error

    def CloseHandle(self, handle):
        self.closed.append(handle)


class SingleInstanceTests(unittest.TestCase):
    @patch("single_instance.sys.platform", "win32")
    def test_first_listener_acquires_mutex(self):
        kernel32 = FakeKernel32(last_error=0)

        self.assertTrue(single_instance.acquire_clap_instance(kernel32))
        self.assertEqual(single_instance._mutex_handle, 42)
        self.assertEqual(kernel32.closed, [])

    @patch("single_instance.sys.platform", "win32")
    def test_second_listener_is_rejected_and_handle_is_closed(self):
        kernel32 = FakeKernel32(last_error=single_instance.ERROR_ALREADY_EXISTS)

        self.assertFalse(single_instance.acquire_clap_instance(kernel32))
        self.assertEqual(kernel32.closed, [42])


if __name__ == "__main__":
    unittest.main()
