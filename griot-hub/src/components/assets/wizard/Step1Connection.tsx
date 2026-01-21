'use client'

import * as React from 'react'
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Check, Loader2, AlertCircle, Database as DatabaseIcon, Server } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/layout/Card'
import { Skeleton } from '@/components/feedback/Skeleton'
import { cn } from '@/lib/utils'
import { api, queryKeys } from '@/lib/api/client'
import { useToast } from '@/lib/hooks/useToast'
import type { AssetFormData, Connection } from '@/types'

interface Step1Props {
  data: AssetFormData
  onUpdate: (data: Partial<AssetFormData>) => void
  onNext: () => void
}

// Database type icons
const getDatabaseIcon = (type: string): string => {
  switch (type) {
    case 'snowflake':
      return '❄️'
    case 'bigquery':
      return '🔷'
    case 'databricks':
      return '🧱'
    case 'postgres':
      return '🐘'
    case 'redshift':
      return '🔶'
    default:
      return '💾'
  }
}

// Connection Card Component
function ConnectionCard({
  connection,
  selected,
  onSelect,
  onTest,
  isTesting,
}: {
  connection: Connection
  selected: boolean
  onSelect: () => void
  onTest: () => void
  isTesting: boolean
}) {
  const lastTestedRecently = connection.lastTestedAt &&
    (new Date().getTime() - new Date(connection.lastTestedAt).getTime()) < 3600000 // Within last hour

  return (
    <button
      onClick={onSelect}
      className={cn(
        'w-full p-4 rounded-lg border-2 text-left transition-all duration-200',
        'hover:border-primary-300 hover:shadow-sm hover:scale-[1.01]',
        selected
          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 shadow-md'
          : 'border-border-default bg-bg-secondary'
      )}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="text-3xl">{getDatabaseIcon(connection.type)}</div>
          <div>
            <div className="font-medium text-text-primary">{connection.name}</div>
            <div className="text-sm text-text-secondary capitalize">
              {connection.type}
              {connection.config.database && ` • ${connection.config.database}`}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {connection.lastTestStatus === 'success' && lastTestedRecently && (
            <span className="text-xs text-green-600 dark:text-green-400 flex items-center gap-1">
              <Check className="w-3 h-3" />
              Connected
            </span>
          )}

          {connection.lastTestStatus === 'error' && (
            <span className="text-xs text-error-text flex items-center gap-1">
              <AlertCircle className="w-3 h-3" />
              Error
            </span>
          )}

          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation()
              onTest()
            }}
            loading={isTesting}
          >
            Test
          </Button>

          {selected && (
            <div className="w-5 h-5 rounded-full bg-primary-500 flex items-center justify-center">
              <Check className="w-3 h-3 text-white" />
            </div>
          )}
        </div>
      </div>
    </button>
  )
}

// Connection Card Skeleton
function ConnectionCardSkeleton() {
  return (
    <div className="w-full p-4 rounded-lg border-2 border-border-default bg-bg-secondary">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Skeleton className="h-10 w-10 rounded" />
          <div>
            <Skeleton className="h-5 w-32 mb-1" />
            <Skeleton className="h-4 w-24" />
          </div>
        </div>
        <Skeleton className="h-8 w-16" />
      </div>
    </div>
  )
}

export function Step1Connection({ data, onUpdate, onNext }: Step1Props) {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [showNewConnection, setShowNewConnection] = useState(false)
  const [testingConnectionId, setTestingConnectionId] = useState<string | null>(null)

  // Fetch existing connections
  const { data: connections, isLoading } = useQuery({
    queryKey: queryKeys.connections.all,
    queryFn: () => api.get<Connection[]>('/connections'),
  })

  // Test connection mutation
  const testMutation = useMutation({
    mutationFn: (connectionId: string) =>
      api.post(`/connections/${connectionId}/test`),
    onMutate: (connectionId) => {
      setTestingConnectionId(connectionId)
    },
    onSuccess: (_, connectionId) => {
      toast({
        title: 'Connection successful',
        description: 'Database connection is working correctly',
        variant: 'success',
      })
      // Update the connection status in the cache
      queryClient.invalidateQueries({ queryKey: queryKeys.connections.all })
    },
    onError: (error: Error) => {
      toast({
        title: 'Connection failed',
        description: error.message || 'Failed to connect to database',
        variant: 'error',
      })
    },
    onSettled: () => {
      setTestingConnectionId(null)
    },
  })

  const handleSelectConnection = (connection: Connection) => {
    onUpdate({ connectionId: connection.id, connection })
  }

  const canProceed = !!data.connectionId

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-medium text-text-primary">
          Step 1: Select Database Connection
        </h2>
        <p className="text-sm text-text-secondary mt-1">
          Choose an existing connection or create a new one
        </p>
      </div>

      {/* Existing Connections */}
      <div className="space-y-3">
        <h3 className="text-sm font-medium text-text-primary">
          Existing Connections
        </h3>

        {isLoading ? (
          <div className="grid grid-cols-1 gap-3">
            {[1, 2, 3].map((i) => (
              <ConnectionCardSkeleton key={i} />
            ))}
          </div>
        ) : connections?.length === 0 || !connections ? (
          <Card className="p-6 text-center">
            <Server className="w-12 h-12 mx-auto mb-3 text-text-tertiary" />
            <p className="text-text-secondary mb-2">No connections configured yet</p>
            <p className="text-sm text-text-tertiary">
              Create your first database connection to get started
            </p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 gap-3">
            {connections.map((connection) => (
              <ConnectionCard
                key={connection.id}
                connection={connection}
                selected={data.connectionId === connection.id}
                onSelect={() => handleSelectConnection(connection)}
                onTest={() => testMutation.mutate(connection.id)}
                isTesting={testingConnectionId === connection.id && testMutation.isPending}
              />
            ))}
          </div>
        )}
      </div>

      {/* Create New Connection - Placeholder */}
      {!showNewConnection ? (
        <Button
          variant="secondary"
          onClick={() => setShowNewConnection(true)}
          className="w-full"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create New Connection
        </Button>
      ) : (
        <Card className="p-6">
          <h3 className="text-sm font-medium text-text-primary mb-4">
            New Database Connection
          </h3>
          <div className="text-center py-8">
            <DatabaseIcon className="w-12 h-12 mx-auto mb-3 text-text-tertiary" />
            <p className="text-text-secondary mb-4">
              Connection creation form will be implemented here
            </p>
            <Button
              variant="secondary"
              onClick={() => setShowNewConnection(false)}
            >
              Cancel
            </Button>
          </div>
        </Card>
      )}

      {/* Navigation */}
      <div className="flex justify-end pt-6 border-t border-border-default">
        <Button onClick={onNext} disabled={!canProceed}>
          Next: Select Tables
        </Button>
      </div>
    </div>
  )
}
