# Agent 4: Platform Features

## Mission Statement
Build the platform infrastructure: My Tasks, Issues management, Admin pages, Settings, and cross-feature navigation. Ensure smooth navigation and global functionality like search and notifications.

---

## Pages Owned

```
/app/
├── studio/
│   ├── tasks/page.tsx          # My Tasks
│   └── issues/
│       ├── page.tsx            # All Issues
│       └── [issueId]/page.tsx  # Issue detail
├── settings/
│   ├── page.tsx                # Settings overview
│   ├── profile/page.tsx        # User profile
│   ├── notifications/page.tsx  # Notification prefs
│   └── integrations/page.tsx   # API keys
└── admin/
    ├── page.tsx                # Admin overview
    ├── users/page.tsx          # User management
    ├── teams/page.tsx          # Team management
    └── roles/page.tsx          # Roles & permissions
```

---

## Task Specifications

### A4-01: My Tasks Page

```tsx
'use client'

import { useState } from 'react'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/Tabs'

export default function MyTasksPage() {
  const { data: tasks, isLoading } = useQuery({
    queryKey: ['my-tasks'],
    queryFn: fetchMyTasks,
  })
  
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">My Tasks</h1>
        <p className="text-text-secondary">
          Items requiring your attention
        </p>
      </div>
      
      <Tabs defaultValue="authorizations">
        <TabsList>
          <TabsTrigger value="authorizations">
            Pending Authorization
            {tasks?.authorizations.length > 0 && (
              <Badge className="ml-2">{tasks.authorizations.length}</Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="comments">
            Comments to Review
            {tasks?.comments.length > 0 && (
              <Badge className="ml-2">{tasks.comments.length}</Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="drafts">
            My Drafts
            {tasks?.drafts.length > 0 && (
              <Badge className="ml-2">{tasks.drafts.length}</Badge>
            )}
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="authorizations" className="mt-6">
          <PendingAuthorizationsList 
            items={tasks?.authorizations}
            loading={isLoading}
          />
        </TabsContent>
        
        <TabsContent value="comments" className="mt-6">
          <CommentsToReviewList 
            items={tasks?.comments}
            loading={isLoading}
          />
        </TabsContent>
        
        <TabsContent value="drafts" className="mt-6">
          <DraftsList 
            items={tasks?.drafts}
            loading={isLoading}
          />
        </TabsContent>
      </Tabs>
    </div>
  )
}
```

### A4-02: Pending Authorizations List

```tsx
function PendingAuthorizationsList({ items, loading }: ListProps) {
  const approveMutation = useMutation({
    mutationFn: approveContract,
    onSuccess: () => {
      toast.success('Contract approved')
      queryClient.invalidateQueries(['my-tasks'])
    },
  })
  
  const rejectMutation = useMutation({
    mutationFn: rejectContract,
  })
  
  if (loading) return <AuthorizationsSkeleton />
  
  if (items?.length === 0) {
    return (
      <EmptyState
        icon={CheckCircle}
        title="All caught up!"
        description="No contracts waiting for your approval"
      />
    )
  }
  
  return (
    <div className="space-y-4">
      {items?.map(item => (
        <Card key={item.id} className="p-4">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-4">
              <div className="p-2 rounded-lg bg-yellow-100 dark:bg-yellow-900/30">
                <Clock className="w-5 h-5 text-yellow-600" />
              </div>
              <div>
                <Link 
                  href={`/studio/contracts/${item.contractId}`}
                  className="font-medium text-text-primary hover:text-text-link"
                >
                  {item.contractName}
                </Link>
                <p className="text-sm text-text-secondary mt-1">
                  Requested by {item.requestedBy} • {formatRelativeTime(item.requestedAt)}
                </p>
                <div className="flex items-center gap-2 mt-2">
                  <Badge variant="secondary">{item.domain}</Badge>
                  <Badge variant={item.priority === 'high' ? 'warning' : 'secondary'}>
                    {item.priority} priority
                  </Badge>
                </div>
              </div>
            </div>
            
            <div className="flex gap-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => rejectMutation.mutate(item.contractId)}
                loading={rejectMutation.isPending}
              >
                Request Changes
              </Button>
              <Button
                size="sm"
                onClick={() => approveMutation.mutate(item.contractId)}
                loading={approveMutation.isPending}
              >
                Approve
              </Button>
            </div>
          </div>
        </Card>
      ))}
    </div>
  )
}
```

