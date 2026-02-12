from datetime import datetime, timedelta
import threading
import time
import logging
import win32gui
from src.db.manager import DatabaseManager
from src.core.tracker import get_active_window_info, WindowEventObserver
from src.utils.idle import is_user_idle, get_idle_duration


class TrackingEngine:
    def __init__(self, db_manager: DatabaseManager, interval: int = 60):
        self.db = db_manager
        self.interval = interval
        self.is_running = False
        self.observer = WindowEventObserver(self._on_window_change)
        self._stop_event = threading.Event()

        # Smart Idle State
        self.idle_threshold = int(self.db.get_setting("idle_threshold", "300"))
        self.is_in_idle_mode = False
        self.idle_started_at = None
        self.on_idle_return_callback = None  # Will be set by UI
        self.reload_settings()

    def reload_settings(self):
        """Reloads configuration from the database."""
        self.idle_threshold = int(self.db.get_setting("idle_threshold", "300"))
        logging.info(
            f"Engine settings reloaded. Idle Threshold: {self.idle_threshold}s"
        )

    def start(self):
        self.is_running = True

        # 1. Start Event Observer in a dedicated thread
        # This thread will block on win32gui.PumpMessages()
        self.observer_thread = threading.Thread(target=self._run_observer, daemon=True)
        self.observer_thread.start()

        # 2. Initial capture
        info = get_active_window_info()
        if info:
            self._on_window_change(info[0], info[1])

        # 3. Start Heartbeat in a dedicated thread
        self.heartbeat_thread = threading.Thread(
            target=self._run_heartbeat, daemon=True
        )
        self.heartbeat_thread.start()

        logging.info("Pro-level Tracking Engine started (Multi-threaded).")

        # Keep the main thread alive until stop is called
        try:
            while not self._stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def _run_observer(self):
        """Runs the blocking Windows message pump."""
        if self.observer.start():
            logging.info("Windows Event Hook active.")
            win32gui.PumpMessages()

    def _run_heartbeat(self):
        """Standard 60s timer to increment durations."""
        while not self._stop_event.is_set():
            time.sleep(self.interval)
            try:
                self._heartbeat_tick()
            except Exception as e:
                logging.error(f"Heartbeat error: {e}")

    def _on_window_change(self, app_name, window_title):
        """Called immediately by the Windows Hook signal."""
        idle_sec = get_idle_duration()
        logging.debug(f"Window Change: {app_name} (Idle: {idle_sec:.1f}s)")

        # If we are in idle mode and suddenly return (hook catches it before heartbeat)
        if self.is_in_idle_mode and idle_sec < self.idle_threshold:
            self.is_in_idle_mode = False
            return_time = datetime.now()
            logging.info(f"User returned from idle (via Hook) at: {return_time}")
            if self.on_idle_return_callback:
                self.on_idle_return_callback(self.idle_started_at, return_time)
            self.idle_started_at = None

            # Start a new block for the window we returned to
            self.db.create_block(app_name, window_title)
            return

        # Normal case: check if we should ignore changes during idle
        if idle_sec > self.idle_threshold:
            return

        last_block = self.db.get_last_block()
        if not last_block or last_block["app_name"] != app_name:
            self.db.create_block(app_name, window_title)
            logging.info(f"Signal: New block -> {app_name}")

    def _heartbeat_tick(self):
        """Increments duration of the active block or detects return from idle."""
        idle_sec = get_idle_duration()
        logging.debug(
            f"Heartbeat tick (Idle: {idle_sec:.1f}s, Threshold: {self.idle_threshold}s)"
        )

        if idle_sec > self.idle_threshold:
            if not self.is_in_idle_mode:
                self.is_in_idle_mode = True
                self.idle_started_at = datetime.now() - timedelta(seconds=idle_sec)
                logging.info(f"Idle mode entered. Started at: {self.idle_started_at}")
            return

        # Return from idle detection (Heartbeat case)
        if self.is_in_idle_mode:
            self.is_in_idle_mode = False
            return_time = datetime.now()
            logging.info(f"User returned from idle (via Heartbeat) at: {return_time}")
            if self.on_idle_return_callback:
                self.on_idle_return_callback(self.idle_started_at, return_time)
            self.idle_started_at = None
            return

        # Normal tracking
        info = get_active_window_info()
        if not info:
            return

        app_name, window_title = info
        last_block = self.db.get_last_block()

        if last_block and last_block["app_name"] == app_name:
            # Duration is time from start to now
            start_time = (
                datetime.fromisoformat(last_block["start_time"])
                if isinstance(last_block["start_time"], str)
                else last_block["start_time"]
            )
            new_duration = max(
                1, int((datetime.now() - start_time).total_seconds() / 60)
            )
            self.db.update_last_block(last_block["id"], new_duration)
            logging.info(f"Heartbeat: {app_name} ({new_duration} min)")
        else:
            # This handles cases where focus didn't change but app name might have (rare)
            # or if we missed an event
            self._on_window_change(app_name, window_title)

    def handle_idle_decision(
        self, decision: str, idle_start: datetime, idle_end: datetime
    ):
        """Processes the user's choice regarding the idle period."""
        if decision == "break":
            last_block = self.db.get_last_block()
            if last_block:
                start_time = (
                    datetime.fromisoformat(last_block["start_time"])
                    if isinstance(last_block["start_time"], str)
                    else last_block["start_time"]
                )
                # Calculate duration until the moment idle started
                duration = max(1, int((idle_start - start_time).total_seconds() / 60))
                self.db.update_last_block(
                    last_block["id"], duration, end_time=idle_start
                )
                logging.info(
                    f"Idle Decision: Break. Block truncated to {duration} min."
                )

            # Start a new block for the current active window
            info = get_active_window_info()
            if info:
                self.db.create_block(info[0], info[1])
        else:
            # "work" - Include the idle time in the current block
            last_block = self.db.get_last_block()
            if last_block:
                start_time = (
                    datetime.fromisoformat(last_block["start_time"])
                    if isinstance(last_block["start_time"], str)
                    else last_block["start_time"]
                )
                duration = max(1, int((idle_end - start_time).total_seconds() / 60))
                self.db.update_last_block(last_block["id"], duration, end_time=idle_end)
                logging.info(f"Idle Decision: Work. Gap included ({duration} min).")

    def stop(self):
        self.is_running = False
        self._stop_event.set()
        self.observer.stop()
        # Note: win32gui.PostQuitMessage(0) could be used to stop PumpMessages
        logging.info("Tracking engine stopped.")
