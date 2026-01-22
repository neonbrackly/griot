# REQ-registry-018: POST /auth/forgot-password - Request Password Reset

## Request: Forgot Password Endpoint
**From:** platform
**To:** registry
**Priority:** Medium
**Blocking:** No

### Description
Need an endpoint to request a password reset email. User provides their email and receives a reset link.

### Context
The platform frontend (Forgot Password page) handles:
1. Email input form
2. Submit request
3. Display success message (always, for security)
4. Link back to login

### API Specification

**Endpoint:** `POST /api/v1/auth/forgot-password`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Sample Request:**
```bash
curl -X POST "https://api.griot.com/api/v1/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

**Expected Response (200 OK):**
```json
{
  "message": "If the email exists, a reset link has been sent"
}
```

Note: Always return 200 OK regardless of whether email exists (security best practice).

### Business Rules
1. Generate secure random reset token (32+ bytes)
2. Token expires in 1 hour
3. Store token hash (not plaintext)
4. Send email with reset link: `{frontend_url}/reset-password?token={token}`
5. Rate limit: 3 requests per email per hour
6. Always return success to prevent email enumeration

### Email Content
```
Subject: Reset your Griot password

Hi {name},

We received a request to reset your password. Click the link below to set a new password:

{reset_link}

This link expires in 1 hour.

If you didn't request this, you can safely ignore this email.

- The Griot Team
```

### Security Requirements
1. Constant-time email lookup to prevent timing attacks
2. Token stored as hash (SHA-256)
3. Rate limiting per email
4. Secure random token generation

### Frontend Implementation
Location: `src/app/forgot-password/page.tsx`
- Email input
- Submit button
- Success message display
- Link to login page

### Deadline
Medium priority - can be implemented after core auth