### A4-03: My Drafts List

```tsx
function DraftsList({ items, loading }: ListProps) {
  const deleteMutation = useMutation({
    mutationFn: deleteDraft,
    onSuccess: () => {
      toast.success('Draft deleted')
      queryClient.invalidateQueries(['my-tasks'])
    },
  })
  
  if (loading) return <DraftsSkeleton />
  
  if (items?.length === 0) {
    return (
      <EmptyState
        icon={FileEdit}
        title="No drafts"
        description="Contracts you save as draft will appear here"
        action={{
          label: 'Create Contract',
          onClick: () => router.push('/studio/contracts/new'),
        }}
      />
    )
  }
  
  return (
    <div className="space-y-3">
      {items?.map(draft => (
        <Card key={draft.id} className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-2 rounded-lg bg-bg-tertiary">
                <FileEdit className="w-5 h-5 text-text-secondary" />
              </div>
              <div>
                <div className="font-medium text-text-primary">
                  {draft.name || 'Untitled Contract'}
                </div>
                <div className="text-sm text-text-secondary">
                  Last edited {formatRelativeTime(draft.updatedAt)}
                  {draft.completionPercent && (
                    <span className="ml-2">• {draft.completionPercent}% complete</span>
                  )}
                </div>
              </div>
            </div>
            
            <div className="flex gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => deleteMutation.mutate(draft.id)}
              >
                Delete
              </Button>
              <Button size="sm" asChild>
                <Link href={`/studio/contracts/new/wizard?draft=${draft.id}`}>
                  Continue Editing
                </Link>
              </Button>
            </div>
          </div>
          
          {/* Progress bar */}
          {draft.completionPercent && (
            <div className="mt-3 h-1 bg-bg-tertiary rounded-full overflow-hidden">
              <div 
                className="h-full bg-primary-500 rounded-full"
                style={{ width: `${draft.completionPercent}%` }}
              />
            </div>
          )}
        </Card>
      ))}
    </div>
  )
}
```

---

### A4-04: Issues List Page

