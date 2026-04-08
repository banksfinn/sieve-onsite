# AGENTS.md

## Documentation Vault (REQUIRED)

This project maintains an Obsidian-style documentation vault in `docs/`. **You MUST consult relevant vault notes before making changes.**

### Before Starting Work

1. Read `docs/Index.md` for the full vault map
2. Read the relevant Architecture, Client, Model, or Decision notes for the area you're working in
3. Read `docs/Product Notes.md` for customer-facing constraints and business rules

### Vault Structure

```
docs/
├── Index.md                          # Map of Content - start here
├── Architecture/
│   ├── Architecture Overview.md      # System diagram, data flow, key boundaries
│   ├── Backend Architecture.md       # FastAPI gateway, libs, tools tiers
│   ├── Frontend Architecture.md      # React SPA structure and conventions
│   └── Infrastructure.md             # Docker Compose, ports, env vars
├── Clients/
│   ├── DatabaseClient.md             # Async SQLAlchemy engine + sessions
│   ├── BaseEntityStore.md            # Generic CRUD store pattern
│   ├── UserStore.md                  # User data access
│   ├── GCSClient.md                  # Google Cloud Storage operations
│   └── GoogleOAuthClient.md          # Google OAuth flow
├── Models/
│   ├── Data Model Overview.md        # Entity system + how to add entities
│   ├── BaseEntity.md                 # Shared fields and base types
│   └── User Model.md                 # User entity definition
├── API/
│   ├── API Overview.md               # Route registration, conventions
│   ├── Authentication Routes.md      # Google OAuth login endpoint
│   └── User Routes.md                # Profile and preferences
├── Decisions/
│   ├── Cookie-Based JWT Auth.md      # Why cookies over headers
│   ├── Async-First Backend.md        # asyncpg + no lazy loading
│   ├── Editable Library Installs.md  # Monorepo lib architecture
│   ├── OpenAPI Type Generation.md    # Orval codegen for frontend types
│   ├── Redux Plus React Query.md     # Dual state management
│   └── Blueprint Pattern.md          # Entity type convention
├── Frontend/
│   ├── Provider Stack.md             # App.tsx wrapper hierarchy
│   ├── Auth Flow.md                  # Session init + route protection
│   ├── State Management.md           # Redux + React Query usage
│   └── Component Library.md          # shadcn/ui + custom components
├── Product Notes.md                  # Business rules and customer constraints
├── Project Requirements.md           # Problem statement and rubric
└── project_requirements.md           # Original requirements document
```

### Navigation

Notes use `[[wikilinks]]` extensively. Key entry points by task:

| Task | Start With |
|------|-----------|
| Adding a new entity | [[Data Model Overview]], [[Blueprint Pattern]], [[BaseEntityStore]] |
| Adding an API route | [[API Overview]], [[OpenAPI Type Generation]] |
| Working on auth | [[Cookie-Based JWT Auth]], [[Auth Flow]], [[Authentication Routes]] |
| Frontend components | [[Component Library]], [[Frontend Architecture]] |
| Database changes | [[DatabaseClient]], [[Async-First Backend]] |
| Cloud storage | [[GCSClient]], [[Project Requirements]] |
| Understanding the stack | [[Architecture Overview]] |

### Updating Documentation

When you make significant changes:
- Update the relevant vault note to reflect the new state
- Add new notes for new entities, clients, or design decisions
- Use `[[wikilinks]]` to connect new notes to existing ones
- Every note should have a `## See Also` section with links to related notes

### Product Constraints

Always check `docs/Product Notes.md` before making product decisions. It contains business rules from product conversations that aren't obvious from the code.

## MCP Tools for the Vault

The MCP server (`backend/tools/mcp_server/`) exposes tools for querying the vault programmatically:

| Tool | Purpose |
|------|---------|
| `get_vault_index()` | Read the full vault map - **start here** |
| `get_product_notes()` | Business rules and constraints - **check before product decisions** |
| `get_vault_note(name)` | Read a specific note by title or path |
| `search_vault(query)` | Search all vault notes for a term |
| `get_vault_area(area)` | Get all notes for an area (backend, frontend, auth, database, api, infrastructure, product) |
| `list_design_decisions()` | List all architectural decision notes with summaries |

### Recommended MCP Workflow

1. Call `get_vault_index()` to orient yourself
2. Call `get_product_notes()` before any product-facing work
3. Call `get_vault_area("backend")` (or frontend, auth, etc.) for the area you're working in
4. Call `get_vault_note("Blueprint Pattern")` for specific topics
5. Call `search_vault("async")` to find notes mentioning a concept

## Common Commands

```bash
make setup              # Initial project setup
make build              # Build Docker images
make run                # Run full stack
make run_no_frontend    # Backend + DB only
make stop               # Stop containers
make db_generate_migration  # New Alembic migration
make db_apply_migration     # Apply migrations
make db_reset               # Wipe database
make sync_openapi           # Regenerate frontend types
```

## Pre-Commit Checks

```bash
uv run pytest       # Tests
uv run pyright      # Type checking
uv run ruff check   # Linting
```
