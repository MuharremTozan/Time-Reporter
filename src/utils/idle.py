import win32api


def get_idle_duration() -> float:
    """
    Returns the idle time in seconds.
    """
    last_input_info = win32api.GetLastInputInfo()
    current_tick_count = win32api.GetTickCount()

    # Tick count is in milliseconds
    idle_ms = current_tick_count - last_input_info
    return idle_ms / 1000.0


def is_user_idle(threshold_seconds: int = 300) -> bool:
    """
    Checks if the user has been idle for more than threshold_seconds.
    Default is 5 minutes (300 seconds).
    """
    return get_idle_duration() > threshold_seconds
