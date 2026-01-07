'use client'

import { useState, useEffect, useCallback } from 'react'
import { createClient, RealtimeChannel } from '@supabase/supabase-js'
import {
  Film,
  Mic,
  Music,
  Type,
  Clock,
  Coins,
  ChevronRight,
  Check,
  Loader2,
  AlertCircle,
  Play,
  Pause,
} from 'lucide-react'
import { cn } from '../../lib/utils'

// Scene breakdown from plan
interface SceneBreakdown {
  name: string
  description: string
  duration_seconds: number
  assets_needed: string[]
  video_prompt?: string
  speech_text?: string
  text_content?: string
  credit_estimate: number
}

// Plan from database
interface VideoPlan {
  id: string
  project_id: string
  title: string
  description: string | null
  total_duration_seconds: number | null
  estimated_credits: number | null
  estimated_duration_minutes: number | null
  scenes_breakdown: SceneBreakdown[]
  status: 'pending' | 'approved' | 'executing' | 'completed' | 'completed_with_errors' | 'failed'
  approved_at: string | null
  completed_at: string | null
  created_at: string
}

interface PlanPreviewProps {
  projectId: string
  supabaseUrl: string
  supabaseAnonKey: string
  className?: string
  onApprove?: (planId: string) => void
  onReject?: (planId: string) => void
}

// Asset type icons
const assetIcons: Record<string, typeof Film> = {
  video: Film,
  speech: Mic,
  music: Music,
  text: Type,
}

