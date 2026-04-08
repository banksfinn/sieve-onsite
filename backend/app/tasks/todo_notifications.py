import json
import logging
from datetime import datetime, timedelta, timezone

from locking_manager.celery.task import locked_task
from notification_manager.clients.slack_client import slack_client

from app.blueprints.notification_log import NotificationLogCreateRequest
from app.blueprints.todo import Todo, TodoQuery
from app.stores.notification_log import notification_log_store
from app.stores.tag import tag_store
from app.stores.tag_member import tag_member_store
from app.stores.todo import todo_store
from user_management.blueprints.user import DEFAULT_NOTIFICATION_TIMING
from user_management.stores.user import user_store

logger = logging.getLogger(__name__)

# Notification timing options
TIMING_OPTIONS = [
    "at_due_time",
    "15_minutes_before",
    "30_minutes_before",
    "60_minutes_before",
    "morning_of",
    "night_before",
]


def get_notification_timing(todo: Todo, user_notification_timing: list[str] | None) -> list[str]:
    """
    Get the effective notification timing for a todo.

    If the todo has an override, use that. Otherwise, use the user's default.
    If the user has no default, use the system default (30 minutes before).
    """
    if todo.notification_timing_override:
        return todo.notification_timing_override

    if user_notification_timing:
        return user_notification_timing

    # Parse default timing
    return json.loads(DEFAULT_NOTIFICATION_TIMING)


def should_send_notification(due_at: datetime, timing_type: str) -> bool:
    """
    Check if a notification should be sent now for the given timing type.

    Returns True if the current time falls within the 1-minute window
    for the specified timing type.
    """
    now = datetime.now(timezone.utc)

    if timing_type == "at_due_time":
        target = due_at
    elif timing_type == "15_minutes_before":
        target = due_at - timedelta(minutes=15)
    elif timing_type == "30_minutes_before":
        target = due_at - timedelta(minutes=30)
    elif timing_type == "60_minutes_before":
        target = due_at - timedelta(minutes=60)
    elif timing_type == "morning_of":
        # 9 AM on the due date (UTC)
        target = due_at.replace(hour=9, minute=0, second=0, microsecond=0)
    elif timing_type == "night_before":
        # 8 PM the day before (UTC)
        day_before = due_at - timedelta(days=1)
        target = day_before.replace(hour=20, minute=0, second=0, microsecond=0)
    else:
        return False

    # Check if we're within the 1-minute window
    return target <= now < target + timedelta(minutes=1)


def format_notification_message(todo: Todo, timing_type: str) -> str:
    """Format the notification message based on timing type."""
    timing_labels = {
        "at_due_time": "now due",
        "15_minutes_before": "due in 15 minutes",
        "30_minutes_before": "due in 30 minutes",
        "60_minutes_before": "due in 1 hour",
        "morning_of": "due today",
        "night_before": "due tomorrow",
    }
    timing_label = timing_labels.get(timing_type, "upcoming")
    return f"📋 *TODO Reminder*: {todo.title} ({timing_label})"


@locked_task(use_lock=False)
async def check_notification_timing():
    """
    Celery Beat task that runs every minute to find todos
    that need notifications sent based on their timing preferences.
    """
    # Find todos with slack_notification=True and not completed
    query = TodoQuery(
        completed=False,
        limit=1000,  # Process in batches
    )

    todos_response = await todo_store.search_entities(query)
    todos = todos_response.entities

    queued_count = 0

    for todo in todos:
        if not todo.slack_notification or not todo.due_at:
            continue

        # Get user's notification preferences
        user = await user_store.get_entity_by_id(todo.user_id)
        if not user:
            continue

        # Get effective timing options
        timing_options = get_notification_timing(todo, user.notification_timing)

        for timing_type in timing_options:
            if not should_send_notification(todo.due_at, timing_type):
                continue

            # Check if already sent
            already_sent = await notification_log_store.has_been_sent(todo.id, timing_type)
            if already_sent:
                continue

            # Queue the notification
            send_todo_notification.delay(todo.id, timing_type)  # type: ignore[attr-defined]
            queued_count += 1

    logger.info(f"Checked notification timing: queued {queued_count} notifications")


@locked_task()
async def send_todo_notification(todo_id: int, timing_type: str):
    """
    Send a notification for a specific todo and timing type.

    Determines whether to send to a channel (if tag has one) or DM all tag members.
    """
    todo = await todo_store.get_entity_by_id(todo_id)

    if todo is None:
        logger.warning(f"Todo {todo_id} not found for notification")
        return

    if todo.completed:
        logger.info(f"Todo {todo_id} already completed, skipping notification")
        return

    # Double-check we haven't already sent this
    already_sent = await notification_log_store.has_been_sent(todo_id, timing_type)
    if already_sent:
        logger.info(f"Notification already sent for todo {todo_id}, timing {timing_type}")
        return

    message = format_notification_message(todo, timing_type)
    now = datetime.now(timezone.utc)

    # Check if any tag has a Slack channel
    sent_to_channel = False
    for todo_tag in todo.tags:
        # Get full tag with slack_channel info
        tag = await tag_store.get_entity_by_id(todo_tag.id)
        if tag and tag.slack_channel_id:
            try:
                await slack_client.send_message(tag.slack_channel_id, message)
                await notification_log_store.create_entity(
                    NotificationLogCreateRequest(
                        todo_id=todo_id,
                        timing_type=timing_type,
                        sent_at=now,
                        recipient_type="channel",
                        recipient_id=tag.slack_channel_id,
                    )
                )
                logger.info(f"Sent notification to channel {tag.slack_channel_id} for todo {todo_id}")
                sent_to_channel = True
            except Exception as e:
                logger.error(f"Failed to send to channel {tag.slack_channel_id}: {e}")

    if sent_to_channel:
        return

    # No channel configured - send DMs to all tag members + todo owner
    recipient_user_ids: set[int] = set()

    # Add todo owner
    recipient_user_ids.add(todo.user_id)

    # Add all tag members
    for todo_tag in todo.tags:
        members = await tag_member_store.get_members_for_tag(todo_tag.id)
        for member in members:
            recipient_user_ids.add(member.user_id)

    # Send DMs to each unique user
    for user_id in recipient_user_ids:
        user = await user_store.get_entity_by_id(user_id)
        if not user:
            continue

        try:
            await slack_client.send_dm(user.email_address, message)
            await notification_log_store.create_entity(
                NotificationLogCreateRequest(
                    todo_id=todo_id,
                    timing_type=timing_type,
                    sent_at=now,
                    recipient_type="dm",
                    recipient_id=str(user_id),
                )
            )
            logger.info(f"Sent DM notification to user {user_id} for todo {todo_id}")
        except Exception as e:
            logger.error(f"Failed to send DM to user {user_id}: {e}")
