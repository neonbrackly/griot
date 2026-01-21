/**
 * Dashboard Service - Computes dashboard metrics from available registry API endpoints
 *
 * The griot-registry API doesn't have dedicated dashboard endpoints, so we compute
 * metrics from contracts, issues, validations, and runs endpoints.
 */

import { api } from './client'
import type {
  RegistryContractResponse,
  RegistryIssueResponse,
  RegistryRunResponse,
  RegistryValidationResponse,
  RegistryListResponse,
} from './adapters'
import type { DashboardMetrics, TimelineDay, Issue } from '@/types'

interface Recommendation {
  id: string
  type: 'action' | 'warning' | 'info'
  priority: 'high' | 'medium' | 'low'
  title: string
  description: string
  actionLabel: string
  actionHref: string
}

/**
 * Fetch dashboard metrics computed from available endpoints
 */
export async function fetchDashboardMetrics(): Promise<DashboardMetrics> {
  try {
    // Fetch contracts, issues, and validations in parallel
    const [contractsRes, issuesRes, validationsRes] = await Promise.all([
      api.get<RegistryListResponse<RegistryContractResponse>>('/contracts?limit=100'),
      api.get<RegistryListResponse<RegistryIssueResponse>>('/issues?limit=100'),
      api.get<RegistryListResponse<RegistryValidationResponse>>('/validations?limit=100'),
    ])

    const contracts = contractsRes.items || []
    const issues = issuesRes.items || []
    const validations = validationsRes.items || []

    // Compute contract stats
    const activeContracts = contracts.filter((c) => c.status === 'active').length
    const totalContracts = contracts.length
    const draftContracts = contracts.filter((c) => c.status === 'draft').length

    // Compute issue stats
    const openIssues = issues.filter((i) => i.status === 'open').length
    const criticalIssues = issues.filter((i) => i.status === 'open' && i.severity === 'error').length

    // Compute validation stats
    const passedValidations = validations.filter((v) => v.passed).length
    const totalValidations = validations.length
    const passRate = totalValidations > 0 ? (passedValidations / totalValidations) * 100 : 100

    // Compute health scores
    const complianceScore = Math.min(100, Math.round(passRate))
    const costScore = Math.min(100, Math.round(activeContracts > 0 ? 85 : 50)) // Placeholder
    const analyticsScore = Math.min(100, Math.round((activeContracts / Math.max(totalContracts, 1)) * 100))

    return {
      complianceHealth: {
        score: complianceScore,
        trend: passRate > 90 ? 5 : passRate > 70 ? 0 : -5,
        details: `${passedValidations}/${totalValidations} validations passed`,
      },
      costHealth: {
        score: costScore,
        trend: 2,
        details: `${activeContracts} active contracts`,
      },
      analyticsHealth: {
        score: analyticsScore,
        trend: draftContracts > 0 ? 3 : 0,
        details: `${draftContracts} contracts in draft`,
      },
      activeIssues: openIssues,
      criticalIssues,
      contractsRun: totalValidations,
      contractsPassed: passedValidations,
    }
  } catch (error) {
    console.error('Failed to fetch dashboard metrics:', error)
    // Return default metrics on error
    return {
      complianceHealth: { score: 0, trend: 0, details: 'Unable to load' },
      costHealth: { score: 0, trend: 0, details: 'Unable to load' },
      analyticsHealth: { score: 0, trend: 0, details: 'Unable to load' },
      activeIssues: 0,
      criticalIssues: 0,
      contractsRun: 0,
      contractsPassed: 0,
    }
  }
}

/**
 * Fetch timeline data for the past N days
 */
export async function fetchDashboardTimeline(days: number = 30): Promise<TimelineDay[]> {
  try {
    // Fetch runs and validations
    const [runsRes, validationsRes] = await Promise.all([
      api.get<RegistryListResponse<RegistryRunResponse>>('/runs?limit=100'),
      api.get<RegistryListResponse<RegistryValidationResponse>>('/validations?limit=100'),
    ])

    const runs = runsRes.items || []
    const validations = validationsRes.items || []

    // Generate timeline for the past N days
    const timeline: TimelineDay[] = []
    const now = new Date()

    for (let i = days - 1; i >= 0; i--) {
      const date = new Date(now)
      date.setDate(date.getDate() - i)
      const dateStr = date.toISOString().split('T')[0]

      // Count runs for this day
      const dayRuns = runs.filter((r) => r.created_at.startsWith(dateStr))
      const dayValidations = validations.filter((v) => v.recorded_at.startsWith(dateStr))

      const passed = dayValidations.filter((v) => v.passed).length
      const failed = dayValidations.filter((v) => !v.passed).length
      const total = dayRuns.length + dayValidations.length

      let status: TimelineDay['status'] = 'none'
      if (total > 0) {
        if (failed > 0) {
          status = 'failed'
        } else if (passed > 0) {
          status = 'passed'
        }
      }

      timeline.push({
        date: dateStr,
        status,
        runsCount: total,
        passedCount: passed,
        failedCount: failed,
      })
    }

    return timeline
  } catch (error) {
    console.error('Failed to fetch timeline:', error)
    // Return empty timeline
    return []
  }
}

