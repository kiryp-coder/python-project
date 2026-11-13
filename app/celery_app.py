from celery import Celery

from app.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND, CELERY_TASK_ALWAYS_EAGER

celery_app = Celery(
    "shop",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.tasks"],
)

celery_app.conf.update(
    task_always_eager=CELERY_TASK_ALWAYS_EAGER,
    task_store_eager_result=True,
    task_track_started=True,
    result_expires=3600,
)
