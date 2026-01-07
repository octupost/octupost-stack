'use client'

import { useEffect } from 'react'
import { useQueryState } from 'nuqs'
import { Sparkles, Zap, Crown } from 'lucide-react'
import { useStore } from '../store'
import { cn } from '../lib/utils'

export type TeamTier = 'free' | 'pro' | 'ultimate'

interface TeamConfig {
  id: string
  label: string
  tier: TeamTier
  description: string
  icon: typeof Sparkles
  badgeColor: string
}

const TEAMS: TeamConfig[] = [
  {
    id: 'video-script-team-free',
    label: 'Free',
    tier: 'free',
    description: 'Xiaomi Mimo',
    icon: Sparkles,
    badgeColor: 'bg-slate-500'
  },
  {
    id: 'video-script-team-pro',
    label: 'Pro',
    tier: 'pro',
    description: 'Grok 4.1 Fast',
    icon: Zap,
    badgeColor: 'bg-blue-500'
  },
  {
    id: 'video-script-team-ultimate',
    label: 'Max',
    tier: 'ultimate',
    description: 'Claude Sonnet 4.5',
    icon: Crown,
    badgeColor: 'bg-amber-500'
  }
]

interface TeamTierSelectorProps {
  className?: string
  defaultTeam?: TeamTier
}

export function TeamTierSelector({
  className,
  defaultTeam = 'free'
}: TeamTierSelectorProps) {
  const [teamId, setTeamId] = useQueryState('team')
  const setMode = useStore((s) => s.setMode)
  const addSystemMessage = useStore((s) => s.addSystemMessage)
  const lastTeamTier = useStore((s) => s.lastTeamTier)
  const setLastTeamTier = useStore((s) => s.setLastTeamTier)
  const setLastTeamId = useStore((s) => s.setLastTeamId)

  // Use persisted tier if available, otherwise use defaultTeam prop
  const effectiveDefaultTier = (lastTeamTier as TeamTier) || defaultTeam

  // Set mode to team on mount and persist teamId to localStorage
  useEffect(() => {
    setMode('team')
    if (!teamId) {
      const defaultTeamId =
        TEAMS.find((t) => t.tier === effectiveDefaultTier)?.id || TEAMS[0].id
      setTeamId(defaultTeamId)
      setLastTeamId(defaultTeamId)
    } else {
      setLastTeamId(teamId)
    }
  }, [setMode, teamId, setTeamId, effectiveDefaultTier, setLastTeamId])

  const handleTeamChange = (newTeamId: string) => {
    if (newTeamId === teamId) return
    const newTeam = TEAMS.find((t) => t.id === newTeamId)
    setTeamId(newTeamId)
    // Persist the selected tier and teamId to localStorage
    if (newTeam) {
      setLastTeamTier(newTeam.tier)
      setLastTeamId(newTeamId)
      addSystemMessage(`Switched to ${newTeam.label} model (${newTeam.description})`)
    }
  }

  const currentTeamId = teamId || TEAMS[0].id
  const currentTeam = TEAMS.find((t) => t.id === currentTeamId) || TEAMS[0]

  return (
    <div className={cn('flex flex-col gap-1.5', className)}>
      <label className="text-xs font-medium uppercase text-muted-foreground">
        AI Model
      </label>

      {/* Tier Buttons */}
      <div className="flex h-9 w-full rounded-lg border border-border bg-background p-0.5">
        {TEAMS.map((team) => {
          const IconComponent = team.icon
          const isActive = currentTeamId === team.id

          return (
            <button
              key={team.id}
              onClick={() => handleTeamChange(team.id)}
              title={team.description}
              className={cn(
                'flex flex-1 items-center justify-center gap-1.5 rounded-md px-2 py-1 text-xs font-medium transition-all',
                isActive
                  ? 'bg-primary text-primaryAccent shadow-sm'
                  : 'text-muted-foreground hover:bg-background-secondary hover:text-foreground'
              )}
            >
              <IconComponent className="h-3.5 w-3.5" />
              {team.label}
            </button>
          )
        })}
      </div>

      {/* Inline Model Description */}
      <div className="flex items-center gap-2 text-xs">
        <span className={cn('h-2 w-2 rounded-full', currentTeam.badgeColor)} />
        <span className="text-muted-foreground">{currentTeam.description}</span>
      </div>
    </div>
  )
}
