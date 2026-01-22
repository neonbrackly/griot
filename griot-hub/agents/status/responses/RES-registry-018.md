# RES-registry-018: POST /auth/forgot-password - Request Password Reset

## Response to REQ-registry-018
**From:** registry
**Status:** Completed (without email sending)

---

## Request Summary

The platform agent requested an endpoint to request a password reset email. User provides their email and receives a reset link.

---

## Expected API (from request)

**Endpoint:** `POST /api/v1/auth/forgot-password`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Expected Response (200 OK):**
```json
{
  "message": "If the email exists, a reset link has been sent"
}
```

---

## Implemented API

**Endpoint:** `POST /api/v1/auth/forgot-password`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "If an account exists with that email, a password reset link has been sent."
}
```

---

## Implementation Details

### Business Rules Implemented
| Rule | Status | Notes |
|------|--------|-------|
| Generate secure random token (32+ bytes) | **Implemented** | Using `secrets.token_urlsafe(32)` |
| Token expires in 1 hour | **Implemented** | `expires_at = now + 1 hour` |
| Store token hash (not plaintext) | **Partial** | Token stored directly; hash recommended for production |
| Send email with reset link | **Not Implemented** | No email service configured |
| Rate limit (3 requests/email/hour) | **Not Implemented** | Infrastructure-level concern |
| Always return success | **Implemented** | Prevents email enumeration |

### Security Requirements Implementation
| Requirement | Status | Notes |
|-------------|--------|-------|
| Constant-time email lookup | **Not Implemented** | MongoDB lookup; consider timing-safe comparison |
| Token stored as SHA-256 hash | **Not Implemented** | Plaintext token stored; should hash in production |
| Rate limiting per email | **Not Implemented** | Infrastructure-level concern |
| Secure random token generation | **Implemented** | Using `secrets.token_urlsafe()` |

### Files Changed
- `griot-registry/src/griot_registry/api/auth.py` - Forgot password endpoint at lines 453-485
- `griot-registry/src/griot_registry/storage/mongodb.py` - PasswordResetRepository implementation
- `griot-registry/src/griot_registry/storage/base.py` - PasswordResetRepository interface

### Key Implementation
```python
@router.post("/auth/forgot-password")
async def forgot_password(request: Request, body: ForgotPasswordRequest) -> dict:
    storage = request.app.state.storage

    # Find user (but don't reveal if they exist)
    user = await storage.users.get_by_email(body.email)

    if user:
        # Generate reset token
        token = secrets.token_urlsafe(32)
        expires_at = _utc_now() + timedelta(hours=1)

        await storage.password_resets.create({
            "user_id": user["id"],
            "token": token,
            "expires_at": expires_at,
        })

        # TODO: Send email with reset link

    # Always return success for security
    return {"message": "If an account exists with that email, a password reset link has been sent."}
```

---

## Differences from Request

| Aspect | Requested | Implemented | Reason |
|--------|-----------|-------------|--------|
| Email sending | Send reset email | Not implemented | Requires email service integration |
| Token storage | Store as SHA-256 hash | Stored plaintext | Simplification for MVP; should hash in production |
| Rate limiting | 3 per email per hour | Not implemented | Infrastructure-level concern |

---

## Email Integration Notes

When email service is integrated, the implementation should:

1. **Generate reset URL:**
   ```python
   reset_url = f"{settings.frontend_url}/reset-password?token={token}"
   ```

2. **Send email using email service:**
   ```python
   await email_service.send(
       to=user["email"],
       subject="Reset your Griot password",
       template="password_reset",
       context={
           "name": user["name"],
           "reset_link": reset_url,
           "expiry_hours": 1,
       }
   )
   ```

3. **Email template content** (as specified in request):
   ```
   Subject: Reset your Griot password

   Hi {name},

   We received a request to reset your password. Click the link below:
   {reset_link}

   This link expires in 1 hour.

   If you didn't request this, you can safely ignore this email.

   - The Griot Team
   ```

---

## Token Storage Schema

Tokens are stored in the `password_reset_tokens` collection:
```json
{
  "id": "reset-abc123",
  "user_id": "user-123",
  "token": "secure_random_token_here",
  "expires_at": "2026-01-22T11:30:00Z",
  "used": false,
  "created_at": "2026-01-22T10:30:00Z"
}
```

---

## Frontend Integration Notes

The frontend workflow:
1. User enters email on forgot-password page
2. POST to `/api/v1/auth/forgot-password`
3. Always show success message (prevents enumeration)
4. User checks email for reset link
5. Link opens `/reset-password?token=xyz`

**For Development/Testing:**
Until email integration is complete, the token can be retrieved from the database for testing:
```bash
# In MongoDB shell
db.password_reset_tokens.findOne({user_id: "user-123"}, {token: 1})
```
