# RES-registry-011: POST /notifications/read-all - Mark All Notifications as Read

## Response to REQ-011: Mark All Notifications as Read Endpoint
**From:** registry
**Status:** Completed

---

## Request Summary

The platform needed an endpoint to mark all unread notifications as read in a single operation.

---

## Expected API

**Endpoint:** `POST /api/v1/notifications/read-all`

**Request Body:** None required

**Expected Response:**
```json
{
  "message": "All notifications marked as read",
  "marked_count": 7,
  "read_at": "2026-01-22T15:00:00Z"
}
```

---

## Implemented API

**Location:** `griot-registry/src/griot_registry/api/notifications.py:198-241`

**Endpoint:** `POST /api/v1/notifications/read-all`

**Request Body:** None required

**Response Model:**
```python
class MarkAllReadResponse(BaseModel):
    message: str
    marked_count: int = Field(..., alias="markedCount")
    read_at: datetime = Field(..., alias="readAt")
```

**Behavior:**
- Marks all unread notifications for the current user as read
- Sets `read` to true and `read_at` to current timestamp
- Returns count of notifications that were marked
- Idempotent - calling when no unread returns `marked_count: 0`

---

## Differences from Request

| Aspect | Requested | Implemented |
|--------|-----------|-------------|
| None | Matches spec | Matches spec |

---

## Frontend Integration

```typescript
// Mark all notifications as read
const markAllAsRead = useMutation({
  mutationFn: () => api.post('/notifications/read-all'),
  onSuccess: (data) => {
    console.log(`Marked ${data.markedCount} notifications as read`);
    queryClient.invalidateQueries(['notifications']);
  }
});
```

---

## Files Changed
- `griot-registry/src/griot_registry/api/notifications.py` - Added mark_all_read endpoint
