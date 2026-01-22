import { NextRequest, NextResponse } from 'next/server'

const REGISTRY_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
const USE_MOCKS = process.env.NEXT_PUBLIC_USE_MOCKS !== 'false'

export async function GET(request: NextRequest) {
  // If using real API, proxy to registry
  if (!USE_MOCKS) {
    try {
      const authHeader = request.headers.get('Authorization')

      if (!authHeader) {
        return NextResponse.json(
          { error: { code: 'UNAUTHORIZED', message: 'Not authenticated' } },
          { status: 401 }
        )
      }

      const response = await fetch(`${REGISTRY_URL}/auth/me`, {
        method: 'GET',
        headers: {
          Authorization: authHeader,
        },
      })

      const data = await response.json()
      return NextResponse.json(data, { status: response.status })
    } catch (error) {
      console.error('[API Proxy] Get me error:', error)
      return NextResponse.json(
        { error: { code: 'PROXY_ERROR', message: 'Failed to connect to registry' } },
        { status: 502 }
      )
    }
  }

  // Mock implementation
  try {
    const { getUserFromToken } = await import('@/lib/auth/mock-data')

    const authHeader = request.headers.get('Authorization')

    if (!authHeader?.startsWith('Bearer ')) {
      return NextResponse.json(
        {
          error: {
            code: 'UNAUTHORIZED',
            message: 'Not authenticated',
          },
        },
        { status: 401 }
      )
    }

    const token = authHeader.substring(7)
    const user = getUserFromToken(token)

    if (!user) {
      return NextResponse.json(
        {
          error: {
            code: 'UNAUTHORIZED',
            message: 'Invalid or expired token',
          },
        },
        { status: 401 }
      )
    }

    return NextResponse.json(user)
  } catch (error) {
    console.error('[API] Get current user error:', error)
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
