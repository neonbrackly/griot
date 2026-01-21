'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Camera } from 'lucide-react'
import { api, queryKeys } from '@/lib/api/client'
import { PageContainer, PageHeader } from '@/components/layout'
import { Card } from '@/components/layout/Card'
import { Breadcrumbs } from '@/components/navigation/Breadcrumbs'
import type { BreadcrumbItem } from '@/components/navigation/Breadcrumbs'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Avatar } from '@/components/ui/Avatar'
import { Badge } from '@/components/ui/Badge'
import { FormField } from '@/components/forms/FormField'
import { Skeleton } from '@/components/feedback/Skeleton'
import { useToast } from '@/lib/hooks/useToast'
import type { User } from '@/types'

export default function ProfileSettingsPage() {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Settings', href: '/settings' },
    { label: 'Profile' },
  ]

  const { data: user, isLoading } = useQuery({
    queryKey: queryKeys.users.current(),
    queryFn: () => api.get<User>('/users/me'),
  })

  const [formData, setFormData] = useState({
    name: '',
    email: '',
  })

  const updateMutation = useMutation({
    mutationFn: (data: Partial<User>) => api.patch('/users/me', data),
    onSuccess: () => {
      toast({
        title: 'Profile updated',
        description: 'Your profile has been updated successfully.',
      })
      queryClient.invalidateQueries({ queryKey: queryKeys.users.current() })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to update profile. Please try again.',
        variant: 'error',
      })
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    updateMutation.mutate({
      name: formData.name || user?.name,
      email: formData.email || user?.email,
    })
  }

  if (isLoading) {
    return (
      <PageContainer maxWidth="md">
        <Breadcrumbs items={breadcrumbs} />
        <Skeleton className="h-8 w-48 mb-6" />
        <div className="space-y-4">
          <Skeleton className="h-32 w-full rounded-lg" />
          <Skeleton className="h-48 w-full rounded-lg" />
        </div>
      </PageContainer>
    )
  }

  return (
    <PageContainer maxWidth="md">
      <Breadcrumbs items={breadcrumbs} />
      <PageHeader
        title="Profile"
        description="Manage your personal information"
      />

      {/* Avatar Section */}
      <Card className="p-6">
        <div className="flex items-center gap-6">
          <div className="relative">
            <Avatar src={user?.avatar} fallback={user?.name} size="xl" />
            <button className="absolute bottom-0 right-0 p-1.5 rounded-full bg-primary-600 text-white hover:bg-primary-700 transition-colors">
              <Camera className="w-4 h-4" />
            </button>
          </div>
          <div>
            <h3 className="font-semibold text-text-primary text-lg">{user?.name}</h3>
            <p className="text-text-secondary">{user?.email}</p>
            <div className="flex items-center gap-2 mt-2">
              <Badge variant="primary">{user?.role}</Badge>
              <Badge variant={user?.status === 'active' ? 'success' : 'secondary'}>
                {user?.status}
              </Badge>
            </div>
          </div>
        </div>
      </Card>

      {/* Profile Form */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-text-primary mb-6">Personal Information</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <FormField name="name" label="Full Name">
            <Input
              placeholder={user?.name}
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
          </FormField>
          <FormField name="email" label="Email Address">
            <Input
              type="email"
              placeholder={user?.email}
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            />
          </FormField>
          <FormField name="team" label="Team">
            <Input value={user?.teamId || ''} disabled />
            <p className="text-xs text-text-tertiary mt-1">
              Contact your administrator to change your team assignment.
            </p>
          </FormField>
          <div className="pt-4">
            <Button
              type="submit"
              disabled={updateMutation.isPending}
            >
              Save Changes
            </Button>
          </div>
        </form>
      </Card>

      {/* Account Info */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-text-primary mb-4">Account Information</h3>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between">
            <span className="text-text-tertiary">User ID</span>
            <code className="text-text-secondary bg-bg-tertiary px-2 py-1 rounded">
              {user?.id}
            </code>
          </div>
          <div className="flex justify-between">
            <span className="text-text-tertiary">Account Created</span>
            <span className="text-text-primary">
              {user?.createdAt ? new Date(user.createdAt).toLocaleDateString() : '-'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-text-tertiary">Last Login</span>
            <span className="text-text-primary">
              {user?.lastLoginAt ? new Date(user.lastLoginAt).toLocaleString() : '-'}
            </span>
          </div>
        </div>
      </Card>
    </PageContainer>
  )
}
