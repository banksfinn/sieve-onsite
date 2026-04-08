---
id: authentication
title: Authentication
purpose: Cookie-based authentication flow, UserDependency, and protected routes.
scope:
  paths:
  - backend/libs/user_management/**
  - backend/app/api/routes/auth*
  tags:
  - auth
  - security
  - cookies
---

# Authentication

## Items

<!-- @item source:user status:active enforcement:strict -->
**Cookie-based auth**: Uses first-party cookies. On login/register, backend encrypts user ID into a token and returns it as a cookie. Registration creates the user (password or Google OAuth), login verifies credentials—both result in the same encrypted token format.

<!-- @item source:user status:active enforcement:strict -->
**UserDependency**: Protected routes use `UserDependency` in FastAPI route parameters (defined in `backend/libs/user_management/user_management/api/dependencies.py`). This decodes the cookie token and returns the authenticated user.

<!-- @item source:llm status:proposed -->
**Frontend AuthProvider** (`frontend/src/providers/AuthProvider.tsx`): Top-level provider with no router dependency. On mount, calls `/api/gateway/user/refresh` to validate existing cookies and fetch user data. Stores user in Redux via `authSlice`. Blocks render until initialized.

<!-- @item source:llm status:proposed -->
**Route Configuration** (`frontend/src/router/routes.ts`): Defines all page routes centrally. `PUBLIC_ROUTES` lists routes accessible without authentication (login, register). `isPublicRoute()` helper checks if a path requires auth. Always add new routes here.

<!-- @item source:llm status:proposed -->
**Auth State** (`frontend/src/store/components/authSlice.ts`): Redux slice storing `user` (User object or null) and `isInitialized` (whether auth check completed). Use `useCurrentUser()`, `useIsAuthenticated()`, or `useAuthState()` hooks. `setUser()` and `clearUser()` actions persist to localStorage.

<!-- @item source:llm status:proposed -->
**Refresh Endpoint** (`POST /api/gateway/user/refresh`): Backend endpoint that validates the existing cookie via `UserDependency`, generates a fresh token, sets it as a new cookie, and returns the User object. Used by AuthProvider on app load and by GoogleLoginButton after successful OAuth.

<!-- @item source:llm status:proposed -->
**Login Flow**: GoogleLoginButton calls `/api/gateway/authentication/google/login` with ID token, then calls `/refresh` to get user data and stores it in Redux via `setUser()`. This ensures the user is available immediately after login without redirect loops.

<!-- @item source:llm status:proposed -->
**RouteGuard** (`frontend/src/providers/RouteGuard.tsx`): Must be inside BrowserRouter. Handles redirecting unauthenticated users from protected routes to `/login`. Preserves intended destination in route state for post-login redirect.
