# MCP Server

Development MCP server for sieve-onsite that provides AI-accessible tools.

## Features

- OpenAPI sync between backend and frontend
- Database migration management
- Git operations
- Python package management (uv)
- Code quality tools (ruff, pyright)
- Documentation vault tools (docs/ Obsidian vault)

## Running

The server runs automatically via VSCode tasks. For manual startup:

```bash
cd backend
uv run python -m mcp_server.server
```

## Vault Tools

The server provides tools for querying the Obsidian-style documentation vault in `docs/`:

| Tool | Purpose |
|------|---------|
| `get_vault_index()` | Read the vault map of content |
| `get_vault_note(name)` | Read a specific note by title or path |
| `search_vault(query)` | Search all notes for a term |
| `get_product_notes()` | Business rules and constraints |
| `get_vault_area(area)` | Get all notes for an area |
| `list_design_decisions()` | List architectural decisions |
