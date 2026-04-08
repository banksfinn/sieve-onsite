from logging_manager.logger import get_logger
from notification_manager.core.settings import slack_settings
from notification_manager.schemas.slack import (
    SlackChannel,
    SlackConversationsListResponse,
    SlackConversationsOpenResponse,
    SlackMessage,
    SlackPostMessageResponse,
    SlackUser,
    SlackUserData,
    SlackUserResponse,
)
from slack_sdk.web.async_client import AsyncWebClient


def _user_data_to_slack_user(user_data: SlackUserData) -> SlackUser:
    """Convert validated SlackUserData to SlackUser domain model."""
    return SlackUser(
        id=user_data.id,
        name=user_data.name,
        real_name=user_data.real_name,
        email=user_data.profile.email,
        is_bot=user_data.is_bot,
        is_admin=user_data.is_admin,
        team_id=user_data.team_id,
        profile_image_url=user_data.profile.image_72,
    )


class SlackNotificationClient:
    """
    Async client for Slack operations.

    Provides methods for sending messages, replying to threads,
    and looking up user information.
    """

    def __init__(self, bot_token: str | None = None):
        self._token = bot_token or slack_settings.SLACK_BOT_TOKEN
        self._client: AsyncWebClient | None = None
        self._logger = get_logger()

    @property
    def client(self) -> AsyncWebClient:
        """Lazily initialize and return the Slack client."""
        if self._client is None:
            self._client = AsyncWebClient(token=self._token)
        return self._client

    async def send_message(
        self,
        channel: str,
        text: str,
        thread_ts: str | None = None,
    ) -> SlackMessage:
        """
        Send a message to a Slack channel.

        Args:
            channel: Channel ID (e.g., "C0123456789") or name (e.g., "#general")
            text: Message text content
            thread_ts: If provided, sends as a threaded reply to this message
        """
        self._logger.info(
            "Sending Slack message",
            channel=channel,
            thread_ts=thread_ts,
        )

        raw_response = await self.client.chat_postMessage(  # pyright: ignore[reportUnknownMemberType]
            channel=channel,
            text=text,
            thread_ts=thread_ts,
        )
        response = SlackPostMessageResponse.model_validate(raw_response.data)  # pyright: ignore[reportUnknownMemberType]

        result = SlackMessage(
            channel=response.channel,
            ts=response.ts,
            text=text,
        )

        self._logger.info(
            "Slack message sent",
            channel=result.channel,
            ts=result.ts,
        )

        return result

    async def send_reply(
        self,
        channel: str,
        thread_ts: str,
        text: str,
    ) -> SlackMessage:
        """Send a threaded reply to an existing message."""
        return await self.send_message(
            channel=channel,
            text=text,
            thread_ts=thread_ts,
        )

    async def get_user_by_id(self, user_id: str) -> SlackUser:
        """Look up a Slack user by their user ID."""
        self._logger.info("Looking up Slack user by ID", user_id=user_id)

        raw_response = await self.client.users_info(user=user_id)  # pyright: ignore[reportUnknownMemberType]
        response = SlackUserResponse.model_validate(raw_response.data)  # pyright: ignore[reportUnknownMemberType]
        result = _user_data_to_slack_user(response.user)

        self._logger.info(
            "Slack user found",
            user_id=result.id,
            name=result.name,
        )

        return result

    async def get_user_by_email(self, email: str) -> SlackUser:
        """Look up a Slack user by their email address."""
        self._logger.info("Looking up Slack user by email", email=email)

        raw_response = await self.client.users_lookupByEmail(email=email)  # pyright: ignore[reportUnknownMemberType]
        response = SlackUserResponse.model_validate(raw_response.data)  # pyright: ignore[reportUnknownMemberType]
        result = _user_data_to_slack_user(response.user)

        self._logger.info(
            "Slack user found by email",
            user_id=result.id,
            name=result.name,
        )

        return result

    async def search_channels(self, query: str, limit: int = 20) -> list[SlackChannel]:
        """
        Search for Slack channels by name.

        Fetches all non-archived channels and filters client-side
        since Slack API doesn't provide a native search endpoint.
        """
        self._logger.info("Searching Slack channels", query=query)

        channels: list[SlackChannel] = []
        cursor: str | None = None

        while True:
            raw_response = await self.client.conversations_list(  # pyright: ignore[reportUnknownMemberType]
                types="public_channel,private_channel",
                limit=200,
                exclude_archived=True,
                cursor=cursor,
            )
            response = SlackConversationsListResponse.model_validate(raw_response.data)  # pyright: ignore[reportUnknownMemberType]

            for channel_data in response.channels:
                if query.lower() in channel_data.name.lower():
                    channels.append(
                        SlackChannel(
                            id=channel_data.id,
                            name=channel_data.name,
                            is_private=channel_data.is_private,
                            num_members=channel_data.num_members,
                        )
                    )

                    if len(channels) >= limit:
                        break

            if len(channels) >= limit:
                break

            cursor = response.response_metadata.next_cursor
            if not cursor:
                break

        self._logger.info("Found Slack channels", count=len(channels))
        return channels[:limit]

    async def open_dm_channel(self, user_id: str) -> str:
        """Open a DM channel with a user."""
        self._logger.info("Opening DM channel", user_id=user_id)

        raw_response = await self.client.conversations_open(users=user_id)  # pyright: ignore[reportUnknownMemberType]
        response = SlackConversationsOpenResponse.model_validate(raw_response.data)  # pyright: ignore[reportUnknownMemberType]
        channel_id = response.channel.id

        self._logger.info("DM channel opened", channel_id=channel_id)
        return channel_id

    async def send_dm(self, user_email: str, text: str) -> SlackMessage:
        """
        Send a DM to a user by their email address.

        Looks up the user by email, opens a DM channel, and sends the message.
        """
        self._logger.info("Sending DM by email", email=user_email)

        user = await self.get_user_by_email(user_email)
        channel_id = await self.open_dm_channel(user.id)
        return await self.send_message(channel_id, text)


slack_client = SlackNotificationClient()
