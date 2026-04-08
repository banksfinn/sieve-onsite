# Infrastructure

Local development runs via Docker Compose. Production uses the same images with different configuration.

## Local Services

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| `gateway` | `fullstack_backend:latest` | 1301 | [[Backend Architecture|FastAPI]] with hot reload |
| `frontend` | Built from `frontend/Dockerfile` | 1300 | Vite dev server |
| `fullstack_db` | `postgres:16` | 1303 | PostgreSQL database |
| `migration` | `fullstack_backend:latest` | - | Runs `alembic upgrade head` on startup |
| `backend_builder` | `fullstack_backend:latest` | - | Builds Python env, then exits |

## Docker Compose Architecture

The `backend_builder` service builds the Python environment once. Other backend services (`gateway`, `migration`) depend on it and reuse the image. Source code is volume-mounted for hot reload:

```yaml
volumes:
  - ../../../backend/app:/app/app
  - ../../../backend/libs:/app/libs
  - ../../../backend/tools:/app/tools
```

## Database

- **Engine**: PostgreSQL 16
- **Driver**: asyncpg (async) via [[DatabaseClient]]
- **Migrations**: Alembic, auto-run in Docker via `migration` service
- **Health check**: `pg_isready` with 1s interval
- **Persistence**: Named volume `fullstack_postgres_data`

## Environment Variables

Managed via `.env` files in `infra/docker/local/`. Key variables:

| Variable | Purpose |
|----------|---------|
| `ENV` | `local` or `deploy` |
| `DATABASE_URL` | PostgreSQL connection string |
| `GOOGLE_CLIENT_ID` | OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | OAuth client secret |
| `TOKEN_KEY_IDENTIFIER` | Cookie name |
| `TOKEN_SIGNING_SECRET` | JWT signing key |
| `FRONTEND_URL` | CORS origin |
| `GATEWAY_PORT` | Backend port (1301) |
| `FRONTEND_PORT` | Frontend port (1300) |

## Makefile Commands

| Command | Action |
|---------|--------|
| `make setup` | Initial project setup |
| `make build` | Build Docker images |
| `make run` | Start all services |
| `make run_no_frontend` | Backend + DB only |
| `make stop` | Stop all containers |
| `make db_reset` | Wipe and recreate database |
| `make db_generate_migration` | Create new Alembic migration |
| `make db_apply_migration` | Apply pending migrations |
| `make sync_openapi` | Regenerate frontend types |

## See Also

- [[Architecture Overview]]
- [[DatabaseClient]]
