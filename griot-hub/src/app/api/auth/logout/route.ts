import { NextRequest, NextResponse } from 'next/server'
import { removeToken } from '@/lib/auth/mock-data'

export async function POST(request: NextRequest) {
  try {
    const authHeader = request.headers.get('Authorization')
    if (authHeader?.startsWith('Bearer ')) {
      const token = authHeader.substring(7)
      removeToken(token)
    }

    return NextResponse.json({ message: 'Logged out successfully' })
  } catch (error) {
    console.error('[API] Logout error:', error)
    return NextResponse.json(
      {
        error: {
          code: 'INTERNAL_ERROR',
          message: 'An unexpected error occurred',
        },
      },
      { status: 500 }
    )
  }
}
