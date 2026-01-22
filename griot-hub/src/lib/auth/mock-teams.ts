// Mock teams data

export interface TeamMember {
  id: string
  userId: string
  name: string
  email: string
  avatar: string | null
  role: string
  joinedAt: string
}

export interface Team {
  id: string
  name: string
  description: string
  domains: string[]
  memberCount: number
  defaultRole: string
  createdAt: string
  updatedAt: string
}

export interface TeamDetail extends Team {
  members: TeamMember[]
}

// Use global to survive hot reloads in development
declare global {
  // eslint-disable-next-line no-var
  var __teamsDb: Map<string, TeamDetail> | undefined
}

// Mock teams storage - persist across hot reloads
const teamsDb = globalThis.__teamsDb || new Map<string, TeamDetail>()
globalThis.__teamsDb = teamsDb

// Initialize with default teams (only if empty)
const defaultTeams: TeamDetail[] = [
  {
    id: 'team-001',
    name: 'Platform Team',
    description: 'Core platform development and infrastructure',
    domains: ['platform', 'infrastructure', 'core'],
    memberCount: 5,
    defaultRole: 'Editor',
    createdAt: '2024-01-15T00:00:00Z',
    updatedAt: '2024-01-15T00:00:00Z',
    members: [
      {
        id: 'member-001',
        userId: 'user-admin-001',
        name: 'Brackly Murunga',
        email: 'brackly@griot.com',
        avatar: null,
        role: 'Admin',
        joinedAt: '2024-01-15T00:00:00Z',
      },
      {
        id: 'member-002',
        userId: 'user-002',
        name: 'Jane Doe',
        email: 'jane@griot.com',
        avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100',
        role: 'Editor',
        joinedAt: '2024-02-15T00:00:00Z',
      },
    ],
  },
  {
    id: 'team-002',
    name: 'CRM Team',
    description: 'Customer relationship management and sales data',
    domains: ['crm', 'sales', 'customers'],
    memberCount: 3,
    defaultRole: 'Viewer',
    createdAt: '2024-02-01T00:00:00Z',
    updatedAt: '2024-02-01T00:00:00Z',
    members: [
      {
        id: 'member-003',
        userId: 'user-003',
        name: 'View Only',
        email: 'viewer@griot.com',
        avatar: null,
        role: 'Viewer',
        joinedAt: '2024-06-01T00:00:00Z',
      },
    ],
  },
  {
    id: 'team-003',
    name: 'Analytics Team',
    description: 'Data analytics and business intelligence',
    domains: ['analytics', 'bi', 'reporting'],
    memberCount: 4,
    defaultRole: 'Editor',
    createdAt: '2024-03-01T00:00:00Z',
    updatedAt: '2024-03-01T00:00:00Z',
    members: [],
  },
]

// Initialize teams only if Map is empty (survives hot reloads)
if (teamsDb.size === 0) {
  defaultTeams.forEach((team) => {
    teamsDb.set(team.id, team)
  })
}

// Team CRUD operations
export function getAllTeams(): Team[] {
  return Array.from(teamsDb.values()).map(({ members, ...team }) => ({
    ...team,
    memberCount: members.length,
  }))
}

export function getTeamById(id: string): TeamDetail | undefined {
  return teamsDb.get(id)
}

export function createTeam(data: { name: string; description?: string; defaultRole?: string }): Team {
  const id = `team-${Date.now()}`
  const newTeam: TeamDetail = {
    id,
    name: data.name,
    description: data.description || '',
    domains: [],
    memberCount: 0,
    defaultRole: data.defaultRole || 'Viewer',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    members: [],
  }
  teamsDb.set(id, newTeam)
  return { ...newTeam, memberCount: 0 }
}

export function updateTeam(id: string, data: Partial<Team>): Team | null {
  const team = teamsDb.get(id)
  if (!team) return null

  const updated: TeamDetail = {
    ...team,
    ...data,
    id: team.id, // Don't allow changing ID
    updatedAt: new Date().toISOString(),
    members: team.members, // Preserve members
  }
  teamsDb.set(id, updated)
  return { ...updated, memberCount: updated.members.length }
}

export function deleteTeam(id: string): boolean {
  return teamsDb.delete(id)
}

export function addTeamMember(
  teamId: string,
  member: { userId: string; name: string; email: string; avatar?: string | null; role?: string }
): TeamMember | null {
  const team = teamsDb.get(teamId)
  if (!team) return null

  // Check if member already exists
  if (team.members.some((m) => m.email.toLowerCase() === member.email.toLowerCase())) {
    return null
  }

  const newMember: TeamMember = {
    id: `member-${Date.now()}`,
    userId: member.userId || `user-${Date.now()}`,
    name: member.name,
    email: member.email.toLowerCase(),
    avatar: member.avatar || null,
    role: member.role || team.defaultRole,
    joinedAt: new Date().toISOString(),
  }

  team.members.push(newMember)
  team.memberCount = team.members.length
  team.updatedAt = new Date().toISOString()

  return newMember
}

export function removeTeamMember(teamId: string, memberId: string): boolean {
  const team = teamsDb.get(teamId)
  if (!team) return false

  const index = team.members.findIndex((m) => m.id === memberId)
  if (index === -1) return false

  team.members.splice(index, 1)
  team.memberCount = team.members.length
  team.updatedAt = new Date().toISOString()

  return true
}

export function updateMemberRole(teamId: string, memberId: string, role: string): TeamMember | null {
  const team = teamsDb.get(teamId)
  if (!team) return null

  const member = team.members.find((m) => m.id === memberId)
  if (!member) return null

  member.role = role
  team.updatedAt = new Date().toISOString()

  return member
}
