import sqlite3
from datetime import datetime
import os


class DatabaseManager:
    def __init__(self, db_name: str = "time_reporter.db"):
        # Profesyonel yaklaşım: Verileri AppData altında sakla
        app_data = os.getenv("APPDATA") or os.path.expanduser("~")
        self.db_dir = os.path.join(app_data, "TimeReporter")

        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)

        self.db_path = os.path.join(self.db_dir, db_name)
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS activity_blocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_name TEXT NOT NULL,
                    window_title TEXT,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME NOT NULL,
                    duration_minutes INTEGER DEFAULT 1
                )
            """)
            conn.commit()

    def get_last_block(self) -> dict | None:
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM activity_blocks ORDER BY id DESC LIMIT 1"
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def create_block(self, app_name: str, window_title: str):
        now = datetime.now()
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO activity_blocks (app_name, window_title, start_time, end_time, duration_minutes)
                VALUES (?, ?, ?, ?, ?)
                """,
                (app_name, window_title, now, now, 1),
            )
            conn.commit()

    def get_recent_blocks(self, limit: int = 20) -> list[dict]:
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM activity_blocks ORDER BY id DESC LIMIT ?", (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_app_usage_stats(self, date_str: str | None = None) -> list[dict]:
        """
        Returns total duration per app for a given date (YYYY-MM-DD).
        If date_str is None, uses current date.
        """
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")

        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            # We filter by start_time starting with date_str
            cursor = conn.execute(
                """
                SELECT app_name, SUM(duration_minutes) as total_duration
                FROM activity_blocks
                WHERE start_time LIKE ?
                GROUP BY app_name
                ORDER BY total_duration DESC
                """,
                (f"{date_str}%",),
            )
            return [dict(row) for row in cursor.fetchall()]

    def update_last_block(self, block_id: int, duration_minutes: int):
        now = datetime.now()
        with self._get_connection() as conn:
            conn.execute(
                """
                UPDATE activity_blocks 
                SET end_time = ?, duration_minutes = ?
                WHERE id = ?
                """,
                (now, duration_minutes, block_id),
            )
            conn.commit()
