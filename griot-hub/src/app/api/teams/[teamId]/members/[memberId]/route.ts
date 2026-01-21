import { NextRequest, NextResponse } from 'next/server'
import { removeTeamMember, updateMemberRole } from '@/lib/auth/mock-teams'

interface RouteParams {
  params: Promise<{ teamId: string; memberId: string }>
}

// PATCH /api/teams/:teamId/members/:memberId - Update member role
export async function PATCH(request: NextRequest, { params }: RouteParams) {
  try {
    const { teamId, memberId } = await params
    const body = await request.json()

    if (!body.role) {
      return NextResponse.json(
        { error: { code: 'VALIDATION_ERROR', message: 'Role is required' } },
        { status: 422 }
      )
    }

    const member = updateMemberRole(teamId, memberId, body.role)

    if (!member) {
      return NextResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Team or member not found' } },
        { status: 404 }
      )
    }

    return NextResponse.json(member)
  } catch (error) {
    console.error('[API] Update member role error:', error)
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: 'Failed to update member role' } },
      { status: 500 }
    )
  }
}

// DELETE /api/teams/:teamId/members/:memberId - Remove member from team
export async function DELETE(request: NextRequest, { params }: RouteParams) {
  try {
    const { teamId, memberId } = await params
    const deleted = removeTeamMember(teamId, memberId)

    if (!deleted) {
      return NextResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Team or member not found' } },
        { status: 404 }
      )
    }

    return NextResponse.json({ message: 'Member removed successfully' })
  } catch (error) {
    console.error('[API] Remove team member error:', error)
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: 'Failed to remove team member' } },
      { status: 500 }
    )
  }
}
