import sqlite3
from datetime import datetime, timedelta
import os
import logging


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
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")  # Daha iyi performans ve eşzamanlılık
        return conn

    def _init_db(self):
        conn = self._get_connection()
        try:
            with conn:
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

                # Categories table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS categories (
                        name TEXT PRIMARY KEY
                    )
                """)

                # Add default categories
                default_categories = [
                    ("Development",),
                    ("Browsing",),
                    ("Entertainment",),
                    ("Social",),
                    ("System",),
                    ("Work",),
                    ("Education",),
                    ("Uncategorized",),
                ]
                conn.executemany(
                    "INSERT OR IGNORE INTO categories (name) VALUES (?)",
                    default_categories,
                )

                # App categories mapping table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS app_categories (
                        app_name TEXT PRIMARY KEY,
                        category TEXT NOT NULL
                    )
                """)

                # Add some default mappings
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

                # Settings table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                """)

                # Add default settings
                default_settings = [
                    ("idle_threshold", "300"),
                    ("db_cleanup_days", "30"),
                    ("export_on_exit", "True"),
                    ("merge_short_browsing", "False"),
                ]
                conn.executemany(
                    "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                    default_settings,
                )
        finally:
            conn.close()

    def get_setting(self, key: str, default: str = "") -> str:
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else default
        finally:
            conn.close()

    def set_setting(self, key: str, value: str):
        conn = self._get_connection()
        try:
            with conn:
                conn.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                    (key, str(value)),
                )
        finally:
            conn.close()

    def cleanup_old_data(self, days: int = 30):
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.execute(
                    "DELETE FROM activity_blocks WHERE date(start_time) < ?",
                    (cutoff_date,),
                )
                count = cursor.rowcount
                if count > 0:
                    logging.info(f"Cleaned up {count} records older than {cutoff_date}")
                return count
        finally:
            conn.close()

    def get_categories(self) -> list[str]:
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT name FROM categories ORDER BY name ASC")
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()

    def add_category(self, name: str):
        conn = self._get_connection()
        try:
            with conn:
                conn.execute(
                    "INSERT OR IGNORE INTO categories (name) VALUES (?)", (name,)
                )
                logging.info(f"Category added to DB: {name}")
        finally:
            conn.close()

    def delete_category(self, name: str):
        if name == "Uncategorized":
            return False
        conn = self._get_connection()
        try:
            with conn:
                conn.execute(
                    "UPDATE app_categories SET category = 'Uncategorized' WHERE category = ?",
                    (name,),
                )
                conn.execute("DELETE FROM categories WHERE name = ?", (name,))
                logging.info(f"Category deleted from DB: {name}")
            return True
        finally:
            conn.close()

    def set_app_category(self, app_name: str, category: str):
        conn = self._get_connection()
        try:
            with conn:
                conn.execute(
                    "INSERT OR REPLACE INTO app_categories (app_name, category) VALUES (?, ?)",
                    (app_name, category),
                )
                logging.info(f"Mapping saved: {app_name} -> {category}")
        finally:
            conn.close()

    def get_app_category(self, app_name: str) -> str:
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT category FROM app_categories WHERE app_name = ?", (app_name,)
            )
            row = cursor.fetchone()
            return row[0] if row else "Uncategorized"
        finally:
            conn.close()

    def get_all_app_categories(self) -> dict:
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT app_name, category FROM app_categories")
            return {row[0]: row[1] for row in cursor.fetchall()}
        finally:
            conn.close()

    def get_last_block(self) -> dict | None:
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.execute(
                "SELECT * FROM activity_blocks ORDER BY id DESC LIMIT 1"
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def create_block(self, app_name: str, window_title: str):
        now = datetime.now()
        conn = self._get_connection()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO activity_blocks (app_name, window_title, start_time, end_time, duration_minutes)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (app_name, window_title, now, now, 1),
                )
        finally:
            conn.close()

    def get_recent_blocks(self, limit: int = 20) -> list[dict]:
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.execute(
                "SELECT * FROM activity_blocks ORDER BY id DESC LIMIT ?", (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_app_usage_stats(
        self, start_date: str | None = None, end_date: str | None = None
    ) -> list[dict]:
        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")
        if not end_date:
            end_date = start_date

        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        try:
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
        finally:
            conn.close()

    def get_category_usage_stats(
        self, start_date: str | None = None, end_date: str | None = None
    ) -> list[dict]:
        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")
        if not end_date:
            end_date = start_date

        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        try:
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
        finally:
            conn.close()

    def get_daily_usage_stats(self, days: int = 7) -> list[dict]:
        start_date = (datetime.now() - timedelta(days=days - 1)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")

        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.execute(
                """
                SELECT date(start_time) as date, SUM(duration_minutes) as total_duration
                FROM activity_blocks
                WHERE date(start_time) BETWEEN date(?) AND date(?)
                GROUP BY date(start_time)
                ORDER BY date(start_time) ASC
                """,
                (start_date, end_date),
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def merge_last_two_blocks(self):
        """Merges the very last block into the one before it."""
        blocks = self.get_recent_blocks(limit=2)
        if len(blocks) < 2:
            return

        last = blocks[0]
        prev = blocks[1]

        # Calculate new duration and end_time
        new_end = last["end_time"]
        p_start = (
            datetime.fromisoformat(prev["start_time"])
            if isinstance(prev["start_time"], str)
            else prev["start_time"]
        )
        l_end = (
            datetime.fromisoformat(last["end_time"])
            if isinstance(last["end_time"], str)
            else last["end_time"]
        )
        new_duration = max(1, int((l_end - p_start).total_seconds() / 60))

        conn = self._get_connection()
        try:
            with conn:
                # Update previous block
                conn.execute(
                    "UPDATE activity_blocks SET end_time = ?, duration_minutes = ? WHERE id = ?",
                    (new_end, new_duration, prev["id"]),
                )
                # Delete last block
                conn.execute("DELETE FROM activity_blocks WHERE id = ?", (last["id"],))
                logging.info(f"Merged block {last['id']} into {prev['id']}")
        finally:
            conn.close()

    def delete_block(self, block_id: int):
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM activity_blocks WHERE id = ?", (block_id,))
                logging.info(f"Block deleted: {block_id}")
        finally:
            conn.close()

    def update_last_block(
        self, block_id: int, duration_minutes: int, end_time: datetime | None = None
    ):
        if end_time is None:
            end_time = datetime.now()

        conn = self._get_connection()
        try:
            with conn:
                conn.execute(
                    """
                    UPDATE activity_blocks 
                    SET end_time = ?, duration_minutes = ?
                    WHERE id = ?
                    """,
                    (end_time, duration_minutes, block_id),
                )
        finally:
            conn.close()
