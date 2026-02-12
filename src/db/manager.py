import sqlite3
from datetime import datetime
import os


class DatabaseManager:
    def __init__(self, db_path: str = "time_reporter.db"):
        self.db_path = os.path.abspath(db_path)
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
