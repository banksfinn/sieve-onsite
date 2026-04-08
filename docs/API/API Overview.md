# API Overview

All routes are served under the `/api/gateway/` prefix. The gateway is a FastAPI app defined in `backend/app/gateway.py`.

## Route Registration

Routes are organized by domain in `backend/app/api/routes/`. Each module exports an `APIRouter` that gets registered in `backend/app/api/router.py`:

```python
api_router.include_router(user_router, tags=["user"], prefix="/user")
api_router.include_router(dataset_router, tags=["dataset"], prefix="/dataset")
api_router.include_router(dataset_assignment_router, tags=["dataset_assignment"], prefix="/dataset-assignment")
api_router.include_router(video_router, tags=["video"], prefix="/video")
api_router.include_router(clip_router, tags=["clip"], prefix="/clip")
api_router.include_router(delivery_router, tags=["delivery"], prefix="/delivery")
api_router.include_router(google_auth_router, tags=["authentication"], prefix="/authentication/google")
```

## Route Groups

| Group | Prefix | Auth | Description |
|-------|--------|------|-------------|
| Health | `/health` | No | Health check |
| Auth | `/api/gateway/authentication/google` | No | [[Authentication Routes\|Google OAuth]] |
| User | `/api/gateway/user` | Yes | [[User Routes\|Profile and preferences]] |
| Dataset | `/api/gateway/dataset` | Yes | [[Domain Routes\|Dataset CRUD, versions, clip feedback, ingest]] |
| Dataset Assignment | `/api/gateway/dataset-assignment` | Yes | [[Domain Routes\|User-to-dataset assignments]] |
| Video | `/api/gateway/video` | Yes | [[Domain Routes\|Video CRUD]] |
| Clip | `/api/gateway/clip` | Yes | [[Domain Routes\|Clip CRUD]] |
| Delivery | `/api/gateway/delivery` | Yes | [[Domain Routes\|Delivery CRUD (backend only, not in frontend flow)]] |

## Conventions

- All handlers are `async def` (see [[Async-First Backend]])
- Request/response types are always Pydantic models, never raw `dict`
- Protected routes use `UserDependency` (see [[Cookie-Based JWT Auth]])
- Create endpoints auto-set `created_by`/`user_id` from the authenticated user
- Nested resources use path params (e.g. `/dataset/{id}/version/{vid}/clip/{cid}/feedback`)
- After adding/changing routes, run `make sync_openapi` (see [[OpenAPI Type Generation]])

## OpenAPI Documentation

FastAPI auto-generates OpenAPI docs. Each route gets a unique operation ID via `generate_unique_id` (uses route function name). This ID maps to the generated TypeScript function name.

## See Also

- [[Authentication Routes]]
- [[User Routes]]
- [[Domain Routes]]
- [[OpenAPI Type Generation]]
