'use client'

import { useState, useCallback, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { Command } from 'cmdk'
import { useHotkeys } from 'react-hotkeys-hook'
import {
  Search,
  FileText,
  Database,
  AlertCircle,
  Users,
  Loader2,
  X,
} from 'lucide-react'
import { api, queryKeys } from '@/lib/api/client'
import { cn } from '@/lib/utils'
import { useDebounce } from '@/lib/hooks/useDebounce'
import type { GlobalSearchResults, SearchResult } from '@/types'

// Registry global search response format (from RES-registry-012)
interface RegistrySearchResponse {
  query: string
  results: {
    contracts?: { items: RegistrySearchItem[]; total: number; has_more?: boolean }
    issues?: { items: RegistrySearchItem[]; total: number; has_more?: boolean }
    teams?: { items: RegistrySearchItem[]; total: number; has_more?: boolean }
    users?: { items: RegistrySearchItem[]; total: number; has_more?: boolean }
  }
  quickActions?: Array<{ action: string; href: string; icon?: string }>
  totalResults?: number
  total_results?: number
  searchTimeMs?: number
  search_time_ms?: number
}

interface RegistrySearchItem {
  id: string
  type: string
  title: string
  subtitle?: string
  description?: string
  href: string
  icon?: string
  status?: string
  metadata?: Record<string, unknown>
  score?: number
  highlights?: Array<{ field: string; snippet: string }>
}

// Transform registry search item to frontend SearchResult
function adaptSearchItem(item: RegistrySearchItem): SearchResult {
  return {
    id: item.id,
    type: item.type as SearchResult['type'],
    name: item.title,
    href: item.href,
    domain: item.subtitle || undefined,
  }
}

const typeIcons = {
  contract: FileText,
  asset: Database,
  issue: AlertCircle,
  team: Users,
}

export function GlobalSearch() {
  const [open, setOpen] = useState(false)
  const [search, setSearch] = useState('')
  const router = useRouter()
  const debouncedSearch = useDebounce(search, 200)

  // Keyboard shortcut - Cmd/Ctrl + K
  useHotkeys('mod+k', (e) => {
    e.preventDefault()
    setOpen(true)
  })

  // Close on escape
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && open) {
        setOpen(false)
      }
    }
    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [open])

  const { data: results, isLoading } = useQuery({
    queryKey: queryKeys.search.global(debouncedSearch),
    queryFn: async () => {
      // Registry uses /search/global endpoint with different response format
      const response = await api.get<RegistrySearchResponse | GlobalSearchResults>(
        `/search/global?q=${encodeURIComponent(debouncedSearch)}`
      )

      // Handle registry response format (has 'results' object with nested items)
      if ('results' in response && response.results) {
        return {
          contracts: response.results.contracts?.items.map(adaptSearchItem) || [],
          assets: [], // Registry doesn't have assets search yet
          issues: response.results.issues?.items.map(adaptSearchItem) || [],
          teams: response.results.teams?.items.map(adaptSearchItem) || [],
        } as GlobalSearchResults
      }

      // Legacy format (direct arrays)
      return response as GlobalSearchResults
    },
    enabled: debouncedSearch.length >= 2,
  })

  const handleSelect = useCallback(
    (item: SearchResult) => {
      setOpen(false)
      setSearch('')
      router.push(item.href)
    },
    [router]
  )

  const hasResults =
    results &&
    (results.contracts?.length > 0 ||
      results.assets?.length > 0 ||
      results.issues?.length > 0 ||
      results.teams?.length > 0)

  return (
    <>
      {/* Search Trigger Button */}
      <button
        onClick={() => setOpen(true)}
        className={cn(
          'flex items-center gap-2 px-3 py-1.5 rounded-lg',
          'border border-border-default bg-bg-primary',
          'hover:border-border-strong transition-colors',
          'text-text-tertiary'
        )}
      >
        <Search className="w-4 h-4" />
        <span className="text-sm hidden sm:inline">Search...</span>
        <kbd className="hidden sm:inline-flex h-5 items-center gap-1 rounded border border-border-default bg-bg-tertiary px-1.5 font-mono text-xs">
          ⌘K
        </kbd>
      </button>

      {/* Search Dialog */}
      {open && (
        <div className="fixed inset-0 z-50">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/50 backdrop-blur-sm"
            onClick={() => setOpen(false)}
          />

          {/* Dialog */}
          <div className="fixed left-1/2 top-[15%] -translate-x-1/2 w-full max-w-lg">
            <Command
              className={cn(
                'bg-bg-secondary rounded-xl shadow-2xl border border-border-default overflow-hidden',
                'flex flex-col'
              )}
              shouldFilter={false}
            >
              {/* Input */}
              <div className="flex items-center border-b border-border-default px-4">
                <Search className="w-5 h-5 text-text-tertiary shrink-0" />
                <Command.Input
                  value={search}
                  onValueChange={setSearch}
                  placeholder="Search contracts, assets, issues..."
                  className={cn(
                    'flex-1 h-12 px-3 bg-transparent',
                    'text-text-primary placeholder:text-text-tertiary',
                    'focus:outline-none'
                  )}
                  autoFocus
                />
                {search && (
                  <button
                    onClick={() => setSearch('')}
                    className="p-1 hover:bg-bg-hover rounded"
                  >
                    <X className="w-4 h-4 text-text-tertiary" />
                  </button>
                )}
              </div>

              {/* Results */}
              <Command.List className="max-h-80 overflow-y-auto p-2">
                {isLoading && debouncedSearch.length >= 2 && (
                  <div className="p-8 text-center">
                    <Loader2 className="w-6 h-6 animate-spin mx-auto text-text-tertiary" />
                    <p className="text-sm text-text-secondary mt-2">Searching...</p>
                  </div>
                )}

                {!isLoading && debouncedSearch.length >= 2 && !hasResults && (
                  <div className="p-8 text-center">
                    <Search className="w-8 h-8 mx-auto text-text-tertiary mb-2" />
                    <p className="text-text-secondary">
                      No results found for &quot;{debouncedSearch}&quot;
                    </p>
                  </div>
                )}

                {debouncedSearch.length < 2 && (
                  <div className="p-8 text-center">
                    <p className="text-text-tertiary text-sm">
                      Type at least 2 characters to search
                    </p>
                  </div>
                )}

                {results?.contracts && results.contracts.length > 0 && (
                  <Command.Group heading="Contracts" className="mb-2">
                    <p className="px-2 py-1.5 text-xs font-medium text-text-tertiary uppercase tracking-wider">
                      Contracts
                    </p>
                    {results.contracts.map((item) => (
                      <SearchResultItem
                        key={item.id}
                        item={item}
                        onSelect={handleSelect}
                      />
                    ))}
                  </Command.Group>
                )}

                {results?.assets && results.assets.length > 0 && (
                  <Command.Group heading="Data Assets" className="mb-2">
                    <p className="px-2 py-1.5 text-xs font-medium text-text-tertiary uppercase tracking-wider">
                      Data Assets
                    </p>
                    {results.assets.map((item) => (
                      <SearchResultItem
                        key={item.id}
                        item={item}
                        onSelect={handleSelect}
                      />
                    ))}
                  </Command.Group>
                )}

                {results?.issues && results.issues.length > 0 && (
                  <Command.Group heading="Issues" className="mb-2">
                    <p className="px-2 py-1.5 text-xs font-medium text-text-tertiary uppercase tracking-wider">
                      Issues
                    </p>
                    {results.issues.map((item) => (
                      <SearchResultItem
                        key={item.id}
                        item={item}
                        onSelect={handleSelect}
                      />
                    ))}
                  </Command.Group>
                )}

                {results?.teams && results.teams.length > 0 && (
                  <Command.Group heading="Teams" className="mb-2">
                    <p className="px-2 py-1.5 text-xs font-medium text-text-tertiary uppercase tracking-wider">
                      Teams
                    </p>
                    {results.teams.map((item) => (
                      <SearchResultItem
                        key={item.id}
                        item={item}
                        onSelect={handleSelect}
                      />
                    ))}
                  </Command.Group>
                )}
              </Command.List>

              {/* Footer */}
              <div className="flex items-center justify-between px-4 py-2 border-t border-border-default text-xs text-text-tertiary">
                <div className="flex items-center gap-4">
                  <span className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-bg-tertiary rounded">↑↓</kbd>
                    <span>Navigate</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-bg-tertiary rounded">↵</kbd>
                    <span>Open</span>
                  </span>
                </div>
                <span className="flex items-center gap-1">
                  <kbd className="px-1.5 py-0.5 bg-bg-tertiary rounded">esc</kbd>
                  <span>Close</span>
                </span>
              </div>
            </Command>
          </div>
        </div>
      )}
    </>
  )
}

function SearchResultItem({
  item,
  onSelect,
}: {
  item: SearchResult
  onSelect: (item: SearchResult) => void
}) {
  const Icon = typeIcons[item.type]

  return (
    <Command.Item
      value={`${item.type}-${item.id}`}
      onSelect={() => onSelect(item)}
      className={cn(
        'flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer',
        'hover:bg-bg-hover',
        'aria-selected:bg-bg-hover'
      )}
    >
      <Icon className="w-4 h-4 text-text-tertiary shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="text-sm text-text-primary truncate">{item.name}</p>
        {item.domain && (
          <p className="text-xs text-text-tertiary">{item.domain}</p>
        )}
      </div>
    </Command.Item>
  )
}
