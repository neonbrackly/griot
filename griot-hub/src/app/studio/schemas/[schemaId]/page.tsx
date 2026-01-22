'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  ArrowLeft,
  Edit,
  Trash2,
  MoreVertical,
  Database,
  Key,
  Shield,
  CheckCircle,
  Tag,
  Users,
  Clock,
  FileCode2,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  Send,
  Archive,
} from 'lucide-react'
import { PageContainer, PageHeader } from '@/components/layout/PageShell'
import { Breadcrumbs } from '@/components/navigation/Breadcrumbs'
import type { BreadcrumbItem } from '@/components/navigation/Breadcrumbs'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/layout/Card'
import { Skeleton } from '@/components/feedback/Skeleton'
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from '@/components/ui/DropdownMenu'
import { api, queryKeys } from '@/lib/api/client'
import { useToast } from '@/lib/hooks/useToast'
import { cn, formatRelativeTime } from '@/lib/utils'
import type { Schema } from '@/types'

interface PageProps {
  params: { schemaId: string }
}

function SchemaStatusBadge({ status }: { status: Schema['status'] }) {
  const variants: Record<Schema['status'], 'success' | 'warning' | 'secondary'> = {
    active: 'success',
    draft: 'warning',
    deprecated: 'secondary',
  }
  return (
    <Badge variant={variants[status]} className="capitalize">
      {status}
    </Badge>
  )
}

function SchemaDetailSkeleton() {
  return (
    <PageContainer>
      <div className="mb-6">
        <Skeleton className="h-8 w-64 mb-2" />
        <Skeleton className="h-4 w-96" />
      </div>
      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 space-y-6">
          <Skeleton className="h-48 w-full rounded-lg" />
          <Skeleton className="h-96 w-full rounded-lg" />
        </div>
        <div className="space-y-6">
          <Skeleton className="h-48 w-full rounded-lg" />
          <Skeleton className="h-48 w-full rounded-lg" />
        </div>
      </div>
    </PageContainer>
  )
}

