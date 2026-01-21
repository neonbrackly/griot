import { http, HttpResponse, delay } from 'msw'
import { mockIssues } from '../data/mock-data'

export const issueHandlers = [
  // List issues
  http.get('/api/issues', async ({ request }) => {
    await delay(300)

    const url = new URL(request.url)
    const severity = url.searchParams.get('severity')
    const status = url.searchParams.get('status')
    const search = url.searchParams.get('search')

    let filtered = [...mockIssues]

    if (severity && severity !== 'all') {
      filtered = filtered.filter((i) => i.severity === severity)
    }

    if (status && status !== 'all') {
      filtered = filtered.filter((i) => i.status === status)
    }

    if (search) {
      const searchLower = search.toLowerCase()
      filtered = filtered.filter(
        (i) =>
          i.title.toLowerCase().includes(searchLower) ||
          i.description.toLowerCase().includes(searchLower)
      )
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

  // Get single issue
  http.get('/api/issues/:id', async ({ params }) => {
    await delay(200)

    const issue = mockIssues.find((i) => i.id === params.id)
    if (!issue) {
      return new HttpResponse(null, { status: 404 })
    }

    return HttpResponse.json(issue)
  }),

  // Update issue
  http.patch('/api/issues/:id', async ({ params, request }) => {
    await delay(300)

    const issue = mockIssues.find((i) => i.id === params.id)
    if (!issue) {
      return new HttpResponse(null, { status: 404 })
    }

    const body = (await request.json()) as Record<string, unknown>
    const updated = {
      ...issue,
      ...body,
      updatedAt: new Date().toISOString(),
    }

    return HttpResponse.json(updated)
  }),
]
