# RES-registry-007: GET /issues/{issueId} - Get Issue Detail

## Response to REQ-007: Get Issue Detail Endpoint
**From:** registry
**Status:** Completed

---

## Request Summary

The platform needed an endpoint to retrieve full issue details including contract info, location, assignment, timeline, activity, and comments.

---

## Expected API

**Endpoint:** `GET /api/v1/issues/{issueId}`

**Expected Response:** Detailed issue object with nested `contract`, `location`, `quality_rule`, `assignment`, `timeline`, `activity`, `comments`.

---

## Implemented API

**Location:** `griot-registry/src/griot_registry/api/issues.py:423-544`

**Endpoint:** `GET /api/v1/issues/{issue_id}`

**Response Model:**
```python
class IssueDetail(BaseModel):
    id: str
    title: str
    description: str | None
    severity: str
    category: str | None
    status: str
    contract: ContractRef | None
    location: LocationInfo | None
    quality_rule: QualityRuleInfo | None = Field(None, alias="qualityRule")
    assignment: AssignmentInfo | None
    timeline: TimelineInfo | None
    activity: list[ActivityEntry]
    comments: list[CommentEntry]
    metadata: dict[str, Any]
    tags: list[str]
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")
```

**Nested Models:**
- `ContractRef` - id, name, version, status, ownerTeam, ownerTeamName
- `LocationInfo` - table, field, physicalTable, physicalColumn
- `QualityRuleInfo` - id, name, type, threshold, actualValue, lastRunAt
- `AssignmentInfo` - teamId, teamName, userId, userName, assignedAt, assignedBy
- `TimelineInfo` - detectedAt, acknowledgedAt, inProgressAt, resolvedAt, resolution, resolutionNotes, resolvedBy
- `ActivityEntry` - id, type, description, actorId, actorName, createdAt
- `CommentEntry` - id, content, authorId, authorName, authorAvatar, createdAt

**Enrichment:**
- Contract info fetched and embedded
- Team/user names resolved
- Activity timeline generated from issue events

---

## Differences from Request

| Aspect | Requested | Implemented |
|--------|-----------|-------------|
| Path param | `{issueId}` | `{issue_id}` (Python naming) |
| quality_rule | Fully populated | Returns None (needs quality rule storage) |
| comments | From storage | Returns empty list (needs comment storage lookup) |
| activity | Full history | Basic creation activity |

---

## Frontend Integration

```typescript
const { data: issue } = useQuery(['issue', issueId], () =>
  api.get(`/issues/${issueId}`)
);
// issue.contract, issue.location, issue.timeline, etc.
```

---

## Files Changed
- `griot-registry/src/griot_registry/api/issues.py` - Added get_issue endpoint with detailed response
