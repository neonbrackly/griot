import { NextResponse } from 'next/server'
import { getAllPermissions, getPermissionsByCategory } from '@/lib/auth/mock-roles'

// GET /api/permissions - List all permissions
export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const grouped = searchParams.get('grouped') === 'true'

    if (grouped) {
      const permissionsByCategory = getPermissionsByCategory()
      return NextResponse.json({ data: permissionsByCategory })
    }

    const permissions = getAllPermissions()
    return NextResponse.json({ data: permissions })
  } catch (error) {
    console.error('[API] Get permissions error:', error)
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: 'Failed to fetch permissions' } },
      { status: 500 }
    )
  }
}
