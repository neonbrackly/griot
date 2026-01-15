'use client'

import { useState } from 'react'
import { PageContainer, PageHeader } from '@/components/layout'
import { Card } from '@/components/layout/Card'
import { Breadcrumbs } from '@/components/navigation/Breadcrumbs'
import type { BreadcrumbItem } from '@/components/navigation/Breadcrumbs'
import { Button } from '@/components/ui/Button'
import { Switch } from '@/components/ui/Switch'
import { Label } from '@/components/ui/Label'
import { useToast } from '@/lib/hooks/useToast'

interface NotificationSetting {
  id: string
  title: string
  description: string
  email: boolean
  push: boolean
  inApp: boolean
}

const defaultSettings: NotificationSetting[] = [
  {
    id: 'issues',
    title: 'Issue Alerts',
    description: 'Get notified when new issues are detected',
    email: true,
    push: true,
    inApp: true,
  },
  {
    id: 'approvals',
    title: 'Approval Requests',
    description: 'Notifications for contracts pending your approval',
    email: true,
    push: true,
    inApp: true,
  },
  {
    id: 'comments',
    title: 'Comments & Mentions',
    description: 'When someone comments or mentions you',
    email: true,
    push: false,
    inApp: true,
  },
  {
    id: 'contract_runs',
    title: 'Contract Runs',
    description: 'Results of contract validation runs',
    email: false,
    push: false,
    inApp: true,
  },
  {
    id: 'sla_breach',
    title: 'SLA Breaches',
    description: 'Critical alerts for SLA violations',
    email: true,
    push: true,
    inApp: true,
  },
  {
    id: 'schema_drift',
    title: 'Schema Changes',
    description: 'Notifications when schema drift is detected',
    email: true,
    push: false,
    inApp: true,
  },
]

export default function NotificationSettingsPage() {
  const { toast } = useToast()
  const [settings, setSettings] = useState<NotificationSetting[]>(defaultSettings)
  const [isSaving, setIsSaving] = useState(false)

  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Settings', href: '/settings' },
    { label: 'Notifications' },
  ]

  const toggleSetting = (
    id: string,
    channel: 'email' | 'push' | 'inApp'
  ) => {
    setSettings((prev) =>
      prev.map((s) =>
        s.id === id ? { ...s, [channel]: !s[channel] } : s
      )
    )
  }

  const handleSave = async () => {
    setIsSaving(true)
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 500))
    setIsSaving(false)
    toast({
      title: 'Settings saved',
      description: 'Your notification preferences have been updated.',
    })
  }

  return (
    <PageContainer maxWidth="lg">
      <Breadcrumbs items={breadcrumbs} />
      <PageHeader
        title="Notifications"
        description="Configure how you receive notifications"
      />

      <Card className="p-6">
        <div className="space-y-6">
          {/* Header Row */}
          <div className="grid grid-cols-[1fr,80px,80px,80px] gap-4 items-center text-sm font-medium text-text-tertiary pb-2 border-b border-border-default">
            <span>Notification Type</span>
            <span className="text-center">Email</span>
            <span className="text-center">Push</span>
            <span className="text-center">In-App</span>
          </div>

          {/* Settings Rows */}
          {settings.map((setting) => (
            <div
              key={setting.id}
              className="grid grid-cols-[1fr,80px,80px,80px] gap-4 items-center"
            >
              <div>
                <Label className="font-medium text-text-primary">
                  {setting.title}
                </Label>
                <p className="text-sm text-text-tertiary mt-0.5">
                  {setting.description}
                </p>
              </div>
              <div className="flex justify-center">
                <Switch
                  checked={setting.email}
                  onCheckedChange={() => toggleSetting(setting.id, 'email')}
                />
              </div>
              <div className="flex justify-center">
                <Switch
                  checked={setting.push}
                  onCheckedChange={() => toggleSetting(setting.id, 'push')}
                />
              </div>
              <div className="flex justify-center">
                <Switch
                  checked={setting.inApp}
                  onCheckedChange={() => toggleSetting(setting.id, 'inApp')}
                />
              </div>
            </div>
          ))}
        </div>
      </Card>

      <div className="flex justify-end">
        <Button onClick={handleSave} disabled={isSaving}>
          Save Preferences
        </Button>
      </div>
    </PageContainer>
  )
}