```tsx
'use client'

export default function IssuesPage() {
  const [severity, setSeverity] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  
  const { data: issues, isLoading } = useQuery({
    queryKey: ['issues', { severity, search }],
    queryFn: () => fetchIssues({ severity, search }),
  })
  
  const severityCounts = useMemo(() => ({
    all: issues?.length || 0,
    critical: issues?.filter(i => i.severity === 'critical').length || 0,
    warning: issues?.filter(i => i.severity === 'warning').length || 0,
    info: issues?.filter(i => i.severity === 'info').length || 0,
    resolved: issues?.filter(i => i.status === 'resolved').length || 0,
  }), [issues])
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Issues</h1>
          <p className="text-text-secondary">
            All issues across your contracts
          </p>
        </div>
        <Button variant="secondary">
          <Download className="w-4 h-4 mr-2" />
          Export CSV
        </Button>
      </div>
      
      {/* Severity Tabs */}
      <Tabs value={severity || 'all'} onValueChange={(v) => setSeverity(v === 'all' ? null : v)}>
        <TabsList>
          <TabsTrigger value="all">All ({severityCounts.all})</TabsTrigger>
          <TabsTrigger value="critical" className="text-red-600">
            Critical ({severityCounts.critical})
          </TabsTrigger>
          <TabsTrigger value="warning" className="text-yellow-600">
            Warning ({severityCounts.warning})
          </TabsTrigger>
          <TabsTrigger value="info">Info ({severityCounts.info})</TabsTrigger>
          <TabsTrigger value="resolved">Resolved ({severityCounts.resolved})</TabsTrigger>
        </TabsList>
      </Tabs>
      
      {/* Search and Filters */}
      <div className="flex gap-4">
        <Input
          placeholder="Search issues..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          leftIcon={<Search className="w-4 h-4" />}
          className="max-w-sm"
        />
        <Select placeholder="Category">
          <option value="">All Categories</option>
          <option value="pii">PII Detection</option>
          <option value="schema">Schema Drift</option>
          <option value="sla">SLA Breach</option>
        </Select>
        <Select placeholder="Contract">
          <option value="">All Contracts</option>
          {/* Dynamic contract list */}
        </Select>
      </div>
      
      {/* Issues List */}
      {isLoading ? (
        <IssuesListSkeleton />
      ) : issues?.length === 0 ? (
        <EmptyState
          icon={CheckCircle}
          title="No issues found"
          description="Great! There are no issues matching your filters"
        />
      ) : (
        <div className="space-y-3">
          {issues?.map(issue => (
            <IssueCard key={issue.id} issue={issue} />
          ))}
        </div>
      )}
    </div>
  )
}

function IssueCard({ issue }: { issue: Issue }) {
  return (
    <Card className="p-4">
      <div className="flex items-start gap-4">
        <SeverityIcon severity={issue.severity} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <Link 
              href={`/studio/issues/${issue.id}`}
              className="font-medium text-text-primary hover:text-text-link"
            >
              {issue.title}
            </Link>
            <Badge variant={getSeverityVariant(issue.severity)}>
              {issue.severity}
            </Badge>
          </div>
          
          <p className="text-sm text-text-secondary mt-1">
            {issue.category} • Detected {formatRelativeTime(issue.detectedAt)}
          </p>
          
          {/* Contract attribution */}
          <div className="flex items-center gap-2 mt-2 text-sm">
            <span className="text-text-tertiary">Contract:</span>
            <Link 
              href={`/studio/contracts/${issue.contractId}`}
              className="text-text-link hover:underline"
            >
              {issue.contractName}
            </Link>
            <Badge variant="secondary" size="sm">{issue.contractVersion}</Badge>
          </div>
          
          {issue.field && (
            <div className="text-sm text-text-tertiary mt-1">
              Field: <code className="bg-bg-tertiary px-1 rounded">{issue.field}</code>
            </div>
          )}
        </div>
        
        <div className="text-right">
          <div className="text-sm text-text-secondary">Assigned to</div>
          <div className="text-sm text-text-primary">{issue.assignedTeam}</div>
        </div>
      </div>
    </Card>
  )
}
```

---

### A4-10: User Management

```tsx
'use client'

export default function UserManagementPage() {
  const [showInviteModal, setShowInviteModal] = useState(false)
  
  const { data: users, isLoading } = useQuery({
    queryKey: ['admin', 'users'],
    queryFn: fetchUsers,
  })
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">User Management</h1>
          <p className="text-text-secondary">
            Manage user accounts and permissions
          </p>
        </div>
        <Button onClick={() => setShowInviteModal(true)}>
          <UserPlus className="w-4 h-4 mr-2" />
          Invite User
        </Button>
      </div>
      
      {/* Search */}
      <Input
        placeholder="Search users..."
        leftIcon={<Search className="w-4 h-4" />}
        className="max-w-sm"
      />
      
      {/* Users Table */}
      <DataTable
        data={users || []}
        columns={[
          {
            header: 'User',
            accessorKey: 'name',
            cell: ({ row }) => (
              <div className="flex items-center gap-3">
                <Avatar src={row.original.avatar} fallback={row.original.name[0]} />
                <div>
                  <div className="font-medium">{row.original.name}</div>
                  <div className="text-sm text-text-secondary">{row.original.email}</div>
                </div>
              </div>
            ),
          },
          {
            header: 'Role',
            accessorKey: 'role',
            cell: ({ row }) => <Badge>{row.original.role}</Badge>,
          },
          {
            header: 'Team',
            accessorKey: 'team',
          },
          {
            header: 'Status',
            accessorKey: 'status',
            cell: ({ row }) => (
              <StatusBadge status={row.original.status === 'active' ? 'active' : 'pending'} />
            ),
          },
          {
            header: 'Last Login',
            accessorKey: 'lastLogin',
            cell: ({ row }) => formatRelativeTime(row.original.lastLogin),
          },
          {
            header: '',
            id: 'actions',
            cell: ({ row }) => (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon">
                    <MoreHorizontal className="w-4 h-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem>Edit User</DropdownMenuItem>
                  <DropdownMenuItem>Change Role</DropdownMenuItem>
                  <DropdownMenuItem>Reset Password</DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem className="text-red-600">
                    Deactivate User
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ),
          },
        ]}
        loading={isLoading}
      />
      
      {/* Invite Modal */}
      <InviteUserModal 
        open={showInviteModal}
        onClose={() => setShowInviteModal(false)}
      />
    </div>
  )
}
```

