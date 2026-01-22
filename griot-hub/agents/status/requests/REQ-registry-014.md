# REQ-registry-014: POST /auth/login - User Login

## Request: User Login Endpoint
**From:** platform
**To:** registry
**Priority:** High
**Blocking:** Yes

### Description
Need a production-ready authentication endpoint for user login with email and password. Currently using MSW mocks for development.

### Context
The platform frontend (Login page) handles:
1. Email/password form with validation
2. "Remember me" checkbox
3. Error handling for invalid credentials
4. JWT token storage after successful login
5. Redirect to dashboard

Currently implemented with MSW mocks. Need real API for production.

### API Specification

**Endpoint:** `POST /api/v1/auth/login`

**Request Body:**
```json
{
  "email": "brackly@griot.com",
  "password": "melly",
  "rememberMe": false
}
```

**Field Descriptions:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | Yes | User's email address |
| password | string | Yes | User's password |
| rememberMe | boolean | No | Extend token expiry (default: false) |

**Sample Request:**
```bash
curl -X POST "https://api.griot.com/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "brackly@griot.com",
    "password": "melly",
    "rememberMe": true
  }'
```

**Expected Response (200 OK):**
```json
{
  "user": {
    "id": "user-admin-001",
    "name": "Brackly Murunga",
    "email": "brackly@griot.com",
    "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=brackly",
    "role": {
      "id": "role-admin",
      "name": "Admin"
    },
    "team": {
      "id": "team-001",
      "name": "Data Engineering"
    },
    "status": "active",
    "lastLoginAt": "2026-01-22T10:30:00Z",
    "createdAt": "2025-06-15T08:00:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresAt": "2026-01-23T10:30:00Z"
}
```

**Error Response (401 - Invalid Credentials):**
```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password"
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
      { "field": "email", "message": "Invalid email format" },
      { "field": "password", "message": "Password is required" }
    ]
  }
}
```

**Error Response (423 - Account Locked):**
```json
{
  "error": {
    "code": "ACCOUNT_LOCKED",
    "message": "Account locked due to too many failed attempts. Try again in 15 minutes."
  }
}
```

### Business Rules
1. Validate email format
2. Password minimum 8 characters
3. Lock account after 5 failed attempts (15 minute lockout)
4. Update `lastLoginAt` on successful login
5. Return JWT with configurable expiry:
   - Default: 24 hours
   - With rememberMe: 30 days
6. Log authentication events for audit

### Security Requirements
1. Rate limit: 10 attempts per minute per IP
2. Password not logged or returned in any response
3. Constant-time password comparison to prevent timing attacks
4. HTTPS required

### Frontend Implementation
Location: `src/app/login/page.tsx`
- Email input with validation
- Password input with show/hide toggle
- Remember me checkbox
- Login button with loading state
- Error display for invalid credentials
- Redirect to `/` on success

### Deadline
High priority - required for production deployment
