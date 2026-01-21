'use client'

import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { Users, Shield, Building2, Activity, ArrowRight, Clock } from 'lucide-react'
import { api, queryKeys } from '@/lib/api/client'
import { PageContainer, PageHeader } from '@/components/layout'
import { Card } from '@/components/layout/Card'
import { Breadcrumbs } from '@/components/navigation/Breadcrumbs'
import type { BreadcrumbItem } from '@/components/navigation/Breadcrumbs'
import { Skeleton } from '@/components/feedback/Skeleton'
import { Button } from '@/components/ui/Button'
import type { User, Team, PaginatedResponse } from '@/types'

interface Role {
  id: string
  name: string
  userCount: number
}

const adminSections = [
  {
    title: 'User Management',
    description: 'Manage user accounts, invite new users, and assign roles',
    href: '/admin/users',
    icon: Users,
    color: 'blue',
  },
  {
    title: 'Team Management',
    description: 'Create teams, manage members, and assign domain ownership',
    href: '/admin/teams',
    icon: Building2,
    color: 'green',
  },
  {
    title: 'Roles & Permissions',
    description: 'Define roles and configure access control policies',
    href: '/admin/roles',
    icon: Shield,
    color: 'purple',
  },
]

const recentActivity = [
  {
    type: 'user_added',
    message: 'New user Jane Doe was added to Data Platform team',
    time: '2 hours ago',
    color: 'green',
  },
  {
    type: 'team_updated',
    message: 'Team CRM was updated with new domain ownership',
    time: '5 hours ago',
    color: 'blue',
  },
  {
    type: 'permission_changed',
    message: 'User permissions updated for John Smith',
    time: '1 day ago',
    color: 'yellow',
  },
  {
    type: 'role_created',
    message: 'New role "Team Lead" was created with custom permissions',
    time: '2 days ago',
    color: 'purple',
  },
]

function StatCard({
  icon: Icon,
  label,
  value,
  isLoading,
  color,
}: {
  icon: React.ElementType
  label: string
  value: number | string
  isLoading: boolean
  color: string
}) {
  const colorClasses = {
    blue: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
    green: 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400',
    purple: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400',
    orange: 'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400',
  }

  return (
    <Card className="p-6">
      <div className="flex items-center gap-4">
        <div className={`p-3 rounded-xl ${colorClasses[color as keyof typeof colorClasses]}`}>
          <Icon className="w-6 h-6" />
        </div>
        <div className="flex-1">
          <p className="text-sm font-medium text-text-tertiary">{label}</p>
          {isLoading ? (
            <Skeleton className="h-8 w-16 mt-1" />
          ) : (
            <p className="text-3xl font-bold text-text-primary">{value}</p>
          )}
        </div>
      </div>
    </Card>
  )
}

function SectionCard({
  title,
  description,
  href,
  icon: Icon,
  color,
}: {
  title: string
  description: string
  href: string
  icon: React.ElementType
  color: string
}) {
  const colorClasses = {
    blue: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 group-hover:bg-blue-200 dark:group-hover:bg-blue-900/50',
    green: 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 group-hover:bg-green-200 dark:group-hover:bg-green-900/50',
    purple: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 group-hover:bg-purple-200 dark:group-hover:bg-purple-900/50',
  }

  return (
    <Link href={href} className="group">
      <Card className="p-6 h-full hover:border-border-strong hover:shadow-md transition-all duration-200">
        <div className="flex flex-col h-full">
          <div className={`p-3 rounded-xl w-fit ${colorClasses[color as keyof typeof colorClasses]} transition-colors duration-200`}>
            <Icon className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-semibold text-text-primary mt-4 group-hover:text-primary-600 transition-colors">
            {title}
          </h3>
          <p className="text-sm text-text-secondary mt-2 flex-1">
            {description}
          </p>
          <div className="flex items-center gap-2 mt-4 text-sm font-medium text-primary-600 dark:text-primary-400">
            <span>Manage</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </div>
        </div>
      </Card>
    </Link>
  )
}

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

  const { data: rolesData, isLoading: rolesLoading } = useQuery({
    queryKey: ['roles'],
    queryFn: () => api.get<{ data: Role[] }>('/roles'),
  })

  const metrics = {
    users: usersData?.data?.length || 0,
    teams: teamsData?.data?.length || 0,
    roles: rolesData?.data?.length || 4,
    activeSessions: Math.floor((usersData?.data?.length || 0) * 0.6),
  }

  const isLoading = usersLoading || teamsLoading || rolesLoading

  return (
    <PageContainer className="space-y-8">
      <Breadcrumbs items={breadcrumbs} />

      <PageHeader
        title="Administration"
        description="Manage users, teams, and system settings"
      />

      {/* Quick Stats */}
      <section>
        <h2 className="text-sm font-semibold text-text-tertiary uppercase tracking-wider mb-4">
          Overview
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            icon={Users}
            label="Total Users"
            value={metrics.users}
            isLoading={isLoading}
            color="blue"
          />
          <StatCard
            icon={Building2}
            label="Teams"
            value={metrics.teams}
            isLoading={isLoading}
            color="green"
          />
          <StatCard
            icon={Shield}
            label="Roles"
            value={metrics.roles}
            isLoading={isLoading}
            color="purple"
          />
          <StatCard
            icon={Activity}
            label="Active Sessions"
            value={metrics.activeSessions}
            isLoading={isLoading}
            color="orange"
          />
        </div>
      </section>

      {/* Admin Sections */}
      <section>
        <h2 className="text-sm font-semibold text-text-tertiary uppercase tracking-wider mb-4">
          Manage
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {adminSections.map((section) => (
            <SectionCard
              key={section.href}
              title={section.title}
              description={section.description}
              href={section.href}
              icon={section.icon}
              color={section.color}
            />
          ))}
        </div>
      </section>

      {/* Recent Activity */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-text-tertiary uppercase tracking-wider">
            Recent Activity
          </h2>
          <Button variant="ghost" size="sm">
            View All
          </Button>
        </div>
        <Card className="divide-y divide-border-default">
          {recentActivity.map((activity, index) => (
            <div key={index} className="flex items-center gap-4 p-4">
              <div className={`w-2 h-2 rounded-full bg-${activity.color}-500 shrink-0`} />
              <p className="text-sm text-text-primary flex-1">{activity.message}</p>
              <div className="flex items-center gap-1.5 text-xs text-text-tertiary shrink-0">
                <Clock className="w-3.5 h-3.5" />
                <span>{activity.time}</span>
              </div>
            </div>
          ))}
        </Card>
      </section>
    </PageContainer>
  )
}
