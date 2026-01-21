# Griot-Hub Implementation Status Board

> **Last Updated:** 2026-01-21 by orchestrator
> **Project:** griot-hub (Next.js Frontend)
> **Current Phase:** Phase 2 - Authentication, Admin & User Management + Contract Fixes

---

## Project Overview

Griot-Hub is the Next.js frontend for the Enterprise Data Contract Management System. Phase 1 (feature build with mocks) is complete. Phase 2 focuses on authentication, admin functionality, user management, and critical contract functionality fixes.

---

## Agent Assignments

| Agent | Alias | Primary Responsibility |
|-------|-------|----------------------|
| **design** | Design System Agent | UI components, theming, layout, API infrastructure |
| **schema** | Schema Agent | Data Assets, Database Connections |
| **contracts** | Contracts Agent | Data Contracts, Quality Rules, Wizards |
| **dashboards** | Dashboards-Reports Agent | Dashboard, Reports, Marketplace |
| **platform** | Platform Agent | Tasks, Issues, Admin, Settings, Global features |
| **qa** | QA Agent | Testing, Visual regression, Polish |
| **orchestrator** | Orchestrator | Coordination, task assignment, integration |

---

## Phase 2 - Authentication & Admin (ACTIVE)

### Design Agent Tasks (COMPLETED)

| Task ID | Task | Status | Dependencies |
|---------|------|--------|--------------|
| T-DES-001 | Design Login & Signup UI/UX | ✅ Done | None |
| T-DES-002 | Design Admin Dashboard & User Management UI | ✅ Done | None |
| T-DES-003 | Design Team & Role Management UI | ✅ Done | None |
| T-DES-004 | Create OpenAPI Spec for Auth & Admin endpoints | ✅ Done | T-DES-001, T-DES-002, T-DES-003 |
| T-DES-005 | Implement Next.js API Routes for Auth & Admin | ✅ Done | T-DES-004 |
| T-DES-006 | Implement Authentication Flow | ✅ Done | T-DES-004, T-DES-005 |
| T-DES-007 | Implement Admin Pages with Role-Based Access | ✅ Done | T-DES-006 |
| T-DES-008 | Implement Team & Role Management | ✅ Done | T-DES-007 |
| T-DES-009 | E2E Testing with Playwright | 🔜 Backlog | T-DES-006, T-DES-007, T-DES-008 |
| T-DES-010 | UI Polish & Three-Click Navigation Audit | ✅ Done | T-DES-009 |

---

## Phase 2 - Contract Fixes (ACTIVE)

### Contracts Agent Tasks (HIGH PRIORITY)

| Task ID | Task | Status | Dependencies |
|---------|------|--------|--------------|
| T-CON-001 | Fix Edit Contract Bug (race condition) | 📋 Ready | None |
| T-CON-002 | Add Reviewer Field to Wizard Step 1 | 📋 Ready | None |
| T-CON-003 | Implement Contract Status Workflow | 📋 Ready | T-CON-002 |
| T-CON-004 | Enhance Contract Detail Page | 📋 Ready | None |
| T-CON-005 | Quality Rules at Schema/Property Level | ⏳ Blocked | T-CON-004 |
| T-CON-006 | Privacy Information Display | ⏳ Blocked | T-CON-004 |
| T-CON-007 | E2E Testing for Contracts | ⏳ Blocked | T-CON-001, T-CON-003, T-CON-004, T-CON-010 |
| T-CON-008 | Schema Editing for Draft/Pending Contracts | 📋 Ready | T-CON-001 |
| T-CON-009 | Schema Change Re-approval Workflow | 📋 Ready | T-CON-003, T-CON-008 |
| T-CON-010 | Schema Edit Restrictions by Status | 📋 Ready | T-CON-008 |

---

## Task Details

> **IMPORTANT:** All tasks require **working code implementation**, not wireframes or documentation.
> You must build actual React components and pages that render and are interactive.
> Use MSW mocks so the UI feels fully functional when clicking around.

### T-DES-001: Build Login & Signup Pages

**Objective:** Build fully functional authentication pages with working forms and navigation.

**Build These Pages:**

1. **Login Page** (`/login`) - `src/app/login/page.tsx`
   - Email input field with validation
   - Password input field with show/hide toggle
   - "Remember me" checkbox
   - "Forgot password?" link (navigates to `/forgot-password`)
   - Primary login button (calls mock API, redirects to `/` on success)
   - Divider with "OR" text
   - OAuth buttons: Google, Microsoft, SSO (show toast "Coming soon" or mock login)
   - "Don't have an account? Sign up" link

2. **Signup Page** (`/signup`) - `src/app/signup/page.tsx`
   - Full name input
   - Email input with validation
   - Password input with strength indicator (weak/medium/strong)
   - Confirm password input (must match)
   - Terms & conditions checkbox
   - Primary signup button (calls mock API, redirects to `/` on success)
   - Divider with "OR"
   - OAuth buttons: Google, Microsoft
   - "Already have an account? Log in" link

