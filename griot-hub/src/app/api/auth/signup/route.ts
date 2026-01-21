import { NextRequest, NextResponse } from 'next/server'
import {
  emailExists,
  createUser,
  generateMockToken,
  storeToken,
} from '@/lib/auth/mock-data'

interface SignupRequest {
  name: string
  email: string
  password: string
  confirmPassword: string
  acceptTerms?: boolean
}

export async function POST(request: NextRequest) {
  try {
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
