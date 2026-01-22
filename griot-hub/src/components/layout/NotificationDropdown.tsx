'use client'

import { useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Bell,
  AlertCircle,
  CheckCircle,
  FileText,
  AlertTriangle,
  MessageSquare,
  ClipboardList,
} from 'lucide-react'
import { api, queryKeys } from '@/lib/api/client'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/DropdownMenu'
import type { Notification, NotificationType } from '@/types'

// Registry notification response format (from RES-registry-009)
interface RegistryNotificationResponse {
  items: Notification[]
  pagination: {
    total: number
    unread_count?: number
    unreadCount?: number
    limit: number
    offset: number
  }
}

// Legacy mock response format
interface LegacyNotificationResponse {
  data: Notification[]
  unreadCount: number
}

function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString()
}

function getNotificationIcon(type: NotificationType) {
  switch (type) {
    case 'contract_approved':
      return <CheckCircle className="w-4 h-4 text-green-500" />
    case 'contract_rejected':
      return <AlertCircle className="w-4 h-4 text-red-500" />
    case 'issue_detected':
      return <AlertCircle className="w-4 h-4 text-red-500" />
    case 'sla_breach':
      return <AlertTriangle className="w-4 h-4 text-yellow-500" />
    case 'schema_drift':
      return <AlertTriangle className="w-4 h-4 text-yellow-500" />
    case 'comment_added':
      return <MessageSquare className="w-4 h-4 text-blue-500" />
    case 'task_assigned':
      return <ClipboardList className="w-4 h-4 text-purple-500" />
    default:
      return <FileText className="w-4 h-4 text-text-tertiary" />
  }
}

export function NotificationDropdown() {
  const router = useRouter()
  const queryClient = useQueryClient()

  const { data } = useQuery({
    queryKey: queryKeys.notifications.list(),
    queryFn: async () => {
      const response = await api.get<RegistryNotificationResponse | LegacyNotificationResponse>(
        '/notifications?limit=10'
      )
      // Handle both registry format (items) and legacy format (data)
      const items = 'items' in response ? response.items : response.data
      const unreadCount = 'pagination' in response
        ? (response.pagination.unreadCount ?? response.pagination.unread_count ?? 0)
        : response.unreadCount
      return { items, unreadCount }
    },
    refetchInterval: 30000, // Poll every 30 seconds
  })

  const notifications = data?.items || []
  const unreadCount = data?.unreadCount || 0

  const markAsReadMutation = useMutation({
    mutationFn: (id: string) => api.patch(`/notifications/${id}/read`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.notifications.all })
    },
  })

  const markAllReadMutation = useMutation({
    mutationFn: () => api.post('/notifications/read-all'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.notifications.all })
    },
  })

  const handleNotificationClick = (notification: Notification) => {
    if (!notification.read) {
      markAsReadMutation.mutate(notification.id)
    }
    if (notification.href) {
      router.push(notification.href)
    }
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button className="relative p-2 rounded-lg hover:bg-bg-hover transition-colors">
          <Bell className="w-5 h-5 text-text-secondary" />
          {unreadCount > 0 && (
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
          )}
        </button>
      </DropdownMenuTrigger>

      <DropdownMenuContent align="end" className="w-80">
        {/* Header */}
        <div className="flex items-center justify-between px-3 py-2 border-b border-border-default">
          <span className="font-medium text-text-primary">Notifications</span>
          {unreadCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => markAllReadMutation.mutate()}
              disabled={markAllReadMutation.isPending}
            >
              Mark all read
            </Button>
          )}
        </div>

        {/* Notifications List */}
        <div className="max-h-96 overflow-y-auto">
          {notifications.length === 0 ? (
            <div className="p-8 text-center">
              <Bell className="w-8 h-8 mx-auto text-text-tertiary mb-2" />
              <p className="text-text-secondary text-sm">No notifications</p>
            </div>
          ) : (
            notifications.map((notification) => (
              <DropdownMenuItem
                key={notification.id}
                className={cn(
                  'flex items-start gap-3 p-3 cursor-pointer',
                  !notification.read && 'bg-primary-50 dark:bg-primary-900/10'
                )}
                onClick={() => handleNotificationClick(notification)}
              >
                <div className="shrink-0 mt-0.5">
                  {getNotificationIcon(notification.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-text-primary font-medium">
                    {notification.title}
                  </p>
                  <p className="text-xs text-text-secondary mt-0.5 line-clamp-2">
                    {notification.description}
                  </p>
                  <p className="text-xs text-text-tertiary mt-1">
                    {formatRelativeTime(notification.createdAt)}
                  </p>
                </div>
                {!notification.read && (
                  <div className="w-2 h-2 bg-primary-500 rounded-full shrink-0 mt-1.5" />
                )}
              </DropdownMenuItem>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-border-default p-2">
          <Button
            variant="ghost"
            size="sm"
            className="w-full"
            onClick={() => router.push('/settings/notifications')}
          >
            Notification Settings
          </Button>
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
