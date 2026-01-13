'use client'

import * as React from 'react'
import Link from 'next/link'
import { ChevronRight, Home } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface BreadcrumbItem {
  label: string
  href?: string
  icon?: React.ComponentType<{ className?: string }>
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[]
  className?: string
  showHome?: boolean
  separator?: React.ReactNode
}

export function Breadcrumbs({
  items,
  className,
  showHome = true,
  separator,
}: BreadcrumbsProps) {
  const allItems = showHome
    ? [{ label: 'Home', href: '/', icon: Home }, ...items]
    : items

  return (
    <nav aria-label="Breadcrumb" className={cn('flex items-center', className)}>
      <ol className="flex items-center gap-1">
        {allItems.map((item, index) => {
          const isLast = index === allItems.length - 1
          const Icon = item.icon

          return (
            <li key={index} className="flex items-center">
              {index > 0 && (
                <span className="mx-2 text-text-tertiary">
                  {separator || <ChevronRight className="h-4 w-4" />}
                </span>
              )}

              {isLast ? (
                <span className="flex items-center gap-1.5 text-sm font-medium text-text-primary">
                  {Icon && <Icon className="h-4 w-4" />}
                  {item.label}
                </span>
              ) : item.href ? (
                <Link
                  href={item.href}
                  className={cn(
                    'flex items-center gap-1.5 text-sm text-text-secondary',
                    'hover:text-text-primary transition-colors'
                  )}
                >
                  {Icon && <Icon className="h-4 w-4" />}
                  {item.label}
                </Link>
              ) : (
                <span className="flex items-center gap-1.5 text-sm text-text-secondary">
                  {Icon && <Icon className="h-4 w-4" />}
                  {item.label}
                </span>
              )}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}

// Back link variant
interface BackLinkProps {
  href: string
  label?: string
  className?: string
}

export function BackLink({ href, label = 'Back', className }: BackLinkProps) {
  return (
    <Link
      href={href}
      className={cn(
        'inline-flex items-center gap-1.5 text-sm text-text-secondary hover:text-text-primary transition-colors',
        className
      )}
    >
      <ChevronRight className="h-4 w-4 rotate-180" />
      {label}
    </Link>
  )
}
