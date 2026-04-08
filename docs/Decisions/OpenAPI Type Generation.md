# OpenAPI Type Generation

## Decision

Frontend TypeScript types and API client hooks are auto-generated from the backend's OpenAPI spec using Orval.

## Rationale

- **Type safety**: Frontend types always match backend schemas - no manual sync
- **Developer experience**: React Query hooks generated automatically for every endpoint
- **Single source of truth**: Backend Pydantic models define the contract

## How It Works

1. FastAPI generates an OpenAPI spec from route handlers and Pydantic models
2. `make sync_openapi` runs the Orval codegen tool
3. Output lands in `frontend/src/openapi/sieveBase.ts`
4. Frontend imports generated types and React Query hooks

## Generated Output

`sieveBase.ts` contains:
- TypeScript interfaces matching every Pydantic request/response model
- API client functions using fetch
- React Query hooks (`useQuery`, `useMutation`) for every endpoint
- Operation IDs derived from FastAPI route function names via `generate_unique_id`

## Rules

- **Never edit `openapi/sieveBase.ts` manually** - it will be overwritten
- **Run `make sync_openapi` after any API change** - route additions, schema changes, etc.
- **Route function names become TypeScript function names** - choose them carefully

## Operation ID Generation

In `gateway.py`:
```python
def generate_unique_id(route: APIRoute):
    return f"{route.name}"
```

This means the Python function name (e.g., `google_login`) becomes the TypeScript function name and React Query hook name (e.g., `useGoogleLogin`).

## See Also

- [[API Overview]]
- [[Frontend Architecture]]
- [[State Management]]
