# GoogleOAuthClient

Google OAuth 2.0 client at `backend/libs/oauth_manager/oauth_manager/clients/google/oauth_client.py`.

## Responsibilities

- Generate Google OAuth consent URLs
- Exchange authorization codes for access tokens
- Manage OAuth flow configuration

## Flow

The full auth flow involves two clients:

1. **Frontend**: `@react-oauth/google` handles the Google Sign-In button and returns an ID token
2. **Backend**: Verifies the ID token directly with Google (does not use `GoogleOAuthClient.exchange_code()` for the One Tap flow)

The `GoogleOAuthClient` exists for the full OAuth redirect flow (authorization URL → callback → code exchange), which is an alternative to the One Tap flow currently used.

### One Tap Flow (Current)

```
Frontend                    Backend                     Google
   │                          │                           │
   │─── Google One Tap ──────>│                           │
   │    (ID token)            │── verify_oauth2_token ───>│
   │                          │<── user info ─────────────│
   │                          │── create/find user        │
   │<── set cookie ───────────│                           │
```

See [[Authentication Routes]] for the endpoint implementation and [[Cookie-Based JWT Auth]] for the token strategy.

## Configuration

Via `oauth_manager.core.settings.google_oauth_settings`:

| Setting | Purpose |
|---------|---------|
| `GOOGLE_CLIENT_ID` | OAuth client identifier |
| `GOOGLE_CLIENT_SECRET` | OAuth client secret |
| `GOOGLE_REDIRECT_URI` | Callback URL after consent |
| `GOOGLE_SCOPES` | Requested permissions (openid, email, profile) |

## Token Response

`exchange_code()` returns a `GoogleTokens` object:

| Field | Type | Description |
|-------|------|-------------|
| `access_token` | `str` | API access token |
| `refresh_token` | `str \| None` | For refreshing expired tokens |
| `id_token` | `str \| None` | JWT with user identity |
| `expires_at` | `datetime \| None` | Token expiration |

## File Location

`backend/libs/oauth_manager/oauth_manager/clients/google/oauth_client.py`

## See Also

- [[Cookie-Based JWT Auth]]
- [[Authentication Routes]]
- [[Auth Flow]]
