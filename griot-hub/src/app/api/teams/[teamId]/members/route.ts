import { NextRequest, NextResponse } from 'next/server'
import { getTeamById, addTeamMember } from '@/lib/auth/mock-teams'

interface RouteParams {
  params: Promise<{ teamId: string }>
}

// GET /api/teams/:teamId/members - Get team members
export async function GET(request: NextRequest, { params }: RouteParams) {
  try {
    const { teamId } = await params
    const team = getTeamById(teamId)

    if (!team) {
      return NextResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Team not found' } },
        { status: 404 }
      )
    }

    return NextResponse.json({ data: team.members })
  } catch (error) {
    console.error('[API] Get team members error:', error)
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: 'Failed to fetch team members' } },
      { status: 500 }
    )
  }
}

// POST /api/teams/:teamId/members - Add member to team
export async function POST(request: NextRequest, { params }: RouteParams) {
  try {
    const { teamId } = await params
    const body = await request.json()

    if (!body.email) {
      return NextResponse.json(
        { error: { code: 'VALIDATION_ERROR', message: 'Email is required' } },
        { status: 422 }
      )
    }

    const member = addTeamMember(teamId, {
      userId: body.userId || `user-${Date.now()}`,
      name: body.name || body.email.split('@')[0],
      email: body.email,
      avatar: body.avatar,
      role: body.role,
    })

    if (!member) {
      return NextResponse.json(
        { error: { code: 'CONFLICT', message: 'Member already exists in team or team not found' } },
        { status: 409 }
      )
    }

    return NextResponse.json(member, { status: 201 })
  } catch (error) {
    console.error('[API] Add team member error:', error)
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: 'Failed to add team member' } },
      { status: 500 }
    )
  }
}
