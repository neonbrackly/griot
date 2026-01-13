'use client'

import * as React from 'react'
import Link from 'next/link'
import { Bell, Search, HelpCircle, Plus } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Avatar } from '@/components/ui/Avatar'
import { ThemeToggle } from '@/components/ui/ThemeToggle'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuLabel,
} from '@/components/ui/DropdownMenu'
import { cn } from '@/lib/utils'

interface TopNavProps {
  onSearchClick?: () => void
  notificationCount?: number
  user?: {
    name: string
    email: string
    avatar?: string
  }
}

export function TopNav({ onSearchClick, notificationCount = 0, user }: TopNavProps) {
  return (
    <header className="h-16 bg-bg-secondary border-b border-border-default">
      <div className="flex items-center justify-between h-full px-4">
        {/* Left section - Search */}
        <div className="flex-1 max-w-md">
          <button
            onClick={onSearchClick}
            className={cn(
              'flex items-center gap-2 w-full px-3 py-2 text-sm text-text-tertiary',
              'bg-bg-primary border border-border-default rounded-lg',
              'hover:border-border-strong hover:text-text-secondary',
              'transition-colors duration-fast'
            )}
          >
            <Search className="h-4 w-4" />
            <span>Search contracts, assets, issues...</span>
            <kbd className="hidden sm:inline-flex ml-auto h-5 items-center gap-1 rounded border border-border-default bg-bg-tertiary px-1.5 font-mono text-xs text-text-tertiary">
              <span className="text-xs">⌘</span>K
            </kbd>
          </button>
        </div>

        {/* Right section - Actions */}
        <div className="flex items-center gap-2">
          {/* Quick Create */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button size="sm">
                <Plus className="h-4 w-4 mr-1" />
                Create
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
              <DropdownMenuItem asChild>
                <Link href="/studio/contracts/new">New Contract</Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link href="/studio/assets/new">New Data Asset</Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <Link href="/settings/connections">Add Connection</Link>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Help */}
          <Button variant="ghost" size="icon">
            <HelpCircle className="h-5 w-5 text-text-secondary" />
          </Button>

          {/* Theme Toggle */}
          <ThemeToggle />

          {/* Notifications */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="h-5 w-5 text-text-secondary" />
                {notificationCount > 0 && (
                  <span className="absolute top-1 right-1 w-2 h-2 bg-error-500 rounded-full" />
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-80">
              <div className="flex items-center justify-between px-3 py-2 border-b border-border-default">
                <span className="font-medium text-sm">Notifications</span>
                {notificationCount > 0 && (
                  <Button variant="ghost" size="xs">
                    Mark all read
                  </Button>
                )}
              </div>
              <div className="max-h-80 overflow-y-auto">
                {notificationCount === 0 ? (
                  <div className="p-4 text-center text-text-tertiary text-sm">
                    No new notifications
                  </div>
                ) : (
                  <div className="p-2">
                    {/* Notification items would go here */}
                    <p className="text-sm text-text-secondary p-2">
                      {notificationCount} new notification(s)
                    </p>
                  </div>
                )}
              </div>
              <div className="border-t border-border-default p-2">
                <Button variant="ghost" size="sm" className="w-full" asChild>
                  <Link href="/settings/notifications">Notification Settings</Link>
                </Button>
              </div>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* User Menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="flex items-center gap-2 p-1 rounded-lg hover:bg-bg-hover transition-colors">
                <Avatar
                  size="sm"
                  src={user?.avatar}
                  fallback={user?.name || 'User'}
                  alt={user?.name}
                />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>
                <div className="flex flex-col">
                  <span className="font-medium">{user?.name || 'User'}</span>
                  <span className="text-xs text-text-tertiary font-normal">
                    {user?.email || 'user@example.com'}
                  </span>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <Link href="/settings/profile">Profile Settings</Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link href="/settings">Preferences</Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-error-text">
                Sign Out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  )
}
