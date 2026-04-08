# State Management

Dual strategy: [[Redux Plus React Query|Redux Toolkit for client state, React Query for server state]].

## Redux Toolkit

### Store Configuration

`frontend/src/store/store.ts` - two slices:

| Slice | Purpose | Persistence |
|-------|---------|-------------|
| `auth` | Current user, initialization state | localStorage |
| `snackbar` | Toast notification queue | None (ephemeral) |

### Typed Hooks

`frontend/src/store/hooks.ts` exports:
- `useAppDispatch` - typed dispatch
- `useAppSelector` - typed selector

Always use these instead of raw `useDispatch`/`useSelector`.

### Auth Slice

See [[Redux Plus React Query]] for full details. Key pattern: `setUser` both updates Redux state and persists to localStorage in a single action.

### Snackbar Slice

Priority-based toast system: `error > warning > success > info`. When a new message arrives with higher priority than the current one, it replaces it immediately.

## React Query

### Configuration

```typescript
new QueryClient({
    defaultOptions: {
        queries: { staleTime: Infinity },
    },
})
```

`staleTime: Infinity` disables automatic background refetching. Data is only refetched when explicitly invalidated or when the component remounts.

### Auto-Generated Hooks

[[OpenAPI Type Generation|Orval]] generates React Query hooks in `src/openapi/fullstackBase.ts`. These provide:
- Type-safe request parameters
- Typed response data
- Loading/error states
- Cache key management

### Usage Pattern

```tsx
// Using generated hook
const { data: user } = useGetCurrentUser();

// Using generated mutation
const { mutate: login } = useGoogleLogin();
```

## When to Use Which

| Use Case | Tool |
|----------|------|
| Current user identity | Redux (authSlice) |
| UI feedback (toasts) | Redux (snackbarSlice) |
| API data (entities, lists) | React Query (generated hooks) |
| Form state | Local component state |

## See Also

- [[Redux Plus React Query]]
- [[Provider Stack]]
- [[OpenAPI Type Generation]]
