import { http, HttpResponse, delay } from 'msw'
import { mockTeams } from '../data/mock-data'

export const teamHandlers = [
  // List teams
  http.get('/api/teams', async () => {
    await delay(200)
    return HttpResponse.json(mockTeams)
  }),

  // Get single team
  http.get('/api/teams/:id', async ({ params }) => {
    await delay(150)

    const team = mockTeams.find((t) => t.id === params.id)
    if (!team) {
      return new HttpResponse(null, { status: 404 })
    }

    return HttpResponse.json(team)
  }),

  // Create team
  http.post('/api/teams', async ({ request }) => {
    await delay(300)

    const body = (await request.json()) as Record<string, unknown>
    const newTeam = {
      id: `team-${Date.now()}`,
      ...body,
      memberCount: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }

    return HttpResponse.json(newTeam, { status: 201 })
  }),
]
