import logging
import os
import sys

# Ensure src package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.scheduler.tasks import run_ingestion_pipeline_task

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_firestore_ingestion")


def main():
    """
    Executes the ingestion pipeline task synchronously.
    Can be invoked manually or by CI/CD GitHub Actions cron jobs.
    """
    logger.info("Executing synchronous Firestore ingestion script...")
    # Execute with dry_run=True by default in local/unauthenticated CLI unless FIREBASE_CONFIG is present
    use_dry_run = not bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("FIREBASE_CONFIG"))
    result = run_ingestion_pipeline_task(dry_run=use_dry_run)
    logger.info("Ingestion completed: %s", result)
    return result


if __name__ == "__main__":
    main()
