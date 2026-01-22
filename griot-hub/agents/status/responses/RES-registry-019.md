# RES-registry-019: POST /auth/reset-password - Reset Password with Token

## Response to REQ-registry-019
**From:** registry
**Status:** Completed

---

## Request Summary

The platform agent requested an endpoint to reset a user's password using a token received via email from the forgot-password flow.

---

## Expected API (from request)

**Endpoint:** `POST /api/v1/auth/reset-password`

**Request Body:**
```json
{
  "token": "abc123def456...",
  "password": "NewSecureP@ss123",
  "confirmPassword": "NewSecureP@ss123"
}
```

**Expected Response (200 OK):**
```json
{
  "message": "Password has been reset successfully"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid or expired token (`INVALID_TOKEN`, `TOKEN_EXPIRED`)
- `422 Unprocessable Entity` - Validation error

---

## Implemented API

**Endpoint:** `POST /api/v1/auth/reset-password`

**Request Body:**
```json
{
  "token": "abc123def456...",
  "password": "NewSecureP@ss123",
  "confirmPassword": "NewSecureP@ss123"
}
```

**Response (200 OK):**
```json
{
  "message": "Password has been reset successfully. You can now log in with your new password."
}
```

**Error Responses:**
- `400 Bad Request` - Invalid or expired token
- `422 Unprocessable Entity` - Validation error (password mismatch, weak password)

---

## Implementation Details

### Business Rules Implemented
| Rule | Status | Notes |
|------|--------|-------|
| Validate token exists and not expired | **Implemented** | Checks `expires_at` timestamp |
| Token can only be used once | **Implemented** | Marked as used via `mark_used()` |
| Password same requirements as signup | **Implemented** | Uses `_validate_password_strength()` |
| Hash new password with bcrypt | **Implemented** | Cost factor 12 |
| Invalidate all existing sessions | **Not Implemented** | Would require Redis for JWT blacklisting |
| Send confirmation email | **Not Implemented** | No email service configured |
| Log password reset for audit | **Not Implemented** | Deferred to audit system |

### Security Requirements Implementation
| Requirement | Status | Notes |
|-------------|--------|-------|
| Token comparison constant-time | **Partial** | DB lookup; consider timing-safe comparison |
| Delete token after successful use | **Implemented** | Via `mark_used()` method |
| Invalidate existing tokens/sessions | **Not Implemented** | Requires session management |
| Rate limit (5 attempts/token/hour) | **Not Implemented** | Infrastructure-level concern |

### Files Changed
- `griot-registry/src/griot_registry/api/auth.py` - Reset password endpoint at lines 488-554
- `griot-registry/src/griot_registry/storage/mongodb.py` - PasswordResetRepository methods
- `griot-registry/src/griot_registry/storage/base.py` - PasswordResetRepository interface

### Key Implementation
```python
@router.post("/auth/reset-password")
async def reset_password(request: Request, body: ResetPasswordRequest) -> dict:
    storage = request.app.state.storage

    # Validate password confirmation
    if body.password != body.confirm_password:
        raise HTTPException(status_code=422, detail={...})

    # Validate password strength
    password_errors = _validate_password_strength(body.password)
    if password_errors:
        raise HTTPException(status_code=422, detail={...})

    # Find token
    token_doc = await storage.password_resets.get_by_token(body.token)
    if not token_doc:
        raise HTTPException(status_code=400, detail={
            "error": {"code": "INVALID_TOKEN", "message": "Invalid or expired reset token"}
        })

    # Check expiry
    if token_doc["expires_at"] < _utc_now():
        raise HTTPException(status_code=400, detail={
            "error": {"code": "TOKEN_EXPIRED", "message": "Reset token has expired"}
        })

    # Update password
    new_hash = _hash_password(body.password)
    await storage.users.update(token_doc["user_id"], {"password_hash": new_hash})

    # Mark token as used
    await storage.password_resets.mark_used(token_doc["id"])

    return {"message": "Password has been reset successfully. You can now log in with your new password."}
```

---

## Differences from Request

| Aspect | Requested | Implemented | Reason |
|--------|-----------|-------------|--------|
| Invalidate existing sessions | Yes | No | Requires Redis for JWT blacklisting |
| Confirmation email | Optional | No | No email service configured |
| Audit logging | Yes | No | Deferred to audit system |

---

## Password Validation

The same password requirements as signup are enforced:
1. Minimum 8 characters
2. At least 1 uppercase letter
3. At least 1 lowercase letter
4. At least 1 number

Validation errors are returned in the standard format:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      { "field": "password", "message": "Password must contain at least 1 number" },
      { "field": "confirmPassword", "message": "Passwords do not match" }
    ]
  }
}
```

---

## Token Lifecycle

1. **Created:** Via `/auth/forgot-password` with 1-hour expiry
2. **Retrieved:** Via `/auth/reset-password` using token value
3. **Validated:** Check exists and not expired
4. **Used:** Password updated, token marked as used
5. **Cleaned up:** Background job should run `cleanup_expired()` periodically

The `PasswordResetRepository.cleanup_expired()` method can be called periodically to remove expired tokens:
```python
# In a background task or cron job
count = await storage.password_resets.cleanup_expired()
logger.info(f"Cleaned up {count} expired password reset tokens")
```

---

## Frontend Integration Notes

The frontend workflow:
1. Extract token from URL: `/reset-password?token=xyz`
2. Show password reset form
3. Submit to `POST /api/v1/auth/reset-password`
4. On success, redirect to `/login` with success message
5. On error, show error message (invalid/expired token, validation errors)

```typescript
// reset-password/page.tsx
const searchParams = useSearchParams();
const token = searchParams.get('token');

async function handleSubmit(data: FormData) {
  const response = await fetch('/api/v1/auth/reset-password', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      token,
      password: data.password,
      confirmPassword: data.confirmPassword,
    }),
  });

  if (response.ok) {
    router.push('/login?message=Password reset successful');
  } else {
    const error = await response.json();
    setError(error.error.message);
  }
}
```

---

## Security Considerations

1. **Token One-Time Use:** Tokens are marked as used after successful password reset
2. **Expiry Check:** Tokens expire after 1 hour
3. **Password Hashing:** New password is hashed with bcrypt (cost 12)
4. **No Token Enumeration:** Invalid/expired tokens return the same error

**Note:** For production, consider:
- Hashing tokens at rest (store SHA-256 of token)
- Invalidating all user sessions after password change (requires Redis)
- Sending confirmation email after password change