/**
 * Generate recommendations based on current state
 */
export async function fetchRecommendations(): Promise<Recommendation[]> {
  try {
    // Fetch contracts and issues
    const [contractsRes, issuesRes] = await Promise.all([
      api.get<RegistryListResponse<RegistryContractResponse>>('/contracts?limit=50'),
      api.get<RegistryListResponse<RegistryIssueResponse>>('/issues?status=open&limit=10'),
    ])

    const contracts = contractsRes.items || []
    const issues = issuesRes.items || []

    const recommendations: Recommendation[] = []

    // Check for critical issues
    const criticalIssues = issues.filter((i) => i.severity === 'error')
    if (criticalIssues.length > 0) {
      recommendations.push({
        id: 'critical-issues',
        type: 'warning',
        priority: 'high',
        title: `${criticalIssues.length} critical issue${criticalIssues.length > 1 ? 's' : ''} need attention`,
        description: 'Critical issues can affect data quality and compliance. Review and resolve them.',
        actionLabel: 'Review Issues',
        actionHref: '/studio/issues?severity=critical',
      })
    }

    // Check for draft contracts
    const draftContracts = contracts.filter((c) => c.status === 'draft')
    if (draftContracts.length > 2) {
      recommendations.push({
        id: 'draft-contracts',
        type: 'action',
        priority: 'medium',
        title: `${draftContracts.length} contracts in draft status`,
        description: 'Review and activate draft contracts to improve governance coverage.',
        actionLabel: 'View Drafts',
        actionHref: '/studio/contracts?status=draft',
      })
    }

    // Check for deprecated contracts
    const deprecatedContracts = contracts.filter((c) => c.status === 'deprecated')
    if (deprecatedContracts.length > 0) {
      recommendations.push({
        id: 'deprecated-contracts',
        type: 'info',
        priority: 'low',
        title: `${deprecatedContracts.length} deprecated contract${deprecatedContracts.length > 1 ? 's' : ''}`,
        description: 'Consider retiring deprecated contracts or migrating to new versions.',
        actionLabel: 'View Deprecated',
        actionHref: '/studio/contracts?status=deprecated',
      })
    }

    // Add general recommendations if list is empty
    if (recommendations.length === 0) {
      if (contracts.length === 0) {
        recommendations.push({
          id: 'no-contracts',
          type: 'action',
          priority: 'high',
          title: 'Get started with your first contract',
          description: 'Create a data contract to establish data quality expectations.',
          actionLabel: 'Create Contract',
          actionHref: '/studio/contracts/new',
        })
      } else {
        recommendations.push({
          id: 'all-good',
          type: 'info',
          priority: 'low',
          title: 'Everything looks good!',
          description: 'Your contracts and data quality are in good shape.',
          actionLabel: 'View Contracts',
          actionHref: '/studio/contracts',
        })
      }
    }

    return recommendations
  } catch (error) {
    console.error('Failed to fetch recommendations:', error)
    return []
  }
}

/**
 * Fetch active issues for dashboard display
 */
export async function fetchActiveIssues(limit: number = 5): Promise<Issue[]> {
  try {
    const response = await api.get<RegistryListResponse<RegistryIssueResponse>>(
      `/issues?status=open&limit=${limit}`
    )

    return (response.items || []).map((issue) => ({
      id: issue.id,
      title: issue.title,
      description: issue.description || '',
      severity: issue.severity === 'error' ? 'critical' : issue.severity === 'warning' ? 'warning' : 'info',
      status: issue.status === 'resolved' ? 'resolved' : 'open',
      category: (issue.category as Issue['category']) || 'other',
      contractId: issue.contract_id,
      detectedAt: issue.created_at,
      createdAt: issue.created_at,
      updatedAt: issue.updated_at,
    })) as Issue[]
  } catch (error) {
    console.error('Failed to fetch active issues:', error)
    return []
  }
}
