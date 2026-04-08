# User Routes

User profile and preferences endpoints at `backend/app/api/routes/user.py`. All routes require authentication via `UserDependency` (see [[Cookie-Based JWT Auth]]).

## GET `/api/gateway/user/me`

Returns the current authenticated [[User Model|User]].

Used by the frontend [[Auth Flow|AuthProvider]] indirectly through the refresh endpoint to populate Redux state.

## POST `/api/gateway/user/refresh`

Validates the existing JWT cookie and generates a new token. This is the endpoint [[Auth Flow|AuthProvider]] calls on every app load to check session validity.

### Flow

1. `UserDependency` extracts and validates the cookie token
2. If valid, generates a fresh token with new expiry
3. Sets the new token as a cookie
4. Returns the [[User Model|User]] object

If the cookie is missing or expired, `UserDependency` raises a 401, and the frontend transitions to the unauthenticated state.

## GET `/api/gateway/user/me/notification-preferences`

Returns the user's notification settings (`notification_timing`, `notification_custom_minutes`).

## PATCH `/api/gateway/user/me/notification-preferences`

Updates notification preferences. Uses `UserUpdateRequest` which supports partial updates via `exclude_unset=True` in [[BaseEntityStore]].

## See Also

- [[Authentication Routes]]
- [[Cookie-Based JWT Auth]]
- [[User Model]]
- [[Auth Flow]]
