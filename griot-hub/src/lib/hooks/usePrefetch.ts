'use client'

import { useCallback } from 'react'
import { useQueryClient, type QueryKey, type QueryFunction } from '@tanstack/react-query'

/**
 * Hook for prefetching data on hover/focus
 * Helps create instant-feeling navigation by loading data before the user clicks
 */
export function usePrefetch() {
  const queryClient = useQueryClient()

  const prefetch = useCallback(
    <TData = unknown>(
      queryKey: QueryKey,
      queryFn: QueryFunction<TData>,
      staleTime: number = 5 * 60 * 1000 // 5 minutes default
    ) => {
      queryClient.prefetchQuery({
        queryKey,
        queryFn,
        staleTime,
      })
    },
    [queryClient]
  )

  return { prefetch }
}

/**
 * Hook for creating prefetch handlers for list items
 * Usage:
 * const { createPrefetchHandler } = usePrefetchOnHover()
 * <div onMouseEnter={createPrefetchHandler(['asset', id], () => fetchAsset(id))}>
 */
export function usePrefetchOnHover() {
  const { prefetch } = usePrefetch()

  const createPrefetchHandler = useCallback(
    <TData = unknown>(
      queryKey: QueryKey,
      queryFn: QueryFunction<TData>,
      options?: {
        delay?: number
        staleTime?: number
      }
    ) => {
      let timeoutId: ReturnType<typeof setTimeout> | null = null

      const handleMouseEnter = () => {
        const delay = options?.delay ?? 100 // Default 100ms delay to prevent excessive prefetching
        timeoutId = setTimeout(() => {
          prefetch(queryKey, queryFn, options?.staleTime)
        }, delay)
      }

      const handleMouseLeave = () => {
        if (timeoutId) {
          clearTimeout(timeoutId)
          timeoutId = null
        }
      }

      return {
        onMouseEnter: handleMouseEnter,
        onMouseLeave: handleMouseLeave,
      }
    },
    [prefetch]
  )

  return { createPrefetchHandler, prefetch }
}

/**
 * Hook for prefetching adjacent pages (useful for pagination)
 */
export function usePrefetchPagination() {
  const { prefetch } = usePrefetch()

  const prefetchAdjacentPages = useCallback(
    <TData = unknown>(
      currentPage: number,
      totalPages: number,
      getQueryKey: (page: number) => QueryKey,
      getQueryFn: (page: number) => QueryFunction<TData>
    ) => {
      // Prefetch next page
      if (currentPage < totalPages) {
        const nextPage = currentPage + 1
        prefetch(getQueryKey(nextPage), getQueryFn(nextPage))
      }

      // Prefetch previous page (in case user goes back)
      if (currentPage > 1) {
        const prevPage = currentPage - 1
        prefetch(getQueryKey(prevPage), getQueryFn(prevPage))
      }
    },
    [prefetch]
  )

  return { prefetchAdjacentPages, prefetch }
}
