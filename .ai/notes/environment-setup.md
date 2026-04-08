---
id: environment-setup
title: Development Environment
purpose: |
  Expected local machine state and environment configuration
  required for development.
scope:
  paths:
    - "**/*"
  tags:
    - environment
    - setup
    - node
    - python
    - bitwarden
    - secrets
related:
  - mcp-server
---

# Development Environment

## Items

<!-- @item source:user status:active enforcement:strict -->
Node.js 22.x is required. The MCP server runs commands via `bash -l`, so nvm's default must be set correctly: `nvm alias default 22.15.0`.

<!-- @item source:user status:active enforcement:strict -->
Python 3.12 is required. Use pyenv to manage versions: `pyenv shell 3.12.2`.

<!-- @item source:user status:active enforcement:recommended -->
Use `uv` for Python package management, not pip directly.

<!-- @item source:user status:active enforcement:recommended -->
If MCP tools fail with Node version errors, check that `bash -l -c "node --version"` returns the expected version. The issue is usually nvm's default alias.

<!-- @item source:user status:active enforcement:strict -->
Bitwarden CLI is required for secrets management. Install with `brew install bitwarden-cli` and login with `bw login`.

<!-- @item source:user status:active enforcement:strict -->
`.env` files are generated from `.env.example` using `scripts/administration/env/expand_env.sh`. Values with `bw:` prefix are fetched from Bitwarden. Syntax: `VAR=bw:<item-name>` (password), `bw:<item>/username`, `bw:<item>/notes`, `bw:<item>/field/<name>`.

<!-- @item source:user status:active enforcement:strict -->
Bitwarden secrets are stored in the "Lavender" folder (configured in `expand_env.sh`). The vault must be unlocked before expanding env files.
