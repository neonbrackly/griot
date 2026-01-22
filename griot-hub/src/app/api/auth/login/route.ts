import { NextRequest, NextResponse } from 'next/server'

const REGISTRY_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
const USE_MOCKS = process.env.NEXT_PUBLIC_USE_MOCKS !== 'false'

interface LoginRequest {
  email: string
  password: string
  rememberMe?: boolean
}

export async function POST(request: NextRequest) {
  // If using real API, proxy to registry
  if (!USE_MOCKS) {
    try {
      const body = await request.json()

      const response = await fetch(`${REGISTRY_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      })

      const data = await response.json()
      return NextResponse.json(data, { status: response.status })
    } catch (error) {
      console.error('[API Proxy] Login error:', error)
      return NextResponse.json(
        { error: { code: 'PROXY_ERROR', message: 'Failed to connect to registry' } },
        { status: 502 }
      )
    }
  }

  // Mock implementation for development without registry
  try {
    const { getUserByEmail, generateMockToken, storeToken, updateLastLogin } = await import('@/lib/auth/mock-data')

    const body: LoginRequest = await request.json()

    // Validate required fields
    if (!body.email || !body.password) {
      return NextResponse.json(
        {
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Email and password are required',
            details: [
              ...(!body.email ? [{ field: 'email', message: 'Email is required' }] : []),
              ...(!body.password ? [{ field: 'password', message: 'Password is required' }] : []),
            ],
          },
        },
        { status: 422 }
      )
    }

    // Find user by email
    const userRecord = getUserByEmail(body.email)

    if (!userRecord || userRecord.password !== body.password) {
      return NextResponse.json(
        {
          error: {
            code: 'UNAUTHORIZED',
            message: 'Invalid email or password',
          },
        },
        { status: 401 }
      )
    }

    // Check if user is deactivated
    if (userRecord.user.status === 'deactivated') {
      return NextResponse.json(
        {
          error: {
            code: 'UNAUTHORIZED',
            message: 'Your account has been deactivated. Please contact an administrator.',
          },
        },
        { status: 401 }
      )
    }

    // Generate token
    const token = generateMockToken(userRecord.user)
    storeToken(token, userRecord.user)

    // Update last login
    updateLastLogin(body.email)

    return NextResponse.json({
      user: userRecord.user,
      token,
      expiresAt: new Date(Date.now() + 86400000).toISOString(), // 24 hours
    })
  } catch (error) {
    console.error('[API] Login error:', error)
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
