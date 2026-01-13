'use client'

import { useEffect, useCallback, useState } from 'react'
import { useRouter } from 'next/navigation'

/**
 * Hook to warn users about unsaved changes before leaving the page
 * @param isDirty Whether there are unsaved changes
 * @param message Custom message to show in the confirmation dialog
 */
export function useUnsavedChanges(
  isDirty: boolean,
  message: string = 'You have unsaved changes. Are you sure you want to leave?'
) {
  const router = useRouter()
  const [showModal, setShowModal] = useState(false)
  const [pendingNavigation, setPendingNavigation] = useState<string | null>(null)

  // Handle browser back/forward and tab close
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (isDirty) {
        e.preventDefault()
        e.returnValue = message
        return message
      }
    }

    window.addEventListener('beforeunload', handleBeforeUnload)
    return () => window.removeEventListener('beforeunload', handleBeforeUnload)
  }, [isDirty, message])

  // Intercept navigation
  const handleNavigation = useCallback(
    (href: string) => {
      if (isDirty) {
        setPendingNavigation(href)
        setShowModal(true)
        return false
      }
      return true
    },
    [isDirty]
  )

  // Confirm navigation (discard changes)
  const confirmNavigation = useCallback(() => {
    setShowModal(false)
    if (pendingNavigation) {
      router.push(pendingNavigation)
      setPendingNavigation(null)
    }
  }, [pendingNavigation, router])

  // Cancel navigation (stay on page)
  const cancelNavigation = useCallback(() => {
    setShowModal(false)
    setPendingNavigation(null)
  }, [])

  return {
    showModal,
    confirmNavigation,
    cancelNavigation,
    handleNavigation,
  }
}

/**
 * Simple hook that just returns the isDirty state with a setter
 * Useful for tracking form changes
 */
export function useFormDirty(initialValue = false) {
  const [isDirty, setIsDirty] = useState(initialValue)

  const markDirty = useCallback(() => setIsDirty(true), [])
  const markClean = useCallback(() => setIsDirty(false), [])

  return {
    isDirty,
    markDirty,
    markClean,
    setIsDirty,
  }
}
