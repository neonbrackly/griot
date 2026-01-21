'use client'

import * as React from 'react'
import { Sidebar } from './Sidebar'
import { TopNav } from './TopNav'
import { TooltipProvider } from '@/components/ui/Tooltip'
import { cn } from '@/lib/utils'

interface PageShellProps {
  children: React.ReactNode
  showSidebar?: boolean
  showTopNav?: boolean
}

export function PageShell({
  children,
  showSidebar = true,
  showTopNav = true,
}: PageShellProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = React.useState(false)

  return (
    <TooltipProvider>
      <div className="flex h-screen bg-bg-primary">
        {/* Sidebar */}
        {showSidebar && (
          <Sidebar
            collapsed={sidebarCollapsed}
            onCollapsedChange={setSidebarCollapsed}
          />
        )}

        {/* Main Content Area */}
        <div className="flex flex-1 flex-col overflow-hidden">
          {/* Top Navigation */}
          {showTopNav && <TopNav />}

          {/* Page Content */}
          <main className="flex-1 overflow-auto">
            <div className="h-full">{children}</div>
          </main>
        </div>
      </div>
    </TooltipProvider>
  )
}

// Page container with standard padding
interface PageContainerProps {
  children: React.ReactNode
  className?: string
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full'
}

export function PageContainer({
  children,
  className,
  maxWidth = 'full',
}: PageContainerProps) {
  const maxWidthClass = {
    sm: 'max-w-screen-sm',
    md: 'max-w-screen-md',
    lg: 'max-w-screen-lg',
    xl: 'max-w-screen-xl',
    '2xl': 'max-w-screen-2xl',
    full: '',
  }[maxWidth]

  return (
    <div className={cn('px-8 py-8', maxWidthClass, maxWidthClass && 'mx-auto', className)}>
      {children}
    </div>
  )
}

// Page header component
interface PageHeaderProps {
  title: string
  description?: string
  actions?: React.ReactNode
  breadcrumbs?: React.ReactNode
}

export function PageHeader({
  title,
  description,
  actions,
  breadcrumbs,
}: PageHeaderProps) {
  return (
    <div className="mb-6">
      {breadcrumbs && <div className="mb-4">{breadcrumbs}</div>}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary">{title}</h1>
          {description && (
            <p className="mt-1 text-text-secondary">{description}</p>
          )}
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>
    </div>
  )
}
