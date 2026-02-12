import logging
import sys
from src.db.manager import DatabaseManager
from src.core.engine import TrackingEngine

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

        # Initialize and Start Engine
        # Back to 1 minute as requested
        engine = TrackingEngine(db_manager, interval=60)

        print("--- Time Reporter is active ---")
        print("Tracking application usage in 1-minute blocks.")
        print("Press Ctrl+C to stop.")

        engine.start()

    except KeyboardInterrupt:
        print("\nStopping Time Reporter...")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
