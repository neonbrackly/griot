import { http, HttpResponse, delay } from 'msw'
import { mockNotifications } from '../data/mock-data'

export const notificationHandlers = [
  // List notifications
  http.get('/api/notifications', async ({ request }) => {
    await delay(200)

    const url = new URL(request.url)
    const limit = parseInt(url.searchParams.get('limit') || '10')

    const notifications = mockNotifications.slice(0, limit)

    return HttpResponse.json({
      data: notifications,
      unreadCount: notifications.filter((n) => !n.read).length,
    })
  }),

  // Mark notification as read
  http.patch('/api/notifications/:id/read', async ({ params }) => {
    await delay(200)

    const notification = mockNotifications.find((n) => n.id === params.id)
    if (!notification) {
      return new HttpResponse(null, { status: 404 })
    }

    return HttpResponse.json({ ...notification, read: true })
  }),

  // Mark all as read
  http.post('/api/notifications/read-all', async () => {
    await delay(300)
    return HttpResponse.json({ success: true })
  }),
]
