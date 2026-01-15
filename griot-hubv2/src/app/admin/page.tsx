'use client'

import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { Users, Shield, Building2, Activity } from 'lucide-react'
import { api, queryKeys } from '@/lib/api/client'
import { PageContainer, PageHeader } from '@/components/layout'
import { Card } from '@/components/layout/Card'
import { Breadcrumbs } from '@/components/navigation/Breadcrumbs'
import type { BreadcrumbItem } from '@/components/navigation/Breadcrumbs'
import { Skeleton } from '@/components/feedback/Skeleton'
import type { User, Team, PaginatedResponse } from '@/types'

const adminItems = [
  {
    title: 'User Management',
    description: 'Manage user accounts, roles, and permissions',
    href: '/admin/users',
    icon: Users,
    metric: 'users',
  },
  {
    title: 'Team Management',
    description: 'Organize teams and domain ownership',
    href: '/admin/teams',
    icon: Building2,
    metric: 'teams',
  },
  {
    title: 'Roles & Permissions',
    description: 'Configure access control policies',
    href: '/admin/roles',
    icon: Shield,
    metric: 'roles',
  },
]

export default function AdminPage() {
  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Administration' },
  ]

  const { data: usersData, isLoading: usersLoading } = useQuery({
    queryKey: queryKeys.users.list(),
    queryFn: () => api.get<PaginatedResponse<User>>('/users'),
  })

  const { data: teamsData, isLoading: teamsLoading } = useQuery({
    queryKey: queryKeys.teams.all,
    queryFn: () => api.get<{ data: Team[] }>('/teams'),
  })

  const metrics = {
    users: usersData?.data?.length || 0,
    teams: teamsData?.data?.length || 0,
    roles: 4, // Fixed for now: admin, manager, member, viewer
  }

  const isLoading = usersLoading || teamsLoading

  return (
    <PageContainer>
      <Breadcrumbs items={breadcrumbs} />
      <PageHeader
        title="Administration"
        description="Manage users, teams, and system settings"
      />

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-lg bg-blue-100 dark:bg-blue-900/30">
              <Users className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <p className="text-sm text-text-tertiary">Total Users</p>
              {isLoading ? (
                <Skeleton className="h-8 w-12" />
              ) : (
                <p className="text-2xl font-semibold text-text-primary">
                  {metrics.users}
                </p>
              )}
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-lg bg-green-100 dark:bg-green-900/30">
              <Building2 className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <p className="text-sm text-text-tertiary">Teams</p>
              {isLoading ? (
                <Skeleton className="h-8 w-12" />
              ) : (
                <p className="text-2xl font-semibold text-text-primary">
                  {metrics.teams}
                </p>
              )}
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-lg bg-purple-100 dark:bg-purple-900/30">
              <Shield className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <p className="text-sm text-text-tertiary">Roles</p>
              <p className="text-2xl font-semibold text-text-primary">
                {metrics.roles}
              </p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-lg bg-orange-100 dark:bg-orange-900/30">
              <Activity className="w-6 h-6 text-orange-600 dark:text-orange-400" />
            </div>
            <div>
              <p className="text-sm text-text-tertiary">Active Sessions</p>
              <p className="text-2xl font-semibold text-text-primary">
                {isLoading ? '-' : Math.floor(metrics.users * 0.6)}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Admin Sections */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {adminItems.map((item) => {
          const Icon = item.icon
          return (
            <Link key={item.href} href={item.href}>
              <Card className="p-6 hover:border-border-strong transition-colors h-full">
                <div className="flex flex-col h-full">
                  <div className="flex items-center justify-between mb-4">
                    <div className="p-3 rounded-lg bg-primary-100 dark:bg-primary-900/30">
                      <Icon className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                    </div>
                    {isLoading ? (
                      <Skeleton className="h-6 w-8" />
                    ) : (
                      <span className="text-2xl font-semibold text-text-primary">
                        {metrics[item.metric as keyof typeof metrics]}
                      </span>
                    )}
                  </div>
                  <h3 className="font-semibold text-text-primary">{item.title}</h3>
                  <p className="text-sm text-text-secondary mt-1">
                    {item.description}
                  </p>
                </div>
              </Card>
            </Link>
          )
        })}
      </div>

      {/* Recent Activity Placeholder */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-text-primary mb-4">Recent Activity</h3>
        <div className="space-y-4">
          <div className="flex items-center gap-4 text-sm">
            <div className="w-2 h-2 rounded-full bg-green-500" />
            <span className="text-text-primary">New user Jane Doe was added to Data Platform team</span>
            <span className="text-text-tertiary ml-auto">2 hours ago</span>
          </div>
          <div className="flex items-center gap-4 text-sm">
            <div className="w-2 h-2 rounded-full bg-blue-500" />
            <span className="text-text-primary">Team CRM was updated with new domain ownership</span>
            <span className="text-text-tertiary ml-auto">5 hours ago</span>
          </div>
          <div className="flex items-center gap-4 text-sm">
            <div className="w-2 h-2 rounded-full bg-yellow-500" />
            <span className="text-text-primary">User permissions updated for John Smith</span>
            <span className="text-text-tertiary ml-auto">1 day ago</span>
          </div>
        </div>
      </Card>
    </PageContainer>
  )
}
