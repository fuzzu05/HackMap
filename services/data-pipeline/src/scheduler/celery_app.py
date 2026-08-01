import os
from celery import Celery
from celery.schedules import crontab

# Broker and Backend URLs (Redis by default, configurable via environment variables)
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

app = Celery("hackmap_scheduler", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    # Celery Beat schedule for automated data ingestion every 12 hours
    beat_schedule={
        "scheduled-hackathon-ingestion-12h": {
            "task": "src.scheduler.tasks.run_ingestion_pipeline_task",
            "schedule": crontab(minute=0, hour="*/12"),
            "args": (),
        },
    },
)

# Auto-discover tasks in src.scheduler
app.autodiscover_tasks(["src.scheduler"])
