# Cookie-Based JWT Auth

## Decision

Use HttpOnly cookies for JWT storage instead of `Authorization: Bearer` headers or localStorage.

## Rationale

- **XSS protection**: HttpOnly cookies are inaccessible to JavaScript, preventing token theft via XSS
- **Automatic transmission**: Cookies are sent with every request by the browser - no manual header management needed in the frontend
- **CSRF mitigation**: `SameSite=Lax` prevents cross-site request forgery for state-changing requests
- **Safari compatibility**: Explicit `domain` extraction from `FRONTEND_URL` in deployed environments handles Safari's stricter cookie policies

## Token Details

| Property | Value |
|----------|-------|
| Algorithm | HS256 |
| Expiry | 7 days (`ACCESS_TOKEN_EXPIRE_MINUTES`) |
| Payload | `exp` (timestamp), `user_id` (int) |
| Cookie flags | `httponly=True`, `secure=True`, `samesite=lax`, `path=/` |
| Cookie name | Configured via `TOKEN_KEY_IDENTIFIER` env var |
| Signing key | `TOKEN_SIGNING_SECRET` env var |

## Implementation

- **Token generation**: `user_management/core/security.py` - `generate_access_token()`
- **Token validation**: `user_management/core/security.py` - `decode_access_token()`
- **Cookie setting**: `user_management/core/security.py` - `set_access_token_cookie()`
- **Route protection**: `user_management/api/dependencies.py` - `UserDependency`

## UserDependency

FastAPI dependency that:
1. Reads the JWT from the cookie (key = `TOKEN_KEY_IDENTIFIER`)
2. Decodes and validates expiry
3. Fetches the [[User Model|User]] from [[UserStore]]
4. Returns the User or raises HTTP 401

Used on every protected route:
```python
async def my_route(user: User = Depends(UserDependency)):
```

## Cookie Domain

In deployed mode, the domain is extracted from `FRONTEND_URL` hostname for cross-subdomain cookie sharing. In local dev, `domain=None` lets the browser handle scoping.

## See Also

- [[Authentication Routes]]
- [[Auth Flow]]
- [[GoogleOAuthClient]]
