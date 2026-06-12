from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery(
    "gtm_tracker",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=["app.tasks.sync_tasks"]  # ← yeh add kiya
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    timezone="Asia/Kolkata",
)