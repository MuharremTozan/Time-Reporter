import win32gui
import win32process
import win32con
import ctypes
import ctypes.wintypes
import psutil
import pywintypes
import logging

# Windows constants for events
EVENT_SYSTEM_FOREGROUND = 0x0003
WINEVENT_OUTOFCONTEXT = 0x0000

# Function prototypes for WinAPI
user32 = ctypes.windll.user32
WinEventProcType = ctypes.WINFUNCTYPE(
    None,
    ctypes.wintypes.HANDLE,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.HWND,
    ctypes.wintypes.LONG,
    ctypes.wintypes.LONG,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.DWORD,
)


def get_window_info(hwnd):
    """Helper to get info from a specific HWND"""
    try:
        if not hwnd or not win32gui.IsWindow(hwnd):
            return None

        window_title = win32gui.GetWindowText(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        app_name = process.name()
        return app_name, window_title
    except Exception as e:
        logging.debug(f"Could not get window info for {hwnd}: {e}")
        return None


def get_active_window_info() -> tuple[str, str] | None:
    """Current active window info (polling fallback)"""
    hwnd = win32gui.GetForegroundWindow()
    return get_window_info(hwnd)


class WindowEventObserver:
    """
    Listens for window foreground changes using Windows Hooks.
    """

    def __init__(self, callback):
        self.callback = callback
        self.hook = None

    def _event_handler(
        self,
        hWinEventHook,
        event,
        hwnd,
        idObject,
        idChild,
        dwEventThread,
        dwmsEventTime,
    ):
        if event == EVENT_SYSTEM_FOREGROUND:
            info = get_window_info(hwnd)
            if info:
                self.callback(info[0], info[1])

    def start(self):
        self.proc = WinEventProcType(self._event_handler)
        self.hook = user32.SetWinEventHook(
            EVENT_SYSTEM_FOREGROUND,
            EVENT_SYSTEM_FOREGROUND,
            0,
            self.proc,
            0,
            0,
            WINEVENT_OUTOFCONTEXT,
        )
        if not self.hook:
            logging.error("Failed to set WinEventHook")
            return False
        return True

    def stop(self):
        if self.hook:
            user32.UnhookWinEvent(self.hook)
            self.hook = None