// Format duration
function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${seconds}s`
  }
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return secs > 0 ? `${mins}m ${secs}s` : `${mins}m`
}

export function PlanPreview({
  projectId,
  supabaseUrl,
  supabaseAnonKey,
  className,
  onApprove,
  onReject,
}: PlanPreviewProps) {
  const [plan, setPlan] = useState<VideoPlan | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [expandedScene, setExpandedScene] = useState<number | null>(null)

  const supabase = createClient(supabaseUrl, supabaseAnonKey)

  // Fetch plan data
  const fetchPlan = useCallback(async () => {
    setIsLoading(true)

    try {
      const { data } = await supabase
        .schema('octupost')
        .from('project_video_plans')
        .select('*')
        .eq('project_id', projectId)
        .in('status', ['pending', 'approved', 'executing'])
        .order('created_at', { ascending: false })
        .limit(1)
        .single()

      setPlan(data)
    } catch (error) {
      console.error('Error fetching plan:', error)
      setPlan(null)
    } finally {
      setIsLoading(false)
    }
  }, [projectId, supabase])

  // Set up realtime subscription
  useEffect(() => {
    let channel: RealtimeChannel | null = null

    const setupSubscription = async () => {
      channel = supabase
        .channel(`plan_preview:${projectId}`)
        .on(
          'postgres_changes',
          {
            event: '*',
            schema: 'octupost',
            table: 'project_video_plans',
            filter: `project_id=eq.${projectId}`,
          },
          (payload) => {
            if (payload.eventType === 'INSERT' || payload.eventType === 'UPDATE') {
              const newPlan = payload.new as VideoPlan
              if (['pending', 'approved', 'executing'].includes(newPlan.status)) {
                setPlan(newPlan)
              } else if (plan?.id === newPlan.id) {
                setPlan(null)
              }
            }
          }
        )
        .subscribe()
    }

    fetchPlan()
    setupSubscription()

    return () => {
      if (channel) supabase.removeChannel(channel)
    }
  }, [projectId, supabase, fetchPlan, plan?.id])

  // Don't render if no pending/executing plan
  if (!plan && !isLoading) {
    return null
  }

  // Loading state
  if (isLoading) {
    return (
      <div className={cn('rounded-lg border border-border bg-background-secondary p-4', className)}>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span>Loading plan...</span>
        </div>
      </div>
    )
  }

  if (!plan) return null

  const scenes = plan.scenes_breakdown || []
  const totalDuration = plan.total_duration_seconds || scenes.reduce((acc, s) => acc + s.duration_seconds, 0)
  const totalCredits = plan.estimated_credits || scenes.reduce((acc, s) => acc + s.credit_estimate, 0)

  return (
    <div className={cn('rounded-lg border border-border bg-background-secondary overflow-hidden', className)}>
      {/* Header */}
      <div className="bg-primary/5 border-b border-border p-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Film className="h-4 w-4 text-primary" />
            <h3 className="text-sm font-semibold text-foreground">{plan.title}</h3>
            {plan.status === 'pending' && (
              <span className="px-2 py-0.5 bg-yellow-500/10 text-yellow-600 text-xs font-medium rounded">
                Awaiting Approval
              </span>
            )}
            {plan.status === 'executing' && (
              <span className="px-2 py-0.5 bg-blue-500/10 text-blue-600 text-xs font-medium rounded flex items-center gap-1">
                <Loader2 className="h-3 w-3 animate-spin" />
                Executing
              </span>
            )}
          </div>
        </div>

        {/* Summary stats */}
        <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
          <div className="flex items-center gap-1">
            <Film className="h-3 w-3" />
            <span>{scenes.length} scenes</span>
          </div>
          <div className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            <span>{formatDuration(totalDuration)}</span>
          </div>
          <div className="flex items-center gap-1">
            <Coins className="h-3 w-3" />
            <span>~{totalCredits} credits</span>
          </div>
        </div>
      </div>

      {/* Visual Timeline */}
      <div className="p-3">
        <div className="flex gap-1 mb-3">
          {scenes.map((scene, index) => {
            const widthPercent = (scene.duration_seconds / totalDuration) * 100
            return (
              <div
                key={index}
                className={cn(
                  'h-2 rounded-full bg-primary/20 hover:bg-primary/40 cursor-pointer transition-colors',
                  expandedScene === index && 'bg-primary/60'
                )}
                style={{ width: `${Math.max(widthPercent, 5)}%` }}
                onClick={() => setExpandedScene(expandedScene === index ? null : index)}
                title={`${scene.name} (${formatDuration(scene.duration_seconds)})`}
              />
            )
          })}
        </div>

        {/* Scene list */}
        <div className="space-y-2">
          {scenes.map((scene, index) => {
            const isExpanded = expandedScene === index

            return (
              <div
                key={index}
                className={cn(
                  'rounded-lg border border-border/50 bg-background transition-all',
                  isExpanded && 'border-primary/30 shadow-sm'
                )}
              >
                {/* Scene header */}
                <button
                  onClick={() => setExpandedScene(isExpanded ? null : index)}
                  className="w-full flex items-center justify-between p-2 text-left hover:bg-background-secondary/50 rounded-lg"
                >
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-primary/10 text-primary text-xs font-medium flex items-center justify-center">
                      {index + 1}
                    </span>
                    <span className="text-sm font-medium text-foreground">{scene.name}</span>
                    <span className="text-xs text-muted-foreground">
                      ({formatDuration(scene.duration_seconds)})
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    {/* Asset icons */}
                    <div className="flex items-center gap-1">
                      {scene.assets_needed.map((asset) => {
                        const Icon = assetIcons[asset] || Film
                        return (
                          <div
                            key={asset}
                            className="w-5 h-5 rounded bg-muted/50 flex items-center justify-center"
                            title={asset}
                          >
                            <Icon className="h-3 w-3 text-muted-foreground" />
                          </div>
                        )
                      })}
                    </div>
                    <ChevronRight
                      className={cn(
                        'h-4 w-4 text-muted-foreground transition-transform',
                        isExpanded && 'rotate-90'
                      )}
                    />
                  </div>
                </button>

                {/* Expanded details */}
                {isExpanded && (
                  <div className="px-3 pb-3 pt-1 border-t border-border/30 space-y-2">
                    <p className="text-xs text-muted-foreground">{scene.description}</p>

                    {scene.video_prompt && (
                      <div className="text-xs">
                        <span className="font-medium text-foreground">Video: </span>
                        <span className="text-muted-foreground">{scene.video_prompt}</span>
                      </div>
                    )}

                    {scene.speech_text && (
                      <div className="text-xs">
                        <span className="font-medium text-foreground">Speech: </span>
                        <span className="text-muted-foreground italic">"{scene.speech_text}"</span>
                      </div>
                    )}

                    {scene.text_content && (
                      <div className="text-xs">
                        <span className="font-medium text-foreground">Text: </span>
                        <span className="text-muted-foreground">"{scene.text_content}"</span>
                      </div>
                    )}

                    <div className="flex items-center gap-1 text-xs text-muted-foreground">
                      <Coins className="h-3 w-3" />
                      <span>~{scene.credit_estimate} credits</span>
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Action buttons (only for pending plans) */}
      {plan.status === 'pending' && (onApprove || onReject) && (
        <div className="border-t border-border p-3 flex items-center justify-between bg-background">
          <div className="text-xs text-muted-foreground">
            Total: <span className="font-medium text-foreground">~{totalCredits} credits</span>
          </div>
          <div className="flex items-center gap-2">
            {onReject && (
              <button
                onClick={() => onReject(plan.id)}
                className="px-3 py-1.5 text-xs font-medium text-muted-foreground hover:text-foreground rounded-lg border border-border hover:bg-background-secondary transition-colors"
              >
                Reject
              </button>
            )}
            {onApprove && (
              <button
                onClick={() => onApprove(plan.id)}
                className="px-3 py-1.5 text-xs font-medium text-white bg-primary hover:bg-primary/90 rounded-lg transition-colors flex items-center gap-1"
              >
                <Check className="h-3 w-3" />
                Approve Plan
              </button>
            )}
          </div>
        </div>
      )}

      {/* Executing state */}
      {plan.status === 'executing' && (
        <div className="border-t border-border p-3 bg-blue-500/5">
          <div className="flex items-center gap-2 text-xs text-blue-600">
            <Loader2 className="h-3 w-3 animate-spin" />
            <span>Plan is being executed. Check task progress above.</span>
          </div>
        </div>
      )}
    </div>
  )
}

export default PlanPreview
