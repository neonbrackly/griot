# RES-registry-013: GET /tasks - Get User Tasks (My Tasks Page)

## Response to REQ-013: Get User Tasks Endpoint
**From:** registry
**Status:** Completed

---

## Request Summary

The platform needed an endpoint to retrieve all tasks for the current user, organized into categories: pending authorizations, comments to review, drafts, and reapproval tasks.

---

## Expected API

**Endpoint:** `GET /api/v1/tasks`

**Query Parameters:** type, status, limit

**Expected Response:**
```json
{
  "pending_authorizations": { "items": [...], "total": 2 },
  "comments_to_review": { "items": [...], "total": 1 },
  "drafts": { "items": [...], "total": 2 },
  "reapproval_tasks": { "items": [...], "total": 1 },
  "summary": { "total_pending": 6, "authorizations": 2, "comments": 1, "drafts": 2, "reapprovals": 1 }
}
```

---

## Implemented API

**Location:** `griot-registry/src/griot_registry/api/tasks.py:192-345`

**Endpoint:** `GET /api/v1/tasks`

**Query Parameters:**
- `type` (string) - Filter: authorization, comment, draft, reapproval
- `status` (string, alias for filtering)
- `limit` (int, default: 10, max: 50) - Max items per category

**Response Model:**
```python
class TaskListResponse(BaseModel):
    pending_authorizations: TaskCategory = Field(..., alias="pendingAuthorizations")
    comments_to_review: TaskCategory = Field(..., alias="commentsToReview")
    drafts: TaskCategory
    reapproval_tasks: TaskCategory = Field(..., alias="reapprovalTasks")
    summary: TaskSummary
```

**Task Categories:**

**Pending Authorizations:**
- Contracts where user is reviewer and status is pending_review
- Includes requester info, change type, message

**Comments to Review:**
- Comments on contracts owned by user (excluding own comments)
- Includes content preview, author info

**Drafts:**
- User's contracts in draft status
- Includes completion percentage and details

**Reapproval Tasks:**
- Contracts previously approved that have changes (stub implementation)

---

## Differences from Request

| Aspect | Requested | Implemented |
|--------|-----------|-------------|
| Response fields | camelCase | Aliases for camelCase (pendingAuthorizations, etc.) |
| Reapproval tasks | Full tracking | Stub (returns empty - needs approval history) |
| Asset drafts | Include assets | Contracts only (no asset storage) |

---

## Frontend Integration

```typescript
const { data } = useQuery(['tasks'], () => api.get('/tasks'));

// Tab counts
<Tab label={`Pending (${data.summary.authorizations})`} />
<Tab label={`Comments (${data.summary.comments})`} />
<Tab label={`Drafts (${data.summary.drafts})`} />

// Render items
{data.pendingAuthorizations.items.map(task => (
  <AuthorizationCard key={task.id} task={task} />
))}
```

---

## Files Changed
- `griot-registry/src/griot_registry/api/tasks.py` - New file with My Tasks endpoint
- `griot-registry/src/griot_registry/api/__init__.py` - Added tasks import
- `griot-registry/src/griot_registry/server.py` - Added tasks router