---

### A4-14: Global Search

```tsx
'use client'

import { useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { Command } from 'cmdk'
import { useHotkeys } from 'react-hotkeys-hook'

export function GlobalSearch() {
  const [open, setOpen] = useState(false)
  const [search, setSearch] = useState('')
  const router = useRouter()
  
  // Keyboard shortcut
  useHotkeys('mod+k', () => setOpen(true), { preventDefault: true })
  
  const { data: results, isLoading } = useQuery({
    queryKey: ['global-search', search],
    queryFn: () => globalSearch(search),
    enabled: search.length > 1,
  })
  
  const handleSelect = useCallback((item: SearchResult) => {
    setOpen(false)
    router.push(item.href)
  }, [router])
  
  return (
    <>
      {/* Search Trigger */}
      <button
        onClick={() => setOpen(true)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-border-default hover:border-border-strong transition-colors"
      >
        <Search className="w-4 h-4 text-text-tertiary" />
        <span className="text-sm text-text-tertiary">Search...</span>
        <kbd className="hidden sm:inline-flex h-5 items-center gap-1 rounded border border-border-default bg-bg-tertiary px-1.5 font-mono text-xs text-text-tertiary">
          ⌘K
        </kbd>
      </button>
      
      {/* Search Dialog */}
      <Command.Dialog 
        open={open} 
        onOpenChange={setOpen}
        className="fixed inset-0 z-modal"
      >
        <div className="fixed inset-0 bg-black/50" onClick={() => setOpen(false)} />
        
        <div className="fixed left-1/2 top-1/4 -translate-x-1/2 w-full max-w-lg bg-bg-secondary rounded-xl shadow-xl border border-border-default overflow-hidden">
          <Command.Input
            value={search}
            onValueChange={setSearch}
            placeholder="Search contracts, assets, issues..."
            className="w-full px-4 py-3 border-b border-border-default bg-transparent focus:outline-none"
          />
          
          <Command.List className="max-h-80 overflow-y-auto p-2">
            {isLoading && (
              <Command.Loading>
                <div className="p-4 text-center text-text-secondary">
                  <Loader2 className="w-4 h-4 animate-spin mx-auto" />
                </div>
              </Command.Loading>
            )}
            
            {results?.contracts?.length > 0 && (
              <Command.Group heading="Contracts">
                {results.contracts.map(item => (
                  <Command.Item
                    key={item.id}
                    value={item.name}
                    onSelect={() => handleSelect(item)}
                    className="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer hover:bg-bg-hover"
                  >
                    <FileText className="w-4 h-4 text-text-tertiary" />
                    <div>
                      <div className="text-sm text-text-primary">{item.name}</div>
                      <div className="text-xs text-text-tertiary">{item.domain}</div>
                    </div>
                  </Command.Item>
                ))}
              </Command.Group>
            )}
            
            {results?.assets?.length > 0 && (
              <Command.Group heading="Data Assets">
                {results.assets.map(item => (
                  <Command.Item
                    key={item.id}
                    value={item.name}
                    onSelect={() => handleSelect(item)}
                    className="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer hover:bg-bg-hover"
                  >
                    <Database className="w-4 h-4 text-text-tertiary" />
                    <div>
                      <div className="text-sm text-text-primary">{item.name}</div>
                      <div className="text-xs text-text-tertiary">{item.tables} tables</div>
                    </div>
                  </Command.Item>
                ))}
              </Command.Group>
            )}
            
            {search && !isLoading && !results?.contracts?.length && !results?.assets?.length && (
              <div className="p-4 text-center text-text-secondary">
                No results found for "{search}"
              </div>
            )}
          </Command.List>
        </div>
      </Command.Dialog>
    </>
  )
}
```

