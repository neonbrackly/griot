# REQ-009: GET /notifications - List User Notifications

## Request: List Notifications Endpoint
**From:** platform
**To:** registry
**Priority:** High
**Blocking:** Yes

### Description
Need an endpoint to retrieve notifications for the current user. Notifications are system-generated alerts about events relevant to the user, such as contract approvals, issue detections, and task assignments.

### Context
The platform frontend (Notification Dropdown in TopNav) displays:
1. Bell icon with unread count indicator
2. Scrollable notification list in dropdown
3. Mark individual notification as read on click
4. Mark all as read button
5. Link to notification settings

Frontend polls this endpoint every 30 seconds for real-time updates.

### API Specification

**Endpoint:** `GET /api/v1/notifications`

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| unread_only | boolean | No | If true, only return unread notifications (default: false) |
| limit | integer | No | Maximum notifications to return (default: 20, max: 100) |
| offset | integer | No | Offset for pagination (default: 0) |
| type | string | No | Filter by type: `contract_approved`, `contract_rejected`, `issue_detected`, etc. |

**Sample Request:**
```bash
curl -X GET "https://api.griot.com/api/v1/notifications?unread_only=true&limit=10" \
  -H "Authorization: Bearer <token>"
```

**Expected Response (200 OK):**
```json
{
  "items": [
    {
      "id": "notif-001",
      "type": "contract_approved",
      "title": "Contract Approved",
      "description": "Your contract 'Customer Analytics Contract' has been approved by Jane Doe.",
      "read": false,
      "href": "/studio/contracts/customer-analytics-v1",
      "metadata": {
        "contract_id": "customer-analytics-v1",
        "contract_name": "Customer Analytics Contract",
        "approved_by": "user-002",
        "approved_by_name": "Jane Doe"
      },
      "created_at": "2026-01-22T14:30:00Z"
    },
    {
      "id": "notif-002",
      "type": "issue_detected",
      "title": "Critical Issue Detected",
      "description": "A critical PII exposure issue was detected in 'Customer Analytics Contract'.",
      "read": false,
      "href": "/studio/issues/issue-001",
      "metadata": {
        "issue_id": "issue-001",
        "severity": "critical",
        "contract_id": "customer-analytics-v1",
        "category": "pii_exposure"
      },
      "created_at": "2026-01-22T08:30:00Z"
    },
    {
      "id": "notif-003",
      "type": "task_assigned",
      "title": "New Review Task",
      "description": "You have been assigned to review 'Order Processing Contract'.",
      "read": true,
      "href": "/studio/tasks",
      "metadata": {
        "task_id": "task-001",
        "contract_id": "order-processing-v1",
        "contract_name": "Order Processing Contract"
      },
      "created_at": "2026-01-21T16:00:00Z"
    },
    {
      "id": "notif-004",
      "type": "sla_breach",
      "title": "SLA Breach Warning",
      "description": "The 'Sales Pipeline Contract' is approaching its freshness SLA threshold.",
      "read": true,
      "href": "/studio/contracts/sales-pipeline-v1",
      "metadata": {
        "contract_id": "sales-pipeline-v1",
        "sla_type": "freshness",
        "threshold": "24h",
        "current": "22h"
      },
      "created_at": "2026-01-21T10:00:00Z"
    },
    {
      "id": "notif-005",
      "type": "comment_added",
      "title": "New Comment",
      "description": "Jane Doe commented on 'Customer Analytics Contract': 'Can we discuss the PII classification?'",
      "read": false,
      "href": "/studio/contracts/customer-analytics-v1#comments",
      "metadata": {
        "contract_id": "customer-analytics-v1",
        "comment_id": "comment-001",
        "author_id": "user-002",
        "author_name": "Jane Doe"
      },
      "created_at": "2026-01-22T11:00:00Z"
    }
  ],
  "pagination": {
    "total": 15,
    "unread_count": 4,
    "limit": 10,
    "offset": 0
  }
}
```

**Error Response (401):**
```json
{
  "code": "UNAUTHORIZED",
  "message": "Authentication required"
}
```

### Notification Types
| Type | Description | Generated When |
|------|-------------|----------------|
| `contract_approved` | Contract was approved | Reviewer approves a contract |
| `contract_rejected` | Contract was rejected | Reviewer requests changes |
| `contract_submitted` | Contract submitted for review | Owner submits contract |
| `issue_detected` | New issue detected | Quality run detects issue |
| `issue_assigned` | Issue assigned to you | Issue assigned to user/team |
| `issue_resolved` | Issue was resolved | Issue marked as resolved |
| `sla_breach` | SLA breach warning/violation | SLA threshold approached/exceeded |
| `schema_drift` | Schema drift detected | Source schema changed |
| `comment_added` | New comment on your contract | Comment added to owned contract |
| `task_assigned` | New task assigned | Review/reapproval task assigned |

### Business Rules
1. Notifications are user-specific (authenticated user only sees their own)
2. Unread count should be prominently returned for badge display
3. Notifications are sorted by created_at descending (newest first)
4. Notifications older than 90 days may be archived/deleted
5. Each notification type has relevant metadata for context

### Frontend Implementation
Location: `src/components/layout/NotificationDropdown.tsx`
- Bell icon shows unread count
- Dropdown shows notification list
- Each notification shows icon, title, description, time ago
- Click navigates to relevant page and marks as read
- "Mark all as read" button at bottom
- Link to notification settings

### Deadline
High priority - core user experience feature
