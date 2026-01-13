'use client'

import * as React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard,
  FileText,
  Database,
  AlertCircle,
  CheckSquare,
  BarChart3,
  Store,
  Settings,
  Users,
  ChevronLeft,
  ChevronDown,
  ChevronRight,
  Folder,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/Tooltip'

interface NavItem {
  label: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  badge?: number
  children?: NavItem[]
}

const mainNavItems: NavItem[] = [
  {
    label: 'Dashboard',
    href: '/',
    icon: LayoutDashboard,
  },
  {
    label: 'Studio',
    href: '/studio',
    icon: Folder,
    children: [
      {
        label: 'Contracts',
        href: '/studio/contracts',
        icon: FileText,
      },
      {
        label: 'Data Assets',
        href: '/studio/assets',
        icon: Database,
      },
      {
        label: 'Issues',
        href: '/studio/issues',
        icon: AlertCircle,
      },
      {
        label: 'My Tasks',
        href: '/studio/tasks',
        icon: CheckSquare,
      },
    ],
  },
  {
    label: 'Reports',
    href: '/reports',
    icon: BarChart3,
  },
  {
    label: 'Marketplace',
    href: '/marketplace',
    icon: Store,
  },
]

const bottomNavItems: NavItem[] = [
  {
    label: 'Settings',
    href: '/settings',
    icon: Settings,
  },
  {
    label: 'Admin',
    href: '/admin',
    icon: Users,
  },
]

interface SidebarProps {
  collapsed?: boolean
  onCollapsedChange?: (collapsed: boolean) => void
}

export function Sidebar({ collapsed = false, onCollapsedChange }: SidebarProps) {
  const pathname = usePathname()
  const [expandedItems, setExpandedItems] = React.useState<Set<string>>(new Set(['Studio']))

  const toggleExpand = (label: string) => {
    setExpandedItems((prev) => {
      const next = new Set(prev)
      if (next.has(label)) {
        next.delete(label)
      } else {
        next.add(label)
      }
      return next
    })
  }

  const isActive = (href: string) => {
    if (href === '/') return pathname === '/'
    return pathname.startsWith(href)
  }

  const renderNavItem = (item: NavItem, depth = 0) => {
    const hasChildren = item.children && item.children.length > 0
    const isExpanded = expandedItems.has(item.label)
    const active = isActive(item.href)
    const Icon = item.icon

    const content = (
      <div
        className={cn(
          'flex items-center gap-3 px-3 py-2 rounded-lg transition-colors duration-fast cursor-pointer',
          'hover:bg-bg-hover',
          active && !hasChildren && 'bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400',
          depth > 0 && 'ml-4'
        )}
        onClick={() => hasChildren && !collapsed && toggleExpand(item.label)}
      >
        <Icon className={cn('h-5 w-5 shrink-0', active ? 'text-primary-600' : 'text-text-tertiary')} />
        {!collapsed && (
          <>
            <span className={cn('flex-1 text-sm font-medium', active ? 'text-primary-700 dark:text-primary-400' : 'text-text-primary')}>
              {item.label}
            </span>
            {item.badge !== undefined && (
              <span className="px-2 py-0.5 text-xs font-medium bg-error-bg text-error-text rounded-full">
                {item.badge}
              </span>
            )}
            {hasChildren && (
              <ChevronDown
                className={cn(
                  'h-4 w-4 text-text-tertiary transition-transform duration-fast',
                  isExpanded && 'rotate-180'
                )}
              />
            )}
          </>
        )}
      </div>
    )

    if (collapsed) {
      return (
        <Tooltip key={item.href} delayDuration={0}>
          <TooltipTrigger asChild>
            <Link href={hasChildren ? item.children![0].href : item.href}>
              {content}
            </Link>
          </TooltipTrigger>
          <TooltipContent side="right" className="ml-2">
            {item.label}
          </TooltipContent>
        </Tooltip>
      )
    }

    return (
      <div key={item.href}>
        {hasChildren ? (
          content
        ) : (
          <Link href={item.href}>{content}</Link>
        )}

        <AnimatePresence>
          {hasChildren && isExpanded && !collapsed && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              <div className="mt-1 space-y-1">
                {item.children!.map((child) => renderNavItem(child, depth + 1))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    )
  }

  return (
    <aside
      className={cn(
        'flex flex-col h-screen bg-bg-secondary border-r border-border-default transition-all duration-normal',
        collapsed ? 'w-16' : 'w-60'
      )}
    >
      {/* Logo / Brand */}
      <div className={cn('flex items-center h-16 px-4 border-b border-border-default', collapsed && 'justify-center')}>
        {collapsed ? (
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center text-white font-bold">
            G
          </div>
        ) : (
          <Link href="/" className="flex items-center gap-3">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center text-white font-bold">
              G
            </div>
            <span className="text-lg font-semibold text-text-primary">Griot</span>
          </Link>
        )}
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {mainNavItems.map((item) => renderNavItem(item))}
      </nav>

      {/* Bottom Navigation */}
      <div className="p-3 space-y-1 border-t border-border-default">
        {bottomNavItems.map((item) => renderNavItem(item))}
      </div>

      {/* Collapse Toggle */}
      <div className="p-3 border-t border-border-default">
        <Button
          variant="ghost"
          size={collapsed ? 'icon' : 'sm'}
          onClick={() => onCollapsedChange?.(!collapsed)}
          className={cn('w-full', !collapsed && 'justify-start')}
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <>
              <ChevronLeft className="h-4 w-4 mr-2" />
              <span>Collapse</span>
            </>
          )}
        </Button>
      </div>
    </aside>
  )
}
