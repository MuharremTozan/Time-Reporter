import threading
import time
import logging
import win32gui
from src.db.manager import DatabaseManager
from src.core.tracker import get_active_window_info, WindowEventObserver
from src.utils.idle import is_user_idle


class TrackingEngine:
    def __init__(self, db_manager: DatabaseManager, interval: int = 60):
        self.db = db_manager
        self.interval = interval
        self.is_running = False
        self.observer = WindowEventObserver(self._on_window_change)
        self._stop_event = threading.Event()

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
        if is_user_idle(300):
            return

        last_block = self.db.get_last_block()

        if not last_block or last_block["app_name"] != app_name:
            self.db.create_block(app_name, window_title)
            logging.info(f"Signal: New block -> {app_name}")

    def _heartbeat_tick(self):
        """Increments duration of the active block."""
        if is_user_idle(300):
            return

        info = get_active_window_info()
        if not info:
            return

        app_name, window_title = info
        last_block = self.db.get_last_block()

        if last_block and last_block["app_name"] == app_name:
            new_duration = last_block["duration_minutes"] + 1
            self.db.update_last_block(last_block["id"], new_duration)
            logging.info(f"Heartbeat: {app_name} ({new_duration} min)")
        else:
            self._on_window_change(app_name, window_title)

    def stop(self):
        self.is_running = False
        self._stop_event.set()
        self.observer.stop()
        # Note: win32gui.PostQuitMessage(0) could be used to stop PumpMessages
        logging.info("Tracking engine stopped.")