export default function SchemaDetailPage({ params }: PageProps) {
  const schemaId = params.schemaId
  const router = useRouter()
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const [expandedProperties, setExpandedProperties] = React.useState<Set<string>>(new Set())

  // Fetch schema
  const { data: schema, isLoading } = useQuery({
    queryKey: queryKeys.schemas.detail(schemaId),
    queryFn: () => api.get<Schema>(`/schemas/${schemaId}`),
  })

  // Publish mutation
  const publishMutation = useMutation({
    mutationFn: () => api.post<Schema>(`/schemas/${schemaId}/publish`, {}),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.schemas.detail(schemaId) })
      toast({
        title: 'Schema published',
        description: 'The schema is now active and available for use in contracts.',
        variant: 'success',
      })
    },
    onError: (error: Error) => {
      toast({
        title: 'Failed to publish',
        description: error.message,
        variant: 'error',
      })
    },
  })

  // Deprecate mutation
  const deprecateMutation = useMutation({
    mutationFn: () => api.post<Schema>(`/schemas/${schemaId}/deprecate`, { reason: 'Deprecated by user' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.schemas.detail(schemaId) })
      toast({
        title: 'Schema deprecated',
        description: 'The schema has been marked as deprecated.',
        variant: 'success',
      })
    },
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: () => api.delete(`/schemas/${schemaId}`),
    onSuccess: () => {
      toast({
        title: 'Schema deleted',
        description: 'The schema has been permanently deleted.',
        variant: 'success',
      })
      router.push('/studio/schemas')
    },
    onError: (error: Error) => {
      toast({
        title: 'Failed to delete',
        description: error.message,
        variant: 'error',
      })
    },
  })

  const toggleProperty = (propId: string) => {
    setExpandedProperties((prev) => {
      const next = new Set(prev)
      if (next.has(propId)) {
        next.delete(propId)
      } else {
        next.add(propId)
      }
      return next
    })
  }

  if (isLoading || !schema) {
    return <SchemaDetailSkeleton />
  }

  const breadcrumbItems: BreadcrumbItem[] = [
    { label: 'Studio', href: '/studio' },
    { label: 'Schemas', href: '/studio/schemas' },
    { label: schema.name },
  ]

  const stats = {
    properties: schema.properties?.length || 0,
    primaryKeys: schema.properties?.filter(p => p.primaryKey).length || 0,
    required: schema.properties?.filter(p => p.required).length || 0,
    pii: schema.properties?.filter(p => p.customProperties?.privacy?.is_pii).length || 0,
    schemaQuality: schema.quality?.length || 0,
    propertyQuality: schema.properties?.reduce((acc, p) => acc + (p.quality?.length || 0), 0) || 0,
  }

  return (
    <PageContainer>
      <PageHeader
        title={
          <div className="flex items-center gap-3">
            <span>{schema.businessName || schema.name}</span>
            <SchemaStatusBadge status={schema.status} />
            <Badge variant="outline" className="font-mono">v{schema.version || '1.0.0'}</Badge>
          </div>
        }
        description={schema.description || `Schema: ${schema.name}`}
        breadcrumbs={<Breadcrumbs items={breadcrumbItems} />}
        actions={
          <div className="flex items-center gap-2">
            {schema.status === 'draft' && (
              <Button onClick={() => publishMutation.mutate()} loading={publishMutation.isPending}>
                <Send className="h-4 w-4 mr-2" />
                Publish
              </Button>
            )}
            {schema.status === 'active' && (
              <Button variant="secondary" onClick={() => deprecateMutation.mutate()} loading={deprecateMutation.isPending}>
                <Archive className="h-4 w-4 mr-2" />
                Deprecate
              </Button>
            )}

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="secondary" size="icon">
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => router.push(`/studio/schemas/${schemaId}/edit`)}>
                  <Edit className="h-4 w-4 mr-2" />
                  Edit Schema
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  className="text-error-text"
                  onClick={() => {
                    if (window.confirm('Are you sure you want to delete this schema?')) {
                      deleteMutation.mutate()
                    }
                  }}
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        }
      />

      <div className="grid grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="col-span-2 space-y-6">
          {/* Statistics */}
          <div className="grid grid-cols-6 gap-4">
            <div className="p-4 bg-bg-secondary rounded-lg text-center">
              <p className="text-2xl font-semibold text-text-primary">{stats.properties}</p>
              <p className="text-xs text-text-tertiary">Properties</p>
            </div>
            <div className="p-4 bg-bg-secondary rounded-lg text-center">
              <p className="text-2xl font-semibold text-warning-text">{stats.primaryKeys}</p>
              <p className="text-xs text-text-tertiary">Primary Keys</p>
            </div>
            <div className="p-4 bg-bg-secondary rounded-lg text-center">
              <p className="text-2xl font-semibold text-text-primary">{stats.required}</p>
              <p className="text-xs text-text-tertiary">Required</p>
            </div>
            <div className="p-4 bg-bg-secondary rounded-lg text-center">
              <p className="text-2xl font-semibold text-error-text">{stats.pii}</p>
              <p className="text-xs text-text-tertiary">PII Fields</p>
            </div>
            <div className="p-4 bg-bg-secondary rounded-lg text-center">
              <p className="text-2xl font-semibold text-info-text">{stats.schemaQuality}</p>
              <p className="text-xs text-text-tertiary">Schema Rules</p>
            </div>
            <div className="p-4 bg-bg-secondary rounded-lg text-center">
              <p className="text-2xl font-semibold text-success-text">{stats.propertyQuality}</p>
              <p className="text-xs text-text-tertiary">Property Rules</p>
            </div>
          </div>

          {/* Properties */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Properties ({schema.properties?.length || 0})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="divide-y divide-border-default">
                {schema.properties?.map((prop, index) => {
                  const isExpanded = expandedProperties.has(prop.id || String(index))
                  const hasPii = prop.customProperties?.privacy?.is_pii
                  const hasQuality = prop.quality && prop.quality.length > 0

                  return (
                    <div key={prop.id || index} className="py-3">
                      <div
                        className="flex items-center gap-3 cursor-pointer"
                        onClick={() => toggleProperty(prop.id || String(index))}
                      >
                        <span className="text-sm text-text-tertiary w-6">{index + 1}.</span>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="font-mono font-medium text-text-primary">{prop.name}</span>
                            <Badge variant="outline" size="sm">{prop.logicalType}</Badge>
                            {prop.primaryKey && <Key className="h-4 w-4 text-warning-text" />}
                            {hasPii && <Shield className="h-4 w-4 text-error-text" />}
                          </div>
                          {prop.description && (
                            <p className="text-xs text-text-tertiary mt-1">{prop.description}</p>
                          )}
                        </div>
                        <div className="flex items-center gap-2">
                          {prop.required && <Badge variant="secondary" size="sm">Required</Badge>}
                          {prop.unique && <Badge variant="outline" size="sm">Unique</Badge>}
                          {hasQuality && <Badge variant="success" size="sm">{prop.quality?.length} rules</Badge>}
                        </div>
                        {isExpanded ? (
                          <ChevronUp className="h-4 w-4 text-text-tertiary" />
                        ) : (
                          <ChevronDown className="h-4 w-4 text-text-tertiary" />
                        )}
                      </div>

                      {isExpanded && (
                        <div className="mt-3 ml-8 p-4 bg-bg-secondary rounded-lg space-y-3">
                          <div className="grid grid-cols-3 gap-4 text-sm">
                            <div>
                              <span className="text-text-tertiary">Physical Type:</span>
                              <span className="ml-2 text-text-primary font-mono">{prop.physicalType || '—'}</span>
                            </div>
                            <div>
                              <span className="text-text-tertiary">Nullable:</span>
                              <span className="ml-2 text-text-primary">{prop.nullable ? 'Yes' : 'No'}</span>
                            </div>
                            <div>
                              <span className="text-text-tertiary">Business Name:</span>
                              <span className="ml-2 text-text-primary">{prop.businessName || '—'}</span>
                            </div>
                          </div>

                          {hasPii && (
                            <div className="flex items-center gap-2 text-sm">
                              <Shield className="h-4 w-4 text-error-text" />
                              <span className="text-error-text">PII: {prop.customProperties?.privacy?.pii_type}</span>
                              {prop.customProperties?.privacy?.sensitivity && (
                                <Badge variant="secondary" size="sm">{prop.customProperties.privacy.sensitivity}</Badge>
                              )}
                            </div>
                          )}

                          {hasQuality && (
                            <div>
                              <p className="text-sm font-medium text-text-secondary mb-2">Quality Rules:</p>
                              <div className="space-y-1">
                                {prop.quality?.map((rule, rIdx) => (
                                  <div key={rIdx} className="flex items-center gap-2 text-sm">
                                    <CheckCircle className="h-4 w-4 text-success-text" />
                                    <span className="text-text-primary">{rule.name || rule.metric}</span>
                                    {rule.mustBe !== undefined && (
                                      <span className="text-text-tertiary">= {rule.mustBe}</span>
                                    )}
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          {/* Schema-Level Quality Rules */}
          {schema.quality && schema.quality.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-success-text" />
                  Schema Quality Rules ({schema.quality.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {schema.quality.map((rule, index) => (
                    <div key={index} className="p-3 bg-bg-secondary rounded-lg">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-text-primary">{rule.name}</span>
                        <Badge variant="outline" size="sm">{rule.metric}</Badge>
                      </div>
                      {rule.description && (
                        <p className="text-sm text-text-tertiary">{rule.description}</p>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Metadata */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileCode2 className="h-5 w-5" />
                Schema Details
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <span className="text-xs text-text-tertiary">Name</span>
                <p className="font-mono text-sm text-text-primary">{schema.name}</p>
              </div>
              {schema.physicalName && (
                <div>
                  <span className="text-xs text-text-tertiary">Physical Name</span>
                  <p className="font-mono text-sm text-text-primary">{schema.physicalName}</p>
                </div>
              )}
              <div>
                <span className="text-xs text-text-tertiary">Logical Type</span>
                <p className="text-sm text-text-primary capitalize">{schema.logicalType}</p>
              </div>
              <div>
                <span className="text-xs text-text-tertiary">Physical Type</span>
                <p className="text-sm text-text-primary capitalize">{schema.physicalType || '—'}</p>
              </div>
              <div>
                <span className="text-xs text-text-tertiary">Source</span>
                <Badge variant="outline" className="mt-1 capitalize">{schema.source}</Badge>
              </div>
              {schema.domain && (
                <div>
                  <span className="text-xs text-text-tertiary">Domain</span>
                  <Badge variant="secondary" className="mt-1 capitalize">{schema.domain}</Badge>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Ownership */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Ownership
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {schema.ownerTeamId && (
                <div>
                  <span className="text-xs text-text-tertiary">Owner Team</span>
                  <p className="text-sm text-text-primary">{schema.ownerTeamId}</p>
                </div>
              )}
              {schema.tags && schema.tags.length > 0 && (
                <div>
                  <span className="text-xs text-text-tertiary">Tags</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {schema.tags.map((tag) => (
                      <Badge key={tag} variant="secondary" size="sm">
                        <Tag className="h-3 w-3 mr-1" />
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Timestamps */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                Activity
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <span className="text-xs text-text-tertiary">Created</span>
                <p className="text-sm text-text-primary">{formatRelativeTime(schema.createdAt)}</p>
              </div>
              <div>
                <span className="text-xs text-text-tertiary">Last Updated</span>
                <p className="text-sm text-text-primary">{formatRelativeTime(schema.updatedAt)}</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </PageContainer>
  )
}
