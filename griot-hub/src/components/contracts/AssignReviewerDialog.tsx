'use client'

import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Users, User, Loader2, UserPlus } from 'lucide-react'
import { Button } from '@/components/ui'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/Select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/Dialog'
import { api, queryKeys } from '@/lib/api/client'

interface SimpleUser {
  id: string
  name?: string
  email?: string
  username?: string
}

interface SimpleTeam {
  id: string
  name: string
  description?: string
}

interface AssignReviewerDialogProps {
  isOpen: boolean
  onClose: () => void
  onAssign: (data: { reviewerType: 'user' | 'team'; reviewerId: string; reviewerName: string }) => void
  isSubmitting?: boolean
  currentReviewerId?: string
  currentReviewerType?: 'user' | 'team'
}

export function AssignReviewerDialog({
  isOpen,
  onClose,
  onAssign,
  isSubmitting = false,
  currentReviewerId,
  currentReviewerType,
}: AssignReviewerDialogProps) {
  const [reviewerType, setReviewerType] = useState<'user' | 'team' | ''>(currentReviewerType || '')
  const [reviewerId, setReviewerId] = useState<string>(currentReviewerId || '')

  // Fetch teams for dropdown
  const { data: teams, isLoading: teamsLoading } = useQuery({
    queryKey: queryKeys.teams.list({}),
    queryFn: async () => {
      const response = await api.get<{ data?: SimpleTeam[]; items?: SimpleTeam[] } | SimpleTeam[]>('/teams')
      if (Array.isArray(response)) return response
      return response.items || response.data || []
    },
  })

  // Fetch users for dropdown
  const { data: users, isLoading: usersLoading } = useQuery({
    queryKey: queryKeys.users.all,
    queryFn: async () => {
      const response = await api.get<{ data?: SimpleUser[]; items?: SimpleUser[] } | SimpleUser[]>('/users')
      if (Array.isArray(response)) return response
      return response.items || response.data || []
    },
  })

  const handleTypeChange = (type: 'user' | 'team' | '') => {
    setReviewerType(type)
    setReviewerId('')
  }

  const handleAssign = () => {
    if (!reviewerType || !reviewerId) return

    let reviewerName = ''
    if (reviewerType === 'user') {
      const user = users?.find((u) => u.id === reviewerId)
      reviewerName = user?.name || user?.email || user?.username || reviewerId
    } else {
      const team = teams?.find((t) => t.id === reviewerId)
      reviewerName = team?.name || reviewerId
    }

    onAssign({
      reviewerType,
      reviewerId,
      reviewerName,
    })
  }

  const handleClose = () => {
    setReviewerType(currentReviewerType || '')
    setReviewerId(currentReviewerId || '')
    onClose()
  }

  const isValid = reviewerType && reviewerId

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[480px] border-l-4 border-l-primary-500 p-0 overflow-hidden">
        <div className="p-6">
          <DialogHeader className="p-0 pb-4">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-12 h-12 rounded-full bg-primary-500/10 flex items-center justify-center">
                <UserPlus className="w-6 h-6 text-primary-500" />
              </div>
              <div className="flex-1 min-w-0">
                <DialogTitle className="text-xl font-semibold">Assign Reviewer</DialogTitle>
                <DialogDescription className="mt-1">
                  Select a user or team to review this contract before it can be submitted.
                </DialogDescription>
              </div>
            </div>
          </DialogHeader>

          <div className="mt-4 space-y-4">
            {/* Reviewer Type */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                Reviewer Type
              </label>
              <Select
                value={reviewerType}
                onValueChange={(value) => handleTypeChange(value as 'user' | 'team' | '')}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select reviewer type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="user">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4" />
                      Individual User
                    </div>
                  </SelectItem>
                  <SelectItem value="team">
                    <div className="flex items-center gap-2">
                      <Users className="w-4 h-4" />
                      Team
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Reviewer Selection */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                {reviewerType === 'user' ? 'Select User' : reviewerType === 'team' ? 'Select Team' : 'Reviewer'}
              </label>
              <Select
                value={reviewerId}
                onValueChange={setReviewerId}
                disabled={!reviewerType}
              >
                <SelectTrigger>
                  <SelectValue
                    placeholder={
                      !reviewerType
                        ? 'Select type first'
                        : reviewerType === 'user'
                          ? 'Select a user...'
                          : 'Select a team...'
                    }
                  />
                </SelectTrigger>
                <SelectContent>
                  {reviewerType === 'user' && usersLoading && (
                    <div className="px-2 py-3 text-sm text-text-tertiary flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Loading users...
                    </div>
                  )}
                  {reviewerType === 'user' && !usersLoading && users?.map((user) => (
                    <SelectItem key={user.id} value={user.id}>
                      <div className="flex items-center gap-2">
                        <User className="w-4 h-4 text-text-tertiary" />
                        {user.name || user.email || user.username || user.id}
                      </div>
                    </SelectItem>
                  ))}
                  {reviewerType === 'user' && !usersLoading && (!users || users.length === 0) && (
                    <div className="px-2 py-3 text-sm text-text-tertiary">
                      No users available
                    </div>
                  )}
                  {reviewerType === 'team' && teamsLoading && (
                    <div className="px-2 py-3 text-sm text-text-tertiary flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Loading teams...
                    </div>
                  )}
                  {reviewerType === 'team' && !teamsLoading && teams?.map((team) => (
                    <SelectItem key={team.id} value={team.id}>
                      <div className="flex items-center gap-2">
                        <Users className="w-4 h-4 text-text-tertiary" />
                        {team.name}
                      </div>
                    </SelectItem>
                  ))}
                  {reviewerType === 'team' && !teamsLoading && (!teams || teams.length === 0) && (
                    <div className="px-2 py-3 text-sm text-text-tertiary">
                      No teams available
                    </div>
                  )}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        <DialogFooter className="bg-bg-tertiary border-t border-border-subtle p-4 mt-0">
          <Button variant="ghost" onClick={handleClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleAssign}
            disabled={isSubmitting || !isValid}
            className="min-w-[140px]"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Assigning...
              </>
            ) : (
              <>
                <UserPlus className="w-4 h-4 mr-2" />
                Assign Reviewer
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
