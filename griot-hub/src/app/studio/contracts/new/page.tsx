'use client'

import { useRouter } from 'next/navigation'
import { FileCode, Wand2, FileUp, ArrowRight } from 'lucide-react'

import { PageContainer, Card } from '@/components/layout'
import { Button } from '@/components/ui'
import { BackLink } from '@/components/navigation/Breadcrumbs'

export default function NewContractMethodSelection() {
  const router = useRouter()

  const methods = [
    {
      id: 'wizard',
      icon: Wand2,
      title: 'UI Builder',
      description: 'Build your contract step-by-step with our guided wizard. Perfect for first-time users.',
      features: [
        'Step-by-step guidance',
        'Auto-populated schema from assets',
        'Built-in validation',
        'Save drafts automatically',
      ],
      recommended: true,
      path: '/studio/contracts/new/wizard',
    },
    {
      id: 'yaml',
      icon: FileCode,
      title: 'YAML Editor',
      description: 'Write your contract directly in YAML format. For advanced users familiar with ODCS.',
      features: [
        'Full control over contract definition',
        'Syntax highlighting and validation',
        'Import from existing contracts',
        'Real-time schema validation',
      ],
      recommended: false,
      path: '/studio/contracts/new/yaml',
    },
    {
      id: 'import',
      icon: FileUp,
      title: 'Import YAML',
      description: 'Upload an existing YAML contract file from your local machine.',
      features: [
        'Drag-and-drop file upload',
        'Validates on import',
        'Preview before saving',
        'Supports ODCS v3.3',
      ],
      recommended: false,
      path: '/studio/contracts/new/yaml?mode=import',
    },
  ]

  return (
    <PageContainer>
      <div className="max-w-5xl mx-auto">
        <BackLink href="/studio/contracts" label="All Contracts" />

        <div className="mt-6 mb-8">
          <h1 className="text-2xl font-semibold text-text-primary">Create New Contract</h1>
          <p className="mt-2 text-text-secondary">
            Choose how you'd like to create your data contract
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {methods.map((method) => {
            const Icon = method.icon
            return (
              <Card
                key={method.id}
                className={`p-6 relative hover:shadow-lg transition-all cursor-pointer ${
                  method.recommended ? 'border-primary-500 border-2' : ''
                }`}
                onClick={() => router.push(method.path)}
              >
                {method.recommended && (
                  <div className="absolute -top-3 left-6 px-3 py-1 bg-primary-500 text-white text-xs font-semibold rounded-full">
                    Recommended
                  </div>
                )}

                <div className="flex items-start justify-between mb-4">
                  <div className="p-3 rounded-lg bg-bg-tertiary">
                    <Icon className="h-6 w-6 text-primary-500" />
                  </div>
                </div>

                <h3 className="text-lg font-semibold text-text-primary mb-2">
                  {method.title}
                </h3>

                <p className="text-sm text-text-secondary mb-4">
                  {method.description}
                </p>

                <ul className="space-y-2 mb-6">
                  {method.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-2 text-sm text-text-secondary">
                      <span className="text-success-text mt-0.5">✓</span>
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>

                <Button
                  variant={method.recommended ? 'primary' : 'secondary'}
                  className="w-full"
                  onClick={() => router.push(method.path)}
                >
                  Choose Method
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Card>
            )
          })}
        </div>

        <div className="mt-8 p-4 rounded-lg bg-info-bg/20 border border-info-border">
          <p className="text-sm text-text-secondary">
            <span className="font-semibold text-text-primary">💡 Tip:</span> New to data contracts?
            Start with the UI Builder to learn the structure. Once comfortable, you can switch to
            YAML for faster editing.
          </p>
        </div>
      </div>
    </PageContainer>
  )
}
