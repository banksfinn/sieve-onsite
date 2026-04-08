# MCP Server

Development MCP server for fullstack-base that provides AI-accessible tools.

## Features

- OpenAPI sync between backend and frontend
- Database migration management
- Git operations
- Python package management (uv)
- Code quality tools (ruff, pyright)
- Notes documentation system for AI agents

## Running

The server runs automatically via VSCode tasks. For manual startup:

```bash
cd backend
uv run python -m mcp_server.server
```

## Notes System

The `notes/` subpackage provides a markdown-based documentation system for AI agents with:
- Scoped guidelines (file glob patterns)
- Items with enforcement levels (locked, strict, recommended, flexible)
- Fast index-based lookups
