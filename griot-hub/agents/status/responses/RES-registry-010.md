# RES-registry-010: PATCH /notifications/{notificationId}/read - Mark Notification as Read

## Response to REQ-010: Mark Notification as Read Endpoint
**From:** registry
**Status:** Completed

---

## Request Summary

The platform needed an endpoint to mark a single notification as read when clicked.

---

## Expected API

**Endpoint:** `PATCH /api/v1/notifications/{notificationId}/read`

**Request Body:** None required

**Expected Response:** Updated notification with `read: true` and `read_at` timestamp.

---

## Implemented API

**Location:** `griot-registry/src/griot_registry/api/notifications.py:147-195`

**Endpoint:** `PATCH /api/v1/notifications/{notification_id}/read`

**Request Body:** None required

**Response Model:**
```python
class Notification(BaseModel):
    id: str
    type: str
    title: str
    description: str
    read: bool = True  # Set to true
    read_at: datetime | None = Field(None, alias="readAt")  # Set to now
    href: str | None = None
    metadata: dict[str, Any] = {}
    created_at: datetime = Field(..., alias="createdAt")
```

**Validation:**
- Notification must exist
- User must own the notification
- Idempotent - marking already-read notification returns 200

**Error Responses:**
- 403 `NOT_AUTHORIZED`: Not notification owner
- 404 `NOTIFICATION_NOT_FOUND`: Notification doesn't exist

---

## Differences from Request

| Aspect | Requested | Implemented |
|--------|-----------|-------------|
| Path param | `{notificationId}` | `{notification_id}` (Python naming) |

---

## Frontend Integration

```typescript
// Mark notification as read when clicked
const markAsRead = useMutation({
  mutationFn: (notificationId: string) =>
    api.patch(`/notifications/${notificationId}/read`),
  onSuccess: () => queryClient.invalidateQueries(['notifications'])
});
```

---

## Files Changed
- `griot-registry/src/griot_registry/api/notifications.py` - Added mark_notification_read endpoint
