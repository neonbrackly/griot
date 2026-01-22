# REQ-010: PATCH /notifications/{notificationId}/read - Mark Notification as Read

## Request: Mark Notification as Read Endpoint
**From:** platform
**To:** registry
**Priority:** Medium
**Blocking:** No

### Description
Need an endpoint to mark a single notification as read when the user clicks on it or explicitly marks it.

### Context
The platform frontend (Notification Dropdown) marks notifications as read when:
1. User clicks on a notification (navigates to href)
2. User explicitly clicks a "mark as read" action

### API Specification

**Endpoint:** `PATCH /api/v1/notifications/{notificationId}/read`

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| notificationId | string | Yes | Unique notification identifier |

**Request Body:** None required (empty body or `{}`)

**Sample Request:**
```bash
curl -X PATCH "https://api.griot.com/api/v1/notifications/notif-001/read" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
{
  "id": "notif-001",
  "type": "contract_approved",
  "title": "Contract Approved",
  "description": "Your contract 'Customer Analytics Contract' has been approved by Jane Doe.",
  "read": true,
  "href": "/studio/contracts/customer-analytics-v1",
  "metadata": {
    "contract_id": "customer-analytics-v1",
    "contract_name": "Customer Analytics Contract",
    "approved_by": "user-002",
    "approved_by_name": "Jane Doe"
  },
  "created_at": "2026-01-22T14:30:00Z",
  "read_at": "2026-01-22T15:00:00Z"
}
```

**Error Response (404):**
```json
{
  "code": "NOTIFICATION_NOT_FOUND",
  "message": "Notification with ID 'notif-001' not found"
}
```

**Error Response (403):**
```json
{
  "code": "NOT_AUTHORIZED",
  "message": "You can only mark your own notifications as read"
}
```

### Business Rules
1. Only the notification owner can mark it as read
2. Marking an already-read notification is a no-op (returns 200)
3. Sets `read_at` timestamp when marked as read
4. Updates the `read` boolean to true

### Frontend Implementation
Location: `src/components/layout/NotificationDropdown.tsx`
- Called when user clicks on a notification
- Optimistically updates UI before server response
- Decrements unread count on success

### Deadline
Medium priority - enhances user experience
