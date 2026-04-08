# Environment Setup

Required local machine state for development.

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Node.js | 22.x | `nvm install 22.15.0 && nvm alias default 22.15.0` |
| Python | 3.12 | `pyenv install 3.12` |
| uv | Latest | Python package manager |
| Docker | Latest | Docker Desktop |
| Yarn | 1.x | `npm install -g yarn` |
| Bitwarden CLI | Latest | `brew install bitwarden-cli` |

## Secrets Management

Environment variables use Bitwarden CLI for secret injection. The `.env.example` files contain Bitwarden references that get expanded:

```bash
# .env.example syntax
TOKEN_SIGNING_SECRET=bw:project-secrets          # password field
GOOGLE_CLIENT_ID=bw:google-oauth/field/client_id  # custom field
DATABASE_URL=bw:project-secrets/notes             # notes field
```

Bitwarden reference formats:
- `bw:<item-name>` - item's password field
- `bw:<item>/username` - username field
- `bw:<item>/notes` - notes field
- `bw:<item>/field/<name>` - custom field by name

Secrets are stored in the "Lavender" Bitwarden folder.

### Expanding Environment Files

```bash
# Unlock vault first
bw unlock

# Expand .env.example → .env
scripts/administration/env/expand_env.sh
```

Or use `make setup` which handles this automatically.

## Runtime Environment Variables

### Backend

Read via `app/config.py` Pydantic Settings. See [[Infrastructure]] for the full variable list.

### Frontend

Two mechanisms:
- **Build-time**: `import.meta.env.VITE_*` - baked into the bundle by Vite
- **Runtime**: `window.env.*` - injected via `env.js` into HTML at container start

Use runtime (`window.env`) for values that differ between environments (like `GOOGLE_CLIENT_ID`).

## See Also

- [[Infrastructure]]
- [[Backend Architecture]]
- [[Frontend Architecture]]
