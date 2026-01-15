'use client'

import Link from 'next/link'
import { User, Bell, Key, Shield } from 'lucide-react'
import { PageContainer, PageHeader } from '@/components/layout'
import { Card } from '@/components/layout/Card'
import { Breadcrumbs } from '@/components/navigation/Breadcrumbs'
import type { BreadcrumbItem } from '@/components/navigation/Breadcrumbs'

const settingsItems = [
  {
    title: 'Profile',
    description: 'Manage your personal information and preferences',
    href: '/settings/profile',
    icon: User,
  },
  {
    title: 'Notifications',
    description: 'Configure how you receive notifications',
    href: '/settings/notifications',
    icon: Bell,
  },
  {
    title: 'API & Integrations',
    description: 'Manage API keys and external integrations',
    href: '/settings/integrations',
    icon: Key,
  },
]

export default function SettingsPage() {
  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Settings' },
  ]

  return (
    <PageContainer maxWidth="xl">
      <Breadcrumbs items={breadcrumbs} />
      <PageHeader
        title="Settings"
        description="Manage your account and preferences"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {settingsItems.map((item) => {
          const Icon = item.icon
          return (
            <Link key={item.href} href={item.href}>
              <Card className="p-6 hover:border-border-strong transition-colors h-full">
                <div className="flex items-start gap-4">
                  <div className="p-3 rounded-lg bg-primary-100 dark:bg-primary-900/30">
                    <Icon className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-text-primary">{item.title}</h3>
                    <p className="text-sm text-text-secondary mt-1">
                      {item.description}
                    </p>
                  </div>
                </div>
              </Card>
            </Link>
          )
        })}
      </div>
    </PageContainer>
  )
}
