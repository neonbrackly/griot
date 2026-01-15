import { http, HttpResponse, delay } from 'msw'
import { mockUsers, mockCurrentUser } from '../data/mock-data'

export const userHandlers = [
  // Get current user
  http.get('/api/users/me', async () => {
    await delay(200)
    return HttpResponse.json(mockCurrentUser)
  }),

  // List all users
  http.get('/api/users', async ({ request }) => {
    await delay(300)

    const url = new URL(request.url)
    const search = url.searchParams.get('search')
    const role = url.searchParams.get('role')
    const status = url.searchParams.get('status')

    let filtered = [...mockUsers]

    if (search) {
      const searchLower = search.toLowerCase()
      filtered = filtered.filter(
        (u) =>
          u.name.toLowerCase().includes(searchLower) ||
          u.email.toLowerCase().includes(searchLower)
      )
    }

    if (role && role !== 'all') {
      filtered = filtered.filter((u) => u.role === role)
    }

    if (status && status !== 'all') {
      filtered = filtered.filter((u) => u.status === status)
    }

    return HttpResponse.json({
      data: filtered,
      meta: {
        total: filtered.length,
        page: 1,
        pageSize: 20,
        totalPages: 1,
      },
    })
  }),

  // Get user by ID
  http.get('/api/users/:id', async ({ params }) => {
    await delay(200)

    const user = mockUsers.find((u) => u.id === params.id)
    if (!user) {
      return new HttpResponse(null, { status: 404 })
    }

    return HttpResponse.json(user)
  }),

  // Update user
  http.patch('/api/users/:id', async ({ params, request }) => {
    await delay(300)

    const user = mockUsers.find((u) => u.id === params.id)
    if (!user) {
      return new HttpResponse(null, { status: 404 })
    }

    const body = (await request.json()) as Record<string, unknown>
    const updated = {
      ...user,
      ...body,
      updatedAt: new Date().toISOString(),
    }

    return HttpResponse.json(updated)
  }),

  // Create user (invite)
  http.post('/api/users/invite', async ({ request }) => {
    await delay(500)

    const body = (await request.json()) as Record<string, unknown>
    const newUser = {
      id: `user-${Date.now()}`,
      name: body.name as string,
      email: body.email as string,
      role: body.role as string,
      teamId: body.teamId as string,
      status: 'pending' as const,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }

    return HttpResponse.json(newUser, { status: 201 })
  }),

  // Deactivate user
  http.post('/api/users/:id/deactivate', async ({ params }) => {
    await delay(300)

    const user = mockUsers.find((u) => u.id === params.id)
    if (!user) {
      return new HttpResponse(null, { status: 404 })
    }

    return HttpResponse.json({ success: true })
  }),
]
