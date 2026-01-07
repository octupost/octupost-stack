'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Loader2, ChevronDown, ChevronUp, Video, Image, Mic, Music, UserCircle, Headphones, X } from 'lucide-react'
import { cn } from '../../lib/utils'
import { useActiveGenerations, type ActiveGeneration } from '../../hooks/useActiveGenerations'

interface FloatingProgressToastProps {
  projectId: string
  supabaseUrl?: string
  supabaseAnonKey?: string
  userId?: string
  className?: string
}

// Map job types to icons
const JOB_TYPE_ICONS: Record<string, React.ElementType> = {
  'text-to-video': Video,
  'image-to-video': Video,
  'text-to-image': Image,
  'avatar': UserCircle,
  'text-to-speech': Mic,
  'text-to-audio': Headphones,
  'text-to-music': Music,
  'video-to-audio': Video,
}

function GenerationIcon({ type }: { type: string }) {
  const Icon = JOB_TYPE_ICONS[type] || Video
  return <Icon className="h-3.5 w-3.5" />
}

function ProgressBar({ value }: { value: number }) {
  return (
    <div className="h-1 w-full overflow-hidden rounded-full bg-primary/20">
      <motion.div
        className="h-full bg-primary"
        initial={{ width: 0 }}
        animate={{ width: `${Math.min(value, 100)}%` }}
        transition={{ duration: 0.3, ease: 'easeOut' }}
      />
    </div>
  )
}

function GenerationItem({ generation }: { generation: ActiveGeneration }) {
  const isQueued = generation.status === 'queued'

  return (
    <div className="py-2 first:pt-0 last:pb-0">
      <div className="flex items-center gap-2">
        <GenerationIcon type={generation.type} />
        <span className="flex-1 truncate text-xs font-medium">
          {generation.title}
        </span>
        <span className="text-xs text-muted-foreground">
          {isQueued ? 'Queued' : `${generation.progress}%`}
        </span>
      </div>
      {!isQueued && (
        <div className="mt-1.5">
          <ProgressBar value={generation.progress} />
        </div>
      )}
    </div>
  )
}

export function FloatingProgressToast({
  projectId,
  supabaseUrl,
  supabaseAnonKey,
  userId,
  className,
}: FloatingProgressToastProps) {
  const { activeGenerations, hasActive, count } = useActiveGenerations({
    projectId,
    supabaseUrl,
    supabaseAnonKey,
    userId,
  })

  const [isVisible, setIsVisible] = useState(false)
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [isDismissed, setIsDismissed] = useState(false)

  // Show/hide based on active generations
  useEffect(() => {
    if (hasActive && !isDismissed) {
      setIsVisible(true)
    } else if (!hasActive) {
      // Reset dismissed state when all jobs complete
      setIsDismissed(false)
      // Delay hide for smooth transition
      const timer = setTimeout(() => setIsVisible(false), 500)
      return () => clearTimeout(timer)
    }
  }, [hasActive, isDismissed])

  // Don't render if not visible
  if (!isVisible || !hasActive) {
    return null
  }

  const handleDismiss = () => {
    setIsDismissed(true)
    setIsVisible(false)
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 20, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 20, scale: 0.95 }}
        transition={{ duration: 0.2, ease: 'easeOut' }}
        className={cn(
          'fixed bottom-6 right-6 z-50',
          'rounded-lg border border-border bg-background shadow-lg',
          'transition-all duration-200',
          isCollapsed ? 'w-auto' : 'w-72',
          className
        )}
      >
        {/* Header */}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="flex w-full items-center justify-between px-3 py-2.5 hover:bg-muted/30"
        >
          <div className="flex items-center gap-2">
            <Loader2 className="h-4 w-4 animate-spin text-primary" />
            <span className="text-sm font-medium">
              {isCollapsed ? count : `${count} generating`}
            </span>
          </div>
          <div className="flex items-center gap-1">
            {!isCollapsed && (
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  handleDismiss()
                }}
                className="rounded p-0.5 hover:bg-muted"
                title="Dismiss"
              >
                <X className="h-3.5 w-3.5 text-muted-foreground" />
              </button>
            )}
            {isCollapsed ? (
              <ChevronUp className="h-4 w-4 text-muted-foreground" />
            ) : (
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            )}
          </div>
        </button>

        {/* Expanded content */}
        <AnimatePresence>
          {!isCollapsed && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.15 }}
              className="overflow-hidden"
            >
              <div className="max-h-40 divide-y divide-border/50 overflow-y-auto border-t border-border px-3 py-2">
                {activeGenerations.map((gen) => (
                  <GenerationItem key={gen.id} generation={gen} />
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </AnimatePresence>
  )
}

export default FloatingProgressToast
