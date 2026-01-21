import { NextRequest, NextResponse } from 'next/server'
import {
  getUserByEmail,
  generateMockToken,
  storeToken,
  updateLastLogin,
} from '@/lib/auth/mock-data'

interface LoginRequest {
  email: string
  password: string
  rememberMe?: boolean
}

export async function POST(request: NextRequest) {
  try {
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
