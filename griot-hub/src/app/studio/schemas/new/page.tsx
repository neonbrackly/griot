'use client'

import { useRouter } from 'next/navigation'
import { Database, FileCode2, ArrowRight } from 'lucide-react'
import { PageContainer } from '@/components/layout/PageShell'
import { BackLink } from '@/components/navigation/Breadcrumbs'

interface MethodCardProps {
  icon: React.ComponentType<{ className?: string }>
  title: string
  description: string
  features: string[]
  recommended?: boolean
  onClick: () => void
}

function MethodCard({ icon: Icon, title, description, features, recommended, onClick }: MethodCardProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="relative flex flex-col p-6 rounded-xl border-2 border-border-default hover:border-primary-border hover:bg-bg-secondary transition-all text-left group"
    >
      {recommended && (
        <span className="absolute -top-3 left-4 px-2 py-0.5 text-xs font-medium bg-primary-600 text-white rounded-full">
          Recommended
        </span>
      )}

      <div className="flex items-start justify-between mb-4">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary-50 dark:bg-primary-900/30">
          <Icon className="h-6 w-6 text-primary-600" />
        </div>
        <ArrowRight className="h-5 w-5 text-text-tertiary group-hover:text-primary-600 group-hover:translate-x-1 transition-all" />
      </div>

      <h3 className="text-lg font-semibold text-text-primary mb-2">{title}</h3>
      <p className="text-sm text-text-secondary mb-4">{description}</p>

      <ul className="space-y-2 mt-auto">
        {features.map((feature, i) => (
          <li key={i} className="flex items-center gap-2 text-sm text-text-tertiary">
            <span className="h-1.5 w-1.5 rounded-full bg-primary-500" />
            {feature}
          </li>
        ))}
      </ul>
    </button>
  )
}

export default function NewSchemaPage() {
  const router = useRouter()

  return (
    <PageContainer>
      <div className="max-w-4xl mx-auto">
        <BackLink href="/studio/schemas" label="All Schemas" className="mb-6" />

        <div className="mb-8">
          <h1 className="text-2xl font-semibold text-text-primary">
            Create Schema
          </h1>
          <p className="text-text-secondary mt-1">
            Choose how you want to define your schema
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <MethodCard
            icon={FileCode2}
            title="Manual Definition"
            description="Define your schema structure, properties, constraints, and quality rules from scratch."
            features={[
              'Full control over schema structure',
              'Define field-level constraints',
              'Add schema and property quality rules',
              'Set PII classifications',
            ]}
            recommended
            onClick={() => router.push('/studio/schemas/new/manual')}
          />

          <MethodCard
            icon={Database}
            title="From Database Connection"
            description="Connect to an existing database and import the schema structure automatically."
            features={[
              'Auto-detect tables and columns',
              'Import data types automatically',
              'Preview sample data',
              'Quick setup for existing databases',
            ]}
            onClick={() => router.push('/studio/schemas/new/connection')}
          />
        </div>

        <div className="mt-8 p-4 bg-bg-secondary rounded-lg">
          <h4 className="text-sm font-medium text-text-primary mb-2">Which method should I choose?</h4>
          <ul className="text-sm text-text-secondary space-y-1">
            <li>
              <strong>Manual Definition</strong> is ideal when you want to define a new data contract upfront,
              before the data exists, or when you need precise control over constraints and quality rules.
            </li>
            <li>
              <strong>From Database Connection</strong> is best when you have an existing database and want to
              quickly document its structure as a schema.
            </li>
          </ul>
        </div>
      </div>
    </PageContainer>
  )
}
