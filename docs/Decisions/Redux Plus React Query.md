# Redux Plus React Query

## Decision

Use Redux Toolkit for client-side state and React Query (TanStack Query) for server-side state. They serve different purposes and coexist cleanly.

## Rationale

### Redux Toolkit - Client State

Manages state that lives entirely in the browser:
- **Auth state**: Current user, initialization flag, localStorage persistence
- **UI state**: Snackbar/toast notifications with priority ordering

Auth state persists to localStorage so the UI can render immediately before the server validates the session.

### React Query - Server State

Manages data fetched from the API:
- **Caching**: Automatic cache management with configurable stale times
- **Auto-generated hooks**: [[OpenAPI Type Generation|Orval]] generates React Query hooks for every endpoint
- **Background refetching**: Handles revalidation automatically

## Configuration

### Redux Store

```typescript
// store/store.ts
configureStore({
    reducer: {
        auth: authReducer,
        snackbar: snackbarReducer,
    },
})
```

Typed hooks: `useAppDispatch`, `useAppSelector` in `store/hooks.ts`.

### React Query Client

```typescript
const queryClient = new QueryClient({
    defaultOptions: {
        queries: { staleTime: Infinity },
    },
});
```

`staleTime: Infinity` means queries never go stale automatically - refetching is explicit. This prevents unnecessary background requests.

## Auth Slice Details

| Action | Purpose |
|--------|---------|
| `setUser(user)` | Store user + set `isInitialized=true` + persist to localStorage |
| `clearUser()` | Clear user + set `isInitialized=true` + remove from localStorage |
| `setInitialized(bool)` | Manually control initialization flag |

| Selector | Returns |
|----------|---------|
| `useAuthState()` | Full auth state (user, isInitialized) |
| `useCurrentUser()` | User object or null |
| `useIsAuthenticated()` | Boolean |

## Snackbar Slice

Manages toast notifications with priority: `error > warning > success > info`. Higher priority messages replace lower ones.

## See Also

- [[State Management]]
- [[Auth Flow]]
- [[OpenAPI Type Generation]]
