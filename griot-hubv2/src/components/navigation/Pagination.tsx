'use client'

import * as React from 'react'
import { ChevronLeft, ChevronRight, MoreHorizontal } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'

interface PaginationProps {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
  siblingCount?: number
  className?: string
  showPageNumbers?: boolean
}

export function Pagination({
  currentPage,
  totalPages,
  onPageChange,
  siblingCount = 1,
  className,
  showPageNumbers = true,
}: PaginationProps) {
  // Generate page numbers to display
  const getPageNumbers = React.useMemo(() => {
    const totalPageNumbers = siblingCount * 2 + 3 // siblings + current + first + last
    const totalBlocks = totalPageNumbers + 2 // + 2 for ellipsis

    if (totalPages <= totalBlocks) {
      return Array.from({ length: totalPages }, (_, i) => i + 1)
    }

    const leftSiblingIndex = Math.max(currentPage - siblingCount, 1)
    const rightSiblingIndex = Math.min(currentPage + siblingCount, totalPages)

    const showLeftDots = leftSiblingIndex > 2
    const showRightDots = rightSiblingIndex < totalPages - 1

    if (!showLeftDots && showRightDots) {
      const leftItemCount = 3 + siblingCount * 2
      const leftRange = Array.from({ length: leftItemCount }, (_, i) => i + 1)
      return [...leftRange, 'dots', totalPages]
    }

    if (showLeftDots && !showRightDots) {
      const rightItemCount = 3 + siblingCount * 2
      const rightRange = Array.from(
        { length: rightItemCount },
        (_, i) => totalPages - rightItemCount + i + 1
      )
      return [1, 'dots', ...rightRange]
    }

    const middleRange = Array.from(
      { length: rightSiblingIndex - leftSiblingIndex + 1 },
      (_, i) => leftSiblingIndex + i
    )
    return [1, 'dots', ...middleRange, 'dots', totalPages]
  }, [currentPage, totalPages, siblingCount])

  if (totalPages <= 1) return null

  return (
    <nav
      role="navigation"
      aria-label="Pagination"
      className={cn('flex items-center gap-1', className)}
    >
      {/* Previous button */}
      <Button
        variant="ghost"
        size="icon-sm"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        aria-label="Go to previous page"
      >
        <ChevronLeft className="h-4 w-4" />
      </Button>

      {/* Page numbers */}
      {showPageNumbers && (
        <div className="flex items-center gap-1">
          {getPageNumbers.map((pageNumber, index) => {
            if (pageNumber === 'dots') {
              return (
                <span
                  key={`dots-${index}`}
                  className="w-8 h-8 flex items-center justify-center text-text-tertiary"
                >
                  <MoreHorizontal className="h-4 w-4" />
                </span>
              )
            }

            const page = pageNumber as number
            const isActive = page === currentPage

            return (
              <Button
                key={page}
                variant={isActive ? 'primary' : 'ghost'}
                size="icon-sm"
                onClick={() => onPageChange(page)}
                aria-label={`Go to page ${page}`}
                aria-current={isActive ? 'page' : undefined}
              >
                {page}
              </Button>
            )
          })}
        </div>
      )}

      {/* Next button */}
      <Button
        variant="ghost"
        size="icon-sm"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        aria-label="Go to next page"
      >
        <ChevronRight className="h-4 w-4" />
      </Button>
    </nav>
  )
}

// Compact pagination for limited space
interface PaginationCompactProps {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
  className?: string
}

export function PaginationCompact({
  currentPage,
  totalPages,
  onPageChange,
  className,
}: PaginationCompactProps) {
  if (totalPages <= 1) return null

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <Button
        variant="secondary"
        size="sm"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
      >
        Previous
      </Button>

      <span className="text-sm text-text-secondary px-2">
        Page {currentPage} of {totalPages}
      </span>

      <Button
        variant="secondary"
        size="sm"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
      >
        Next
      </Button>
    </div>
  )
}

// Info text for showing range
interface PaginationInfoProps {
  currentPage: number
  pageSize: number
  totalItems: number
  className?: string
}

export function PaginationInfo({
  currentPage,
  pageSize,
  totalItems,
  className,
}: PaginationInfoProps) {
  const start = (currentPage - 1) * pageSize + 1
  const end = Math.min(currentPage * pageSize, totalItems)

  return (
    <p className={cn('text-sm text-text-secondary', className)}>
      Showing {start} to {end} of {totalItems} results
    </p>
  )
}
