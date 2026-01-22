# Platform Features Agent

## Mission Statement
Build and maintain the platform infrastructure: My Tasks, Issues management, Admin pages, Authentication, Settings, and cross-feature navigation. Ensure smooth navigation and global functionality like search, notifications, and user management.

---

## Implementation Status

### Completed (Phase 2)
- [x] Authentication pages (login, signup, forgot password, reset password)
- [x] My Tasks page with tabs (Pending Authorizations, Comments, Drafts)
- [x] Issues list page with severity filtering
- [x] Issues detail page
- [x] Admin dashboard with stats
- [x] User management (list, invite, update, deactivate)
- [x] Team management (list, create, members)
- [x] Roles & permissions management
- [x] Settings pages (profile, notifications, integrations)
- [x] Global search (Cmd+K)
- [x] Notification dropdown
- [x] All MSW mock handlers (including auth)
- [x] Type definitions

### Pending (Requires Registry API)
- [ ] Replace MSW mocks with real API calls
- [ ] Create reusable component libraries
- [ ] Audit trail / activity logging
- [ ] Bulk operations (bulk invite, bulk role assignment)
- [ ] Saved filters for issues

### Registry API Requests Created
| Request | Endpoint | Description | Status |
|---------|----------|-------------|--------|
| REQ-registry-006 | GET /issues | List issues with filtering | Pending |
| REQ-registry-007 | GET /issues/{id} | Get issue detail | Pending |
| REQ-registry-008 | PATCH /issues/{id} | Update issue | Pending |
| REQ-registry-009 | GET /notifications | List user notifications | Pending |
| REQ-registry-010 | PATCH /notifications/{id}/read | Mark as read | Pending |
| REQ-registry-011 | POST /notifications/read-all | Mark all as read | Pending |
| REQ-registry-012 | GET /search | Global search | Pending |
| REQ-registry-013 | GET /tasks | Get user tasks | Pending |
| REQ-registry-014 | POST /auth/login | User login | Pending |
| REQ-registry-015 | POST /auth/signup | User signup | Pending |
| REQ-registry-016 | POST /auth/logout | User logout | Pending |
| REQ-registry-017 | GET /auth/me | Get current user | Pending |
| REQ-registry-018 | POST /auth/forgot-password | Request password reset | Pending |
| REQ-registry-019 | POST /auth/reset-password | Reset password | Pending |

---

## Feature Ownership

### Core Responsibilities
1. **Authentication** - Login, signup, logout, password reset, OAuth (Google, Microsoft, SSO)
2. **My Tasks** - Pending authorizations, comments to review, drafts, reapproval tasks
3. **Issues Management** - List, filter, track, resolve data quality issues
4. **Admin Pages** - User management, team management, roles & permissions
5. **Settings Pages** - User profile, notifications, API integrations
6. **Global Features** - Global search (Cmd+K), notifications dropdown

### Pages Owned

```
src/app/
├── (auth)/                        # Authentication pages
│   ├── login/
│   │   └── page.tsx               # Login page
│   ├── signup/
│   │   └── page.tsx               # Signup/register page
│   ├── forgot-password/
│   │   └── page.tsx               # Request password reset
│   └── reset-password/
│       └── page.tsx               # Reset password with token
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
    │   ├── page.tsx               # Team management
    │   └── [teamId]/
    │       └── page.tsx           # Team detail with members
    └── roles/
        └── page.tsx               # Roles & permissions
```

### Components Owned

