# Editable Library Installs

## Decision

Backend libraries in `backend/libs/` are standalone Python packages installed via `pip install -e` (editable mode).

## Rationale

- **Modularity**: Each library has clear boundaries and its own `pyproject.toml`
- **Hot reload**: Editable installs reflect code changes immediately - no reinstall needed during development
- **Reusability**: Libraries can be extracted to separate repos if needed
- **Independent testing**: Each library has its own `tests/` directory

## Structure

Each library follows this layout:

```
backend/libs/{name}/
├── {name}/
│   ├── __init__.py
│   ├── core/            # Settings, config
│   ├── clients/         # External service clients
│   ├── blueprints/      # Entity definitions
│   ├── stores/          # Data access
│   ├── api/             # FastAPI dependencies
│   └── schemas/         # Pydantic types
├── tests/
│   └── __init__.py
└── pyproject.toml
```

## Current Libraries

| Library | Purpose | Key Exports |
|---------|---------|-------------|
| `database_manager` | [[DatabaseClient]], [[BaseEntityStore]], [[BaseEntity]] | Database infrastructure |
| `user_management` | [[User Model]], [[UserStore]], JWT security, `UserDependency` | Auth + user management |
| `oauth_manager` | [[GoogleOAuthClient]], OAuth config | Google OAuth |
| `storage_manager` | [[GCSClient]] | Cloud storage |
| `logging_manager` | `configure_logging()`, `get_logger()` | Structured logging |
| `fullstack_types` | Enums, datetime types, pagination | Shared types |

## Import Pattern

Libraries import each other by package name (not relative paths):

```python
from database_manager.store.base_store import BaseEntityStore
from user_management.blueprints.user import User
from logging_manager.logger import get_logger
```

## See Also

- [[Backend Architecture]]
- [[Blueprint Pattern]]