---

### A4-15: Notification Dropdown

```tsx
'use client'

export function NotificationDropdown() {
  const { data: notifications } = useQuery({
    queryKey: ['notifications'],
    queryFn: fetchNotifications,
    refetchInterval: 30000, // Poll every 30s
  })
  
  const unreadCount = notifications?.filter(n => !n.read).length || 0
  
  const markAsReadMutation = useMutation({
    mutationFn: markNotificationAsRead,
    onSuccess: () => {
      queryClient.invalidateQueries(['notifications'])
    },
  })
  
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button className="relative p-2 rounded-lg hover:bg-bg-hover transition-colors">
          <Bell className="w-5 h-5 text-text-secondary" />
          {unreadCount > 0 && (
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
          )}
        </button>
      </DropdownMenuTrigger>
      
      <DropdownMenuContent align="end" className="w-80">
        <div className="flex items-center justify-between px-3 py-2 border-b border-border-default">
          <span className="font-medium">Notifications</span>
          {unreadCount > 0 && (
            <Button variant="ghost" size="sm" onClick={() => markAllAsRead()}>
              Mark all read
            </Button>
          )}
        </div>
        
        <div className="max-h-96 overflow-y-auto">
          {notifications?.length === 0 ? (
            <div className="p-4 text-center text-text-secondary">
              No notifications
            </div>
          ) : (
            notifications?.map(notification => (
              <DropdownMenuItem
                key={notification.id}
                className={cn(
                  "flex items-start gap-3 p-3 cursor-pointer",
                  !notification.read && "bg-primary-50 dark:bg-primary-900/10"
                )}
                onClick={() => {
                  markAsReadMutation.mutate(notification.id)
                  if (notification.href) {
                    router.push(notification.href)
                  }
                }}
              >
                <NotificationIcon type={notification.type} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-text-primary">{notification.title}</p>
                  <p className="text-xs text-text-secondary mt-0.5">
                    {notification.description}
                  </p>
                  <p className="text-xs text-text-tertiary mt-1">
                    {formatRelativeTime(notification.createdAt)}
                  </p>
                </div>
              </DropdownMenuItem>
            ))
          )}
        </div>
        
        <div className="border-t border-border-default p-2">
          <Button variant="ghost" size="sm" className="w-full" asChild>
            <Link href="/settings/notifications">Notification Settings</Link>
          </Button>
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
```

---

## Exit Criteria Checklist

- [ ] My Tasks shows all tabs with correct counts
- [ ] Pending authorizations can be approved/rejected
- [ ] Drafts can be resumed or deleted
- [ ] Issues list shows all issues with contract attribution
- [ ] Issue detail page allows assignment and status updates
- [ ] User management CRUD works
- [ ] Team management CRUD works
- [ ] Global search opens with ⌘K
- [ ] Search returns contracts, assets, and issues
- [ ] Notifications dropdown shows real-time updates
- [ ] Settings pages render correctly
- [ ] Authorization workflow completes end-to-end