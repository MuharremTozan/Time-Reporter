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
    db_manager = None
    exporter = None
    engine = None
    try:
        # 1. Initialize DB & Exporter
        db_manager = DatabaseManager()
        exporter = ExportManager(db_manager)

        # 2. Cleanup
        cleanup_days = int(db_manager.get_setting("db_cleanup_days", "30"))
        db_manager.cleanup_old_data(days=cleanup_days)

        # 3. Initialize UI First
        app = DashboardApp(db_manager)

        # 4. Initialize Engine (10s precision)
        engine = TrackingEngine(db_manager, interval=10, exporter=exporter)
        engine.on_idle_return_callback = app.show_idle_confirmation
        app.set_engine(engine)

        # 5. Start Engine in a background thread
        engine_thread = threading.Thread(target=engine.start, daemon=True)
        engine_thread.start()

        # 6. Tray logic
        def on_tray_exit(icon):
            logging.info("Exiting via tray...")
            if exporter:
                try:
                    exporter.export_today()
                except Exception as e:
                    logging.error(f"Auto-export failed: {e}")
            icon.stop()
            app.destroy()
            sys.exit(0)

        def on_tray_show(icon):
            app.after(0, app.show_window)

        def on_toggle_break():
            return engine.toggle_manual_break()

        tray = TrayIcon(
            on_show=on_tray_show, on_exit=on_tray_exit, on_toggle_break=on_toggle_break
        )
        tray_thread = threading.Thread(target=tray.run, daemon=True)
        tray_thread.start()

        print("--- Time Reporter is active ---")
        print("Core engine is running in background.")
        print("System tray icon is active.")

        # Start UI (Main Thread)
        app.mainloop()

    except KeyboardInterrupt:
        print("\nStopping Time Reporter...")
        if exporter:
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
