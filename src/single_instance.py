"""Prevent more than one Project CLAP listener from running on Windows."""

import ctypes
import sys


ERROR_ALREADY_EXISTS = 183
MUTEX_NAME = "Local\\ProjectCLAPVoiceListener"
_mutex_handle = None


def acquire_clap_instance(kernel32=None):
    """Return False when another CLAP listener already owns the named mutex."""

    global _mutex_handle

    if sys.platform != "win32":
        return True
    if kernel32 is None:
        kernel32 = ctypes.windll.kernel32

    kernel32.CreateMutexW.restype = ctypes.c_void_p
    handle = kernel32.CreateMutexW(None, False, MUTEX_NAME)
    if not handle:
        raise ctypes.WinError()
    if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        kernel32.CloseHandle(handle)
        return False

    _mutex_handle = handle
    return True
