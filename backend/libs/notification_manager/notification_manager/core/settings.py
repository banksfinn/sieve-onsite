import os

from pydantic_settings import BaseSettings


class SlackSettings(BaseSettings):
    """Configuration for Slack integration."""

    SLACK_BOT_TOKEN: str = os.environ.get("SLACK_BOT_TOKEN", "")


slack_settings = SlackSettings()
