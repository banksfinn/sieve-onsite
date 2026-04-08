# API Overview

All routes are served under the `/api/gateway/` prefix. The gateway is a FastAPI app defined in `backend/app/gateway.py`.

## Route Registration

Routes are organized by domain in `backend/app/api/routes/`. Each module exports an `APIRouter` that gets registered in `backend/app/api/router.py`:

```python
api_router.include_router(user_router, tags=["user"], prefix="/user")
api_router.include_router(google_auth_router, tags=["authentication"], prefix="/authentication/google")
```

## Current Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/health` | No | Health check |
| `POST` | `/api/gateway/authentication/google/login` | No | [[Authentication Routes\|Google login]] |
| `GET` | `/api/gateway/user/me` | Yes | [[User Routes\|Current user]] |
| `POST` | `/api/gateway/user/refresh` | Yes | [[User Routes\|Refresh token]] |
| `GET` | `/api/gateway/user/me/notification-preferences` | Yes | [[User Routes\|Get notification prefs]] |
| `PATCH` | `/api/gateway/user/me/notification-preferences` | Yes | [[User Routes\|Update notification prefs]] |

## Conventions

- All handlers are `async def` (see [[Async-First Backend]])
- Request/response types are always Pydantic models, never raw `dict`
- Protected routes use `UserDependency` (see [[Cookie-Based JWT Auth]])
- After adding/changing routes, run `make sync_openapi` (see [[OpenAPI Type Generation]])

## OpenAPI Documentation

FastAPI auto-generates OpenAPI docs. Each route gets a unique operation ID via `generate_unique_id` (uses route function name). This ID maps to the generated TypeScript function name.

## See Also

- [[Authentication Routes]]
- [[User Routes]]
- [[OpenAPI Type Generation]]
