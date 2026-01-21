import { NextRequest, NextResponse } from 'next/server'
import { getAllRoles, createRole } from '@/lib/auth/mock-roles'

// GET /api/roles - List all roles
export async function GET() {
  try {
    const roles = getAllRoles()
    return NextResponse.json({ data: roles })
  } catch (error) {
    console.error('[API] Get roles error:', error)
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: 'Failed to fetch roles' } },
      { status: 500 }
    )
  }
}

// POST /api/roles - Create a new role
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    if (!body.name) {
      return NextResponse.json(
        { error: { code: 'VALIDATION_ERROR', message: 'Role name is required' } },
        { status: 422 }
      )
    }

    if (!body.permissions || !Array.isArray(body.permissions)) {
      return NextResponse.json(
        { error: { code: 'VALIDATION_ERROR', message: 'Permissions array is required' } },
        { status: 422 }
      )
    }

    const role = createRole({
      name: body.name,
      description: body.description,
      permissions: body.permissions,
    })

    return NextResponse.json(role, { status: 201 })
  } catch (error) {
    console.error('[API] Create role error:', error)
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: 'Failed to create role' } },
      { status: 500 }
    )
  }
}
