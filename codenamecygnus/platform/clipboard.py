"""Text on the Windows clipboard, for debug mode's F3 prompt (game/debug.py).

Windows' own clipboard calls, through ctypes, as the port is Windows only
(aidocks/general/project_windows_only.md). pygame's clipboard support differs from one
version to the next, and needs its display set up first, so it is not used.

``get_text()`` gives the clipboard's text, or '' when it holds none or cannot be opened;
``set_text(text)`` puts text there, True when it did. Neither ever raises.
"""
from __future__ import annotations

import ctypes
import logging
import time
from ctypes import wintypes

log = logging.getLogger('clipboard')

CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002
#: Another program can hold the clipboard for a moment; try a few times.
TRIES = 5


def _api():
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    user32.OpenClipboard.argtypes = [wintypes.HWND]
    user32.OpenClipboard.restype = wintypes.BOOL
    user32.CloseClipboard.restype = wintypes.BOOL
    user32.EmptyClipboard.restype = wintypes.BOOL
    user32.GetClipboardData.argtypes = [wintypes.UINT]
    user32.GetClipboardData.restype = wintypes.HANDLE
    user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
    user32.SetClipboardData.restype = wintypes.HANDLE
    kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
    kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalFree.argtypes = [wintypes.HGLOBAL]
    return user32, kernel32


def _open(user32):
    for _ in range(TRIES):
        if user32.OpenClipboard(None):
            return True
        time.sleep(0.02)
    return False


def get_text():
    try:
        user32, kernel32 = _api()
        if not _open(user32):
            log.warning('the clipboard could not be opened')
            return ''
        try:
            handle = user32.GetClipboardData(CF_UNICODETEXT)
            if not handle:
                return ''
            pointer = kernel32.GlobalLock(handle)
            if not pointer:
                return ''
            try:
                return ctypes.wstring_at(pointer)
            finally:
                kernel32.GlobalUnlock(handle)
        finally:
            user32.CloseClipboard()
    except Exception:
        log.exception('could not read the clipboard')
        return ''


def set_text(text):
    try:
        user32, kernel32 = _api()
        data = ctypes.create_unicode_buffer(text)
        size = ctypes.sizeof(data)
        handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, size)
        if not handle:
            return False
        pointer = kernel32.GlobalLock(handle)
        if not pointer:
            kernel32.GlobalFree(handle)
            return False
        ctypes.memmove(pointer, data, size)
        kernel32.GlobalUnlock(handle)
        if not _open(user32):
            kernel32.GlobalFree(handle)
            log.warning('the clipboard could not be opened')
            return False
        try:
            user32.EmptyClipboard()
            if not user32.SetClipboardData(CF_UNICODETEXT, handle):
                kernel32.GlobalFree(handle)     # still ours, since Windows did not take it
                return False
            return True                         # Windows owns the memory now
        finally:
            user32.CloseClipboard()
    except Exception:
        log.exception('could not write the clipboard')
        return False


class Clipboard:
    """The clipboard as the screens use it; the tests give a stand-in instead."""

    def get_text(self):
        return get_text()

    def set_text(self, text):
        return set_text(text)
