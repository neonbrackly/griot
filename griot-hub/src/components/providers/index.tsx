'use client'

import * as React from 'react'
import { ThemeProvider } from './ThemeProvider'
import { QueryProvider } from './QueryProvider'
import { MSWProvider } from './MSWProvider'
import { AuthProvider } from './AuthProvider'
import { TooltipProvider } from '@/components/ui/Tooltip'
import { Toaster } from '@/components/feedback/Toaster'

interface ProvidersProps {
  children: React.ReactNode
}

export function Providers({ children }: ProvidersProps) {
  return (
    <MSWProvider>
      <QueryProvider>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <AuthProvider>
            <TooltipProvider>
              {children}
              <Toaster />
            </TooltipProvider>
          </AuthProvider>
        </ThemeProvider>
      </QueryProvider>
    </MSWProvider>
  )
}

export { ThemeProvider } from './ThemeProvider'
export { QueryProvider } from './QueryProvider'
export { MSWProvider } from './MSWProvider'
export { AuthProvider, useAuth, useCurrentUser, useHasRole } from './AuthProvider'
