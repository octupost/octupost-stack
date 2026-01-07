'use client'

import { useEffect, useRef, useCallback } from 'react'
import { useStore } from '../store'
import { ChatArea } from './chat/ChatArea'
import useChatActions from '../hooks/useChatActions'
import { useCreditBalance } from '../hooks/useCreditBalance'
import ConnectionStatus from './chat/ChatArea/ConnectionStatus'
import { TaskProgress } from './chat/TaskProgress'
import { PlanPreview } from './chat/PlanPreview'
import { FloatingProgressToast } from './chat/FloatingProgressToast'
import { useQueryState } from 'nuqs'
import { Plus, MessageSquare, Bot } from 'lucide-react'
import { cn } from '../lib/utils'

interface VideoEditorChatProps {
  agentOsUrl?: string
  className?: string
  // Project context for session persistence
  projectId?: string
  initialSessionId?: string | null
  onSessionChange?: (sessionId: string | null) => void
  // Supabase config for realtime task tracking
  supabaseUrl?: string
  supabaseAnonKey?: string
}

// Connection status indicator dot
const ConnectionDot = ({
  isActive,
  isLoading
}: {
  isActive: boolean
  isLoading: boolean
}) => {
  if (isLoading) {
    return (
      <div
        className="h-2 w-2 animate-pulse rounded-full bg-yellow-500"
        title="Connecting..."
      />
    )
  }
  return (
    <div
      className={cn(
        'h-2 w-2 rounded-full',
        isActive ? 'bg-green-500' : 'bg-red-500'
      )}
      title={isActive ? 'Connected' : 'Disconnected'}
    />
  )
}

/**
 * VideoEditorChat - A wrapper component for embedding the Agent UI
 * in the video editor's sidebar panel.
 *
 * Uses a single video-creator agent with HITL confirmation.
 * Supports session persistence per project.
 */
export function VideoEditorChat({
  agentOsUrl = 'http://localhost:7777',
  className,
  projectId,
  initialSessionId,
  onSessionChange,
  supabaseUrl,
  supabaseAnonKey,
}: VideoEditorChatProps) {
  const setEndpoint = useStore((s) => s.setSelectedEndpoint)
  const isEndpointLoading = useStore((s) => s.isEndpointLoading)
  const isEndpointActive = useStore((s) => s.isEndpointActive)
  const hydrated = useStore((s) => s.hydrated)
  const setUserId = useStore((s) => s.setUserId)
  const setMode = useStore((s) => s.setMode)
  const lastSessionId = useStore((s) => s.lastSessionId)
  const setLastSessionId = useStore((s) => s.setLastSessionId)
  const { initialize, clearChat, focusChatInput } = useChatActions()

  // Fetch credit balance for cost context in confirmations
  useCreditBalance({ refreshInterval: 30000, autoRefresh: true })

  const [sessionId, setSessionId] = useQueryState('session')
  const [, setAgentId] = useQueryState('agent')

  // Track the last notified session ID to avoid duplicate callbacks
  const lastNotifiedSessionId = useRef<string | null>(null)

  // Configure the store with the endpoint and set agent mode
  useEffect(() => {
    setEndpoint(agentOsUrl)
    setUserId(projectId || null) // Pass projectId as userId for the backend
    setMode('agent') // Use single agent mode
    setAgentId('video-creator') // Set the agent ID
    initialize()
  }, [agentOsUrl, setEndpoint, setUserId, setMode, setAgentId, projectId, initialize])

  // Restore session from initialSessionId or localStorage
  useEffect(() => {
    if (hydrated && isEndpointActive) {
      const effectiveSessionId = initialSessionId || lastSessionId
      if (effectiveSessionId && !sessionId) {
        setSessionId(effectiveSessionId)
      }
    }
  }, [hydrated, isEndpointActive, initialSessionId, lastSessionId, sessionId, setSessionId])

  // Sync session to localStorage
  useEffect(() => {
    if (sessionId) setLastSessionId(sessionId)
  }, [sessionId, setLastSessionId])

  // Notify parent when session changes
  useEffect(() => {
    if (sessionId !== lastNotifiedSessionId.current) {
      lastNotifiedSessionId.current = sessionId
      onSessionChange?.(sessionId)
    }
  }, [sessionId, onSessionChange])

  // Handle New Chat button click
  const handleNewChat = useCallback(() => {
    clearChat()
    setSessionId(null)
    setLastSessionId(null)
    onSessionChange?.(null)
    focusChatInput()
  }, [clearChat, setSessionId, setLastSessionId, onSessionChange, focusChatInput])

  // Show loading state until store is hydrated from localStorage
  if (!hydrated) {
    return (
      <div
        className={cn(
          'flex h-full flex-col items-center justify-center',
          className
        )}
      >
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    )
  }

  return (
    <div className={cn('flex h-full flex-col', className)}>
      {/* Header */}
      <div className="flex shrink-0 items-center justify-between gap-1 border-b border-border px-2 py-2">
        <div className="flex min-w-0 flex-1 items-center gap-1.5">
          <Bot className="h-4 w-4 shrink-0 text-primary" />
          <h2 className="truncate text-sm font-semibold text-primary">AI Assistant</h2>
          <ConnectionDot
            isActive={isEndpointActive}
            isLoading={isEndpointLoading}
          />
        </div>
        <button
          onClick={handleNewChat}
          title="Start new chat"
          className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md border border-border bg-background text-muted-foreground transition-colors hover:border-primary/30 hover:bg-background-secondary hover:text-foreground"
        >
          <Plus className="h-3.5 w-3.5" />
        </button>
      </div>

      {/* Plan Preview (shows when there's a pending/executing plan) */}
      {projectId && supabaseUrl && supabaseAnonKey && (
        <div className="shrink-0 px-2 pt-2">
          <PlanPreview
            projectId={projectId}
            supabaseUrl={supabaseUrl}
            supabaseAnonKey={supabaseAnonKey}
          />
        </div>
      )}

      {/* Task Progress (shows when there's an active plan with tasks) */}
      {projectId && supabaseUrl && supabaseAnonKey && (
        <div className="shrink-0 px-2 pt-2">
          <TaskProgress
            projectId={projectId}
            supabaseUrl={supabaseUrl}
            supabaseAnonKey={supabaseAnonKey}
            defaultCollapsed={false}
          />
        </div>
      )}

      {/* Connection Status / Chat Area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {isEndpointLoading ? (
          <ConnectionStatus status="connecting" />
        ) : !isEndpointActive ? (
          <ConnectionStatus status="error" />
        ) : (
          <ChatArea />
        )}
      </div>

      {/* Floating Progress Toast - shows active generations */}
      {projectId && supabaseUrl && supabaseAnonKey && (
        <FloatingProgressToast
          projectId={projectId}
          supabaseUrl={supabaseUrl}
          supabaseAnonKey={supabaseAnonKey}
        />
      )}
    </div>
  )
}