3. **Forgot Password Page** (`/forgot-password`) - `src/app/forgot-password/page.tsx`
   - Email input
   - "Send Reset Link" button (shows success toast)
   - "Back to login" link

4. **Reset Password Page** (`/reset-password`) - `src/app/reset-password/page.tsx`
   - New password input with strength indicator
   - Confirm password input
   - "Reset Password" button (shows success, redirects to login)

**Functional Requirements:**
- Forms validate on submit AND on blur
- Show inline error messages under invalid fields
- Buttons show loading spinner when submitting
- Toast notifications for success/error
- After successful login/signup, redirect to dashboard
- Store auth token in localStorage (mock JWT)
- Update AuthProvider with logged-in user
- TopNav shows user name and avatar when logged in

**Deliverable:** Working pages you can click through and test

---

### T-DES-002: Build Admin Dashboard & User Management Pages

**Objective:** Build fully functional admin pages with role-based visibility.

**Build/Update These:**

1. **Update Sidebar** (`src/components/layout/Sidebar.tsx`)
   - Add role check from AuthContext
   - Only show Admin nav link if `user.role.name === 'Admin'`
   - Non-admins should NOT see the admin section at all

2. **Admin Dashboard** (`/admin`) - `src/app/admin/page.tsx`
   - Clean card grid layout (2x2 or responsive)
   - Metric cards: Total Users, Active Users, Teams, Pending Invites
   - Each card is clickable, navigates to relevant page
   - Quick action buttons: "Invite User", "Create Team", "Manage Roles"
   - Recent activity list (last 5-10 items, well-formatted with timestamps)

3. **User Management** (`/admin/users`) - `src/app/admin/users/page.tsx`
   - Page header with "Invite User" button
   - Search input (filters table in real-time)
   - Filter dropdowns: Role, Team, Status
   - DataTable with columns:
     - User (avatar + name + email stacked)
     - Role (badge)
     - Team name
     - Status (badge: active/pending/deactivated)
     - Actions (dropdown: Edit, Change Role, Deactivate)
   - "Change Role" opens dialog with role selector
   - "Invite User" opens modal with email, role, team fields

4. **Hardcoded Admin User** (in mock data)
   ```typescript
   {
     id: 'user-admin-001',
     email: 'brackly@griot.com',
     name: 'Brackly Murunga',
     role: { id: 'role-admin', name: 'Admin' },
     status: 'active'
   }
   ```
   Password `melly` checked in auth mock handler.

5. **Role Assignment Flow**
   - Click "Change Role" in actions dropdown
   - Dialog opens with current role shown
   - Select new role from dropdown (Viewer, Editor, Admin)
   - Confirm button updates user (mock API call)
   - Toast shows "Role updated successfully"
   - Table refreshes to show new role

**Deliverable:** Working admin pages where you can manage users and see role-based sidebar

---

### T-DES-003: Build Team & Role Management Pages

**Objective:** Build fully functional team and role management with permission system.

**Build These Pages:**

1. **Team Management** (`/admin/teams`) - `src/app/admin/teams/page.tsx`
   - Page header with "Create Team" button
   - Search input
   - Grid of team cards OR DataTable (your choice)
   - Each team shows: Name, Description, Member count, Default role badge
   - Click team card/row navigates to team detail

2. **Create Team Modal** (triggered from teams page)
   - Team name input (required)
   - Description textarea
   - Default role dropdown (Viewer, Editor, Admin)
   - "Create Team" button (calls mock API, closes modal, refreshes list)

3. **Team Detail Page** (`/admin/teams/[teamId]`) - `src/app/admin/teams/[teamId]/page.tsx`
   - Header: Team name, description, edit button
   - "Default Role" badge with change button
   - "Add Member" button opens user selector modal
   - Members DataTable:
     - User (avatar + name + email)
     - Role (shows "Inherited" badge if from team, or explicit role)
     - Joined date
     - Actions: Change Role, Remove from Team
   - Remove member shows confirmation dialog

4. **Roles & Permissions** (`/admin/roles`) - `src/app/admin/roles/page.tsx`
   - Page header with "Create Role" button
   - Roles displayed as cards or list:
     - Role name
     - Description
     - Permission count badge (e.g., "12 permissions")
     - "System" badge for built-in roles (Admin, Editor, Viewer)
     - Edit button (disabled for system roles)
   - Click opens edit modal

5. **Create/Edit Role Modal**
   - Role name input
   - Description textarea
   - Permissions grouped by category with checkboxes:
     ```
     Contracts
     ☑ View contracts
     ☑ Create contracts
     ☐ Edit contracts
     ☐ Delete contracts
     ☐ Approve contracts

     Assets
     ☑ View assets
     ☐ Create assets
     ...

     Admin
     ☐ View users
     ☐ Manage users
     ☐ Manage teams
     ☐ Manage roles
     ```
   - "Save Role" button

6. **Permission Cascade** (in mock logic)
   - When user is added to team, they inherit team's default role
   - Show "Inherited from team" indicator on user's role
   - Allow explicit role override per user

