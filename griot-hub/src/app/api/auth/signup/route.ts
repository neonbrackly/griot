import { NextRequest, NextResponse } from 'next/server'

const REGISTRY_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
const USE_MOCKS = process.env.NEXT_PUBLIC_USE_MOCKS !== 'false'

interface SignupRequest {
  name: string
  email: string
  password: string
  confirmPassword: string
  acceptTerms?: boolean
}

export async function POST(request: NextRequest) {
  // If using real API, proxy to registry
  if (!USE_MOCKS) {
    try {
      const body = await request.json()

      const response = await fetch(`${REGISTRY_URL}/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      })

      const data = await response.json()
      return NextResponse.json(data, { status: response.status })
    } catch (error) {
      console.error('[API Proxy] Signup error:', error)
      return NextResponse.json(
        { error: { code: 'PROXY_ERROR', message: 'Failed to connect to registry' } },
        { status: 502 }
      )
    }
  }

  // Mock implementation for development without registry
  try {
    const { emailExists, createUser, generateMockToken, storeToken } = await import('@/lib/auth/mock-data')

    const body: SignupRequest = await request.json()

    // Validate required fields
    const errors: Array<{ field: string; message: string }> = []
    if (!body.name) errors.push({ field: 'name', message: 'Name is required' })
    if (!body.email) errors.push({ field: 'email', message: 'Email is required' })
    if (!body.password) errors.push({ field: 'password', message: 'Password is required' })
    if (body.password !== body.confirmPassword) {
      errors.push({ field: 'confirmPassword', message: 'Passwords do not match' })
    }
    if (body.password && body.password.length < 8) {
      errors.push({ field: 'password', message: 'Password must be at least 8 characters' })
    }

    if (errors.length > 0) {
      return NextResponse.json(
        {
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Validation failed',
            details: errors,
          },
        },
        { status: 422 }
      )
    }

    // Check if email already exists
    if (emailExists(body.email)) {
      return NextResponse.json(
        {
          error: {
            code: 'CONFLICT',
            message: 'An account with this email already exists',
          },
        },
        { status: 409 }
      )
    }

    // Create new user
    const newUser = createUser(body.email, body.password, body.name)

    // Generate token
    const token = generateMockToken(newUser)
    storeToken(token, newUser)

    return NextResponse.json(
      {
        user: newUser,
        token,
        expiresAt: new Date(Date.now() + 86400000).toISOString(),
      },
      { status: 201 }
    )
  } catch (error) {
    console.error('[API] Signup error:', error)
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
