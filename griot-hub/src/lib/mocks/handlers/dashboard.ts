import { http, HttpResponse, delay } from 'msw'
import { mockDashboardMetrics, generateTimeline } from '../data/mock-data'

export const dashboardHandlers = [
  // Get dashboard metrics
  http.get('/api/dashboard/metrics', async () => {
    await delay(300)
    return HttpResponse.json(mockDashboardMetrics)
  }),

  // Get timeline data
  http.get('/api/dashboard/timeline', async ({ request }) => {
    await delay(200)

    const url = new URL(request.url)
    const days = parseInt(url.searchParams.get('days') || '30')

    return HttpResponse.json(generateTimeline(days))
  }),

  // Get recommendations
  http.get('/api/dashboard/recommendations', async () => {
    await delay(250)

    return HttpResponse.json([
      {
        id: 'rec-1',
        type: 'action',
        priority: 'high',
        title: '3 contracts pending review for more than 7 days',
        description: 'Consider reviewing and approving or rejecting these contracts.',
        actionLabel: 'View pending contracts',
        actionHref: '/studio/contracts?status=pending_review',
      },
      {
        id: 'rec-2',
        type: 'warning',
        priority: 'medium',
        title: 'High null rate in customer_events.email',
        description: '32% of records have null email values.',
        actionLabel: 'View issue',
        actionHref: '/studio/issues/issue-1',
      },
      {
        id: 'rec-3',
        type: 'info',
        priority: 'low',
        title: '2 potential duplicate assets detected',
        description: 'customer_data and Customer360 may be redundant.',
        actionLabel: 'Compare assets',
        actionHref: '/studio/assets?compare=asset-1,asset-2',
      },
    ])
  }),
]