**Deliverable:** Working team and role management where you can create teams, add members, and configure permissions

---

### T-DES-004: Create OpenAPI Spec for Auth & Admin Endpoints

**Objective:** Document all API endpoints as OpenAPI 3.0 spec.

**Location:** `agents/specs/auth-admin-api.yaml`

**Endpoints Required:**

**Authentication:**
- `POST /api/auth/login` - Email/password login
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/logout` - Logout current user
- `GET /api/auth/me` - Get current user
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password with token
- `POST /api/auth/oauth/google` - Google OAuth callback
- `POST /api/auth/oauth/microsoft` - Microsoft OAuth callback
- `POST /api/auth/oauth/sso` - Enterprise SSO callback

**Users:**
- `GET /api/users` - List all users (admin only)
- `GET /api/users/:id` - Get user by ID
- `POST /api/users/invite` - Invite new user
- `PATCH /api/users/:id` - Update user
- `PATCH /api/users/:id/role` - Change user role
- `DELETE /api/users/:id` - Deactivate user

**Teams:**
- `GET /api/teams` - List all teams
- `POST /api/teams` - Create team
- `GET /api/teams/:id` - Get team details
- `PATCH /api/teams/:id` - Update team
- `DELETE /api/teams/:id` - Delete team
- `POST /api/teams/:id/members` - Add member to team
- `DELETE /api/teams/:id/members/:userId` - Remove member

**Roles:**
- `GET /api/roles` - List all roles
- `POST /api/roles` - Create role (admin only)
- `GET /api/roles/:id` - Get role details
- `PATCH /api/roles/:id` - Update role
- `DELETE /api/roles/:id` - Delete role
- `GET /api/permissions` - List all permissions

**Deliverables:**
- Complete OpenAPI 3.0 YAML specification
- Request/response schemas
- Error response definitions
- Authentication headers documentation

---

### T-DES-005: Implement MSW Mocks for Auth & Admin APIs

**Objective:** Create mock handlers matching the OpenAPI spec.

**Requirements:**
- All endpoints from OpenAPI spec mocked
- Realistic response data
- Proper error responses (401, 403, 404, 422)
- Hardcoded admin user (`brackly@griot.com` / `melly`)
- JWT token simulation in localStorage
- Token validation in protected routes

**Files:**
- `src/lib/mocks/handlers/auth.ts`
- `src/lib/mocks/handlers/users.ts`
- `src/lib/mocks/handlers/teams.ts`
- `src/lib/mocks/handlers/roles.ts`
- `src/lib/mocks/data/auth.ts`
- `src/lib/mocks/data/users.ts`
- `src/lib/mocks/data/roles.ts`

---

### T-DES-006: Implement Authentication Flow

**Objective:** Build working auth with mock backend.

**Requirements:**
- Login page with form validation
- Signup page with password strength
- OAuth buttons (mock flow for now)
- Auth context with user state
- Protected route wrapper
- Redirect unauthenticated users to login
- Display user name/avatar in TopNav
- Logout functionality

---

### T-DES-007: Implement Admin Pages with Role-Based Access

**Objective:** Build admin pages with proper access control.

**Requirements:**
- Admin sidebar link visibility based on role
- Admin dashboard with metrics
- User management with role assignment
- Permission checks on actions
- Clean, consistent layout

---

### T-DES-008: Implement Team & Role Management

**Objective:** Build team and role CRUD functionality.

**Requirements:**
- Team list and creation
- Team detail with member management
- Role list and creation
- Permission matrix editor
- Role cascade to team members

---

### T-DES-009: E2E Testing with Playwright

**Objective:** Comprehensive test coverage for auth and admin.

**Test Scenarios:**
1. **Authentication:**
   - Login with valid credentials
   - Login with invalid credentials
   - Signup new user
   - Forgot password flow
   - Logout

2. **Admin Access:**
   - Admin can see admin sidebar
   - Non-admin cannot see admin sidebar
   - Admin can access admin pages
   - Non-admin gets redirected from admin pages

3. **User Management:**
   - List users
   - Change user role
   - Invite new user

4. **Team Management:**
   - Create team
   - Add member to team
   - Remove member from team

5. **Role Management:**
   - View roles
   - Create custom role
   - Edit role permissions

---

### T-DES-010: UI Polish & Three-Click Navigation Audit

**Objective:** Ensure beautiful UI and efficient navigation.

**Requirements:**
1. **Three-Click Rule Audit:**
   - Map all pages and count clicks from dashboard
   - No page should require more than 3 clicks
   - Document navigation paths

2. **UI Polish:**
   - Consistent spacing (4px/8px grid)
   - Proper padding on all cards/sections
   - Aligned form labels and inputs
   - Consistent button sizes
   - Loading states everywhere
   - Empty states with CTAs
   - Error states with recovery options

3. **Layout Fixes:**
   - Admin dashboard card alignment
   - User table column widths
   - Modal sizing consistency
   - Responsive breakpoints

**Deliverables:**
- Navigation map with click counts
- List of UI fixes applied
- Screenshot comparisons before/after

---

## Contracts Agent Task Details

> **IMPORTANT:** All tasks require **working code implementation**, not wireframes or documentation.
> API is deployed at `http://localhost:8000/api/v1/` - see `agents/specs/registry.yaml` for details.
> Use real API calls, not MSW mocks.

