# REQ-registry-016: POST /auth/logout - User Logout

## Request: User Logout Endpoint
**From:** platform
**To:** registry
**Priority:** Medium
**Blocking:** No

### Description
Need an endpoint to invalidate the user's session/token on logout.

### Context
The platform frontend handles logout by:
1. Calling logout API
2. Clearing localStorage token
3. Redirecting to login page

### API Specification

**Endpoint:** `POST /api/v1/auth/logout`

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:** None required

**Sample Request:**
```bash
curl -X POST "https://api.griot.com/api/v1/auth/logout" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Expected Response (200 OK):**
```json
{
  "message": "Logged out successfully"
}
```

**Error Response (401 - Not Authenticated):**
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Not authenticated"
  }
}
```

### Business Rules
1. Invalidate the current token (add to blacklist or delete from session store)
2. Log the logout event for audit
3. Return success even if token was already expired (idempotent)

### Security Requirements
1. Token blacklisting or session invalidation
2. Audit log entry

### Frontend Implementation
Location: `src/components/layout/TopNav.tsx` (user menu dropdown)
- Logout menu item
- Clears localStorage
- Redirects to `/login`

### Deadline
Medium priority - can function with client-side token clearing initially
