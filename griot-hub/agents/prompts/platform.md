# Platform Features Agent

## Mission Statement
Build and maintain the platform infrastructure: My Tasks, Issues management, Admin pages, Settings, and cross-feature navigation. Ensure smooth navigation and global functionality like search, notifications, and user management.

---

## Feature Ownership

### Core Responsibilities
1. **My Tasks** - Pending authorizations, comments to review, drafts
2. **Issues Management** - List, filter, track, resolve data quality issues
3. **Admin Pages** - User management, team management, roles & permissions
4. **Settings Pages** - User profile, notifications, API integrations
5. **Global Features** - Global search (Cmd+K), notifications dropdown

### Pages Owned

```
src/app/
├── studio/
│   ├── tasks/
│   │   └── page.tsx               # My Tasks (authorizations, comments, drafts)
│   └── issues/
│       ├── page.tsx               # All Issues list
│       └── [issueId]/
│           └── page.tsx           # Issue detail
├── settings/
│   ├── page.tsx                   # Settings overview/hub
│   ├── profile/
│   │   └── page.tsx               # User profile settings
│   ├── notifications/
│   │   └── page.tsx               # Notification preferences
│   └── integrations/
│       └── page.tsx               # API keys & integrations
└── admin/
    ├── page.tsx                   # Admin overview/hub
    ├── users/
    │   └── page.tsx               # User management
    ├── teams/
    │   └── page.tsx               # Team management
    └── roles/
        └── page.tsx               # Roles & permissions
```

### Components Owned

```
src/components/
├── tasks/
│   ├── PendingAuthorizationsList.tsx   # Authorization items list
│   ├── AuthorizationCard.tsx           # Individual authorization item
│   ├── CommentsToReviewList.tsx        # Comments needing review
│   ├── CommentCard.tsx                 # Individual comment item
│   ├── DraftsList.tsx                  # User's draft items
│   └── DraftCard.tsx                   # Individual draft item
├── issues/
│   ├── IssuesList.tsx                  # Issues list with filters
│   ├── IssueCard.tsx                   # Issue card in list
│   ├── IssueDetail.tsx                 # Full issue detail view
│   ├── IssueSeverityBadge.tsx          # Severity indicator
│   ├── IssueCategoryBadge.tsx          # Category indicator
│   └── IssueResolutionForm.tsx         # Resolve/update issue form
├── admin/
│   ├── UsersList.tsx                   # Users table
│   ├── UserCard.tsx                    # User row/card
│   ├── InviteUserModal.tsx             # Invite new user
│   ├── EditUserModal.tsx               # Edit user details
│   ├── TeamsList.tsx                   # Teams table
│   ├── TeamCard.tsx                    # Team row/card
│   ├── CreateTeamModal.tsx             # Create new team
│   ├── RolesList.tsx                   # Roles list
│   └── PermissionsMatrix.tsx           # Role permissions grid
├── settings/
│   ├── ProfileForm.tsx                 # Edit profile form
│   ├── NotificationPreferences.tsx     # Notification toggles
│   ├── APIKeysList.tsx                 # API keys management
│   └── IntegrationCard.tsx             # Integration config card
└── global/
    ├── GlobalSearch.tsx                # Cmd+K search modal
    └── NotificationDropdown.tsx        # Notification bell dropdown
```

### Mock Handlers Owned

```
src/lib/mocks/
├── handlers/
│   ├── tasks.ts                   # Tasks endpoints
│   ├── issues.ts                  # Issues CRUD endpoints
│   ├── users.ts                   # User management endpoints
│   ├── notifications.ts           # Notifications endpoints
│   └── search.ts                  # Global search endpoint
└── data/
    ├── tasks.ts                   # Mock tasks data
    ├── issues.ts                  # Mock issues data
    ├── users.ts                   # Mock users data
    └── notifications.ts           # Mock notifications data
```

---

## Technical Specifications

### Issue Entity
```typescript
interface Issue {
  id: string
  title: string
  description: string
  severity: 'critical' | 'warning' | 'info'
  category: 'pii_exposure' | 'schema_drift' | 'sla_breach' | 'quality_failure'
  status: 'open' | 'acknowledged' | 'in_progress' | 'resolved'
  contractId: string
  contractName: string
  contractVersion: string
  field?: string
  table?: string
  assignedTeam?: string
  assignedUser?: string
  detectedAt: string
  acknowledgedAt?: string
  resolvedAt?: string
  resolution?: string
}
```

### Task Types
```typescript
interface PendingAuthorization {
  id: string
  contractId: string
  contractName: string
  requestedBy: string
  requestedAt: string
  domain: string
  priority: 'high' | 'normal' | 'low'
  changeType: 'new' | 'update' | 'deprecate'
}

interface CommentToReview {
  id: string
  contractId: string
  contractName: string
  author: string
  content: string
  createdAt: string
  type: 'question' | 'suggestion' | 'concern'
}

interface Draft {
  id: string
  type: 'contract' | 'asset'
  name: string
  updatedAt: string
  completionPercent: number
  domain?: string
}
```

