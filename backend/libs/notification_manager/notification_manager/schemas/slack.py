from pydantic import BaseModel


# =============================================================================
# Slack API Response Models
# These models represent the raw responses from Slack's API and are used
# for immediate validation after API calls.
# =============================================================================


class SlackUserProfile(BaseModel):
    """User profile nested within user data."""

    email: str | None = None
    image_72: str | None = None


class SlackUserData(BaseModel):
    """Raw user data from Slack API responses."""

    id: str
    name: str
    real_name: str | None = None
    is_bot: bool = False
    is_admin: bool = False
    team_id: str | None = None
    profile: SlackUserProfile = SlackUserProfile()


class SlackUserResponse(BaseModel):
    """Response from users.info or users.lookupByEmail."""

    user: SlackUserData


class SlackPostMessageResponse(BaseModel):
    """Response from chat.postMessage."""

    channel: str
    ts: str


class SlackChannelData(BaseModel):
    """Raw channel data from Slack API conversations.list."""

    id: str
    name: str
    is_private: bool = False
    num_members: int | None = None


class SlackResponseMetadata(BaseModel):
    """Pagination metadata from Slack API responses."""

    next_cursor: str | None = None


class SlackConversationsListResponse(BaseModel):
    """Response from conversations.list."""

    channels: list[SlackChannelData]
    response_metadata: SlackResponseMetadata = SlackResponseMetadata()


class SlackConversationChannel(BaseModel):
    """Channel object within conversations.open response."""

    id: str


class SlackConversationsOpenResponse(BaseModel):
    """Response from conversations.open."""

    channel: SlackConversationChannel


# =============================================================================
# Domain Models
# These models are the clean representations used throughout the application.
# =============================================================================


class SlackMessage(BaseModel):
    """Result from posting a Slack message."""

    channel: str
    ts: str  # Timestamp ID of the message (used for threading)
    text: str


class SlackUser(BaseModel):
    """User information retrieved from Slack."""

    id: str
    name: str
    real_name: str | None = None
    email: str | None = None
    is_bot: bool = False
    is_admin: bool = False
    team_id: str | None = None
    profile_image_url: str | None = None


class SendMessageRequest(BaseModel):
    """Request to send a Slack message."""

    channel: str  # Channel ID or name
    text: str
    thread_ts: str | None = None  # If provided, sends as a threaded reply


class LookupUserRequest(BaseModel):
    """Request to look up a Slack user."""

    user_id: str | None = None
    email: str | None = None  # Either user_id or email must be provided


class SlackChannel(BaseModel):
    """Channel information from Slack."""

    id: str
    name: str
    is_private: bool = False
    num_members: int | None = None