```
src/components/
├── auth/                               # Authentication components
│   ├── LoginForm.tsx                   # Login form with validation
│   ├── SignupForm.tsx                  # Signup form with password strength
│   ├── ForgotPasswordForm.tsx          # Request password reset form
│   ├── ResetPasswordForm.tsx           # Reset password form
│   ├── PasswordStrengthIndicator.tsx   # Password strength visual feedback
│   ├── OAuthButtons.tsx                # Google, Microsoft, SSO buttons
│   └── AuthLayout.tsx                  # Layout wrapper for auth pages
├── tasks/                              # TO BE CREATED - Task-specific components
│   ├── PendingAuthorizationsList.tsx   # Authorization items list
│   ├── AuthorizationCard.tsx           # Individual authorization item
│   ├── CommentsToReviewList.tsx        # Comments needing review
│   ├── CommentCard.tsx                 # Individual comment item
│   ├── DraftsList.tsx                  # User's draft items
│   ├── DraftCard.tsx                   # Individual draft item
│   ├── ReapprovalTaskCard.tsx          # Re-approval task item (NEW)
│   └── TaskSummaryBadges.tsx           # Summary badges for tabs (NEW)
├── issues/                             # TO BE CREATED - Issue-specific components
│   ├── IssuesList.tsx                  # Issues list with filters
│   ├── IssueCard.tsx                   # Issue card in list
│   ├── IssueDetail.tsx                 # Full issue detail view
│   ├── IssueSeverityBadge.tsx          # Severity indicator
│   ├── IssueCategoryBadge.tsx          # Category indicator
│   ├── IssueStatusBadge.tsx            # Status indicator (NEW)
│   ├── IssueResolutionForm.tsx         # Resolve/update issue form
│   ├── IssueActivityTimeline.tsx       # Activity/comment timeline (NEW)
│   ├── IssueAssignmentForm.tsx         # Assign team/user form (NEW)
│   └── IssueFilters.tsx                # Reusable filter controls (NEW)
├── admin/                              # TO BE CREATED - Admin-specific components
│   ├── UsersList.tsx                   # Users table
│   ├── UserCard.tsx                    # User row/card
│   ├── InviteUserModal.tsx             # Invite new user
│   ├── EditUserModal.tsx               # Edit user details
│   ├── ChangeRoleModal.tsx             # Change user role (NEW)
│   ├── TeamsList.tsx                   # Teams table
│   ├── TeamCard.tsx                    # Team row/card
│   ├── CreateTeamModal.tsx             # Create new team
│   ├── EditTeamModal.tsx               # Edit team details (NEW)
│   ├── TeamMembersList.tsx             # Team members table (NEW)
│   ├── AddMemberModal.tsx              # Add member to team (NEW)
│   ├── RolesList.tsx                   # Roles list
│   ├── CreateRoleModal.tsx             # Create new role (NEW)
│   ├── EditRoleModal.tsx               # Edit role (NEW)
│   ├── PermissionsMatrix.tsx           # Role permissions grid
│   └── AdminStatsCard.tsx              # Admin dashboard stat card (NEW)
├── settings/                           # TO BE CREATED - Settings-specific components
│   ├── ProfileForm.tsx                 # Edit profile form
│   ├── AvatarUpload.tsx                # Avatar upload component (NEW)
│   ├── PasswordChangeForm.tsx          # Change password form (NEW)
│   ├── NotificationPreferences.tsx     # Notification toggles
│   ├── NotificationChannelToggle.tsx   # Channel-specific toggle (NEW)
│   ├── APIKeysList.tsx                 # API keys management
│   ├── CreateAPIKeyModal.tsx           # Create new API key (NEW)
│   └── IntegrationCard.tsx             # Integration config card
└── global/                             # Located in src/components/layout/
    ├── GlobalSearch.tsx                # Cmd+K search modal (EXISTS)
    └── NotificationDropdown.tsx        # Notification bell dropdown (EXISTS)
```

### Mock Handlers Owned

