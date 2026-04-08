# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Documentation Vault (REQUIRED - READ FIRST)

This project maintains an Obsidian-style documentation vault in `docs/`. **Before starting any task**, read `AGENTS.md` in the project root and consult the relevant vault notes.

### Required Workflow

1. **At the start of every task**: Call `get_vault_area()` for the area you're working in, or `get_vault_index()` to orient yourself
2. **Before product decisions**: Call `get_product_notes()` to check business rules
3. **For specific topics**: Call `get_vault_note("note title")` to read a specific note
4. **When searching**: Call `search_vault("term")` to find relevant documentation

### MCP Tools Reference

| Tool | Purpose |
|------|---------|
| `get_vault_index()` | **Read first** - Get the full vault map (docs/Index.md) |
| `get_product_notes()` | **Check before product decisions** - Business rules and constraints |
| `get_vault_note(name)` | Read a specific note by title or path |
| `search_vault(query)` | Search all vault notes for a term |
| `get_vault_area(area)` | Get all notes for an area (backend, frontend, auth, database, api, infrastructure, product) |
| `list_design_decisions()` | List all architectural decision notes with summaries |

### Key Entry Points

- `docs/Index.md` - Full map of all documentation
- `docs/Product Notes.md` - Business rules and customer constraints
- `docs/Architecture/Architecture Overview.md` - System-level understanding
- `docs/Decisions/` - Design decision rationale

See `AGENTS.md` for the complete vault structure and navigation guide.

## Project Overview

Full stack application template using FastAPI (Python 3.12) backend and React (TypeScript) frontend with automatic type generation from OpenAPI specs.

## Common Commands

### Development
```bash
make setup          # Initial project setup (installs deps, generates env)
make build          # Build Docker images
make run            # Run full stack (frontend + backend + database)
make run_no_frontend # Run gateway + database only (for faster frontend hot reload)
make stop           # Stop all containers
```

### Database
```bash
make db_generate_migration  # Generate new Alembic migration (prompts for subject)
make db_apply_migration     # Apply pending migrations
make db_reset               # Wipe and recreate database
make db_shell               # Connect to PostgreSQL shell
```

### API Type Generation
```bash
make sync_openapi   # Regenerate frontend types from backend OpenAPI spec
```

### Backend (inside backend/ directory)
```bash
uv sync             # Install Python dependencies
uv run pytest       # Run tests
uv run ruff check   # Lint Python code
uv run pyright      # Type check Python code
```

### Frontend (inside frontend/ directory)
```bash
yarn install        # Install Node dependencies
yarn start          # Run dev server
yarn build          # Build for production
yarn lint           # Lint TypeScript code
```
