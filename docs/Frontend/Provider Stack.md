# Provider Stack

The `App.tsx` component wraps the application in a specific provider hierarchy. Order matters.

## Hierarchy

```tsx
<Provider store={store}>              // 1. Redux state
  <AuthProvider>                      // 2. Session validation
    <GoogleOAuthProvider>             // 3. Google OAuth context
      <QueryClientProvider>           // 4. React Query cache
        <SnackbarProvider>            // 5. Toast notifications
          <BrowserRouter>             // 6. Routing
            <RouteGuard>              // 7. Auth-based redirects
              <Router />              // 8. Route definitions
            </RouteGuard>
          </BrowserRouter>
        </SnackbarProvider>
      </QueryClientProvider>
    </GoogleOAuthProvider>
  </AuthProvider>
</Provider>
```

## Why This Order

1. **Redux first**: Everything else may need to dispatch actions or read state
2. **AuthProvider before Router**: Validates session on mount, blocks render until `isInitialized=true`. Has no router dependency - can wrap BrowserRouter
3. **GoogleOAuthProvider**: Provides OAuth context for `GoogleLoginButton`
4. **QueryClientProvider**: React Query needs to be available for API hooks
5. **SnackbarProvider**: UI feedback layer, available to all components
6. **BrowserRouter**: Enables routing
7. **RouteGuard inside Router**: Needs router context to read current path and redirect

## Key Design: AuthProvider Has No Router Dependency

[[Auth Flow|AuthProvider]] calls `refreshToken()` directly (not via a React Query hook) and dispatches to Redux. This means it can sit outside BrowserRouter. Route protection is a separate concern handled by RouteGuard inside the router.

## See Also

- [[Auth Flow]]
- [[State Management]]
- [[Frontend Architecture]]
