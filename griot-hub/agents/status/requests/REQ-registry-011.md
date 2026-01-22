# REQ-011: POST /notifications/read-all - Mark All Notifications as Read

## Request: Mark All Notifications as Read Endpoint
**From:** platform
**To:** registry
**Priority:** Medium
**Blocking:** No

### Description
Need an endpoint to mark all unread notifications as read in a single operation. This is a convenience endpoint for users who want to clear their notification queue.

### Context
The platform frontend (Notification Dropdown) provides a "Mark all as read" button that clears all unread notifications at once.

### API Specification

**Endpoint:** `POST /api/v1/notifications/read-all`

**Request Body:** None required (empty body or `{}`)

**Sample Request:**
```bash
curl -X POST "https://api.griot.com/api/v1/notifications/read-all" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
{
  "message": "All notifications marked as read",
  "marked_count": 7,
  "read_at": "2026-01-22T15:00:00Z"
}
```

**Error Response (401):**
```json
{
  "code": "UNAUTHORIZED",
  "message": "Authentication required"
}
```

### Business Rules
1. Only affects the authenticated user's notifications
2. Returns count of notifications that were marked as read
3. Idempotent - calling when no unread notifications returns `marked_count: 0`
4. Sets `read_at` timestamp on all affected notifications

### Frontend Implementation
Location: `src/components/layout/NotificationDropdown.tsx`
- "Mark all as read" button at bottom of dropdown
- Optimistically clears unread indicator
- Updates all notifications in local state to `read: true`

### Deadline
Medium priority - convenience feature
