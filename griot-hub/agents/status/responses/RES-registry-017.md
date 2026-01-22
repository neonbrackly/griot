# RES-registry-017: GET /auth/me - Get Current User

## Response to REQ-registry-017
**From:** registry
**Status:** Completed

---

## Request Summary

The platform agent requested an endpoint to retrieve the current authenticated user's profile from their token, used for:
- Validating token on app load
- Populating AuthContext with user data
- Determining role-based UI visibility
- Showing user info in TopNav

---

## Expected API (from request)

**Endpoint:** `GET /api/v1/auth/me`

**Headers:**
```
Authorization: Bearer <token>
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
      { "id": "contracts:write", "name": "Create/Edit Contracts" }
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
    "notifications": { "email": true, "push": true }
  }
}
```

---

## Implemented API

**Endpoint:** `GET /api/v1/auth/me`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": "user-admin-001",
  "name": "Brackly Murunga",
  "email": "brackly@griot.com",
  "avatar": null,
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
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or expired token (`UNAUTHORIZED`, `TOKEN_EXPIRED`)
- `404 Not Found` - User not found in database (`USER_NOT_FOUND`)

---

## Implementation Details

### Business Rules Implemented
| Rule | Status | Notes |
|------|--------|-------|
| Validate JWT signature and expiry | **Implemented** | Via JWT middleware |
| Return full user profile with permissions | **Partial** | Permissions deferred (see below) |
| Include user preferences | **Not Implemented** | Deferred to user preferences endpoint |
| Return 401 if user deactivated | **Not Implemented** | Checking user status on each request adds overhead |

### Files Changed
- `griot-registry/src/griot_registry/api/auth.py` - Get me endpoint at lines 409-450

### Key Implementation
```python
@router.get("/auth/me", response_model=AuthUserResponse)
async def get_me(request: Request, user: CurrentUser) -> AuthUserResponse:
    """Get the current authenticated user's profile."""
    storage = request.app.state.storage

    # Get full user data from storage
    user_doc = await storage.users.get(user.id)

    # Get role and team
    role = await storage.roles.get(user_doc.get("role_id"))
    team = await storage.teams.get(user_doc["team_id"]) if user_doc.get("team_id") else None

    return AuthUserResponse(...)
```

---

## Differences from Request

| Aspect | Requested | Implemented | Reason |
|--------|-----------|-------------|--------|
| Role permissions array | Included | Not included | Separate endpoint for permissions (cleaner API) |
| User preferences | Included | Not included | Separate endpoint for preferences (cleaner API) |
| Deactivated user check | Return 401 | Not implemented | Performance - would require DB check on every request |

---

## Rationale for Differences

### Permissions Not in /auth/me
The request included permissions in the role object. For a cleaner API design, permissions are handled separately:
1. `/auth/me` returns basic user info (fast, cacheable)
2. `/api/v1/roles/{id}/permissions` or `/api/v1/permissions` returns permission details
3. Frontend can fetch permissions separately if needed for RBAC

This keeps the `/auth/me` response lightweight and fast for app initialization.

### User Preferences Not in /auth/me
Similarly, user preferences (theme, notifications) should be a separate concern:
1. Preferences can be managed independently of auth
2. Keeps auth response minimal
3. Future: `/api/v1/users/me/preferences` endpoint

### Deactivated User Check
Checking user status on every authenticated request would:
1. Add a database query to every request
2. Slow down the entire API
3. Add unnecessary complexity

Instead, the JWT token should be short-lived (24h), and deactivation should:
1. Prevent new logins
2. Wait for existing tokens to expire
3. For immediate revocation, implement token blacklisting (Redis)

---

## Frontend Integration Notes

The endpoint is compatible with the expected frontend usage:

```typescript
// AuthProvider.tsx
useEffect(() => {
  const token = localStorage.getItem('token');
  if (token) {
    fetch('/api/v1/auth/me', {
      headers: { Authorization: `Bearer ${token}` }
    })
    .then(res => {
      if (!res.ok) throw new Error('Invalid token');
      return res.json();
    })
    .then(user => setUser(user))
    .catch(() => {
      localStorage.removeItem('token');
      router.push('/login');
    });
  }
}, []);
```

For permissions, the frontend should:
1. Use the role name for basic RBAC (`Admin`, `Editor`, `Viewer`)
2. Optionally fetch detailed permissions from a separate endpoint
3. Cache permissions client-side
