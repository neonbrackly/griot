import { http, HttpResponse, delay } from 'msw'
import { mockContracts, mockAssets, mockIssues, mockTeams } from '../data/mock-data'

export const searchHandlers = [
  // Global search
  http.get('/api/search', async ({ request }) => {
    await delay(200)

    const url = new URL(request.url)
    const query = url.searchParams.get('q')?.toLowerCase() || ''

    if (!query || query.length < 2) {
      return HttpResponse.json({
        contracts: [],
        assets: [],
        issues: [],
        teams: [],
      })
    }

    const contracts = mockContracts
      .filter(
        (c) =>
          c.name.toLowerCase().includes(query) ||
          c.description?.toLowerCase().includes(query) ||
          c.domain.toLowerCase().includes(query)
      )
      .slice(0, 5)
      .map((c) => ({
        id: c.id,
        name: c.name,
        type: 'contract' as const,
        href: `/studio/contracts/${c.id}`,
        description: c.description,
        domain: c.domain,
      }))

    const assets = mockAssets
      .filter(
        (a) =>
          a.name.toLowerCase().includes(query) ||
          a.description?.toLowerCase().includes(query) ||
          a.domain.toLowerCase().includes(query)
      )
      .slice(0, 5)
      .map((a) => ({
        id: a.id,
        name: a.name,
        type: 'asset' as const,
        href: `/studio/assets/${a.id}`,
        description: a.description,
        domain: a.domain,
      }))

    const issues = mockIssues
      .filter(
        (i) =>
          i.title.toLowerCase().includes(query) ||
          i.description.toLowerCase().includes(query)
      )
      .slice(0, 5)
      .map((i) => ({
        id: i.id,
        name: i.title,
        type: 'issue' as const,
        href: `/studio/issues/${i.id}`,
        description: i.description,
      }))

    const teams = mockTeams
      .filter(
        (t) =>
          t.name.toLowerCase().includes(query) ||
          t.description?.toLowerCase().includes(query)
      )
      .slice(0, 5)
      .map((t) => ({
        id: t.id,
        name: t.name,
        type: 'team' as const,
        href: `/marketplace/teams/${t.id}`,
        description: t.description,
      }))

    return HttpResponse.json({
      contracts,
      assets,
      issues,
      teams,
    })
  }),
]
