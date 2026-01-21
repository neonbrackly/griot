'use client'

import * as React from 'react'
import Link from 'next/link'
import { HelpCircle, Plus, LogOut, User, Settings } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Avatar } from '@/components/ui/Avatar'
import { Badge } from '@/components/ui/Badge'
import { ThemeToggle } from '@/components/ui/ThemeToggle'
import { GlobalSearch } from '@/components/layout/GlobalSearch'
import { NotificationDropdown } from '@/components/layout/NotificationDropdown'
import { useAuth } from '@/components/providers/AuthProvider'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuLabel,
} from '@/components/ui/DropdownMenu'

export function TopNav() {
  const { user, logout, isAuthenticated } = useAuth()

  return (
    <header className="h-16 bg-bg-secondary border-b border-border-default">
      <div className="flex items-center justify-between h-full px-4">
        {/* Left section - Search */}
        <div className="flex-1 max-w-md">
          <GlobalSearch />
        </div>

        {/* Right section - Actions */}
        <div className="flex items-center gap-2">
          {isAuthenticated && (
            <>
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
              <NotificationDropdown />
            </>
          )}

          {/* User Menu */}
          {isAuthenticated && user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="flex items-center p-1 rounded-full hover:bg-bg-hover transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2">
                  <Avatar
                    size="sm"
                    src={user.avatar || undefined}
                    fallback={user.name || user.email}
                    alt={user.name}
                  />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>
                  <div className="flex flex-col">
                    <span className="font-medium">{user.name}</span>
                    <span className="text-xs text-text-tertiary font-normal">
                      {user.email}
                    </span>
                    <Badge variant="secondary" className="mt-1.5 w-fit text-xs">
                      {user.role?.name}
                    </Badge>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link href="/settings/profile" className="flex items-center">
                    <User className="h-4 w-4 mr-2" />
                    Profile Settings
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/settings" className="flex items-center">
                    <Settings className="h-4 w-4 mr-2" />
                    Preferences
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  className="text-error-text cursor-pointer"
                  onClick={logout}
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  Sign Out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <div className="flex items-center gap-2">
              <ThemeToggle />
              <Link href="/login">
                <Button size="sm">Sign In</Button>
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
