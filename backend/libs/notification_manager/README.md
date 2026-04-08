# Notification Manager

Async Slack notification client library for sending messages and looking up users.

## Configuration

Set the following environment variable:

- `SLACK_BOT_TOKEN`: Your Slack bot token (xoxb-...)

## Required Slack Bot Permissions

Your Slack app needs these OAuth scopes:
- `chat:write` - Send messages
- `users:read` - Look up users by ID
- `users:read.email` - Look up users by email
