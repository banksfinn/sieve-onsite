# Backend Architecture

The backend is a FastAPI application (`backend/app/gateway.py`) organized into three tiers.

## Directory Structure

```
backend/
├── app/                    # Production application code
│   ├── gateway.py          # FastAPI app, CORS, health check
│   ├── config.py           # Pydantic Settings (env vars)
│   ├── models.py           # Model imports for Alembic discovery
│   ├── api/
│   │   ├── router.py       # Central route registration
│   │   └── routes/         # Route handlers by domain
│   ├── blueprints/         # Entity definitions (Model + Schema)
│   ├── stores/             # Data access layer
│   └── schemas/            # Request/response Pydantic models
├── libs/                   # Reusable libraries (editable installs)
│   ├── database_manager/   # [[DatabaseClient]] + [[BaseEntityStore]]
│   ├── user_management/    # [[User Model]] + auth + [[UserStore]]
│   ├── oauth_manager/      # [[GoogleOAuthClient]] + config
│   ├── storage_manager/    # [[GCSClient]]
│   ├── logging_manager/    # structlog wrapper
│   └── fullstack_types/    # Shared enums, datetime types, pagination
└── tools/
    ├── alembic/            # Database migrations
    ├── mcp_server/         # FastMCP dev server
    └── openapi/            # [[OpenAPI Type Generation]] scripts
```

## Tier Responsibilities

### `app/` - Application Layer

The gateway is kept lightweight. It handles:
- FastAPI initialization with CORS
- Health check endpoint (`/health`)
- Route registration at `/api/gateway/` prefix
- Settings via `config.py` (reads env vars through Pydantic)

Routes live in `app/api/routes/` organized by domain. Each route module creates an `APIRouter` and registers in `app/api/router.py`.

### `libs/` - Library Layer

Each library is a standalone Python package with its own `pyproject.toml`, installed as [[Editable Library Installs|editable installs]] (`pip install -e`). This means:
- Libraries can import each other
- Changes reflect immediately (no reinstall needed)
- Each has independent test infrastructure

Key libraries:
- **[[DatabaseClient|database_manager]]** - Async engine, session management, [[BaseEntityStore]], [[BaseEntity]] base classes
- **[[User Model|user_management]]** - User entity, JWT security, `UserDependency` for protected routes
- **[[GoogleOAuthClient|oauth_manager]]** - Google OAuth flow configuration and token exchange
- **[[GCSClient|storage_manager]]** - Google Cloud Storage operations
- **logging_manager** - `configure_logging()` and `get_logger()` using structlog
- **fullstack_types** - `Environment` enum, datetime types, pagination constants

### `tools/` - Development Utilities

Not shipped to production. Contains Alembic migrations, the MCP dev server, and OpenAPI sync scripts.

## Configuration

`app/config.py` uses Pydantic `BaseSettings`:

| Setting | Source | Purpose |
|---------|--------|---------|
| `ENVIRONMENT` | `ENV` env var | local vs deploy mode |
| `TOKEN_KEY_IDENTIFIER` | env var | Cookie name for JWT |
| `TOKEN_SIGNING_SECRET` | env var | JWT signing key |
| `FRONTEND_URL` | env var | CORS origin, cookie domain |

The `is_deployed` property gates CORS strictness and cookie domain extraction.

## See Also

- [[Architecture Overview]]
- [[Blueprint Pattern]]
- [[Async-First Backend]]
