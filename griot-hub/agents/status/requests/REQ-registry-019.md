# REQ-registry-019: POST /auth/reset-password - Reset Password with Token

## Request: Reset Password Endpoint
**From:** platform
**To:** registry
**Priority:** Medium
**Blocking:** No

### Description
Need an endpoint to reset a user's password using a token received via email from the forgot-password flow.

### Context
The platform frontend (Reset Password page) handles:
1. Extract token from URL query param
2. New password form with confirmation
3. Password strength indicator
4. Submit and redirect to login

### API Specification

**Endpoint:** `POST /api/v1/auth/reset-password`

**Request Body:**
```json
{
  "token": "abc123def456...",
  "password": "NewSecureP@ss123",
  "confirmPassword": "NewSecureP@ss123"
}
```

**Field Descriptions:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| token | string | Yes | Reset token from email |
| password | string | Yes | New password (same requirements as signup) |
| confirmPassword | string | Yes | Must match password |

**Sample Request:**
```bash
curl -X POST "https://api.griot.com/api/v1/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "abc123def456...",
    "password": "NewSecureP@ss123",
    "confirmPassword": "NewSecureP@ss123"
  }'
```

**Expected Response (200 OK):**
```json
{
  "message": "Password has been reset successfully"
}
```

**Error Response (400 - Invalid Token):**
```json
{
  "error": {
    "code": "INVALID_TOKEN",
    "message": "Invalid or expired reset token"
  }
}
```

**Error Response (400 - Token Expired):**
```json
{
  "error": {
    "code": "TOKEN_EXPIRED",
    "message": "Reset token has expired. Please request a new one."
  }
}
```

**Error Response (422 - Validation Error):**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      { "field": "password", "message": "Password must be at least 8 characters" },
      { "field": "confirmPassword", "message": "Passwords do not match" }
    ]
  }
}
```

### Business Rules
1. Validate token exists and is not expired
2. Token can only be used once (delete after use)
3. Password requirements same as signup:
   - Minimum 8 characters
   - At least 1 uppercase, 1 lowercase, 1 number
4. Hash new password with bcrypt
5. Invalidate all existing sessions for user
6. Send confirmation email (optional)
7. Log password reset for audit

### Security Requirements
1. Token comparison must be constant-time
2. Delete token after successful use
3. Invalidate existing tokens/sessions
4. Rate limit: 5 attempts per token per hour

### Frontend Implementation
Location: `src/app/reset-password/page.tsx`
- Extract token from `?token=` query param
- New password input with strength indicator
- Confirm password input
- Reset button
- Success message with login link
- Error handling for invalid/expired tokens

### Deadline
Medium priority - can be implemented after core auth
