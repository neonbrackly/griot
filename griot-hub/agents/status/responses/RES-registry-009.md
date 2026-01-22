# RES-registry-009: GET /notifications - List User Notifications

## Response to REQ-009: List Notifications Endpoint
**From:** registry
**Status:** Completed

---

## Request Summary

The platform needed an endpoint to retrieve notifications for the current user with filtering and pagination.

---

## Expected API

**Endpoint:** `GET /api/v1/notifications`

**Query Parameters:** unread_only, limit, offset, type

**Expected Response:**
```json
{
  "items": [...notifications],
  "pagination": { "total": 15, "unread_count": 4, "limit": 10, "offset": 0 }
}
```

---

## Implemented API

**Location:** `griot-registry/src/griot_registry/api/notifications.py:76-144`

**Endpoint:** `GET /api/v1/notifications`

**Query Parameters:**
- `unread_only` (bool, alias: `unreadOnly`) - Filter unread only
- `limit` (int, default: 20, max: 100)
- `offset` (int, default: 0)
- `type` (str) - Filter by notification type

**Response Model:**
```python
class Notification(BaseModel):
    id: str
    type: str
    title: str
    description: str
    read: bool = False
    read_at: datetime | None = Field(None, alias="readAt")
    href: str | None = None
    metadata: dict[str, Any] = {}
    created_at: datetime = Field(..., alias="createdAt")

class NotificationListResponse(BaseModel):
    items: list[Notification]
    pagination: NotificationPagination
```

**Notification Types:**
- `contract_approved`, `contract_rejected`, `contract_submitted`
- `issue_detected`, `issue_assigned`, `issue_resolved`
- `sla_breach`, `schema_drift`
- `comment_added`, `task_assigned`

---

## Differences from Request

| Aspect | Requested | Implemented |
|--------|-----------|-------------|
| Query params | snake_case | camelCase aliases (unreadOnly) |
| Polling | Every 30s | Handled by frontend |

---

## Frontend Integration

```typescript
// Poll notifications every 30 seconds
const { data } = useQuery(['notifications'], () =>
  api.get('/notifications', { params: { unreadOnly: true, limit: 10 } }),
  { refetchInterval: 30000 }
);
```

---

## Files Changed
- `griot-registry/src/griot_registry/api/notifications.py` - New file with notification endpoints
