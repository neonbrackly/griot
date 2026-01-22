import { NextRequest, NextResponse } from 'next/server'

const REGISTRY_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
const USE_MOCKS = process.env.NEXT_PUBLIC_USE_MOCKS !== 'false'

async function proxyRequest(request: NextRequest, method: string) {
  // Extract the path from the URL (everything after /api/v1/)
  const url = new URL(request.url)
  const pathMatch = url.pathname.match(/^\/api\/v1\/(.*)$/)
  const path = pathMatch ? pathMatch[1] : ''
  const queryString = url.search

  // If using mocks, return 501 Not Implemented (let MSW handle it)
  if (USE_MOCKS) {
    return NextResponse.json(
      { error: { code: 'NOT_IMPLEMENTED', message: 'Mock not available for this endpoint' } },
      { status: 501 }
    )
  }

  try {
    const targetUrl = `${REGISTRY_URL}/${path}${queryString}`

    // Forward headers (especially Authorization)
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    const authHeader = request.headers.get('Authorization')
    if (authHeader) {
      headers['Authorization'] = authHeader
    }

    // Build fetch options
    const fetchOptions: RequestInit = {
      method,
      headers,
    }

    // Include body for methods that support it
    if (['POST', 'PUT', 'PATCH'].includes(method)) {
      try {
        const body = await request.text()
        if (body) {
          fetchOptions.body = body
        }
      } catch {
        // No body to forward
      }
    }

    const response = await fetch(targetUrl, fetchOptions)

    // Handle 204 No Content
    if (response.status === 204) {
      return new NextResponse(null, { status: 204 })
    }

    // Forward the response
    const data = await response.json().catch(() => ({}))
    return NextResponse.json(data, { status: response.status })
  } catch (error) {
    console.error('[API Proxy] Error:', error)
    return NextResponse.json(
      { error: { code: 'PROXY_ERROR', message: 'Failed to connect to registry' } },
      { status: 502 }
    )
  }
}

export async function GET(request: NextRequest) {
  return proxyRequest(request, 'GET')
}

export async function POST(request: NextRequest) {
  return proxyRequest(request, 'POST')
}

export async function PUT(request: NextRequest) {
  return proxyRequest(request, 'PUT')
}

export async function PATCH(request: NextRequest) {
  return proxyRequest(request, 'PATCH')
}

export async function DELETE(request: NextRequest) {
  return proxyRequest(request, 'DELETE')
}