### T-CON-001: Fix Edit Contract Bug (CRITICAL)

**Objective:** Fix the "Original contract data not available" error when saving edits.

**Problem Description:**
- File: `src/app/studio/contracts/[contractId]/edit/page.tsx`
- Error occurs at lines 100-101 when `originalOdcsContract` is null
- Root cause: Race condition between React Query completion and state synchronization
- The `setOriginalOdcsContract(response)` is called in the queryFn, but the state update is asynchronous
- When user clicks "Save Changes", `originalOdcsContract` may still be null

**Technical Fix:**
1. Option A (Recommended): Use a ref instead of state for `originalOdcsContract`
   - Refs update synchronously
   - Change `useState` to `useRef`
   - Update the ref in queryFn: `originalOdcsContractRef.current = response`

2. Option B: Disable save button until `originalOdcsContract` is set
   - Add a check: `disabled={!originalOdcsContract || updateMutation.isPending}`
   - This ensures user can't submit before data is ready

3. Option C: Use queryClient.getQueryData() in mutation
   - Instead of storing in state, fetch from cache when needed
   - `const cachedData = queryClient.getQueryData<RegistryContractResponse>(queryKeys.contracts.detail(contractId))`

**Files to Modify:**
- `src/app/studio/contracts/[contractId]/edit/page.tsx`

**Acceptance Criteria:**
- [ ] User can click Edit on any contract
- [ ] Edit form loads with current contract data
- [ ] User can modify fields and click Save
- [ ] Contract updates successfully without errors
- [ ] Toast shows "Contract updated"
- [ ] User is redirected to detail page

**Deliverable:** Working edit functionality with no race condition errors

---

### T-CON-002: Add Reviewer Field to Wizard Step 1

**Objective:** Add a reviewer assignment field (user or team dropdown) to the contract creation wizard.

**Requirements:**
1. **Add Reviewer Field to Step 1** (`src/components/contracts/wizard/Step1BasicInfo.tsx`)
   - Add "Reviewer" field after the Status field
   - Two-part selector:
     - Type: Dropdown to select "User" or "Team"
     - Value: Searchable dropdown with users or teams based on type selection
   - Optional field (not required)
   - When type is "User", show user dropdown (fetch from `/api/users`)
   - When type is "Team", show team dropdown (fetch from `/api/teams`)

2. **Update ContractFormData Type**
   - Add `reviewerType?: 'user' | 'team'`
   - Add `reviewerId?: string`
   - Add `reviewerName?: string` (for display)

3. **Update Wizard Page** (`src/app/studio/contracts/new/wizard/page.tsx`)
   - Include reviewer data in form state
   - Pass reviewer to API when creating contract

4. **Update Create Contract API Call**
   - Include `reviewer_id` and `reviewer_type` in POST payload

**UI Design:**
```
Reviewer (Optional)
┌─────────────────────────────────────────┐
│ [User ▼]  │  [Select user...        ▼] │
└─────────────────────────────────────────┘
   Type         Searchable dropdown
```

**Files to Modify:**
- `src/components/contracts/wizard/Step1BasicInfo.tsx`
- `src/app/studio/contracts/new/wizard/page.tsx`
- `src/types/index.ts` (if ContractFormData is defined there)

**Acceptance Criteria:**
- [ ] Reviewer field appears in Step 1 of wizard
- [ ] User can select "User" or "Team" as reviewer type
- [ ] Dropdown shows available users or teams based on selection
- [ ] Reviewer is optional - can proceed without selecting
- [ ] Selected reviewer is included when contract is created

**Deliverable:** Working reviewer selection in contract creation wizard

---

### T-CON-003: Implement Contract Status Workflow

**Objective:** Implement the full contract status workflow with reviewer approval.

**Status Flow:**
```
draft → pending_review → active
                       ↓
                    rejected (back to draft)

active → deprecated
```

**Requirements:**

1. **Submit for Review** (from detail page)
   - Add "Submit for Review" button on draft contracts
   - Button opens confirmation dialog
   - On confirm: PATCH `/contracts/{id}` with `status: 'pending_review'`
   - Toast: "Contract submitted for review"
   - Only owner/creator can submit

2. **Review Actions** (for reviewer on pending_review contracts)
   - Show "Approve" and "Request Changes" buttons
   - Only visible to assigned reviewer OR admins
   - **Approve**: PATCH with `status: 'active'`, shows success toast
   - **Request Changes**: Opens dialog with text field for feedback
     - On submit: PATCH with `status: 'draft'` and `review_feedback`
     - Toast: "Changes requested"

3. **Deprecate** (for active contracts)
   - Add "Deprecate" button on active contracts
   - Opens confirmation dialog with reason field
   - On confirm: PATCH with `status: 'deprecated'`
   - Only owner or admin can deprecate

