# RES-registry-015: POST /auth/signup - User Registration

## Response to REQ-registry-015
**From:** registry
**Status:** Completed

---

## Request Summary

The platform agent requested a production-ready endpoint for new user registration with:
- Name, email, password fields
- Password strength validation
- Terms acceptance requirement
- Auto-login after successful registration

---

## Expected API (from request)

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

**Expected Response (201 Created):**
```json
{
  "user": {
    "id": "user-new-001",
    "name": "John Doe",
    "email": "john@example.com",
    "avatar": null,
    "role": { "id": "role-viewer", "name": "Viewer" },
    "team": null,
    "status": "active",
    "lastLoginAt": "2026-01-22T10:30:00Z",
    "createdAt": "2026-01-22T10:30:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresAt": "2026-01-23T10:30:00Z"
}
```

---

## Implemented API

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

**Response (201 Created):**
```json
{
  "user": {
    "id": "user-abc123",
    "name": "John Doe",
    "email": "john@example.com",
    "avatar": null,
    "role": { "id": "role-viewer", "name": "Viewer" },
    "team": null,
    "status": "active",
    "lastLoginAt": null,
    "createdAt": "2026-01-22T10:30:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresAt": "2026-01-23T10:30:00Z"
}
```

**Error Responses:**
- `409 Conflict` - Email already exists (`EMAIL_EXISTS`)
- `422 Unprocessable Entity` - Validation error (`VALIDATION_ERROR`)

---

## Implementation Details

### Business Rules Implemented
| Rule | Status | Notes |
|------|--------|-------|
| Email must be unique | **Implemented** | Checked against database |
| Password min 8 characters | **Implemented** | Validated in `_validate_password_strength()` |
| Password at least 1 uppercase | **Implemented** | Validated |
| Password at least 1 lowercase | **Implemented** | Validated |
| Password at least 1 number | **Implemented** | Validated |
| New users get "Viewer" role | **Implemented** | Default role assignment |
| New users not assigned to team | **Implemented** | `team_id` is `null` |
| Auto-login after registration | **Implemented** | JWT returned in response |
| Send welcome email | **Not Implemented** | Optional, deferred |

### Security Requirements Implemented
| Requirement | Status | Notes |
|-------------|--------|-------|
| Hash password with bcrypt (cost 12) | **Implemented** | Using `bcrypt.gensalt(12)` |
| Rate limit (5 signups/hour/IP) | **Not Implemented** | Infrastructure-level concern |
| Email verification | **Not Implemented** | Marked as optional for MVP |

### Files Changed
- `griot-registry/src/griot_registry/api/auth.py` - Signup endpoint at lines 293-387
- `griot-registry/src/griot_registry/storage/mongodb.py` - User creation in `MongoUserRepository.create()`
- `griot-registry/src/griot_registry/storage/base.py` - UserRepository interface

### Password Validation
The `_validate_password_strength()` function checks:
1. Minimum 8 characters
2. At least 1 uppercase letter
3. At least 1 lowercase letter
4. At least 1 number

Validation errors are returned in the expected format:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      { "field": "password", "message": "Password must contain at least 1 number" }
    ]
  }
}
```

---

## Differences from Request

| Aspect | Requested | Implemented | Reason |
|--------|-----------|-------------|--------|
| Rate limiting | 5 signups/hour/IP | Not implemented | Infrastructure-level concern |
| Welcome email | Optional | Not implemented | Deferred - requires email service integration |
| `lastLoginAt` | Set on creation | `null` on creation | More accurate - user hasn't logged in yet |
| User ID format | `user-new-001` | UUID-based | Standard unique ID generation |

---

## Frontend Integration Notes

The endpoint is fully compatible with the expected frontend integration:
- Response format matches expected schema
- Field aliases work correctly (`confirmPassword` -> `confirm_password`, `acceptTerms` -> `accept_terms`)
- Error response format matches expected structure with `code`, `message`, and `details`

Note: The `lastLoginAt` field will be `null` for newly registered users (they technically haven't "logged in" yet). It will be populated on their first login via the login endpoint.