```
src/lib/mocks/
├── handlers/
│   ├── auth.ts                    # Authentication endpoints (EXISTS)
│   ├── tasks.ts                   # Tasks endpoints (EXISTS)
│   ├── issues.ts                  # Issues CRUD endpoints (EXISTS)
│   ├── users.ts                   # User management endpoints (EXISTS)
│   ├── teams.ts                   # Team management endpoints (EXISTS)
│   ├── roles.ts                   # Role management endpoints (EXISTS)
│   ├── notifications.ts           # Notifications endpoints (EXISTS)
│   └── search.ts                  # Global search endpoint (EXISTS)
└── data/
    └── mock-data.ts               # All mock data consolidated (EXISTS)
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
  category: 'pii_exposure' | 'schema_drift' | 'sla_breach' | 'quality_failure' | 'other'
  status: 'open' | 'in_progress' | 'resolved' | 'ignored'
  contractId: string
  contractName: string
  contractVersion: string
  table?: string
  field?: string
  qualityRuleId?: string
  assignedTeam?: string
  assignedTeamName?: string
  assignedUser?: string
  assignedUserName?: string
  detectedAt: string
  acknowledgedAt?: string
  resolvedAt?: string
  resolution?: 'fixed' | 'wont_fix' | 'false_positive' | 'deferred'
  resolutionNotes?: string
  resolvedBy?: string
  tags?: string[]
  createdAt: string
  updatedAt: string
}
```

### Task Types
```typescript
interface PendingAuthorization {
  id: string
  contractId: string
  contractName: string
  contractVersion: string
  requestedBy: string
  requestedByName: string
  requestedByAvatar?: string
  requestedAt: string
  domain: string
  priority: 'high' | 'normal' | 'low'
  changeType: 'new' | 'update' | 'deprecate'
  changeSummary?: string
  message?: string
  href: string
}

interface CommentToReview {
  id: string
  contractId: string
  contractName: string
  authorId: string
  authorName: string
  authorAvatar?: string
  content: string
  contentPreview: string
  type: 'question' | 'suggestion' | 'concern'
  createdAt: string
  href: string
}

interface Draft {
  id: string
  type: 'contract' | 'asset'
  name: string
  domain?: string
  updatedAt: string
  completionPercent: number
  completionDetails: Record<string, boolean>
  href: string
}

interface ReapprovalTask {
  id: string
  contractId: string
  contractName: string
  contractVersion: string
  previousVersion: string
  changedBy: string
  changedByName: string
  changedAt: string
  changeReason: string
  schemaDiffSummary: string
  priority: 'high' | 'normal' | 'low'
  href: string
}

interface MyTasks {
  pendingAuthorizations: { items: PendingAuthorization[]; total: number }
  commentsToReview: { items: CommentToReview[]; total: number }
  drafts: { items: Draft[]; total: number }
  reapprovalTasks: { items: ReapprovalTask[]; total: number }
  summary: {
    totalPending: number
    authorizations: number
    comments: number
    drafts: number
    reapprovals: number
  }
}
```

### User & Team Entities
```typescript
interface User {
  id: string
  name: string
  email: string
  avatar?: string
  role: Role
  team?: TeamSummary
  status: 'active' | 'pending' | 'deactivated'
  lastLoginAt?: string
  createdAt: string
}

interface Team {
  id: string
  name: string
  description?: string
  memberCount: number
  defaultRole?: RoleSummary
  domains: string[]
  ownedAssets?: number
  ownedContracts?: number
  createdAt: string
}

interface TeamMember {
  user: User
  role: RoleSummary
  isRoleInherited: boolean
  joinedAt: string
}

interface Role {
  id: string
  name: string
  description: string
  permissions: Permission[]
  isSystem: boolean
  userCount?: number
  createdAt: string
}

interface Permission {
  id: string
  name: string
  category: 'contracts' | 'assets' | 'issues' | 'admin' | 'reports' | 'rules'
  description: string
}
```

### Notification Entity
```typescript
interface Notification {
  id: string
  type: NotificationType
  title: string
  description: string
  read: boolean
  readAt?: string
  href?: string
  metadata?: Record<string, unknown>
  createdAt: string
}

type NotificationType =
  | 'contract_approved'
  | 'contract_rejected'
  | 'contract_submitted'
  | 'issue_detected'
  | 'issue_assigned'
  | 'issue_resolved'
  | 'sla_breach'
  | 'schema_drift'
  | 'comment_added'
  | 'task_assigned'
```