4. **Visual Status Indicators**
   - Show reviewer name on pending_review contracts
   - Show "Awaiting your review" badge if current user is reviewer
   - Show review feedback on rejected contracts
   - Disable edit for pending_review contracts (frozen during review)

**Files to Modify:**
- `src/app/studio/contracts/[contractId]/page.tsx` - Add status action buttons
- `src/components/contracts/ContractHeader.tsx` - If exists, update header actions
- Create: `src/components/contracts/ReviewDialog.tsx` - For request changes dialog
- Create: `src/components/contracts/StatusActionButton.tsx` - Reusable status action component

**API Endpoints:**
- PATCH `/contracts/{id}` with body: `{ status: 'pending_review' | 'active' | 'draft' | 'deprecated', review_feedback?: string }`

**Acceptance Criteria:**
- [ ] Draft contracts show "Submit for Review" button
- [ ] Pending contracts show reviewer info and "Approve"/"Request Changes" for reviewer
- [ ] Active contracts show "Deprecate" button for owner/admin
- [ ] Status changes update immediately after action
- [ ] Review feedback is shown when contract is sent back to draft
- [ ] All actions have confirmation dialogs

**Deliverable:** Working status workflow with reviewer approval flow

---

### T-CON-004: Enhance Contract Detail Page

**Objective:** Show complete contract details including all metadata, quality rules, and privacy information.

**Requirements:**

1. **Ownership & Governance Section** (new card in right column)
   - Owner team (link to team page)
   - Owner user (avatar + name)
   - Reviewer (if assigned)
   - Approver (if active, who approved it)
   - Created by / Updated by

2. **Enhanced Quality Rules Display**
   - Group rules by type (Completeness, Uniqueness, Validity, Custom)
   - Show threshold values with progress indicators
   - Show last run result per rule (passed/failed/pending)
   - Expandable rule details with expression/config

3. **Privacy Information Section** (new card)
   - Show PII field summary: count of PII fields by category
   - List all PII fields with their categories
   - Privacy classification badge (High/Medium/Low based on PII presence)
   - Link to data classification policy (placeholder)

4. **Schema Enhancement**
   - Show PII badge next to fields with PII classification
   - Show field-level quality rules inline
   - Expandable field details (description, constraints)

5. **Version History** (new card in right column)
   - Show last 5 version changes
   - Each shows: version number, change type (patch/minor/major), date, author
   - "View all" link to version history page (placeholder)

**Files to Modify:**
- `src/app/studio/contracts/[contractId]/page.tsx`
- `src/lib/api/adapters.ts` - Ensure quality rules and PII info are adapted

**Data Source:**
Quality rules come from the registry API. The adapter currently sets `qualityRules: []`.
Need to check if quality rules are in the contract response or need separate API call.

**Acceptance Criteria:**
- [ ] Contract detail shows owner team and user
- [ ] Quality rules are grouped and show thresholds
- [ ] PII fields are highlighted in schema view
- [ ] Privacy summary shows PII field counts
- [ ] Version history shows recent changes

**Deliverable:** Comprehensive contract detail page with all governance information

---

### T-CON-005: Quality Rules at Schema/Property Level

**Objective:** Display quality rules associated with specific schema tables and fields.

**Requirements:**

1. **Table-Level Rules**
   - Show rules that apply to entire table (e.g., row count checks)
   - Display as badges or list under table header
   - Indicate rule status from last run

2. **Field-Level Rules**
   - Show rules that apply to specific fields
   - Display inline with field in schema view
   - Types: completeness (null %), uniqueness, format/validity
   - Show threshold and last result

3. **Rule Indicators**
   - Icon badge showing number of rules per field
   - Click to expand rule details
   - Color coding: green (all passing), yellow (warnings), red (failures)

**Files to Modify:**
- `src/app/studio/contracts/[contractId]/page.tsx` - Schema section
- Create: `src/components/contracts/FieldRuleBadge.tsx`
- Create: `src/components/contracts/TableRulesSummary.tsx`

**Acceptance Criteria:**
- [ ] Schema shows rule count badges on fields with rules
- [ ] Clicking badge expands rule details
- [ ] Rules show threshold and last result
- [ ] Visual indication of passing/failing rules

**Deliverable:** Quality rules integrated into schema display

---

### T-CON-006: Privacy Information Display

**Objective:** Display comprehensive privacy and PII information on contracts.

**Requirements:**

1. **PII Summary Card**
   - Total PII fields count
   - Breakdown by category (Personal, Financial, Health, etc.)
   - Overall privacy classification (High/Medium/Low/None)

2. **PII Field List**
   - Table of all PII fields
   - Columns: Field Name, Table, PII Category, Handling Requirements
   - Sortable and filterable

3. **Schema Integration**
   - Badge on fields: "PII: Personal", "PII: Financial", etc.
   - Different badge colors per category
   - Tooltip with handling requirements

