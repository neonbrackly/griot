import { http, HttpResponse, delay } from 'msw'
import { mockUsersDb, type AuthUser } from './auth'
import { rolesDb } from './roles'

// Team type
interface Team {
  id: string
  name: string
  description: string | null
  memberCount: number
  defaultRole: { id: string; name: string }
  domains: string[]
  createdAt: string
  updatedAt: string
}

// Team member type
interface TeamMember {
  user: AuthUser
  role: { id: string; name: string }
  isRoleInherited: boolean
  joinedAt: string
}

// Team detail type
interface TeamDetail extends Team {
  members: TeamMember[]
}

// Default teams
const mockTeamsData: Team[] = [
  {
    id: 'team-001',
    name: 'Platform Team',
    description: 'Core platform and infrastructure team',
    memberCount: 3,
    defaultRole: { id: 'role-editor', name: 'Editor' },
    domains: ['analytics', 'infrastructure'],
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2025-01-10T00:00:00Z',
  },
  {
    id: 'team-002',
    name: 'CRM Team',
    description: 'Customer relationship management',
    memberCount: 2,
    defaultRole: { id: 'role-viewer', name: 'Viewer' },
    domains: ['crm', 'customer'],
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2025-01-10T00:00:00Z',
  },
  {
    id: 'team-003',
    name: 'Finance Analytics',
    description: 'Financial data and reporting',
    memberCount: 1,
    defaultRole: { id: 'role-viewer', name: 'Viewer' },
    domains: ['finance', 'reporting'],
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2025-01-10T00:00:00Z',
  },
  {
    id: 'team-004',
    name: 'Data Engineering',
    description: 'Data pipeline and ETL team',
    memberCount: 0,
    defaultRole: { id: 'role-editor', name: 'Editor' },
    domains: ['data', 'engineering'],
    createdAt: '2024-06-15T00:00:00Z',
    updatedAt: '2025-01-05T00:00:00Z',
  },
]

// In-memory teams storage
const teamsDb = new Map<string, Team>()
mockTeamsData.forEach(team => teamsDb.set(team.id, team))

// Team membership storage (teamId -> userId -> joinedAt)
const teamMemberships = new Map<string, Map<string, { joinedAt: string; roleOverride?: string }>>()

// Initialize some memberships
teamMemberships.set('team-001', new Map([
  ['user-admin-001', { joinedAt: '2024-01-01T00:00:00Z' }],
  ['user-002', { joinedAt: '2024-02-15T00:00:00Z' }],
]))
teamMemberships.set('team-002', new Map([
  ['user-003', { joinedAt: '2024-06-01T00:00:00Z' }],
]))

// Helper: Get team members
function getTeamMembers(teamId: string): TeamMember[] {
  const membership = teamMemberships.get(teamId)
  if (!membership) return []

  const team = teamsDb.get(teamId)
  const members: TeamMember[] = []

  for (const [userId, data] of membership.entries()) {
    // Find user in mockUsersDb
    for (const record of mockUsersDb.values()) {
      if (record.user.id === userId) {
        members.push({
          user: record.user,
          role: data.roleOverride
            ? { id: data.roleOverride, name: rolesDb.get(data.roleOverride)?.name || 'Unknown' }
            : team?.defaultRole || { id: 'role-viewer', name: 'Viewer' },
          isRoleInherited: !data.roleOverride,
          joinedAt: data.joinedAt,
        })
        break
      }
    }
  }

  return members
}