### Search Result Types
```typescript
interface SearchResult {
  id: string
  type: 'contract' | 'asset' | 'issue' | 'team' | 'user'
  title: string
  subtitle: string
  description?: string
  href: string
  icon: string
  status?: string
  metadata?: Record<string, unknown>
  score: number
  highlights?: Array<{ field: string; snippet: string }>
}

interface GlobalSearchResults {
  query: string
  results: {
    contracts: { items: SearchResult[]; total: number; hasMore: boolean }
    assets: { items: SearchResult[]; total: number; hasMore: boolean }
    issues: { items: SearchResult[]; total: number; hasMore: boolean }
    teams: { items: SearchResult[]; total: number; hasMore: boolean }
    users: { items: SearchResult[]; total: number; hasMore: boolean }
  }
  quickActions: Array<{
    id: string
    title: string
    subtitle: string
    href: string
    icon: string
  }>
  totalResults: number
  searchTimeMs: number
}
```

---

## API Endpoints

### Authentication Endpoints
| Method | Endpoint | Description | Request File |
|--------|----------|-------------|--------------|
| POST | `/api/v1/auth/login` | Login with email/password | REQ-registry-014 |
| POST | `/api/v1/auth/signup` | Register new user | REQ-registry-015 |
| POST | `/api/v1/auth/logout` | Logout current user | REQ-registry-016 |
| GET | `/api/v1/auth/me` | Get current user profile | REQ-registry-017 |
| POST | `/api/v1/auth/forgot-password` | Request password reset | REQ-registry-018 |
| POST | `/api/v1/auth/reset-password` | Reset password with token | REQ-registry-019 |
| POST | `/api/v1/auth/oauth/google` | Google OAuth | Spec only |
| POST | `/api/v1/auth/oauth/microsoft` | Microsoft OAuth | Spec only |
| POST | `/api/v1/auth/oauth/sso` | Enterprise SSO | Spec only |

### Tasks Endpoints
| Method | Endpoint | Description | Request File |
|--------|----------|-------------|--------------|
| GET | `/api/v1/tasks` | Get user's tasks (auth, comments, drafts, reapprovals) | REQ-registry-013 |

### Issues Endpoints
| Method | Endpoint | Description | Request File |
|--------|----------|-------------|--------------|
| GET | `/api/v1/issues` | List issues with filters and pagination | REQ-registry-006 |
| GET | `/api/v1/issues/{id}` | Get issue detail with activity | REQ-registry-007 |
| PATCH | `/api/v1/issues/{id}` | Update issue status/assignment | REQ-registry-008 |

### Notification Endpoints
| Method | Endpoint | Description | Request File |
|--------|----------|-------------|--------------|
| GET | `/api/v1/notifications` | Get user notifications | REQ-registry-009 |
| PATCH | `/api/v1/notifications/{id}/read` | Mark notification as read | REQ-registry-010 |
| POST | `/api/v1/notifications/read-all` | Mark all as read | REQ-registry-011 |

### Search Endpoint
| Method | Endpoint | Description | Request File |
|--------|----------|-------------|--------------|
| GET | `/api/v1/search?q=` | Global search | REQ-registry-012 |

