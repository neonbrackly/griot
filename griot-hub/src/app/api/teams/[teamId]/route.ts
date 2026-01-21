import { NextRequest, NextResponse } from 'next/server'
import { getTeamById, updateTeam, deleteTeam } from '@/lib/auth/mock-teams'

interface RouteParams {
  params: Promise<{ teamId: string }>
}

// GET /api/teams/:teamId - Get team details with members
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

    return NextResponse.json(team)
  } catch (error) {
    console.error('[API] Get team error:', error)
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: 'Failed to fetch team' } },
      { status: 500 }
    )
  }
}

// PATCH /api/teams/:teamId - Update team
export async function PATCH(request: NextRequest, { params }: RouteParams) {
  try {
    const { teamId } = await params
    const body = await request.json()

    const team = updateTeam(teamId, body)

    if (!team) {
      return NextResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Team not found' } },
        { status: 404 }
      )
    }

    return NextResponse.json(team)
  } catch (error) {
    console.error('[API] Update team error:', error)
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: 'Failed to update team' } },
      { status: 500 }
    )
  }
}

// DELETE /api/teams/:teamId - Delete team
export async function DELETE(request: NextRequest, { params }: RouteParams) {
  try {
    const { teamId } = await params
    const deleted = deleteTeam(teamId)

    if (!deleted) {
      return NextResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Team not found' } },
        { status: 404 }
      )
    }

    return NextResponse.json({ message: 'Team deleted successfully' })
  } catch (error) {
    console.error('[API] Delete team error:', error)
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: 'Failed to delete team' } },
      { status: 500 }
    )
  }
}
