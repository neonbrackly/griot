import { http, HttpResponse, delay } from 'msw'
import { mockAssets } from '../data/mock-data'

export const assetHandlers = [
  // List assets
  http.get('/api/assets', async ({ request }) => {
    await delay(300)

    const url = new URL(request.url)
    const status = url.searchParams.get('status')
    const search = url.searchParams.get('search')
    const page = parseInt(url.searchParams.get('page') || '1')
    const pageSize = parseInt(url.searchParams.get('pageSize') || '20')

    let filtered = [...mockAssets]

    if (status && status !== 'all') {
      filtered = filtered.filter((a) => a.status === status)
    }

    if (search) {
      const searchLower = search.toLowerCase()
      filtered = filtered.filter(
        (a) =>
          a.name.toLowerCase().includes(searchLower) ||
          a.description?.toLowerCase().includes(searchLower)
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

  // Get single asset
  http.get('/api/assets/:id', async ({ params }) => {
    await delay(200)

    const asset = mockAssets.find((a) => a.id === params.id)

    if (!asset) {
      return new HttpResponse(null, { status: 404 })
    }

    return HttpResponse.json(asset)
  }),

  // Create asset
  http.post('/api/assets', async ({ request }) => {
    await delay(500)

    const body = (await request.json()) as Record<string, unknown>
    const newAsset = {
      id: `asset-${Date.now()}`,
      ...body,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }

    return HttpResponse.json(newAsset, { status: 201 })
  }),

  // Sync asset schema
  http.post('/api/assets/:id/sync', async ({ params }) => {
    await delay(1500)

    const asset = mockAssets.find((a) => a.id === params.id)
    if (!asset) {
      return new HttpResponse(null, { status: 404 })
    }

    return HttpResponse.json({
      ...asset,
      lastSyncedAt: new Date().toISOString(),
    })
  }),
]