### Admin Endpoints (Implemented by Design Agent)
| Method | Endpoint | Description | Spec |
|--------|----------|-------------|------|
| GET | `/api/users` | List users | auth-admin-api.yaml |
| POST | `/api/users` | Create/invite user | auth-admin-api.yaml |
| PATCH | `/api/users/{id}` | Update user | auth-admin-api.yaml |
| DELETE | `/api/users/{id}` | Deactivate user | auth-admin-api.yaml |
| GET | `/api/teams` | List teams | auth-admin-api.yaml |
| POST | `/api/teams` | Create team | auth-admin-api.yaml |
| GET | `/api/teams/{id}` | Get team detail | auth-admin-api.yaml |
| PATCH | `/api/teams/{id}` | Update team | auth-admin-api.yaml |
| DELETE | `/api/teams/{id}` | Delete team | auth-admin-api.yaml |
| POST | `/api/teams/{id}/members` | Add member | auth-admin-api.yaml |
| PATCH | `/api/teams/{id}/members/{memberId}` | Update member role | auth-admin-api.yaml |
| DELETE | `/api/teams/{id}/members/{memberId}` | Remove member | auth-admin-api.yaml |
| GET | `/api/roles` | List roles | auth-admin-api.yaml |
| POST | `/api/roles` | Create role | auth-admin-api.yaml |
| GET | `/api/roles/{id}` | Get role detail | auth-admin-api.yaml |
| PATCH | `/api/roles/{id}` | Update role | auth-admin-api.yaml |
| DELETE | `/api/roles/{id}` | Delete role | auth-admin-api.yaml |
| GET | `/api/permissions` | List permissions | auth-admin-api.yaml |

---

## UX Requirements

| Requirement | Implementation |
|-------------|----------------|
| Task counts | Badge counts in tabs, updated in real-time |
| Approval workflow | One-click approve with confirmation dialog |
| Issue severity | Visual distinction (red=critical, yellow=warning, blue=info) |
| Global search | Cmd+K shortcut, debounced 300ms, instant results |
| Notifications | Polling every 30s, unread count indicator |
| Keyboard navigation | Arrow keys in search, Escape to close modals |
| Loading states | Skeleton loaders on all data fetches |
| Empty states | Helpful messages with CTAs |
| Error handling | Toast notifications with retry options |

---

## Feature Details

### My Tasks Page
**Four Tabs:**
1. **Pending Authorizations** - Contracts awaiting approval
   - Approve/Request Changes buttons
   - Domain and priority badges
   - Requested by (avatar + name) and time ago
   - Change summary preview

2. **Comments to Review** - Comments needing response
   - Comment content preview (truncated)
   - Type badge (question/suggestion/concern)
   - Author info and timestamp
   - Link to contract with anchor

3. **My Drafts** - Incomplete contracts/assets
   - Completion percentage progress bar
   - Continue Editing / Delete buttons
   - Last edited timestamp
   - Type indicator (contract/asset)

4. **Re-approvals** - Schema changes on approved contracts
   - Schema diff summary
   - Change reason from editor
   - Previous vs current version
   - Approve/Reject actions

### Issues List Page
- Severity tabs: All, Critical, Warning, Info, Resolved (with counts from summary)
- Search by title, description, contract name
- Filters: Category, Contract, Assigned Team, Date Range
- Export to CSV button
- DataTable with sortable columns: Title, Severity, Category, Contract, Detected, Status, Assigned

### Issue Detail Page
- Issue header with severity badge and status
- Description card with full text
- Location info (contract, table, field)
- Quality rule that triggered the issue
- Assignment section (team dropdown, user dropdown)
- Resolution form with:
  - Status dropdown (open, in_progress, resolved, ignored)
  - Resolution type (when resolving): fixed, wont_fix, false_positive, deferred
  - Resolution notes textarea
- Activity timeline (chronological events and comments)
- Comments section with add comment form

### Admin Overview
- Metric cards: Total Users, Active Users, Teams, Roles
- Recent activity feed (last 10 actions)
- Quick action buttons: Invite User, Create Team, Manage Roles
- Navigation cards to sub-pages

### User Management
- Users table with search and filters
- Columns: User (avatar + name + email), Role (badge), Team, Status (badge), Last Login
- Actions dropdown: View Profile, Change Role, Reset Password, Deactivate
- Invite User modal with email, role selector, team selector
- Bulk actions: Bulk invite via CSV (future)

### Team Management
- Teams grid/table with search
- Team card shows: Name, Description, Member count, Domain badges, Asset/Contract counts
- Create Team modal with name, description, default role
- Team detail page with:
  - Team info header with edit button
  - Members table with role badges
  - Add Member modal (search users, assign role)
  - Remove member confirmation

