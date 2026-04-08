# Architecture Overview

## System Diagram

```
Frontend (React/TS)          Backend (FastAPI)              Database
┌─────────────────┐         ┌──────────────────┐         ┌──────────┐
│  Vite Dev Server │ ──────> │  Gateway (app/)  │ ──────> │ Postgres │
│  Port 1300       │  HTTP   │  Port 1301       │  asyncpg│ Port 1303│
│                  │ <────── │                  │ <────── │          │
│  React Router    │  JSON   │  API Router      │  SQL    │          │
│  Redux + RQ      │         │  Libs (libs/)    │         │          │
│  shadcn/ui       │         │  Tools (tools/)  │         │          │
└─────────────────┘         └──────────────────┘         └──────────┘
                                     │
                                     │ GCS SDK
                                     v
                            ┌──────────────────┐
                            │  Google Cloud     │
                            │  Storage          │
                            │  (gs://product-   │
                            │   onsite/)        │
                            └──────────────────┘
```

## Key Boundaries

| Layer | Responsibility | Location |
|-------|---------------|----------|
| Frontend | UI rendering, client state, route protection | `frontend/src/` |
| Gateway | HTTP handling, auth middleware, request validation | `backend/app/` |
| Libs | Reusable business logic, data access, external clients | `backend/libs/` |
| Tools | Dev utilities, migrations, MCP server | `backend/tools/` |
| Infra | Docker, compose, env management | `infra/` |

## Data Flow

1. Frontend calls API via [[OpenAPI Type Generation|auto-generated Orval hooks]]
2. Gateway validates request with Pydantic schemas
3. [[BaseEntityStore]] handles database operations via [[DatabaseClient]]
4. Response serialized back through Pydantic models
5. Frontend types stay in sync via `make sync_openapi`

## Authentication Flow

See [[Cookie-Based JWT Auth]] and [[Auth Flow]] for full details.

1. User authenticates via Google OAuth on frontend
2. Backend verifies ID token, creates/finds user
3. JWT set as HttpOnly cookie
4. [[Auth Flow|AuthProvider]] validates session on every app load
5. [[Auth Flow|RouteGuard]] protects routes inside the router

## See Also

- [[Backend Architecture]]
- [[Frontend Architecture]]
- [[Infrastructure]]
