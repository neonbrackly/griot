'use client'

import * as React from 'react'

interface MSWProviderProps {
  children: React.ReactNode
}

export function MSWProvider({ children }: MSWProviderProps) {
  React.useEffect(() => {
    async function enableMocking() {
      if (process.env.NODE_ENV !== 'development') {
        return
      }

      try {
        const { worker } = await import('@/lib/mocks/browser')
        await worker.start({
          onUnhandledRequest: 'bypass',
          quiet: true,
        })
        console.log('[MSW] Mock Service Worker started')
      } catch (error) {
        console.warn('[MSW] Failed to start Mock Service Worker:', error)
      }
    }

    enableMocking()
  }, [])

  // Always render children - MSW will intercept requests once started
  // This prevents hydration issues and 404s during SSR
  return <>{children}</>
}
