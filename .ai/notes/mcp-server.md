---
id: mcp-server
title: MCP Dev Server
purpose: 'Guidelines for the FastMCP development server that provides

  AI-accessible tools for common development tasks.

  '
scope:
  paths:
  - backend/tools/mcp_server/**/*
  tags:
  - mcp
  - dev-tools
  - ai
related:
- agents
---

# MCP Dev Server

## Items

<!-- @item source:user status:active enforcement:strict -->
The MCP server runs automatically on startup via VSCode tasks (`.vscode/tasks.json`). No manual startup required during normal development.

<!-- @item source:user status:active enforcement:recommended -->
Use Pydantic models for tool return types to maintain type safety.

<!-- @item source:user status:active enforcement:recommended -->
Use explicit imports from submodules: `from mcp_server.notes.models import Note` rather than re-exports from `__init__.py`. The `notes/` subpackage has no `__init__.py` file.

<!-- @item source:user status:active enforcement:strict -->
The MCP server is structured as a proper Python package at `tools/mcp_server/` with its own `pyproject.toml`. The package code lives in `tools/mcp_server/mcp_server/` following the standard pattern for editable installs.
