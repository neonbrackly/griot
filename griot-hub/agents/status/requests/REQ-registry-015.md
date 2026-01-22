# REQ-registry-015: POST /auth/signup - User Registration

## Request: User Signup Endpoint
**From:** platform
**To:** registry
**Priority:** High
**Blocking:** Yes

### Description
Need a production-ready endpoint for new user registration. Currently using MSW mocks.

### Context
The platform frontend (Signup page) handles:
1. Registration form with name, email, password
2. Password strength indicator
3. Terms acceptance
4. Account creation and auto-login

### API Specification

**Endpoint:** `POST /api/v1/auth/signup`

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecureP@ss123",
  "confirmPassword": "SecureP@ss123",
  "acceptTerms": true
}
```

**Field Descriptions:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | User's full name (2-100 chars) |
| email | string | Yes | User's email address |
| password | string | Yes | Password (min 8 chars, 1 upper, 1 lower, 1 number) |
| confirmPassword | string | Yes | Must match password |
| acceptTerms | boolean | Yes | Must be true |

**Sample Request:**
```bash
curl -X POST "https://api.griot.com/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecureP@ss123",
    "confirmPassword": "SecureP@ss123",
    "acceptTerms": true
  }'
```

**Expected Response (201 Created):**
```json
{
  "user": {
    "id": "user-new-001",
    "name": "John Doe",
    "email": "john@example.com",
    "avatar": null,
    "role": {
      "id": "role-viewer",
      "name": "Viewer"
    },
    "team": null,
    "status": "active",
    "lastLoginAt": "2026-01-22T10:30:00Z",
    "createdAt": "2026-01-22T10:30:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresAt": "2026-01-23T10:30:00Z"
}
```

**Error Response (409 - Email Exists):**
```json
{
  "error": {
    "code": "EMAIL_EXISTS",
    "message": "An account with this email already exists"
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
      { "field": "confirmPassword", "message": "Passwords do not match" },
      { "field": "acceptTerms", "message": "You must accept the terms of service" }
    ]
  }
}
```

### Business Rules
1. Email must be unique across all users
2. Password requirements:
   - Minimum 8 characters
   - At least 1 uppercase letter
   - At least 1 lowercase letter
   - At least 1 number
3. New users get default "Viewer" role
4. New users are not assigned to a team (null)
5. Auto-login after successful registration
6. Send welcome email (optional, can be async)

### Security Requirements
1. Hash password with bcrypt (cost factor 12)
2. Rate limit: 5 signups per hour per IP
3. Email verification (optional for MVP)

### Frontend Implementation
Location: `src/app/signup/page.tsx`
- Full name input
- Email input with validation
- Password input with strength indicator
- Confirm password input
- Terms checkbox
- Signup button with loading state

### Deadline
High priority - required for production deployment