### Roles & Permissions
- Roles list showing: Name, Description, Permission count, User count, System badge
- Create Role modal with:
  - Name and description
  - Permissions grouped by category with checkboxes
- Edit Role (disabled for system roles)
- Permissions matrix view

### Global Search (Cmd+K)
- Opens modal on Cmd+K / Ctrl+K
- Search input with clear button
- Debounced search (300ms)
- Results grouped by type with icons
- Keyboard navigation (up/down arrows, Enter to select)
- Recent searches (localStorage)
- Quick actions: Create Contract, Create Asset, etc.

### Notifications Dropdown
- Bell icon in TopNav
- Unread count badge (red dot with number)
- Dropdown with scrollable list (max 10 visible)
- Each notification: type icon, title, description, time ago
- Click navigates to href and marks as read
- Mark all as read button
- Link to notification settings

---

## Dependencies

### Provides To Other Agents
- Issue data for dashboard metrics (Dashboards-Reports Agent)
- User/Team data for asset/contract ownership (Schema, Contracts Agents)
- Notification system for all status changes
- Search functionality for global navigation
- Task data for contract workflow (Contracts Agent)

### Depends On
- **Design Agent**: UI components (DataTable, Toast, Dialog, Dropdown, Badge, Avatar)
- **Contracts Agent**: Contract data for authorizations and issue linking
- **Design Agent**: API client, mock infrastructure, auth context

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
| Team detail | `src/app/admin/teams/[teamId]/page.tsx` |
| Roles management | `src/app/admin/roles/page.tsx` |
| Settings hub | `src/app/settings/page.tsx` |
| Profile settings | `src/app/settings/profile/page.tsx` |
| Notification prefs | `src/app/settings/notifications/page.tsx` |
| Integrations | `src/app/settings/integrations/page.tsx` |
| Global search | `src/components/layout/GlobalSearch.tsx` |
| Notifications | `src/components/layout/NotificationDropdown.tsx` |
| Mock handlers | `src/lib/mocks/handlers/*.ts` |
| Types | `src/types/index.ts` |

### OpenAPI Specs
| Spec | Path | Contents |
|------|------|----------|
| Auth & Admin | `agents/specs/auth-admin-api.yaml` | Authentication, Users, Teams, Roles |
| Contracts | `agents/specs/contracts.yaml` | Contract workflow, Tasks, Quality Rules |

### Registry Requests
| Request | Path | Description |
|---------|------|-------------|
| REQ-registry-006 | `agents/status/requests/REQ-registry-006.md` | Issues List |
| REQ-registry-007 | `agents/status/requests/REQ-registry-007.md` | Issue Detail |
| REQ-registry-008 | `agents/status/requests/REQ-registry-008.md` | Issue Update |
| REQ-registry-009 | `agents/status/requests/REQ-registry-009.md` | Notifications List |
| REQ-registry-010 | `agents/status/requests/REQ-registry-010.md` | Mark Notification Read |
| REQ-registry-011 | `agents/status/requests/REQ-registry-011.md` | Mark All Read |
| REQ-registry-012 | `agents/status/requests/REQ-registry-012.md` | Global Search |
| REQ-registry-013 | `agents/status/requests/REQ-registry-013.md` | User Tasks |
| REQ-registry-014 | `agents/status/requests/REQ-registry-014.md` | User Login |
| REQ-registry-015 | `agents/status/requests/REQ-registry-015.md` | User Signup |
| REQ-registry-016 | `agents/status/requests/REQ-registry-016.md` | User Logout |
| REQ-registry-017 | `agents/status/requests/REQ-registry-017.md` | Get Current User |
| REQ-registry-018 | `agents/status/requests/REQ-registry-018.md` | Forgot Password |
| REQ-registry-019 | `agents/status/requests/REQ-registry-019.md` | Reset Password |
