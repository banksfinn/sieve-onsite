# Fullstack Base

A production-ready full stack application template with FastAPI (Python 3.12) backend and React (TypeScript) frontend, featuring automatic type generation from OpenAPI specs.

## Tech Stack

**Backend**
- FastAPI with async route handlers
- SQLAlchemy ORM with Alembic migrations
- PostgreSQL database
- Celery for background tasks
- Google OAuth authentication
- uv for Python package management

**Frontend**
- React 18 with TypeScript
- Vite build tooling
- shadcn/ui components + Tailwind CSS
- React Query (TanStack Query) for server state
- Redux Toolkit for client state
- Orval for automatic OpenAPI type generation

**Infrastructure**
- Docker Compose for local development
- Structured logging with structlog

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12
- Node.js 20+
- Yarn

### Setup

```bash
# Clone and setup
git clone git@github.com:banksfinn/fullstack-base.git
cd fullstack-base
make setup

# Build and run
make build
make run
```

The app will be available at `http://localhost:5173` (frontend) and `http://localhost:6012` (API).

## Development Commands

```bash
# Run full stack
make run

# Run backend only (for faster frontend hot reload)
make run_no_frontend
cd frontend && yarn start

# Database
make db_generate_migration  # Create new migration
make db_apply_migration     # Apply migrations
make db_reset               # Wipe and recreate database

# Sync frontend types from backend OpenAPI
make sync_openapi
```

## Project Structure

```
backend/
├── app/
│   ├── api/routes/      # API route handlers
│   ├── blueprints/      # SQLAlchemy models + Pydantic schemas
│   ├── stores/          # Data access layer
│   └── gateway.py       # FastAPI app entry point
├── libs/                # Reusable libraries
└── tools/
    └── alembic/         # Database migrations

frontend/
├── src/
│   ├── components/      # React components
│   ├── pages/           # Page components
│   ├── openapi/         # Auto-generated API types
│   └── store/           # Redux state management
```

## AI-Assisted Development

This repository includes documentation in `.ai/notes/` designed for AI coding assistants. The notes cover patterns for backend structure, database operations, API design, and frontend conventions.

## License

MIT License - see LICENSE file for details.
