import pytest
from src.scheduler.tasks import run_ingestion_pipeline_task, update_user_recommendations_task


def test_run_ingestion_pipeline_task_dry_run():
    res = run_ingestion_pipeline_task(dry_run=True)
    assert res["status"] == "SUCCESS"
    assert res["total_collected"] > 0
    assert res["unique_records"] > 0
    assert res["upserted_count"] == res["unique_records"]


def test_update_user_recommendations_task_dry_run():
    sample_profile = {
        "preferredTags": ["AI / Machine Learning", "LLM"],
        "preferredTechStack": ["Python", "Next.js"],
        "preferredMode": "ONLINE",
    }
    res = update_user_recommendations_task("test_user_001", sample_profile, dry_run=True)
    assert res["status"] == "SUCCESS"
    assert res["user_id"] == "test_user_001"
    assert res["ranked_count"] == 10
    assert res["top_hackathon_id"] is not None