4. **Privacy Policy Link**
   - Link to organization's data classification policy
   - Placeholder URL for now

**PII Categories (from ODCS standard):**
- `personal` - Name, email, phone, address
- `financial` - Account numbers, transactions
- `health` - Medical records
- `sensitive` - SSN, passport, etc.
- `behavioral` - Usage patterns, preferences

**Files to Create:**
- `src/components/contracts/PIISummaryCard.tsx`
- `src/components/contracts/PIIFieldBadge.tsx`

**Files to Modify:**
- `src/app/studio/contracts/[contractId]/page.tsx`

**Acceptance Criteria:**
- [ ] PII summary card shows on detail page
- [ ] All PII fields are listed with categories
- [ ] Schema fields show PII badges
- [ ] Privacy classification is calculated and displayed

**Deliverable:** Complete privacy information visibility

---

### T-CON-007: E2E Testing for Contracts

**Objective:** Comprehensive Playwright tests for all contract functionality.

**Test Scenarios:**

1. **Contract List**
   - List loads with contracts
   - Status tabs filter correctly
   - Search filters by name
   - Click navigates to detail

2. **Contract Detail**
   - Detail page loads correctly
   - Schema displays with fields
   - Quality rules section shows
   - PII information displays
   - Edit button navigates to edit page
   - Status actions work (submit, approve, etc.)

3. **Contract Edit**
   - Edit page loads with current data
   - Form fields are editable
   - Save updates contract (no errors!)
   - Cancel returns to detail
   - Validation errors show correctly

4. **Contract Create (Wizard)**
   - All 4 steps complete successfully
   - Reviewer field works
   - Contract is created
   - Redirects to detail page

5. **Status Workflow**
   - Submit for review works
   - Approve works (as reviewer)
   - Request changes works
   - Deprecate works

6. **Schema Editing**
   - Draft contract allows schema editing
   - Pending_review contract allows editing with warning
   - Active contract shows re-approval confirmation
   - Active contract schema change creates task
   - Retired contract schema is read-only
   - Deprecated contract schema is read-only
   - Can add/edit/remove tables and fields

**Test Files:**
- `tests/e2e/contracts/list.spec.ts`
- `tests/e2e/contracts/detail.spec.ts`
- `tests/e2e/contracts/edit.spec.ts`
- `tests/e2e/contracts/wizard.spec.ts`
- `tests/e2e/contracts/workflow.spec.ts`
- `tests/e2e/contracts/schema-editing.spec.ts`

**Acceptance Criteria:**
- [ ] All contract list tests pass
- [ ] All contract detail tests pass
- [ ] All contract edit tests pass
- [ ] All contract wizard tests pass
- [ ] All workflow tests pass
- [ ] All schema editing tests pass

**Deliverable:** Complete E2E test coverage for contracts

---

### T-CON-008: Schema Editing for Draft/Pending Contracts

**Objective:** Enable schema editing on the contract edit page for contracts in `draft` or `pending_review` status.

**Current State:**
- Edit page (`src/app/studio/contracts/[contractId]/edit/page.tsx`) shows schema as read-only
- Message says "Schema is read-only. To modify schema, re-sync from the linked data asset."
- No ability to add/edit/remove tables or fields

**Requirements:**

1. **Enable Schema Editing for Draft Contracts**
   - Add "Edit Schema" button that opens schema editor
   - Allow adding new tables
   - Allow editing existing tables (name, description)
   - Allow adding/editing/removing fields
   - Field properties: name, type, required, primaryKey, piiCategory, description

2. **Enable Schema Editing for Pending Review Contracts**
   - Same editing capabilities as draft
   - Show warning: "Editing schema will require re-review"
   - When schema is changed on pending_review contract:
     - Keep status as `pending_review`
     - Add note that schema was modified since submission
     - Notify reviewer of schema changes

3. **Schema Editor Component**
   - Reuse wizard Step3Schema component OR create dedicated editor
   - Inline editing in the edit page
   - Real-time validation (field names unique, types valid)
   - Save button updates contract with new schema

**UI Design:**
```
Schema
┌────────────────────────────────────────────────────────────────┐
│  [+ Add Table]                                    [Edit Mode ✓]│
├────────────────────────────────────────────────────────────────┤
│  📋 customers                                      [Edit] [×]  │
│     ├─ id (string) PK Required                    [Edit] [×]  │
│     ├─ email (string) Required PII:personal       [Edit] [×]  │
│     └─ [+ Add Field]                                           │
├────────────────────────────────────────────────────────────────┤
│  📋 orders                                         [Edit] [×]  │
│     └─ ...                                                     │
└────────────────────────────────────────────────────────────────┘
```

**Files to Modify:**
- `src/app/studio/contracts/[contractId]/edit/page.tsx` - Add schema editing section
- Create: `src/components/contracts/SchemaEditor.tsx` - Reusable schema editor
- Create: `src/components/contracts/TableEditor.tsx` - Table add/edit form
- Create: `src/components/contracts/FieldEditor.tsx` - Field add/edit form

