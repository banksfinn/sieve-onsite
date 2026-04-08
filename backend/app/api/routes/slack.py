from fastapi import APIRouter
from pydantic import BaseModel

from notification_manager.clients.slack_client import slack_client
from notification_manager.schemas.slack import SlackChannel
from user_management.api.dependencies import UserDependency

router = APIRouter()


class ChannelSearchResponse(BaseModel):
    """Response containing list of Slack channels."""

    channels: list[SlackChannel]


@router.get("/channels/search")
async def search_slack_channels(user: UserDependency, q: str) -> ChannelSearchResponse:
    """
    Search for Slack channels by name.

    Args:
        q: Search query to match against channel names

    Returns:
        List of matching Slack channels
    """
    channels = await slack_client.search_channels(q)
    return ChannelSearchResponse(channels=channels)
