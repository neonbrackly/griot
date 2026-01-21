import { NextRequest, NextResponse } from 'next/server'
import { getRoleById, updateRole, deleteRole } from '@/lib/auth/mock-roles'

interface RouteParams {
  params: Promise<{ roleId: string }>
}

// GET /api/roles/:roleId - Get role details
export async function GET(request: NextRequest, { params }: RouteParams) {
  try {
    const { roleId } = await params
    const role = getRoleById(roleId)

    if (!role) {
      return NextResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Role not found' } },
        { status: 404 }
      )
    }

    return NextResponse.json(role)
  } catch (error) {
    console.error('[API] Get role error:', error)
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: 'Failed to fetch role' } },
      { status: 500 }
    )
  }
}

// PATCH /api/roles/:roleId - Update role
export async function PATCH(request: NextRequest, { params }: RouteParams) {
  try {
    const { roleId } = await params
    const body = await request.json()

    const role = updateRole(roleId, body)

    if (!role) {
      return NextResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Role not found or is a system role' } },
        { status: 404 }
      )
    }

    return NextResponse.json(role)
  } catch (error) {
    console.error('[API] Update role error:', error)
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: 'Failed to update role' } },
      { status: 500 }
    )
  }
}

// DELETE /api/roles/:roleId - Delete role
export async function DELETE(request: NextRequest, { params }: RouteParams) {
  try {
    const { roleId } = await params
    const deleted = deleteRole(roleId)

    if (!deleted) {
      return NextResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Role not found or is a system role' } },
        { status: 404 }
      )
    }

    return NextResponse.json({ message: 'Role deleted successfully' })
  } catch (error) {
    console.error('[API] Delete role error:', error)
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: 'Failed to delete role' } },
      { status: 500 }
    )
  }
}
