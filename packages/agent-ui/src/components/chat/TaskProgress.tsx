'use client'

import { useEffect, useState, useCallback } from 'react'
import { createClient, RealtimeChannel } from '@supabase/supabase-js'
import {
  CheckCircle2,
  Circle,
  Loader2,
  XCircle,
  ChevronDown,
  ChevronUp,
  ListTodo,
  Sparkles,
} from 'lucide-react'
import { cn } from '../../lib/utils'

// Task type from database
interface ProjectTask {
  id: string
  project_id: string
  plan_id: string | null
  scene_id: string | null
  title: string
  description: string | null
  task_type: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'skipped'
  order_index: number
  metadata: Record<string, unknown>
  error_message: string | null
  started_at: string | null
  completed_at: string | null
  created_at: string
  updated_at: string
}

// Plan type from database
interface VideoPlan {
  id: string
  project_id: string
  title: string
  description: string | null
  status: 'pending' | 'approved' | 'executing' | 'completed' | 'completed_with_errors' | 'failed'
  estimated_credits: number | null
  scenes_breakdown: unknown[]
  created_at: string
}

interface TaskProgressProps {
  projectId: string
  supabaseUrl: string
  supabaseAnonKey: string
  className?: string
  // Optional: collapse by default
  defaultCollapsed?: boolean
}

const statusConfig = {
  pending: {
    icon: Circle,
    className: 'text-muted-foreground',
    label: 'Pending',
  },
  in_progress: {
    icon: Loader2,
    className: 'text-blue-500 animate-spin',
    label: 'In Progress',
  },
  completed: {
    icon: CheckCircle2,
    className: 'text-green-500',
    label: 'Completed',
  },
  failed: {
    icon: XCircle,
    className: 'text-red-500',
    label: 'Failed',
  },
  skipped: {
    icon: Circle,
    className: 'text-muted-foreground/50',
    label: 'Skipped',
  },
}

