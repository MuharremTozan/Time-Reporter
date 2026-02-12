import logging
import sys
import threading
from src.db.manager import DatabaseManager
from src.core.engine import TrackingEngine
from src.ui.dashboard import DashboardApp
from src.utils.tray import TrayIcon
from src.utils.exporter import ExportManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def main():
    # Initialize Database
    db_manager = DatabaseManager()
    # Initialize Exporter
    exporter = ExportManager(db_manager)

    try:
        # Initialize Engine
        engine = TrackingEngine(db_manager, interval=60)

        # Start Engine in a background thread
        engine_thread = threading.Thread(target=engine.start, daemon=True)
        engine_thread.start()

        # Initialize Exporter
        exporter = ExportManager(db_manager)

        # Initialize UI
        app = DashboardApp(db_manager)

        # Tray logic
        def on_tray_exit(icon):
            logging.info("Exiting via tray...")
            try:
                exporter.export_today()
            except Exception as e:
                logging.error(f"Auto-export failed: {e}")
            icon.stop()
            app.destroy()
            sys.exit(0)

        def on_tray_show(icon):
            app.after(0, app.show_window)

        tray = TrayIcon(on_show=on_tray_show, on_exit=on_tray_exit)
        tray_thread = threading.Thread(target=tray.run, daemon=True)
        tray_thread.start()

        print("--- Time Reporter is active ---")
        print("Core engine is running in background.")
        print("System tray icon is active.")

        # Start UI (Main Thread)
        app.mainloop()

    except KeyboardInterrupt:
        print("\nStopping Time Reporter...")
        try:
            exporter.export_today()
        except:
            pass
        sys.exit(0)
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
