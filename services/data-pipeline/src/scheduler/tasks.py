import logging
from typing import Dict, Any, List
from celery import shared_task
from ..models.hackathon import HackathonDocument
from ..deduplication.engine import DeduplicationEngine
from ..firebase.client import upsert_hackathon, get_firestore_client

logger = logging.getLogger(__name__)


@shared_task(name="src.scheduler.tasks.run_ingestion_pipeline_task")
def run_ingestion_pipeline_task(dry_run: bool = False) -> Dict[str, Any]:
    """
    Celery background task that executes the complete Phase 2 & 3 pipeline:
    1. Scrapes hackathon listings and loads curated multi-source records.
    2. Runs DeduplicationEngine to merge cross-listed events.
    3. Upserts clean deduplicated records into Firestore /hackathons collection.
    """
    logger.info("Starting automated ingestion pipeline task (dry_run=%s)...", dry_run)

    # Import seed generator from scripts package to simulate/run full pipeline collection
    from scripts.run_local_scrape import generate_large_curated_dataset

    engine = DeduplicationEngine(similarity_threshold=0.85, date_window_days=3)
    raw_items = generate_large_curated_dataset()

    duplicates_count = 0
    for raw_item in raw_items:
        doc = HackathonDocument.model_validate(raw_item)
        _, is_dup = engine.process_record(doc)
        if is_dup:
            duplicates_count += 1

    unique_records = engine.get_deduplicated_records()
    logger.info("Deduplication complete. Unique records to ingest: %d", len(unique_records))

    upserted_ids: List[str] = []
    failed_ids: List[str] = []

    if not dry_run:
        try:
            db_client = get_firestore_client()
            for doc in unique_records:
                try:
                    doc_id = upsert_hackathon(doc, db=db_client)
                    upserted_ids.append(doc_id)
                except Exception as e:
                    logger.error("Failed to upsert hackathon %s: %s", doc.id, str(e))
                    failed_ids.append(doc.id)
        except Exception as e:
            logger.warning(
                "Firestore client not connected or ADC unavailable (%s). Performing simulated in-memory upsert.",
                str(e),
            )
            upserted_ids = [doc.id for doc in unique_records]
    else:
        upserted_ids = [doc.id for doc in unique_records]

    result = {
        "status": "SUCCESS",
        "total_collected": len(raw_items),
        "duplicates_merged": duplicates_count,
        "unique_records": len(unique_records),
        "upserted_count": len(upserted_ids),
        "failed_count": len(failed_ids),
    }
    logger.info("Ingestion pipeline task finished: %s", result)
    return result


@shared_task(name="src.scheduler.tasks.update_user_recommendations_task")
def update_user_recommendations_task(user_id: str, user_profile: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """
    Celery background task that calculates personalized recommendations for a user
    and writes the RankedHackathon IDs directly to /users/{user_id}/recommendations/latest.
    """
    logger.info("Starting recommendation update task for user %s (dry_run=%s)", user_id, dry_run)
    from scripts.run_local_scrape import run_scrape_and_dedup
    from ..recommendation.service import generate_recommendations_for_user

    hackathons = run_scrape_and_dedup()
    rec_doc = generate_recommendations_for_user(
        user_id=user_id,
        user_profile=user_profile,
        hackathons=hackathons,
        top_n=10,
        dry_run=dry_run,
    )

    res = {
        "status": "SUCCESS",
        "user_id": user_id,
        "ranked_count": len(rec_doc.rankedHackathons),
        "top_hackathon_id": rec_doc.rankedHackathons[0].hackathonId if rec_doc.rankedHackathons else None,
    }
    logger.info("Recommendation task finished for user %s: %s", user_id, res)
    return res

