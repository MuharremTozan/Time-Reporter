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
            # Activity blocks table
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

            # App categories mapping table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS app_categories (
                    app_name TEXT PRIMARY KEY,
                    category TEXT NOT NULL
                )
            """)

            # Add some default mappings if they don't exist
            default_mappings = [
                ("code.exe", "Development"),
                ("pycharm64.exe", "Development"),
                ("chrome.exe", "Browsing"),
                ("msedge.exe", "Browsing"),
                ("vlc.exe", "Entertainment"),
                ("spotify.exe", "Entertainment"),
                ("discord.exe", "Social"),
                ("slack.exe", "Social"),
                ("cmd.exe", "System"),
                ("powershell.exe", "System"),
                ("explorer.exe", "System"),
            ]
            conn.executemany(
                "INSERT OR IGNORE INTO app_categories (app_name, category) VALUES (?, ?)",
                default_mappings,
            )
            conn.commit()

    def set_app_category(self, app_name: str, category: str):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO app_categories (app_name, category) VALUES (?, ?)",
                (app_name, category),
            )
            conn.commit()

    def get_app_category(self, app_name: str) -> str:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT category FROM app_categories WHERE app_name = ?", (app_name,)
            )
            row = cursor.fetchone()
            return row[0] if row else "Uncategorized"

    def get_all_app_categories(self) -> dict:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT app_name, category FROM app_categories")
            return {row[0]: row[1] for row in cursor.fetchall()}

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

    def get_app_usage_stats(
        self, start_date: str | None = None, end_date: str | None = None
    ) -> list[dict]:
        """
        Returns total duration per app for a given date range (YYYY-MM-DD).
        If dates are missing, defaults to today.
        """
        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")
        if not end_date:
            end_date = start_date

        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT ab.app_name, SUM(ab.duration_minutes) as total_duration, 
                       COALESCE(ac.category, 'Uncategorized') as category
                FROM activity_blocks ab
                LEFT JOIN app_categories ac ON ab.app_name = ac.app_name
                WHERE date(ab.start_time) BETWEEN date(?) AND date(?)
                GROUP BY ab.app_name
                ORDER BY total_duration DESC
                """,
                (start_date, end_date),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_category_usage_stats(
        self, start_date: str | None = None, end_date: str | None = None
    ) -> list[dict]:
        """
        Returns total duration per category for a given date range.
        """
        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")
        if not end_date:
            end_date = start_date

        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT COALESCE(ac.category, 'Uncategorized') as category, 
                       SUM(ab.duration_minutes) as total_duration
                FROM activity_blocks ab
                LEFT JOIN app_categories ac ON ab.app_name = ac.app_name
                WHERE date(ab.start_time) BETWEEN date(?) AND date(?)
                GROUP BY category
                ORDER BY total_duration DESC
                """,
                (start_date, end_date),
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
