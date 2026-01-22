# REQ-registry-017: GET /auth/me - Get Current User

## Request: Get Current User Endpoint
**From:** platform
**To:** registry
**Priority:** High
**Blocking:** Yes

### Description
Need an endpoint to retrieve the current authenticated user's profile from their token. Used on app initialization to restore auth state.

### Context
The platform frontend uses this endpoint to:
1. Validate token on app load
2. Populate AuthContext with user data
3. Determine role-based UI visibility
4. Show user info in TopNav

### API Specification

**Endpoint:** `GET /api/v1/auth/me`

**Headers:**
```
Authorization: Bearer <token>
```

**Sample Request:**
```bash
curl -X GET "https://api.griot.com/api/v1/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Expected Response (200 OK):**
```json
{
  "id": "user-admin-001",
  "name": "Brackly Murunga",
  "email": "brackly@griot.com",
  "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=brackly",
  "role": {
    "id": "role-admin",
    "name": "Admin",
    "permissions": [
      { "id": "contracts:read", "name": "View Contracts" },
      { "id": "contracts:write", "name": "Create/Edit Contracts" },
      { "id": "admin:users", "name": "Manage Users" },
      { "id": "admin:teams", "name": "Manage Teams" }
    ]
  },
  "team": {
    "id": "team-001",
    "name": "Data Engineering"
  },
  "status": "active",
  "lastLoginAt": "2026-01-22T10:30:00Z",
  "createdAt": "2025-06-15T08:00:00Z",
  "preferences": {
    "theme": "system",
    "notifications": {
      "email": true,
      "push": true
    }
  }
}
```

**Error Response (401 - Invalid Token):**
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token"
  }
}
```

**Error Response (401 - Token Expired):**
```json
{
  "error": {
    "code": "TOKEN_EXPIRED",
    "message": "Token has expired"
  }
}
```

### Business Rules
1. Validate JWT signature and expiry
2. Return full user profile with permissions
3. Include user preferences for UI customization
4. If user is deactivated, return 401

### Security Requirements
1. Token validation (signature, expiry, blacklist check)
2. Do not return sensitive data (password hash)

### Frontend Implementation
Location: `src/components/providers/AuthProvider.tsx`
- Called on app mount if token exists in localStorage
- Populates user context on success
- Clears token and redirects to login on 401

### Deadline
High priority - required for authenticated app functionality
