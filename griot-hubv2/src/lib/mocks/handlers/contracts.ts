import { http, HttpResponse, delay } from 'msw'
import { mockContracts } from '../data/mock-data'

export const contractHandlers = [
  // List contracts
  http.get('/api/contracts', async ({ request }) => {
    await delay(300)

    const url = new URL(request.url)
    const status = url.searchParams.get('status')
    const search = url.searchParams.get('search')
    const page = parseInt(url.searchParams.get('page') || '1')
    const pageSize = parseInt(url.searchParams.get('pageSize') || '20')

    let filtered = [...mockContracts]

    if (status && status !== 'all') {
      filtered = filtered.filter((c) => c.status === status)
    }

    if (search) {
      const searchLower = search.toLowerCase()
      filtered = filtered.filter(
        (c) =>
          c.name.toLowerCase().includes(searchLower) ||
          c.description?.toLowerCase().includes(searchLower)
      )
    }

    const total = filtered.length
    const start = (page - 1) * pageSize
    const data = filtered.slice(start, start + pageSize)

    return HttpResponse.json({
      data,
      meta: {
        total,
        page,
        pageSize,
        totalPages: Math.ceil(total / pageSize),
      },
    })
  }),

  // Get single contract
  http.get('/api/contracts/:id', async ({ params }) => {
    await delay(200)

    const contract = mockContracts.find((c) => c.id === params.id)

    if (!contract) {
      return new HttpResponse(null, { status: 404 })
    }

    return HttpResponse.json(contract)
  }),

  // Create contract
  http.post('/api/contracts', async ({ request }) => {
    await delay(500)

    const body = (await request.json()) as Record<string, unknown>
    const newContract = {
      id: `contract-${Date.now()}`,
      ...body,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }

    return HttpResponse.json(newContract, { status: 201 })
  }),

  // Update contract
  http.patch('/api/contracts/:id', async ({ params, request }) => {
    await delay(300)

    const contract = mockContracts.find((c) => c.id === params.id)
    if (!contract) {
      return new HttpResponse(null, { status: 404 })
    }

    const body = (await request.json()) as Record<string, unknown>
    const updated = {
      ...contract,
      ...body,
      updatedAt: new Date().toISOString(),
    }

    return HttpResponse.json(updated)
  }),

  // Run contract checks
  http.post('/api/contracts/:id/run', async ({ params }) => {
    await delay(1000)

    return HttpResponse.json({
      id: `run-${Date.now()}`,
      contractId: params.id,
      status: 'passed',
      startedAt: new Date().toISOString(),
      completedAt: new Date().toISOString(),
      ruleResults: [],
      summary: {
        totalRules: 5,
        passed: 5,
        failed: 0,
        warnings: 0,
      },
    })
  }),
]
