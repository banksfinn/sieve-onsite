from celery import Celery

from app.config import settings
from app.models import all_models  # type: ignore # noqa: F401
from app.tasks.todo_notifications import check_notification_timing, send_todo_notification

ALL_TASKS = [check_notification_timing, send_todo_notification]

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Celery Beat schedule configuration
celery_app.conf.beat_schedule = {  # type: ignore[reportUnknownMemberType]
    "check-notification-timing": {
        "task": "app.tasks.todo_notifications.check_notification_timing",
        "schedule": 60.0,  # Run every 60 seconds
    },
}
