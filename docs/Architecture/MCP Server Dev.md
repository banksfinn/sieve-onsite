# MCP Server Dev

Guidelines for the FastMCP development server at `backend/tools/mcp_server/`.

## Structure

```
backend/tools/mcp_server/
├── pyproject.toml              # Standalone package (fastmcp, pydantic, pyyaml)
├── mcp_server/
│   └── server.py               # All tool definitions
└── tests/
```

The server is a standalone Python package following the [[Editable Library Installs]] pattern used by other `libs/` packages.

## Running

The server auto-starts via VSCode tasks (`.vscode/tasks.json`). For manual startup:

```bash
cd backend
uv run python -m mcp_server.server
```

Runs on `127.0.0.1:8100` with streamable HTTP transport.

## Adding Tools

Define tools as functions decorated with `@mcp.tool()`:

```python
@mcp.tool()
def my_tool(arg: str) -> MyResponse:
    """
    Tool description shown to AI agents.

    Args:
        arg: Description of the argument
    """
    return MyResponse(...)
```

Rules:
- Use Pydantic `BaseModel` for return types (not raw dicts)
- Use explicit imports from submodules
- Shell commands go through `run_command()` which uses a login shell for proper PATH
- 5-minute timeout on all shell commands

## Available Tool Categories

| Category | Tools |
|----------|-------|
| Dev workflow | `sync_openapi`, `create_migration`, `apply_migration`, `git_commit` |
| Package management | `uv_lock`, `uv_sync`, `uv_add` |
| Code quality | `run_linters` (ruff + pyright) |
| Environment | `generate_env` |
| Documentation vault | `get_vault_index`, `get_vault_note`, `search_vault`, `get_product_notes`, `get_vault_area`, `list_design_decisions` |

## See Also

- [[Backend Architecture]]
- [[Editable Library Installs]]
- [[Infrastructure]]
