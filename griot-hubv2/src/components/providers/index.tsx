'use client'

import * as React from 'react'
import { ThemeProvider } from './ThemeProvider'
import { QueryProvider } from './QueryProvider'
import { MSWProvider } from './MSWProvider'
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
          <TooltipProvider>
            {children}
            <Toaster />
          </TooltipProvider>
        </ThemeProvider>
      </QueryProvider>
    </MSWProvider>
  )
}

export { ThemeProvider } from './ThemeProvider'
export { QueryProvider } from './QueryProvider'
export { MSWProvider } from './MSWProvider'
