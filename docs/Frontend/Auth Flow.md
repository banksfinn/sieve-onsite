# Auth Flow

Two-phase authentication: session validation on mount, then route protection.

## Phase 1: Session Validation (AuthProvider)

`frontend/src/providers/AuthProvider.tsx`

On every app load:

1. `useEffect` fires once (guarded by `hasAttemptedRefresh` ref)
2. Calls `refreshToken()` - the raw function, not a React Query hook
3. **Success**: Backend validates cookie, returns User → dispatched to Redux via `setUser()`
4. **Failure**: Cookie missing/expired → `clearUser()` dispatched
5. Either way, `isInitialized` becomes `true`

Until `isInitialized` is `true`, AuthProvider renders `null` - preventing flash of protected content.

## Phase 2: Route Protection (RouteGuard)

`frontend/src/providers/RouteGuard.tsx`

After initialization:
- Reads `isAuthenticated` from Redux
- If unauthenticated and on a protected route → redirect to `/login`
- If authenticated and on `/login` or `/register` → redirect to `/home`

## Login Flow

```
User clicks Google Sign-In
    │
    v
GoogleLoginButton gets ID token from Google
    │
    v
POST /api/gateway/authentication/google/login
    │
    v
Backend verifies token, creates/finds user
Sets HttpOnly JWT cookie
    │
    v
Frontend receives success response
Calls refreshToken() to get User object
    │
    v
Dispatch setUser() → Redux + localStorage
    │
    v
RouteGuard redirects to /home
```

## Token Refresh

The [[User Routes|refresh endpoint]] generates a new JWT on every successful validation. This implements sliding session expiry - active users never expire.

## State Persistence

Auth state is persisted to localStorage by the Redux `authSlice`. On page reload, the stored user renders immediately while `AuthProvider` validates with the server in the background. If the server rejects, the state is cleared.

## See Also

- [[Cookie-Based JWT Auth]]
- [[Provider Stack]]
- [[Authentication Routes]]
- [[Redux Plus React Query]]
