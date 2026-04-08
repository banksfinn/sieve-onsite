# Notification Manager

Async Slack notification client library for sending messages and looking up users.

## Installation

This library is installed as a local dependency via uv:

```bash
cd backend
uv sync
```

## Configuration

Set the following environment variable:

- `SLACK_BOT_TOKEN`: Your Slack bot token (xoxb-...)

## Usage

### Sending a message

```python
from notification_manager.clients.slack_client import slack_client

# Send to a channel
message = await slack_client.send_message(
    channel="C0123456789",  # or "#channel-name"
    text="Hello, world!"
)
print(f"Message sent with ts: {message.ts}")
```

### Sending a threaded reply

```python
# Reply to an existing message
reply = await slack_client.send_reply(
    channel="C0123456789",
    thread_ts=message.ts,  # The parent message's timestamp
    text="This is a reply!"
)
```

### Looking up a user

```python
# By user ID
user = await slack_client.get_user_by_id("U0123456789")
print(f"User: {user.real_name} ({user.email})")

# By email
user = await slack_client.get_user_by_email("user@example.com")
```

## Required Slack Bot Permissions

Your Slack app needs these OAuth scopes:
- `chat:write` - Send messages
- `users:read` - Look up users by ID
- `users:read.email` - Look up users by email
