import { NextRequest, NextResponse } from 'next/server'

const REGISTRY_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

// GET /api/v1/users - List all users
export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get('Authorization')
    const url = new URL(request.url)
    const queryString = url.search

    const response = await fetch(`${REGISTRY_URL}/users${queryString}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(authHeader ? { Authorization: authHeader } : {}),
      },
    })

    const data = await response.json()
    return NextResponse.json(data, { status: response.status })
  } catch (error) {
    console.error('[API Proxy] Get users error:', error)
    return NextResponse.json(
      { error: { code: 'PROXY_ERROR', message: 'Failed to connect to registry' } },
      { status: 502 }
    )
  }
}
