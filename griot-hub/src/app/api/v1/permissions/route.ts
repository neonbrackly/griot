import { NextRequest, NextResponse } from 'next/server'

const REGISTRY_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

// GET /api/v1/permissions - List all available permissions
export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get('Authorization')
    const response = await fetch(`${REGISTRY_URL}/permissions`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(authHeader ? { Authorization: authHeader } : {}),
      },
    })

    const data = await response.json()
    return NextResponse.json(data, { status: response.status })
  } catch (error) {
    console.error('[API Proxy] Get permissions error:', error)
    return NextResponse.json(
      { error: { code: 'PROXY_ERROR', message: 'Failed to connect to registry' } },
      { status: 502 }
    )
  }
}