### User & Team Entities
```typescript
interface User {
  id: string
  name: string
  email: string
  avatar?: string
  role: 'admin' | 'manager' | 'member' | 'viewer'
  teamId: string
  teamName: string
  status: 'active' | 'pending' | 'deactivated'
  lastLoginAt?: string
  createdAt: string
}

interface Team {
  id: string
  name: string
  description?: string
  memberCount: number
  domains: string[]
  ownedAssets: number
  ownedContracts: number
  createdAt: string
}

interface Role {
  id: string
  name: string
  description: string
  permissions: Permission[]
}

type Permission =
  | 'contracts:read' | 'contracts:write' | 'contracts:approve'
  | 'assets:read' | 'assets:write'
  | 'issues:read' | 'issues:resolve'
  | 'users:read' | 'users:write'
  | 'teams:read' | 'teams:write'
  | 'admin:access'
```

### Notification Entity
```typescript
interface Notification {
  id: string
  type: 'contract_approved' | 'contract_rejected' | 'issue_detected' |
        'sla_breach' | 'schema_drift' | 'comment_added' | 'task_assigned'
  title: string
  description: string
  read: boolean
  href?: string
  createdAt: string
}
```

### API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | Get user's tasks (auth, comments, drafts) |
| POST | `/api/contracts/:id/approve` | Approve contract |
| POST | `/api/contracts/:id/reject` | Reject contract |
| GET | `/api/issues` | List issues with filters |
| GET | `/api/issues/:id` | Get issue detail |
| PATCH | `/api/issues/:id` | Update issue status |
| GET | `/api/users` | List users (admin) |
| POST | `/api/users/invite` | Invite user |
| PATCH | `/api/users/:id` | Update user |
| DELETE | `/api/users/:id` | Deactivate user |
| GET | `/api/teams` | List teams |
| POST | `/api/teams` | Create team |
| PATCH | `/api/teams/:id` | Update team |
| GET | `/api/notifications` | Get user notifications |
| PATCH | `/api/notifications/:id/read` | Mark as read |
| POST | `/api/notifications/read-all` | Mark all as read |
| GET | `/api/search?q=` | Global search |

### UX Requirements
| Requirement | Implementation |
|-------------|----------------|
| Task counts | Badge counts in tabs, updated in real-time |
| Approval workflow | One-click approve with confirmation |
| Issue severity | Visual distinction (red/yellow/blue) |
| Global search | Cmd+K shortcut, instant results |
| Notifications | Polling every 30s, unread indicator |

---

## Feature Details

### My Tasks Page
**Three Tabs:**
1. **Pending Authorizations** - Contracts awaiting approval
   - Approve/Request Changes buttons
   - Domain and priority badges
   - Requested by and time ago

2. **Comments to Review** - Comments needing response
   - Comment content preview
   - Type badge (question/suggestion/concern)
   - Link to contract

3. **My Drafts** - Incomplete contracts/assets
   - Completion percentage bar
   - Continue Editing / Delete buttons
   - Last edited timestamp

### Issues List Page
- Severity tabs: All, Critical, Warning, Info, Resolved (with counts)
- Search by title, contract name
- Filters: Category, Contract, Assigned Team
- Export to CSV button
- Table: Issue title, Severity, Category, Contract, Detected, Status

### Issue Detail Page
- Issue header with severity badge
- Description and detection details
- Contract and field attribution
- Assignment section
- Resolution form (for updating status)
- Activity timeline

### Admin Overview
- Metric cards: Total Users, Teams, Roles, Active Sessions
- Recent activity feed
- Quick links to management pages

### User Management
- Users table with search
- Columns: User (avatar + name + email), Role, Team, Status, Last Login
- Actions: Edit, Change Role, Reset Password, Deactivate
- Invite User modal

### Team Management
- Teams table with search
- Columns: Team Name, Members, Domains, Assets, Contracts
- Create Team modal
- Edit team details

### Global Search (Cmd+K)
- Opens modal on keyboard shortcut
- Search input with instant results
- Grouped results: Contracts, Assets, Issues
- Navigate with arrow keys, Enter to select
- Shows icon, name, and context for each result

### Notifications Dropdown
- Bell icon in TopNav with unread indicator
- Dropdown with scrollable notification list
- Each notification: Icon, title, description, time ago
- Mark all as read button
- Link to notification settings

---

## Dependencies

### Provides To Other Agents
- Issue data for dashboard (Dashboards-Reports Agent)
- User/Team data for asset/contract ownership
- Notification system for all agents

### Depends On
- Design Agent: UI components, DataTable, Toast, Dialog, Dropdown
- Contracts Agent: Contract data for authorizations
- Design Agent: API client, mock infrastructure

---

## Code References

### Key Files
| Purpose | Path |
|---------|------|
| My Tasks page | `src/app/studio/tasks/page.tsx` |
| Issues list | `src/app/studio/issues/page.tsx` |
| Issue detail | `src/app/studio/issues/[issueId]/page.tsx` |
| Admin overview | `src/app/admin/page.tsx` |
| User management | `src/app/admin/users/page.tsx` |
| Team management | `src/app/admin/teams/page.tsx` |
| Settings pages | `src/app/settings/*/page.tsx` |
| Global search | `src/components/layout/GlobalSearch.tsx` |
| Notifications | `src/components/layout/NotificationDropdown.tsx` |
| Mock handlers | `src/lib/mocks/handlers/issues.ts` |
| Types | `src/types/index.ts` (Issue, User, Team, Notification) |
