import logging
import sys
import threading
from src.db.manager import DatabaseManager
from src.core.engine import TrackingEngine
from src.ui.dashboard import DashboardApp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def main():
    try:
        # Initialize Database
        db_manager = DatabaseManager()

        # Initialize Engine
        engine = TrackingEngine(db_manager, interval=60)

        # Start Engine in a background thread
        engine_thread = threading.Thread(target=engine.start, daemon=True)
        engine_thread.start()

        print("--- Time Reporter is active ---")
        print("Core engine is running in background.")

        # Initialize and Start UI (Main Thread)
        app = DashboardApp(db_manager)
        app.mainloop()

    except KeyboardInterrupt:
        print("\nStopping Time Reporter...")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
