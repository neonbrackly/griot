'use client'

import { PageShell, PageContainer, PageHeader, Card } from '@/components/layout'
import { Button, Input, Badge } from '@/components/ui'
import { Search, Users, Mail, Database } from 'lucide-react'
import { BackLink } from '@/components/navigation'
import { useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { api, queryKeys } from '@/lib/api/client'
import type { Team } from '@/types'
import { useState, useMemo } from 'react'
import { useDebounce } from '@/lib/hooks'
import { Skeleton } from '@/components/feedback'

export default function TeamsDirectoryPage() {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState('')
  const debouncedSearch = useDebounce(searchQuery, 300)

  // Fetch teams
  const {
    data: teamsData,
    isLoading,
  } = useQuery<Team[]>({
    queryKey: queryKeys.teams.all,
    queryFn: () => api.get('/teams'),
  })

  const teams = teamsData || []

  // Filter teams
  const filteredTeams = useMemo(() => {
    return teams.filter((team) => {
      const matchesSearch =
        !debouncedSearch ||
        team.name.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
        team.description?.toLowerCase().includes(debouncedSearch.toLowerCase())

      return matchesSearch
    })
  }, [teams, debouncedSearch])

  return (
    <PageShell>
      <PageContainer>
        <BackLink href="/marketplace" />

        <PageHeader
          title="Teams Directory"
          description="Explore teams and their data assets"
          actions={
            <Button variant="secondary">
              <Mail className="w-4 h-4 mr-2" />
              Contact Admin
            </Button>
          }
        />

        {/* Search */}
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-text-tertiary" />
            <Input
              placeholder="Search teams..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Teams Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {isLoading ? (
            <>
              {Array.from({ length: 6 }).map((_, i) => (
                <Card key={i} padding="lg">
                  <Skeleton className="h-32" />
                </Card>
              ))}
            </>
          ) : (
            filteredTeams.map((team) => (
              <Card
                key={team.id}
                padding="lg"
                className="cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => router.push(`/marketplace/teams/${team.id}`)}
              >
                <div className="flex items-start gap-3 mb-4">
                  <div className="p-2 rounded-lg bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400">
                    <Users className="w-5 h-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-text-primary truncate">{team.name}</h3>
                    <p className="text-sm text-text-secondary line-clamp-2 mt-1">{team.description || 'No description'}</p>
                  </div>
                </div>

                <div className="space-y-2 pt-4 border-t border-border-default">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-text-tertiary">Members</span>
                    <Badge variant="secondary" size="sm">
                      {Math.floor(Math.random() * 20) + 5}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-text-tertiary">Assets</span>
                    <div className="flex items-center gap-1">
                      <Database className="w-3 h-3 text-text-tertiary" />
                      <span className="text-text-secondary">{Math.floor(Math.random() * 10) + 1}</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-text-tertiary">Domains</span>
                    <Badge variant="secondary" size="sm">
                      {team.domains && team.domains.length > 0 ? team.domains.join(', ') : 'General'}
                    </Badge>
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>

        {filteredTeams.length === 0 && !isLoading && (
          <Card padding="lg" className="text-center">
            <Users className="w-12 h-12 mx-auto mb-3 text-text-tertiary opacity-50" />
            <p className="text-text-secondary">No teams found</p>
          </Card>
        )}
      </PageContainer>
    </PageShell>
  )
}
