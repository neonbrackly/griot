import { http, HttpResponse, delay } from 'msw'
import { mockMyTasks } from '../data/mock-data'

export const taskHandlers = [
  // Get my tasks
  http.get('/api/tasks/my', async () => {
    await delay(300)
    return HttpResponse.json(mockMyTasks)
  }),

  // Approve contract authorization
  http.post('/api/tasks/authorize/:id/approve', async ({ params }) => {
    await delay(500)
    const auth = mockMyTasks.authorizations.find((a) => a.id === params.id)
    if (!auth) {
      return new HttpResponse(null, { status: 404 })
    }
    return HttpResponse.json({ success: true, message: 'Contract approved' })
  }),

  // Reject contract authorization
  http.post('/api/tasks/authorize/:id/reject', async ({ params }) => {
    await delay(500)
    const auth = mockMyTasks.authorizations.find((a) => a.id === params.id)
    if (!auth) {
      return new HttpResponse(null, { status: 404 })
    }
    return HttpResponse.json({ success: true, message: 'Changes requested' })
  }),

  // Mark comment as reviewed
  http.post('/api/tasks/comments/:id/review', async ({ params }) => {
    await delay(300)
    const comment = mockMyTasks.comments.find((c) => c.id === params.id)
    if (!comment) {
      return new HttpResponse(null, { status: 404 })
    }
    return HttpResponse.json({ success: true })
  }),

  // Delete draft
  http.delete('/api/tasks/drafts/:id', async ({ params }) => {
    await delay(300)
    const draft = mockMyTasks.drafts.find((d) => d.id === params.id)
    if (!draft) {
      return new HttpResponse(null, { status: 404 })
    }
    return HttpResponse.json({ success: true })
  }),
]
