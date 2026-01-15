'use client'

import { useState } from 'react'
import { Copy, Eye, EyeOff, Plus, Trash2, RefreshCw } from 'lucide-react'
import { PageContainer, PageHeader } from '@/components/layout'
import { Card } from '@/components/layout/Card'
import { Breadcrumbs } from '@/components/navigation/Breadcrumbs'
import type { BreadcrumbItem } from '@/components/navigation/Breadcrumbs'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Badge } from '@/components/ui/Badge'
import { FormField } from '@/components/forms/FormField'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/Dialog'
import { useToast } from '@/lib/hooks/useToast'

interface ApiKey {
  id: string
  name: string
  prefix: string
  createdAt: string
  lastUsed: string | null
  status: 'active' | 'revoked'
}

const mockApiKeys: ApiKey[] = [
  {
    id: 'key-1',
    name: 'Production API Key',
    prefix: 'griot_prod_***',
    createdAt: '2024-11-15T10:00:00Z',
    lastUsed: '2025-01-13T08:30:00Z',
    status: 'active',
  },
  {
    id: 'key-2',
    name: 'Development Key',
    prefix: 'griot_dev_***',
    createdAt: '2024-12-01T14:00:00Z',
    lastUsed: '2025-01-12T16:45:00Z',
    status: 'active',
  },
]

export default function IntegrationsSettingsPage() {
  const { toast } = useToast()
  const [apiKeys, setApiKeys] = useState<ApiKey[]>(mockApiKeys)
  const [showNewKeyDialog, setShowNewKeyDialog] = useState(false)
  const [newKeyName, setNewKeyName] = useState('')
  const [newKey, setNewKey] = useState<string | null>(null)
  const [showKey, setShowKey] = useState(false)

  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Settings', href: '/settings' },
    { label: 'API & Integrations' },
  ]

  const generateApiKey = () => {
    const key = `griot_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`
    return key
  }

  const handleCreateKey = () => {
    if (!newKeyName.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a name for the API key.',
        variant: 'error',
      })
      return
    }

    const generatedKey = generateApiKey()
    const newApiKey: ApiKey = {
      id: `key-${Date.now()}`,
      name: newKeyName,
      prefix: generatedKey.substring(0, 15) + '***',
      createdAt: new Date().toISOString(),
      lastUsed: null,
      status: 'active',
    }

    setApiKeys([newApiKey, ...apiKeys])
    setNewKey(generatedKey)
    setNewKeyName('')
  }

  const handleCopyKey = (key: string) => {
    navigator.clipboard.writeText(key)
    toast({
      title: 'Copied',
      description: 'API key copied to clipboard.',
    })
  }

  const handleRevokeKey = (keyId: string) => {
    setApiKeys(
      apiKeys.map((k) =>
        k.id === keyId ? { ...k, status: 'revoked' as const } : k
      )
    )
    toast({
      title: 'Key revoked',
      description: 'The API key has been revoked and can no longer be used.',
    })
  }

  const handleDeleteKey = (keyId: string) => {
    setApiKeys(apiKeys.filter((k) => k.id !== keyId))
    toast({
      title: 'Key deleted',
      description: 'The API key has been permanently deleted.',
    })
  }

  const handleCloseDialog = () => {
    setShowNewKeyDialog(false)
    setNewKey(null)
    setNewKeyName('')
    setShowKey(false)
  }

  return (
    <PageContainer maxWidth="lg">
      <Breadcrumbs items={breadcrumbs} />
      <PageHeader
        title="API & Integrations"
        description="Manage API keys and external integrations"
        actions={
          <Dialog open={showNewKeyDialog} onOpenChange={setShowNewKeyDialog}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Create API Key
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>
                  {newKey ? 'API Key Created' : 'Create New API Key'}
                </DialogTitle>
                <DialogDescription>
                  {newKey
                    ? 'Copy your API key now. You won\'t be able to see it again.'
                    : 'Create a new API key for accessing the Griot API.'}
                </DialogDescription>
              </DialogHeader>
              {newKey ? (
                <div className="space-y-4">
                  <div className="p-4 bg-warning-bg rounded-lg border border-warning-text/20">
                    <p className="text-sm text-warning-text font-medium mb-2">
                      Save this key now - it won&apos;t be shown again!
                    </p>
                    <div className="flex items-center gap-2">
                      <Input
                        type={showKey ? 'text' : 'password'}
                        value={newKey}
                        readOnly
                        className="font-mono text-sm"
                      />
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setShowKey(!showKey)}
                      >
                        {showKey ? (
                          <EyeOff className="w-4 h-4" />
                        ) : (
                          <Eye className="w-4 h-4" />
                        )}
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleCopyKey(newKey)}
                      >
                        <Copy className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                  <DialogFooter>
                    <Button onClick={handleCloseDialog}>Done</Button>
                  </DialogFooter>
                </div>
              ) : (
                <div className="space-y-4">
                  <FormField name="keyName" label="Key Name" required>
                    <Input
                      placeholder="e.g., Production API Key"
                      value={newKeyName}
                      onChange={(e) => setNewKeyName(e.target.value)}
                    />
                  </FormField>
                  <DialogFooter>
                    <Button variant="secondary" onClick={handleCloseDialog}>
                      Cancel
                    </Button>
                    <Button onClick={handleCreateKey}>Create Key</Button>
                  </DialogFooter>
                </div>
              )}
            </DialogContent>
          </Dialog>
        }
      />
      {/* API Keys List */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-text-primary mb-4">API Keys</h3>
        {apiKeys.length === 0 ? (
          <p className="text-text-secondary text-center py-8">
            No API keys created yet. Create one to get started.
          </p>
        ) : (
          <div className="space-y-4">
            {apiKeys.map((key) => (
              <div
                key={key.id}
                className="flex items-center justify-between p-4 border border-border-default rounded-lg"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-text-primary">{key.name}</span>
                    <Badge
                      variant={key.status === 'active' ? 'success' : 'secondary'}
                      size="xs"
                    >
                      {key.status}
                    </Badge>
                  </div>
                  <code className="text-sm text-text-tertiary">{key.prefix}</code>
                  <div className="text-xs text-text-tertiary">
                    Created {new Date(key.createdAt).toLocaleDateString()} •{' '}
                    {key.lastUsed
                      ? `Last used ${new Date(key.lastUsed).toLocaleDateString()}`
                      : 'Never used'}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {key.status === 'active' && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRevokeKey(key.id)}
                    >
                      <RefreshCw className="w-4 h-4 mr-1" />
                      Revoke
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDeleteKey(key.id)}
                    className="text-error-text hover:text-error-text"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* API Documentation Link */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-text-primary mb-2">API Documentation</h3>
        <p className="text-text-secondary mb-4">
          Learn how to use the Griot API to integrate with your systems.
        </p>
        <Button variant="secondary">View Documentation</Button>
      </Card>
    </PageContainer>
  )
}
