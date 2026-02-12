import os
import logging
from datetime import datetime, timedelta


class ExportManager:
    def __init__(self, db_manager):
        self.db = db_manager
        app_data = os.getenv("APPDATA") or os.path.expanduser("~")
        self.export_dir = os.path.join(app_data, "TimeReporter", "Exports")

        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)

    def export_today(self):
        """Exports today's activity to a text file."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        return self.export_date(today_str)

    def export_date(self, date_str):
        """Exports activity for a specific date (YYYY-MM-DD)."""
        blocks = self.db.get_app_usage_stats(
            date_str, date_str
        )  # This gets totals, we need raw blocks

        # We need raw blocks to reconstruct the timeline
        raw_blocks = self._get_raw_blocks_for_date(date_str)

        if not raw_blocks:
            logging.info(f"No data to export for {date_str}")
            return None

        file_path = os.path.join(self.export_dir, f"activity_{date_str}.txt")

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"--- Activity Report: {date_str} ---\n\n")

                last_end_time = None

                for block in raw_blocks:
                    start_time = datetime.fromisoformat(block["start_time"])
                    end_time = datetime.fromisoformat(block["end_time"])
                    app_name = block["app_name"]
                    category = self.db.get_app_category(app_name)

                    # Check for gaps (Breaks)
                    if last_end_time:
                        gap = (start_time - last_end_time).total_seconds()
                        if gap > 120:  # Gap > 2 minutes is a break
                            break_time = last_end_time.strftime("%H:%M")
                            f.write(f"{break_time} - break\n")

                    time_str = start_time.strftime("%H:%M")
                    # Use category if available, otherwise app name
                    label = category if category != "Uncategorized" else app_name
                    f.write(f"{time_str} - {label.lower()}\n")

                    last_end_time = end_time

                f.write(
                    f"\nReport generated at: {datetime.now().strftime('%H:%M:%S')}\n"
                )

            logging.info(f"Exported data to {file_path}")
            return file_path
        except Exception as e:
            logging.error(f"Failed to export data: {e}")
            return None

    def _get_raw_blocks_for_date(self, date_str):
        """Helper to get chronological blocks for a day."""
        with self.db._get_connection() as conn:
            import sqlite3

            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM activity_blocks WHERE date(start_time) = ? ORDER BY start_time ASC",
                (date_str,),
            )
            return [dict(row) for row in cursor.fetchall()]