**API:**
- PUT `/contracts/{id}` with updated schema in payload

**Acceptance Criteria:**
- [ ] Draft contracts show editable schema section
- [ ] Pending_review contracts show editable schema with warning
- [ ] Can add/edit/remove tables
- [ ] Can add/edit/remove fields with all properties
- [ ] Schema changes are saved to API
- [ ] Validation prevents invalid schemas

**Deliverable:** Working schema editor on contract edit page for draft/pending contracts

---

### T-CON-009: Schema Change Re-approval Workflow

**Objective:** When an `active` contract's schema is changed, invalidate the approval and create a re-approval task.

**Business Rule:**
Active contracts have been approved. If the schema changes:
1. The approval is invalidated (set `approved_by` to null, `approved_at` to null)
2. Status changes to `pending_review`
3. A task is created for the original approver (or assigned reviewer) to re-approve
4. The contract cannot be used in production until re-approved

**Requirements:**

1. **Schema Change Detection**
   - When saving an active contract with schema changes
   - Compare new schema to original schema
   - Detect: added tables, removed tables, added fields, removed fields, changed field types

2. **Approval Invalidation**
   - On schema change for active contract:
     - Set `status: 'pending_review'`
     - Clear `approved_by` and `approved_at`
     - Store `previous_version` reference
     - Record `schema_change_reason` (require user to provide)

