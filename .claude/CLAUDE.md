# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Documentation System (REQUIRED)

This project uses a note-based documentation system in `.ai/notes/` accessible via MCP tools. **You MUST actively use this system throughout every task.**

### Required Workflow

1. **At the start of every task**: Call `get_notes_for_path("path/to/file")` for each file you'll be working with
2. **Before making changes**: Review the guidelines and enforcement levels
3. **After completing work**: Document any new patterns or gotchas discovered using `add_item()`

### Enforcement Levels
- `locked`: Do not deviate without explicit user approval
- `strict`: Follow unless there's a strong reason not to
- `recommended`: Preferred approach, alternatives acceptable
- `flexible`: Suggestion only

### When You Learn Something Important
- Call `add_item(note_id, content)` to document patterns, gotchas, or conventions discovered during work
- Your items start as `proposed` with `flexible` enforcement until the user approves them
- Use `search_notes()` to find the appropriate note, or `create_note()` if none exists

### Working with Items
- **User items** (`source: user`): Ask the user before making any edits
- **LLM items** (`source: llm`): Can be updated directly via `update_item()`

### MCP Tools Reference
| Tool | Purpose |
|------|---------|
| `get_notes_for_path(file_path)` | **Use first** - Get guidelines for a specific file |
| `search_notes(query, tags, source)` | Search across all notes |
| `get_note(note_id)` | Get full content of a note |
| `create_note(id, title, purpose, paths)` | Create a new note |
| `add_item(note_id, content)` | Add a guideline to a note |
| `update_item(note_id, item_index, ...)` | Update an item |

### Available Notes
| Note ID | Scope |
|---------|-------|
| `agents` | All files (`**/*`) - core AI guidelines |
| `environment-setup` | All files (`**/*`) - required local environment |
| `backend-structure` | `backend/**/*.py` - architecture & patterns |
| `frontend-patterns` | `frontend/src/**/*.{ts,tsx}` - React/TypeScript |
| `database-patterns` | blueprints, stores, migrations |
| `api-patterns` | routes, OpenAPI |
| `docker-infrastructure` | Docker, compose files |
| `authentication` | user_management, auth routes |
| `mcp-server` | `backend/tools/mcp_server/**/*` - MCP dev server |

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
