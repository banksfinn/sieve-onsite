# Authentication Routes

Google OAuth login endpoint at `backend/app/api/routes/authentication/google.py`.

## POST `/api/gateway/authentication/google/login`

Authenticates a user via Google One Tap / Sign-In.

### Flow

1. Frontend sends `credential` (Google ID token JWT)
2. Backend verifies token with Google using `google.oauth2.id_token.verify_oauth2_token()`
3. Extracts `email` and `name` from the verified token
4. Searches [[UserStore]] for existing user by email
5. If not found, creates new user via [[UserStore]]
6. Generates JWT access token (see [[Cookie-Based JWT Auth]])
7. Sets HttpOnly cookie on the response
8. Returns success/failure response

### Request

```python
class GoogleCredentialRequest(BaseModel):
    credential: str  # Google ID token JWT
```

### Response

```python
class GoogleLoginResponse(BaseModel):
    success: bool
    email: str | None = None
    message: str
```

### Error Handling

Token verification failure returns a 200 with `success=False` rather than raising an HTTP exception. This allows the frontend to show a user-friendly error.

### Security

- ID token verified against `GOOGLE_CLIENT_ID` to prevent token substitution
- Token verification uses Google's public keys (fetched automatically)
- No user input reaches the database without Google verification first

## See Also

- [[Cookie-Based JWT Auth]]
- [[GoogleOAuthClient]]
- [[Auth Flow]]
- [[User Routes]]
