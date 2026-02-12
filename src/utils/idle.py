import ctypes


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("dwTime", ctypes.c_uint),
    ]


def get_idle_duration() -> float:
    """
    Returns the idle time in seconds using native user32.GetLastInputInfo.
    """
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)

    # Get last input time
    if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
        # Get system up time in milliseconds
        current_tick = ctypes.windll.kernel32.GetTickCount()

        # Calculate difference (handle potential wrap-around, though TickCount wraps at ~49 days)
        # Note: In C-style unsigned math (current - last) handles wrap automatically.
        # Python ints don't wrap, so we simulate it with 32-bit mask if needed.
        idle_ms = (current_tick & 0xFFFFFFFF) - (lii.dwTime & 0xFFFFFFFF)

        # If result is negative due to wrap-around handling
        if idle_ms < 0:
            idle_ms += 0x100000000

        return max(0, idle_ms / 1000.0)

    return 0.0


def is_user_idle(threshold_seconds: int = 300) -> bool:
    """
    Checks if the user has been idle for more than threshold_seconds.
    Default is 5 minutes (300 seconds).
    """
    return get_idle_duration() > threshold_seconds
