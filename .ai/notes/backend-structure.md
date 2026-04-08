---
id: backend-structure
title: Backend Structure & Patterns
purpose: Architecture and patterns for the FastAPI backend including directory structure,
  entry points, and code organization.
scope:
  paths:
  - backend/**
  tags:
  - backend
  - python
  - fastapi
  - architecture
---

# Backend Structure & Patterns

## Items

<!-- @item source:user status:active enforcement:strict -->
The backend follows a two-tier architecture: `app/` contains production runtime code, `libs/` contains reusable libraries, and `tools/` contains development tooling (not deployed).

<!-- @item source:user status:active enforcement:strict -->
Place route handlers in `app/api/routes/`.

<!-- @item source:user status:active enforcement:recommended -->
Place Celery task definitions in `app/tasks/`.

<!-- @item source:user status:active enforcement:strict -->
Entity definitions (SQLAlchemy models + Pydantic schemas) belong in `app/blueprints/`. Each entity gets its own subdirectory.

<!-- @item source:user status:active enforcement:strict -->
Data access layer implementations (BaseEntityStore subclasses) belong in `app/stores/`.

<!-- @item source:user status:active enforcement:recommended -->
Entry points: `app/gateway.py` (FastAPI app), `app/worker.py` (Celery app), `app/config.py` (configuration).

<!-- @item source:user status:active enforcement:recommended -->
Reusable libraries in `libs/` include: `database_manager/` (SQLAlchemy abstraction), `user_management/` (auth), `fullstack_types/` (shared Pydantic types), `logging_manager/` (structured logging).

<!-- @item source:user status:active -->
The Gateway (`app/gateway.py`) should be kept lightweight, containing only truly global configuration. Business logic should live in libs or be delegated to services.

<!-- @item source:user status:active enforcement:strict -->
`__init__.py` files must always be empty. Only place them at the root of a package (e.g., `locking_manager/__init__.py`), not in subpackages. Use explicit imports in consuming code instead of re-exporting from `__init__.py`.

<!-- @item source:user status:active enforcement:strict -->
The `tools/` directory contains development tooling (not deployed). Single-file scripts are fine as standalone files. Multi-file projects that require imports across files must be converted to proper packages with `pyproject.toml` (see `tools/mcp_server/` as an example).
