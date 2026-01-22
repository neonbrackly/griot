import { NextRequest, NextResponse } from 'next/server'

const REGISTRY_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
const USE_MOCKS = process.env.NEXT_PUBLIC_USE_MOCKS !== 'false'

export async function POST(request: NextRequest) {
  // If using real API, proxy to registry
  if (!USE_MOCKS) {
    try {
      const authHeader = request.headers.get('Authorization')

      const response = await fetch(`${REGISTRY_URL}/auth/logout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(authHeader ? { Authorization: authHeader } : {}),
        },
      })

      // Registry returns 204 No Content
      if (response.status === 204) {
        return new NextResponse(null, { status: 204 })
      }

      const data = await response.json()
      return NextResponse.json(data, { status: response.status })
    } catch (error) {
      console.error('[API Proxy] Logout error:', error)
      return NextResponse.json(
        { error: { code: 'PROXY_ERROR', message: 'Failed to connect to registry' } },
        { status: 502 }
      )
    }
  }

  // Mock implementation
  try {
    const { removeToken } = await import('@/lib/auth/mock-data')

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