3. **Re-approval Task Creation**
   - Create task in tasks system (Platform Agent's domain)
   - Task type: `contract_reapproval`
   - Assigned to: original approver OR assigned reviewer
   - Task contains:
     - Contract link
     - Schema diff summary (what changed)
     - Change reason provided by editor
     - Approve/Reject actions

4. **Confirmation Dialog**
   - When user tries to save schema changes on active contract
   - Show warning dialog:
     ```
     ⚠️ Schema Change Requires Re-approval

     This contract is active and has been approved. Changing the schema will:
     • Invalidate the current approval
     • Change status to "Pending Review"
     • Create a re-approval task for [Approver Name]

     Please provide a reason for this schema change:
     [textarea]

     [Cancel] [Proceed with Changes]
     ```

5. **Visual Indicators**
   - On contract detail, show "Re-approval Required" banner
   - Show what changed (schema diff)
   - Show who needs to approve

**Files to Modify:**
- `src/app/studio/contracts/[contractId]/edit/page.tsx` - Add confirmation flow
- Create: `src/components/contracts/SchemaChangeDialog.tsx` - Confirmation dialog
- Create: `src/lib/utils/schema-diff.ts` - Schema comparison utility
- Platform Agent: `src/lib/mocks/data/tasks.ts` - Add task type (request to Platform Agent)

**API Calls:**
1. PUT `/contracts/{id}` with:
   - Updated schema
   - `status: 'pending_review'`
   - `schema_change_reason: string`
   - `change_type: 'major'` (schema changes are always major)

2. POST `/tasks` (or equivalent) to create re-approval task

**Acceptance Criteria:**
- [ ] Saving schema changes on active contract shows confirmation dialog
- [ ] User must provide change reason
- [ ] Contract status changes to pending_review
- [ ] Approval fields are cleared
- [ ] Re-approval task is created
- [ ] Reviewer sees schema diff in task

**Deliverable:** Working re-approval workflow for schema changes on active contracts

---

### T-CON-010: Schema Edit Restrictions by Status

**Objective:** Enforce schema editing restrictions based on contract status.

**Status Rules:**

| Status | Schema Editable? | Behavior |
|--------|------------------|----------|
| `draft` | ✅ Yes | Free editing, no restrictions |
| `pending_review` | ✅ Yes | Allowed with warning, notifies reviewer |
| `active` | ⚠️ Conditional | Requires re-approval workflow (T-CON-009) |
| `retired` | ❌ No | Schema locked, show "Contract retired" message |
| `deprecated` | ❌ No | Schema locked, show "Contract deprecated" message |

**Requirements:**

1. **Draft Status**
   - Full schema editing enabled
   - No warnings or restrictions
   - Changes saved immediately

2. **Pending Review Status**
   - Schema editing enabled
   - Show info banner: "This contract is under review. Schema changes will be visible to the reviewer."
   - Optionally notify reviewer of changes (toast or email)

3. **Active Status**
   - Schema editing enabled BUT triggers re-approval (T-CON-009)
   - Show warning banner: "This contract is active. Schema changes require re-approval."
   - "Edit Schema" button shows confirmation first

4. **Retired Status**
   - Schema section shows as read-only
   - Edit button disabled or hidden
   - Show message: "This contract has been retired. Schema cannot be modified."
   - Suggest: "Create a new version if changes are needed"

5. **Deprecated Status**
   - Schema section shows as read-only
   - Edit button disabled or hidden
   - Show message: "This contract is deprecated. Schema cannot be modified."
   - Suggest: "This contract should not be used. Consider creating a replacement."

6. **UI Implementation**
   - Conditional rendering based on `contract.status`
   - Disable/enable schema editor controls
   - Appropriate messaging for each status

**Files to Modify:**
- `src/app/studio/contracts/[contractId]/edit/page.tsx` - Add status-based conditionals
- `src/components/contracts/SchemaEditor.tsx` - Accept `readonly` and `status` props

**Acceptance Criteria:**
- [ ] Draft contracts allow free schema editing
- [ ] Pending_review contracts allow editing with info banner
- [ ] Active contracts show re-approval warning before editing
- [ ] Retired contracts show read-only schema with message
- [ ] Deprecated contracts show read-only schema with message
- [ ] Edit controls are properly disabled for locked statuses

**Deliverable:** Status-aware schema editing with appropriate restrictions and messaging

---

## Task Status Legend

| Status | Meaning |
|--------|---------|
| 📋 Ready | Ready to start, no blockers |
| 🔄 In Progress | Currently being worked on |
| ⏳ Blocked | Waiting on dependency |
| ✅ Done | Completed |
| 🔜 Backlog | Planned for future |

---

## Notes for Design Agent

1. **Read First:**
   - `agents/prompts/design.md` - Your responsibilities
   - `agents/specs/auth-admin-api.yaml` - API spec (create this first)

2. **Design Before Implement:**
   - Complete T-DES-001, T-DES-002, T-DES-003 (design tasks) first
   - Then create OpenAPI spec (T-DES-004)
   - Then implement in order

3. **Testing Reference:**
   - Use MSW for all API calls
   - Structure mocks to be swappable with real APIs
   - Test with Playwright for E2E coverage

4. **Hardcoded Admin:**
   - Email: `brackly@griot.com`
   - Password: `melly`
   - Full admin privileges
   - Use for testing admin flows

---

## Notes for Contracts Agent

1. **Read First:**
   - `agents/prompts/contracts.md` - Your feature ownership
   - `agents/specs/contracts.yaml` - **Missing APIs spec** (what needs to be built)
   - `src/lib/api/adapters.ts` - Data transformation layer

2. **Critical Bug First:**
   - T-CON-001 (Edit Bug) is the HIGHEST PRIORITY
   - This is blocking users from editing contracts
   - Fix the race condition before other tasks

3. **API Information:**
   - Registry API: `http://localhost:8000/api/v1/`
   - Uses ODCS (Open Data Contract Standard) format
   - Contract format transforms: Registry ODCS → Hub internal format
   - See `adaptContract()` in `src/lib/api/adapters.ts`

4. **Quality Rules Note:**
   - Adapter currently sets `qualityRules: []`
   - Need to investigate if rules are in contract response or separate endpoint
   - Check registry API docs for `/contracts/{id}/quality-rules`

5. **Missing APIs:**
   - See `agents/specs/contracts.yaml` for full OpenAPI spec
   - Status workflow endpoints (submit, approve, reject, deprecate) - **NOT IMPLEMENTED**
   - Quality rules CRUD endpoints - **NOT IMPLEMENTED**
   - Version history/diff endpoints - **NOT IMPLEMENTED**
   - Tasks endpoints for re-approval workflow - **NOT IMPLEMENTED**
   - **Frontend should mock these until backend implements them**

6. **Testing:**
   - Use Playwright for E2E tests
   - Test against real API (localhost:8000)
   - Login with `brackly@griot.com` / `melly` for admin access

7. **Execution Order:**
   1. T-CON-001 (Fix Edit Bug) - CRITICAL
   2. T-CON-002 (Add Reviewer Field)
   3. T-CON-003 (Status Workflow)
   4. T-CON-004 (Enhance Detail Page)
   5. T-CON-008 (Schema Editing for Draft/Pending)
   6. T-CON-009 (Schema Change Re-approval)
   7. T-CON-010 (Schema Edit Restrictions)
   8. T-CON-005 & T-CON-006 (Quality Rules & Privacy)
   9. T-CON-007 (E2E Tests)

---

## Next Milestones

### Milestone 1: Authentication & Admin (Design Agent) - COMPLETED
- [x] Login/signup pages with OAuth support
- [x] Admin-only sidebar visibility
- [x] User management with role assignment
- [x] Team creation and member management
- [x] Role/permission management

### Milestone 2: Contract Fixes (Contracts Agent) - IN PROGRESS

**Target:** Fully functional contract management with real API

**Key Deliverables:**
1. Fix edit contract bug (race condition) - CRITICAL
2. Add reviewer field to contract creation
3. Contract status workflow (draft → pending_review → active)
4. Enhanced contract detail page with quality rules and PII info
5. Schema editing for draft/pending contracts
6. Schema change re-approval workflow for active contracts
7. Schema edit restrictions by status (locked for retired/deprecated)
8. E2E tests passing for all contract functionality

**Success Criteria:**
- User can edit any contract without errors
- User can assign reviewer when creating contract
- Reviewer can approve or request changes
- Contract detail shows complete governance information
- User can edit schema on draft and pending_review contracts
- Schema changes on active contracts trigger re-approval workflow
- Schema is read-only for retired and deprecated contracts
- All E2E tests pass
