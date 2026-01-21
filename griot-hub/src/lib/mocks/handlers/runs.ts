import { http, HttpResponse, delay } from 'msw'
import { mockContracts } from '../data/mock-data'
import type { ContractRun } from '@/types'

// Generate mock runs for a specific date
function generateRunsForDate(date: string): ContractRun[] {
  return mockContracts.slice(0, 5).map((contract, index) => {
    const statuses: Array<'passed' | 'warning' | 'failed'> = ['passed', 'passed', 'warning', 'failed']
    const status = statuses[index % statuses.length]
    const duration = Math.floor(Math.random() * 300) + 30 // 30-330 seconds

    const totalRules = Math.floor(Math.random() * 10) + 5
    const failed = status === 'failed' ? Math.floor(Math.random() * 3) + 1 : 0
    const warnings = status === 'warning' ? Math.floor(Math.random() * 3) + 1 : 0
    const passed = totalRules - failed - warnings

    return {
      id: `run-${date}-${contract.id}`,
      contractId: contract.id,
      status,
      startedAt: `${date}T02:00:00Z`,
      completedAt: `${date}T02:${String(Math.floor(duration / 60)).padStart(2, '0')}:${String(duration % 60).padStart(2, '0')}Z`,
      duration,
      ruleResults: [],
      summary: {
        totalRules,
        passed,
        failed,
        warnings,
      },
      createdAt: `${date}T02:00:00Z`,
      updatedAt: `${date}T02:00:00Z`,
    }
  })
}

export const runHandlers = [
  // Get runs for a specific date
  http.get('/api/runs/:date', async ({ params }) => {
    await delay(300)

    const { date } = params
    const runs = generateRunsForDate(date as string)

    // Calculate summary stats
    const totalRuns = runs.length
    const passedRuns = runs.filter((r) => r.status === 'passed').length
    const warningRuns = runs.filter((r) => r.status === 'warning').length
    const failedRuns = runs.filter((r) => r.status === 'failed').length
    const totalDuration = runs.reduce((sum, r) => sum + (r.duration || 0), 0)

    // Find earliest start and latest completion
    const startTimes = runs.map((r) => new Date(r.startedAt).getTime())
    const endTimes = runs
      .filter((r) => r.completedAt)
      .map((r) => new Date(r.completedAt!).getTime())

    const startedAt = new Date(Math.min(...startTimes)).toISOString()
    const completedAt = new Date(Math.max(...endTimes)).toISOString()

    return HttpResponse.json({
      date,
      summary: {
        total: totalRuns,
        passed: passedRuns,
        warnings: warningRuns,
        failed: failedRuns,
        duration: totalDuration,
        startedAt,
        completedAt,
      },
      runs,
    })
  }),

  // Get run detail by ID
  http.get('/api/runs/:date/:runId', async ({ params }) => {
    await delay(200)

    const { date, runId } = params
    const runs = generateRunsForDate(date as string)
    const run = runs.find((r) => r.id === runId)

    if (!run) {
      return new HttpResponse(null, { status: 404 })
    }

    return HttpResponse.json(run)
  }),
]