export function TaskProgress({
  projectId,
  supabaseUrl,
  supabaseAnonKey,
  className,
  defaultCollapsed = false,
}: TaskProgressProps) {
  const [tasks, setTasks] = useState<ProjectTask[]>([])
  const [plan, setPlan] = useState<VideoPlan | null>(null)
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed)
  const [isLoading, setIsLoading] = useState(true)

  // Create Supabase client
  const supabase = createClient(supabaseUrl, supabaseAnonKey)

  // Fetch initial data
  const fetchData = useCallback(async () => {
    setIsLoading(true)

    try {
      // Fetch active plan
      const { data: planData } = await supabase
        .schema('octupost')
        .from('project_video_plans')
        .select('*')
        .eq('project_id', projectId)
        .in('status', ['pending', 'approved', 'executing'])
        .order('created_at', { ascending: false })
        .limit(1)
        .single()

      if (planData) {
        setPlan(planData)

        // Fetch tasks for this plan
        const { data: taskData } = await supabase
          .schema('octupost')
          .from('project_tasks')
          .select('*')
          .eq('plan_id', planData.id)
          .order('order_index', { ascending: true })

        setTasks(taskData || [])
      } else {
        setPlan(null)
        setTasks([])
      }
    } catch (error) {
      console.error('Error fetching task data:', error)
    } finally {
      setIsLoading(false)
    }
  }, [projectId, supabase])

  // Set up realtime subscription
  useEffect(() => {
    let tasksChannel: RealtimeChannel | null = null
    let plansChannel: RealtimeChannel | null = null

    const setupSubscriptions = async () => {
      // Subscribe to tasks changes
      tasksChannel = supabase
        .channel(`project_tasks:${projectId}`)
        .on(
          'postgres_changes',
          {
            event: '*',
            schema: 'octupost',
            table: 'project_tasks',
            filter: `project_id=eq.${projectId}`,
          },
          (payload) => {
            if (payload.eventType === 'INSERT') {
              setTasks((prev) => {
                const newTask = payload.new as ProjectTask
                // Insert in order
                const updated = [...prev, newTask].sort(
                  (a, b) => a.order_index - b.order_index
                )
                return updated
              })
            } else if (payload.eventType === 'UPDATE') {
              setTasks((prev) =>
                prev.map((t) =>
                  t.id === payload.new.id ? (payload.new as ProjectTask) : t
                )
              )
            } else if (payload.eventType === 'DELETE') {
              setTasks((prev) => prev.filter((t) => t.id !== payload.old.id))
            }
          }
        )
        .subscribe()

      // Subscribe to plans changes
      plansChannel = supabase
        .channel(`project_plans:${projectId}`)
        .on(
          'postgres_changes',
          {
            event: '*',
            schema: 'octupost',
            table: 'project_video_plans',
            filter: `project_id=eq.${projectId}`,
          },
          (payload) => {
            if (
              payload.eventType === 'INSERT' ||
              payload.eventType === 'UPDATE'
            ) {
              const newPlan = payload.new as VideoPlan
              // Only show active plans
              if (
                ['pending', 'approved', 'executing'].includes(newPlan.status)
              ) {
                setPlan(newPlan)
                // Refresh tasks when plan changes
                fetchData()
              } else if (plan?.id === newPlan.id) {
                // Plan completed/failed - clear it
                setPlan(null)
                setTasks([])
              }
            }
          }
        )
        .subscribe()
    }

    // Initial fetch
    fetchData()

    // Setup subscriptions
    setupSubscriptions()

    // Cleanup
    return () => {
      if (tasksChannel) supabase.removeChannel(tasksChannel)
      if (plansChannel) supabase.removeChannel(plansChannel)
    }
  }, [projectId, supabase, fetchData, plan?.id])

  // Calculate progress
  const completedCount = tasks.filter(
    (t) => t.status === 'completed' || t.status === 'skipped'
  ).length
  const failedCount = tasks.filter((t) => t.status === 'failed').length
  const totalCount = tasks.length
  const progressPercent =
    totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0

  // Find current task (first in_progress or first pending)
  const currentTask =
    tasks.find((t) => t.status === 'in_progress') ||
    tasks.find((t) => t.status === 'pending')

  // Don't render if no active plan
  if (!plan && !isLoading) {
    return null
  }

  // Loading state
  if (isLoading) {
    return (
      <div
        className={cn(
          'rounded-lg border border-border bg-background-secondary p-3',
          className
        )}
      >
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span>Loading tasks...</span>
        </div>
      </div>
    )
  }

  return (
    <div
      className={cn(
        'rounded-lg border border-border bg-background-secondary overflow-hidden',
        className
      )}
    >
      {/* Header */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="flex w-full items-center justify-between p-3 text-left hover:bg-background/50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <ListTodo className="h-4 w-4 text-primary" />
          <span className="text-sm font-medium text-foreground">
            {plan?.title || 'Video Plan'}
          </span>
          {plan?.status === 'executing' && (
            <Sparkles className="h-3 w-3 text-yellow-500 animate-pulse" />
          )}
        </div>
        <div className="flex items-center gap-3">
          {/* Progress badge */}
          <div className="flex items-center gap-1.5">
            <span className="text-xs font-medium text-muted-foreground">
              {completedCount}/{totalCount}
            </span>
            {failedCount > 0 && (
              <span className="text-xs font-medium text-red-500">
                ({failedCount} failed)
              </span>
            )}
          </div>
          {isCollapsed ? (
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          ) : (
            <ChevronUp className="h-4 w-4 text-muted-foreground" />
          )}
        </div>
      </button>

      {/* Progress bar */}
      <div className="h-1 bg-background">
        <div
          className={cn(
            'h-full transition-all duration-500',
            failedCount > 0 ? 'bg-yellow-500' : 'bg-green-500'
          )}
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {/* Task list (collapsible) */}
      {!isCollapsed && (
        <div className="divide-y divide-border/50">
          {/* Current task highlight */}
          {currentTask && (
            <div className="bg-primary/5 px-3 py-2 border-l-2 border-primary">
              <div className="flex items-center gap-2">
                <Loader2 className="h-3.5 w-3.5 text-primary animate-spin" />
                <span className="text-xs font-medium text-primary">
                  {currentTask.status === 'in_progress'
                    ? 'Working on:'
                    : 'Next up:'}
                </span>
                <span className="text-xs text-foreground truncate">
                  {currentTask.title}
                </span>
              </div>
            </div>
          )}

          {/* Task list */}
          <div className="max-h-48 overflow-y-auto">
            {tasks.map((task) => {
              const config = statusConfig[task.status]
              const Icon = config.icon

              return (
                <div
                  key={task.id}
                  className={cn(
                    'flex items-start gap-2 px-3 py-2 transition-colors',
                    task.status === 'in_progress' && 'bg-blue-500/5',
                    task.status === 'failed' && 'bg-red-500/5'
                  )}
                >
                  <Icon className={cn('h-4 w-4 mt-0.5 shrink-0', config.className)} />
                  <div className="flex-1 min-w-0">
                    <p
                      className={cn(
                        'text-xs truncate',
                        task.status === 'completed' && 'text-muted-foreground line-through',
                        task.status === 'skipped' && 'text-muted-foreground/50 line-through',
                        task.status === 'failed' && 'text-red-600',
                        task.status === 'in_progress' && 'text-foreground font-medium',
                        task.status === 'pending' && 'text-muted-foreground'
                      )}
                    >
                      {task.title}
                    </p>
                    {task.error_message && (
                      <p className="text-xs text-red-500 mt-0.5 truncate">
                        {task.error_message}
                      </p>
                    )}
                  </div>
                </div>
              )
            })}
          </div>

          {/* Completion message */}
          {totalCount > 0 && completedCount === totalCount && failedCount === 0 && (
            <div className="px-3 py-2 bg-green-500/10 text-center">
              <span className="text-xs font-medium text-green-600">
                All tasks completed!
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default TaskProgress
