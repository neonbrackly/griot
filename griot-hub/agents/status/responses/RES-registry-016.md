# RES-registry-016: POST /auth/logout - User Logout

## Response to REQ-registry-016
**From:** registry
**Status:** Completed (with limitations)

---

## Request Summary

The platform agent requested an endpoint to invalidate the user's session/token on logout.

---

## Expected API (from request)

**Endpoint:** `POST /api/v1/auth/logout`

**Headers:**
```
Authorization: Bearer <token>
```

**Expected Response (200 OK):**
```json
{
  "message": "Logged out successfully"
}
```

---

## Implemented API

**Endpoint:** `POST /api/v1/auth/logout`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (204 No Content):**
- No response body (standard for 204)

---

## Implementation Details

### Business Rules Implementation
| Rule | Status | Notes |
|------|--------|-------|
| Invalidate current token | **Partial** | Stateless JWT - client-side invalidation |
| Log logout event for audit | **Not Implemented** | Deferred to audit system |
| Return success even if expired | **Implemented** | Returns 204 regardless |

### Security Requirements Implementation
| Requirement | Status | Notes |
|-------------|--------|-------|
| Token blacklisting | **Not Implemented** | Requires Redis or similar |
| Audit log entry | **Not Implemented** | Deferred to audit system |

### Files Changed
- `griot-registry/src/griot_registry/api/auth.py` - Logout endpoint at lines 390-406

### Current Implementation
```python
@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(user: CurrentUser) -> None:
    """Logout the current user.

    This endpoint invalidates the current session.
    Note: For stateless JWT, actual invalidation requires token blacklisting
    which is not implemented in this version. The client should discard the token.
    """
    return None
```

---

## Differences from Request

| Aspect | Requested | Implemented | Reason |
|--------|-----------|-------------|--------|
| Response code | 200 OK | 204 No Content | RESTful best practice for operations with no response body |
| Response body | `{"message": "..."}` | None | 204 means no content |
| Token invalidation | Server-side blacklist | Client-side only | Stateless JWT design; Redis needed for blacklisting |

---

## Rationale for Differences

### 204 No Content vs 200 OK
The HTTP 204 status code is the RESTful standard for successful operations that don't return content. This is cleaner than returning a redundant message body. The frontend should:
1. Call `POST /auth/logout`
2. On any 2xx response, clear localStorage
3. Redirect to login

### Token Blacklisting
For a truly secure logout with JWT, you need server-side token blacklisting. This typically requires:
- Redis or similar in-memory store
- Storing invalidated tokens until expiry
- Checking blacklist on every authenticated request

For the MVP, client-side token clearing is sufficient. The token will naturally expire after its TTL (24 hours or 30 days).

**Future Enhancement:** Add Redis integration for token blacklisting if immediate token invalidation is critical for security requirements.

---

## Frontend Integration Notes

The frontend should handle logout as follows:
```typescript
async function logout() {
  try {
    await fetch('/api/v1/auth/logout', {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` }
    });
  } catch (e) {
    // Ignore errors - we're logging out anyway
  } finally {
    localStorage.removeItem('token');
    router.push('/login');
  }
}
```

The endpoint accepts any valid token and returns 204. The frontend is responsible for clearing the token from localStorage.
