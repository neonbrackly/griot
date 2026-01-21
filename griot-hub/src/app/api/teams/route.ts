import { NextRequest, NextResponse } from 'next/server'
import { getAllTeams, createTeam } from '@/lib/auth/mock-teams'

// GET /api/teams - List all teams
export async function GET() {
  try {
    const teams = getAllTeams()
    return NextResponse.json({ data: teams })
  } catch (error) {
    console.error('[API] Get teams error:', error)
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: 'Failed to fetch teams' } },
      { status: 500 }
    )
  }
}

// POST /api/teams - Create a new team
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    if (!body.name) {
      return NextResponse.json(
        { error: { code: 'VALIDATION_ERROR', message: 'Team name is required' } },
        { status: 422 }
      )
    }

    const team = createTeam({
      name: body.name,
      description: body.description,
      defaultRole: body.defaultRole,
    })

    return NextResponse.json(team, { status: 201 })
  } catch (error) {
    console.error('[API] Create team error:', error)
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: 'Failed to create team' } },
      { status: 500 }
    )
  }
}
