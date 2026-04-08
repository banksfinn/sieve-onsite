from fastapi import APIRouter, Response
from pydantic import BaseModel

from user_management.api.dependencies import UserDependency
from user_management.blueprints.user import User, UserUpdateRequest
from user_management.core.security import generate_access_token, set_access_token_cookie
from user_management.stores.user import user_store

router = APIRouter()


@router.get("/me", response_model=User)
async def get_me(user: UserDependency) -> User:
    """Get the current authenticated user."""
    return user


@router.post("/refresh", response_model=User)
async def refresh_token(user: UserDependency, response: Response) -> User:
    """
    Refresh the current user's access token.

    Validates the existing token via UserDependency, generates a new token,
    and sets it as an HTTP-only cookie. Use this to extend sessions or
    verify authentication status on app load.
    """
    access_token = generate_access_token(user.id)
    set_access_token_cookie(response, access_token)
    return user


class NotificationPreferences(BaseModel):
    """User notification preferences."""

    notification_timing: list[str] | None = None
    notification_custom_minutes: int | None = None


class UpdateNotificationPreferencesRequest(BaseModel):
    """Request to update notification preferences."""

    notification_timing: list[str] | None = None
    notification_custom_minutes: int | None = None


@router.get("/me/notification-preferences")
async def get_notification_preferences(user: UserDependency) -> NotificationPreferences:
    """Get the current user's notification preferences."""
    return NotificationPreferences(
        notification_timing=user.notification_timing,
        notification_custom_minutes=user.notification_custom_minutes,
    )


@router.patch("/me/notification-preferences")
async def update_notification_preferences(
    user: UserDependency, request: UpdateNotificationPreferencesRequest
) -> NotificationPreferences:
    """Update the current user's notification preferences."""
    updated_user = await user_store.update_entity(
        UserUpdateRequest(
            id=user.id,
            notification_timing=request.notification_timing,
            notification_custom_minutes=request.notification_custom_minutes,
        )
    )
    return NotificationPreferences(
        notification_timing=updated_user.notification_timing,
        notification_custom_minutes=updated_user.notification_custom_minutes,
    )