export const teamHandlers = [
  // List teams
  http.get('/api/teams', async ({ request }) => {
    await delay(200)

    const url = new URL(request.url)
    const search = url.searchParams.get('search')
    const page = parseInt(url.searchParams.get('page') || '1')
    const limit = parseInt(url.searchParams.get('limit') || '20')

    let teams = Array.from(teamsDb.values())

    if (search) {
      const searchLower = search.toLowerCase()
      teams = teams.filter(t =>
        t.name.toLowerCase().includes(searchLower) ||
        t.description?.toLowerCase().includes(searchLower)
      )
    }

    const total = teams.length
    const startIndex = (page - 1) * limit
    const paginatedData = teams.slice(startIndex, startIndex + limit)

    return HttpResponse.json({
      data: paginatedData,
      pagination: {
        total,
        page,
        limit,
        totalPages: Math.ceil(total / limit),
      },
    })
  }),

  // Get single team (with members)
  http.get('/api/teams/:id', async ({ params }) => {
    await delay(150)

    const team = teamsDb.get(params.id as string)
    if (!team) {
      return HttpResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Team not found' } },
        { status: 404 }
      )
    }

    const teamDetail: TeamDetail = {
      ...team,
      members: getTeamMembers(team.id),
    }

    return HttpResponse.json(teamDetail)
  }),

  // Create team
  http.post('/api/teams', async ({ request }) => {
    await delay(300)

    const body = (await request.json()) as {
      name: string
      description?: string
      defaultRoleId?: string
      domains?: string[]
    }

    if (!body.name) {
      return HttpResponse.json(
        { error: { code: 'VALIDATION_ERROR', message: 'Team name is required' } },
        { status: 422 }
      )
    }

    const defaultRoleId = body.defaultRoleId || 'role-viewer'
    const defaultRole = rolesDb.get(defaultRoleId)

    const newTeam: Team = {
      id: `team-${Date.now()}`,
      name: body.name,
      description: body.description || null,
      memberCount: 0,
      defaultRole: defaultRole
        ? { id: defaultRole.id, name: defaultRole.name }
        : { id: 'role-viewer', name: 'Viewer' },
      domains: body.domains || [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }

    teamsDb.set(newTeam.id, newTeam)
    teamMemberships.set(newTeam.id, new Map())

    return HttpResponse.json(newTeam, { status: 201 })
  }),

  // Update team
  http.patch('/api/teams/:id', async ({ params, request }) => {
    await delay(300)

    const team = teamsDb.get(params.id as string)
    if (!team) {
      return HttpResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Team not found' } },
        { status: 404 }
      )
    }

    const body = (await request.json()) as Partial<{
      name: string
      description: string
      defaultRoleId: string
      domains: string[]
    }>

    let defaultRole = team.defaultRole
    if (body.defaultRoleId) {
      const role = rolesDb.get(body.defaultRoleId)
      if (role) {
        defaultRole = { id: role.id, name: role.name }
      }
    }

    const updated: Team = {
      ...team,
      ...(body.name && { name: body.name }),
      ...(body.description !== undefined && { description: body.description }),
      ...(body.domains && { domains: body.domains }),
      defaultRole,
      updatedAt: new Date().toISOString(),
    }

    teamsDb.set(team.id, updated)

    return HttpResponse.json(updated)
  }),

  // Delete team
  http.delete('/api/teams/:id', async ({ params }) => {
    await delay(300)

    const team = teamsDb.get(params.id as string)
    if (!team) {
      return HttpResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Team not found' } },
        { status: 404 }
      )
    }

    teamsDb.delete(team.id)
    teamMemberships.delete(team.id)

    return HttpResponse.json({ message: 'Team deleted successfully' })
  }),

  // Add member to team
  http.post('/api/teams/:id/members', async ({ params, request }) => {
    await delay(300)

    const teamId = params.id as string
    const team = teamsDb.get(teamId)
    if (!team) {
      return HttpResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Team not found' } },
        { status: 404 }
      )
    }

    const body = (await request.json()) as {
      userId: string
      roleId?: string
    }

    if (!body.userId) {
      return HttpResponse.json(
        { error: { code: 'VALIDATION_ERROR', message: 'User ID is required' } },
        { status: 422 }
      )
    }

    // Check if user exists
    let userExists = false
    for (const record of mockUsersDb.values()) {
      if (record.user.id === body.userId) {
        userExists = true
        break
      }
    }

    if (!userExists) {
      return HttpResponse.json(
        { error: { code: 'NOT_FOUND', message: 'User not found' } },
        { status: 404 }
      )
    }

    // Add to membership
    let membership = teamMemberships.get(teamId)
    if (!membership) {
      membership = new Map()
      teamMemberships.set(teamId, membership)
    }

    membership.set(body.userId, {
      joinedAt: new Date().toISOString(),
      roleOverride: body.roleId,
    })

    // Update member count
    team.memberCount = membership.size
    teamsDb.set(teamId, team)

    // Return updated team detail
    const teamDetail: TeamDetail = {
      ...team,
      members: getTeamMembers(teamId),
    }

    return HttpResponse.json(teamDetail)
  }),

  // Remove member from team
  http.delete('/api/teams/:teamId/members/:userId', async ({ params }) => {
    await delay(300)

    const teamId = params.teamId as string
    const userId = params.userId as string

    const team = teamsDb.get(teamId)
    if (!team) {
      return HttpResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Team not found' } },
        { status: 404 }
      )
    }

    const membership = teamMemberships.get(teamId)
    if (!membership || !membership.has(userId)) {
      return HttpResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Member not found in team' } },
        { status: 404 }
      )
    }

    membership.delete(userId)

    // Update member count
    team.memberCount = membership.size
    teamsDb.set(teamId, team)

    return HttpResponse.json({ message: 'Member removed from team' })
  }),
]

// Export for use in other handlers
export { teamsDb, teamMemberships, getTeamMembers }
export type { Team, TeamDetail, TeamMember }
