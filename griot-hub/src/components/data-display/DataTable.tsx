'use client'

import * as React from 'react'
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  getFilteredRowModel,
  flexRender,
  type ColumnDef,
  type SortingState,
  type ColumnFiltersState,
  type RowSelectionState,
  type PaginationState,
} from '@tanstack/react-table'
import { ChevronDown, ChevronUp, ChevronsUpDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Checkbox } from '@/components/ui/Checkbox'
import { Skeleton } from '@/components/feedback/Skeleton'

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
  loading?: boolean
  // Selection
  enableSelection?: boolean
  onSelectionChange?: (rows: TData[]) => void
  // Sorting
  enableSorting?: boolean
  defaultSorting?: SortingState
  // Pagination
  enablePagination?: boolean
  pageSize?: number
  // Styling
  className?: string
  stickyHeader?: boolean
  // Row actions
  onRowClick?: (row: TData) => void
  onRowHover?: (row: TData) => void
}

export function DataTable<TData, TValue>({
  columns,
  data,
  loading = false,
  enableSelection = false,
  onSelectionChange,
  enableSorting = true,
  defaultSorting = [],
  enablePagination = false,
  pageSize = 10,
  className,
  stickyHeader = false,
  onRowClick,
  onRowHover,
}: DataTableProps<TData, TValue>) {
  const [sorting, setSorting] = React.useState<SortingState>(defaultSorting)
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([])
  const [rowSelection, setRowSelection] = React.useState<RowSelectionState>({})
  const [pagination, setPagination] = React.useState<PaginationState>({
    pageIndex: 0,
    pageSize,
  })

  // Add selection column if enabled
  const tableColumns = React.useMemo(() => {
    if (!enableSelection) return columns

    const selectionColumn: ColumnDef<TData, TValue> = {
      id: 'select',
      header: ({ table }) => (
        <Checkbox
          checked={table.getIsAllPageRowsSelected()}
          indeterminate={table.getIsSomePageRowsSelected()}
          onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
          aria-label="Select all"
        />
      ),
      cell: ({ row }) => (
        <Checkbox
          checked={row.getIsSelected()}
          onCheckedChange={(value) => row.toggleSelected(!!value)}
          aria-label="Select row"
          onClick={(e) => e.stopPropagation()}
        />
      ),
      enableSorting: false,
      enableHiding: false,
    }

    return [selectionColumn, ...columns]
  }, [columns, enableSelection])

  const table = useReactTable({
    data,
    columns: tableColumns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: enableSorting ? getSortedRowModel() : undefined,
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: enablePagination ? getPaginationRowModel() : undefined,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onRowSelectionChange: setRowSelection,
    onPaginationChange: setPagination,
    state: {
      sorting,
      columnFilters,
      rowSelection,
      pagination,
    },
  })

  // Notify parent of selection changes
  React.useEffect(() => {
    if (onSelectionChange) {
      const selectedRows = table.getFilteredSelectedRowModel().rows.map((row) => row.original)
      onSelectionChange(selectedRows)
    }
  }, [rowSelection, table, onSelectionChange])

  if (loading) {
    return <DataTableSkeleton columns={columns.length + (enableSelection ? 1 : 0)} rows={pageSize} />
  }

  return (
    <div className={cn('rounded-lg border border-border-default overflow-hidden', className)}>
      <div className={cn('overflow-auto', stickyHeader && 'max-h-[600px]')}>
        <table className="w-full text-sm">
          <thead className={cn('bg-bg-tertiary', stickyHeader && 'sticky top-0 z-10')}>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className={cn(
                      'px-4 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wide',
                      header.column.getCanSort() && 'cursor-pointer select-none hover:bg-bg-hover'
                    )}
                    onClick={header.column.getToggleSortingHandler()}
                  >
                    <div className="flex items-center gap-1">
                      {header.isPlaceholder
                        ? null
                        : flexRender(header.column.columnDef.header, header.getContext())}
                      {header.column.getCanSort() && (
                        <span className="ml-1">
                          {{
                            asc: <ChevronUp className="h-4 w-4" />,
                            desc: <ChevronDown className="h-4 w-4" />,
                          }[header.column.getIsSorted() as string] ?? (
                            <ChevronsUpDown className="h-4 w-4 text-text-tertiary" />
                          )}
                        </span>
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="divide-y divide-border-default bg-bg-secondary">
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <tr
                  key={row.id}
                  className={cn(
                    'transition-colors duration-fast',
                    row.getIsSelected() && 'bg-primary-50 dark:bg-primary-900/10',
                    onRowClick && 'cursor-pointer hover:bg-bg-hover'
                  )}
                  onClick={() => onRowClick?.(row.original)}
                  onMouseEnter={() => onRowHover?.(row.original)}
                >
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id} className="px-4 py-3 text-text-primary">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td
                  colSpan={tableColumns.length}
                  className="h-24 text-center text-text-tertiary"
                >
                  No results found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {enablePagination && data.length > pageSize && (
        <div className="flex items-center justify-between px-4 py-3 border-t border-border-default bg-bg-tertiary">
          <div className="text-sm text-text-secondary">
            Showing {pagination.pageIndex * pagination.pageSize + 1} to{' '}
            {Math.min((pagination.pageIndex + 1) * pagination.pageSize, data.length)} of{' '}
            {data.length} results
          </div>
          <div className="flex items-center gap-2">
            <button
              className="px-3 py-1 text-sm font-medium rounded-md border border-border-default hover:bg-bg-hover disabled:opacity-50 disabled:cursor-not-allowed"
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
            >
              Previous
            </button>
            <span className="text-sm text-text-secondary">
              Page {pagination.pageIndex + 1} of {table.getPageCount()}
            </span>
            <button
              className="px-3 py-1 text-sm font-medium rounded-md border border-border-default hover:bg-bg-hover disabled:opacity-50 disabled:cursor-not-allowed"
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

// Loading skeleton for DataTable
function DataTableSkeleton({ columns, rows }: { columns: number; rows: number }) {
  return (
    <div className="rounded-lg border border-border-default overflow-hidden">
      <table className="w-full">
        <thead className="bg-bg-tertiary">
          <tr>
            {Array.from({ length: columns }).map((_, i) => (
              <th key={i} className="px-4 py-3">
                <Skeleton className="h-4 w-20" />
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border-default bg-bg-secondary">
          {Array.from({ length: rows }).map((_, rowIdx) => (
            <tr key={rowIdx}>
              {Array.from({ length: columns }).map((_, colIdx) => (
                <td key={colIdx} className="px-4 py-3">
                  <Skeleton className="h-5 w-full max-w-[200px]" />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
