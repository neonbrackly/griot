# REQ-013: GET /tasks - Get User Tasks (My Tasks Page)

## Request: Get User Tasks Endpoint
**From:** platform
**To:** registry
**Priority:** High
**Blocking:** Yes

### Description
Need an endpoint to retrieve all tasks for the current user. This powers the "My Tasks" page which shows pending authorizations, comments to review, and user's drafts in a unified view.

### Context
The platform frontend (My Tasks page) displays three categories of tasks:
1. **Pending Authorizations** - Contracts awaiting the user's approval
2. **Comments to Review** - Comments on user's contracts that need response
3. **My Drafts** - Incomplete contracts/assets the user has started

The contracts.yaml spec has generic task endpoints, but this endpoint needs to return structured data specific to the My Tasks page requirements.

### API Specification

**Endpoint:** `GET /api/v1/tasks`

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| type | string | No | Filter by type: `authorization`, `comment`, `draft`, `reapproval`, `issue` |
| status | string | No | Filter by status: `pending`, `completed`, `dismissed` |
| limit | integer | No | Max items per category (default: 10) |

**Sample Request:**
```bash
curl -X GET "https://api.griot.com/api/v1/tasks" \
  -H "Authorization: Bearer <token>"
```

**Expected Response (200 OK):**
```json
{
  "pending_authorizations": {
    "items": [
      {
        "id": "auth-001",
        "contract_id": "customer-analytics-v1",
        "contract_name": "Customer Analytics Contract",
        "contract_version": "1.2.0",
        "requested_by": "user-001",
        "requested_by_name": "Brackly Murunga",
        "requested_by_avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=brackly",
        "requested_at": "2026-01-22T10:30:00Z",
        "domain": "analytics",
        "priority": "high",
        "change_type": "update",
        "change_summary": "Added new PII classifications to customer fields",
        "message": "Please review the new PII classifications on the email and phone fields.",
        "href": "/studio/contracts/customer-analytics-v1"
      },
      {
        "id": "auth-002",
        "contract_id": "order-processing-v1",
        "contract_name": "Order Processing Contract",
        "contract_version": "1.0.0",
        "requested_by": "user-003",
        "requested_by_name": "Alex Smith",
        "requested_by_avatar": null,
        "requested_at": "2026-01-21T14:00:00Z",
        "domain": "sales",
        "priority": "normal",
        "change_type": "new",
        "change_summary": "New contract for order processing pipeline",
        "message": null,
        "href": "/studio/contracts/order-processing-v1"
      }
    ],
    "total": 2
  },

  "comments_to_review": {
    "items": [
      {
        "id": "comment-001",
        "contract_id": "customer-analytics-v1",
        "contract_name": "Customer Analytics Contract",
        "author_id": "user-002",
        "author_name": "Jane Doe",
        "author_avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=jane",
        "content": "Can we discuss the PII classification for the loyalty_tier field? I think it should be marked as behavioral data.",
        "content_preview": "Can we discuss the PII classification for the loyalty_tier field?...",
        "type": "question",
        "created_at": "2026-01-22T11:00:00Z",
        "href": "/studio/contracts/customer-analytics-v1#comments"
      }
    ],
    "total": 1
  },

  "drafts": {
    "items": [
      {
        "id": "draft-001",
        "type": "contract",
        "name": "Marketing Campaign Contract",
        "domain": "marketing",
        "updated_at": "2026-01-21T16:30:00Z",
        "completion_percent": 65,
        "completion_details": {
          "basic_info": true,
          "schema": true,
          "quality_rules": false,
          "review": false
        },
        "href": "/studio/contracts/new/wizard?draft=draft-001"
      },
      {
        "id": "draft-002",
        "type": "asset",
        "name": "Campaign Events Table",
        "domain": "marketing",
        "updated_at": "2026-01-20T09:00:00Z",
        "completion_percent": 30,
        "completion_details": {
          "connection": true,
          "schema": false,
          "metadata": false
        },
        "href": "/studio/assets/new?draft=draft-002"
      }
    ],
    "total": 2
  },

  "reapproval_tasks": {
    "items": [
      {
        "id": "reapproval-001",
        "contract_id": "sales-pipeline-v1",
        "contract_name": "Sales Pipeline Contract",
        "contract_version": "2.0.0",
        "previous_version": "1.5.0",
        "changed_by": "user-003",
        "changed_by_name": "Alex Smith",
        "changed_at": "2026-01-22T09:00:00Z",
        "change_reason": "Added new lead scoring fields to support marketing automation",
        "schema_diff_summary": "Added 3 fields: lead_score, engagement_level, last_activity",
        "priority": "high",
        "href": "/studio/contracts/sales-pipeline-v1"
      }
    ],
    "total": 1
  },

  "summary": {
    "total_pending": 6,
    "authorizations": 2,
    "comments": 1,
    "drafts": 2,
    "reapprovals": 1
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

### Task Types Breakdown

#### Pending Authorizations
Tasks where the user is assigned as reviewer for a contract submitted for review.

#### Comments to Review
Comments on contracts where the user is the owner that need response/acknowledgment.

#### My Drafts
Incomplete contracts or assets that the user started creating but hasn't submitted.

#### Reapproval Tasks
Contracts that the user previously approved but have had schema changes requiring re-review.

### Business Rules
1. Tasks are user-specific (authenticated user only sees their own)
2. Summary counts enable badge displays on tabs
3. Pending authorizations include contracts where user is direct reviewer OR team member of reviewing team
4. Drafts are contracts/assets in draft status owned by the user
5. Reapproval tasks are only shown to original approvers

### Frontend Implementation
Location: `src/app/studio/tasks/page.tsx`
- Three tabs: Pending Authorizations, Comments to Review, My Drafts
- Each tab shows badge count from summary
- Authorization cards have Approve/Request Changes buttons
- Comment cards link to contract with anchor to comment
- Draft cards have Continue Editing and Delete buttons

### Deadline
High priority - core workflow feature
