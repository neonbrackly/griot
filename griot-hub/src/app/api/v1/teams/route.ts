import { NextRequest, NextResponse } from 'next/server'

const REGISTRY_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

// GET /api/v1/teams - List all teams
export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get('Authorization')
    const response = await fetch(`${REGISTRY_URL}/teams`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(authHeader ? { Authorization: authHeader } : {}),
      },
    })

    const data = await response.json()
    return NextResponse.json(data, { status: response.status })
  } catch (error) {
    console.error('[API Proxy] Get teams error:', error)
    return NextResponse.json(
      { error: { code: 'PROXY_ERROR', message: 'Failed to connect to registry' } },
      { status: 502 }
    )
  }
}

// POST /api/v1/teams - Create a new team
export async function POST(request: NextRequest) {
  try {
    const authHeader = request.headers.get('Authorization')
    const body = await request.json()

    const response = await fetch(`${REGISTRY_URL}/teams`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(authHeader ? { Authorization: authHeader } : {}),
      },
      body: JSON.stringify(body),
    })

    const data = await response.json()
    return NextResponse.json(data, { status: response.status })
  } catch (error) {
    console.error('[API Proxy] Create team error:', error)
    return NextResponse.json(
      { error: { code: 'PROXY_ERROR', message: 'Failed to connect to registry' } },
      { status: 502 }
    )
  }
}
