'use client'

import React, { useMemo } from 'react'
import { Video, Mic, Music, Image, Type, Coins, Film, Clock, ListChecks, CheckCircle2, AlertTriangle } from 'lucide-react'
import { cn } from '../../../../lib/utils'
import { useStore } from '../../../../store'

interface GenerationPreviewProps {
  toolName: string
  toolArgs: Record<string, unknown>
  estimatedCredits: number
}

interface SceneBreakdown {
  name: string
  description?: string
  duration_seconds: number
  assets_needed?: string[]
  video_prompt?: string
  speech_text?: string
  credit_estimate?: number
}

interface PreviewContent {
  type: 'video' | 'speech' | 'music' | 'image' | 'text' | 'plan' | 'other'
  icon: React.ElementType
  description: string
  duration?: string
  model?: string
  color: string
  bgColor: string
  // Plan-specific
  scenes?: SceneBreakdown[]
  title?: string
}

function getPreviewContent(toolName: string, toolArgs: Record<string, unknown>): PreviewContent {
  const lowerToolName = toolName.toLowerCase()

  // Video Plan - special handling for plan approval
  if (lowerToolName.includes('video_plan') || lowerToolName.includes('create_plan')) {
    const title = String(toolArgs.title || 'Video Plan')
    const scenes = (toolArgs.scenes || []) as SceneBreakdown[]
    const totalDuration = Number(toolArgs.total_duration_seconds || 0)
    const totalCredits = Number(toolArgs.estimated_credits || 0)

    return {
      type: 'plan',
      icon: ListChecks,
      title,
      description: `${scenes.length} scenes • ${totalDuration}s total`,
      duration: `${totalDuration}s`,
      scenes,
      color: 'text-primary',
      bgColor: 'bg-primary/10'
    }
  }

  // Video generation
  if (lowerToolName.includes('video') || lowerToolName.includes('scene_video')) {
    const prompt = String(toolArgs.prompt || toolArgs.description || '')
    const duration = Number(toolArgs.duration_seconds || toolArgs.duration || 5)
    const model = String(toolArgs.model || 'Video Model')

    return {
      type: 'video',
      icon: Video,
      description: prompt.length > 100 ? prompt.slice(0, 100) + '...' : prompt || 'Video generation',
      duration: `${duration}s`,
      model: formatModelName(model),
      color: 'text-blue-500',
      bgColor: 'bg-blue-500/10'
    }
  }

  // Speech/voiceover generation
  if (lowerToolName.includes('speech') || lowerToolName.includes('voice') || lowerToolName.includes('tts')) {
    const text = String(toolArgs.text || toolArgs.script || '')
    const voice = String(toolArgs.voice_id || toolArgs.voice || '')
    const estimatedDuration = Math.ceil(text.length / 15) // ~15 chars per second

    return {
      type: 'speech',
      icon: Mic,
      description: text.length > 100 ? text.slice(0, 100) + '...' : text || 'Speech generation',
      duration: `~${estimatedDuration}s`,
      model: voice ? `Voice: ${formatModelName(voice)}` : undefined,
      color: 'text-purple-500',
      bgColor: 'bg-purple-500/10'
    }
  }

  // Music generation
  if (lowerToolName.includes('music') || lowerToolName.includes('audio') || lowerToolName.includes('soundtrack')) {
    const prompt = String(toolArgs.prompt || toolArgs.description || '')
    const duration = Number(toolArgs.duration_seconds || toolArgs.duration || 30)

    return {
      type: 'music',
      icon: Music,
      description: prompt.length > 100 ? prompt.slice(0, 100) + '...' : prompt || 'Music generation',
      duration: `${duration}s`,
      color: 'text-green-500',
      bgColor: 'bg-green-500/10'
    }
  }

  // Image generation
  if (lowerToolName.includes('image') || lowerToolName.includes('photo') || lowerToolName.includes('picture')) {
    const prompt = String(toolArgs.prompt || toolArgs.description || '')
    const model = String(toolArgs.model || 'Image Model')

    return {
      type: 'image',
      icon: Image,
      description: prompt.length > 100 ? prompt.slice(0, 100) + '...' : prompt || 'Image generation',
      model: formatModelName(model),
      color: 'text-pink-500',
      bgColor: 'bg-pink-500/10'
    }
  }

  // Text overlay
  if (lowerToolName.includes('text') || lowerToolName.includes('overlay') || lowerToolName.includes('caption')) {
    const text = String(toolArgs.text || toolArgs.content || '')

    return {
      type: 'text',
      icon: Type,
      description: text.length > 100 ? text.slice(0, 100) + '...' : text || 'Text overlay',
      color: 'text-orange-500',
      bgColor: 'bg-orange-500/10'
    }
  }

  // Default/other
  return {
    type: 'other',
    icon: Video,
    description: formatToolName(toolName),
    color: 'text-gray-500',
    bgColor: 'bg-gray-500/10'
  }
}

function formatToolName(name: string): string {
  return name
    .replace(/_/g, ' ')
    .replace(/([A-Z])/g, ' $1')
    .replace(/-/g, ' ')
    .trim()
    .split(' ')
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')
}

function formatModelName(name: string): string {
  // Clean up common model name patterns
  return name
    .replace(/_/g, ' ')
    .replace(/-/g, ' ')
    .replace(/v(\d)/gi, 'v$1')
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

// Asset type icons for plan scenes
const assetIcons: Record<string, React.ElementType> = {
  video: Video,
  speech: Mic,
  music: Music,
  text: Type,
}

export function GenerationPreview({ toolName, toolArgs, estimatedCredits }: GenerationPreviewProps) {
  const preview = useMemo(() => getPreviewContent(toolName, toolArgs), [toolName, toolArgs])
  const Icon = preview.icon
  const creditBalance = useStore((s) => s.creditBalance)

  // Special rendering for video plans
  if (preview.type === 'plan' && preview.scenes) {
    const scenes = preview.scenes
    const totalDuration = scenes.reduce((acc, s) => acc + (s.duration_seconds || 0), 0)
    const hasEnoughCredits = creditBalance === null || creditBalance >= estimatedCredits
    const remainingAfter = creditBalance !== null ? creditBalance - estimatedCredits : null

    return (
      <div className="mt-3 rounded-lg border border-primary/30 bg-primary/5 overflow-hidden">
        {/* Plan header */}
        <div className="flex items-center gap-2 px-3 py-2 border-b border-border/40">
          <ListChecks className="h-4 w-4 text-primary" />
          <span className="text-sm font-semibold text-foreground">{preview.title}</span>
          <span className="text-xs text-muted-foreground ml-auto">
            {scenes.length} scenes • {totalDuration}s
          </span>
        </div>

        {/* Visual timeline bar */}
        <div className="px-3 py-2">
          <div className="flex gap-0.5 h-2 rounded-full overflow-hidden bg-muted">
            {scenes.map((scene, i) => {
              const widthPercent = totalDuration > 0
                ? (scene.duration_seconds / totalDuration) * 100
                : 100 / scenes.length
              return (
                <div
                  key={i}
                  className="h-full bg-primary/40 first:rounded-l-full last:rounded-r-full"
                  style={{ width: `${Math.max(widthPercent, 5)}%` }}
                  title={`${scene.name} (${scene.duration_seconds}s)`}
                />
              )
            })}
          </div>
        </div>

        {/* Scene list */}
        <div className="px-3 pb-2 space-y-1.5 max-h-48 overflow-y-auto">
          {scenes.map((scene, i) => (
            <div
              key={i}
              className="flex items-center gap-2 p-2 rounded-md bg-background/50 border border-border/30"
            >
              <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary text-xs font-medium">
                {i + 1}
              </span>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-foreground truncate">{scene.name}</p>
                {scene.description && (
                  <p className="text-xs text-muted-foreground truncate">{scene.description}</p>
                )}
              </div>
              <div className="flex items-center gap-1 shrink-0">
                {/* Asset type icons */}
                {scene.assets_needed?.map((asset) => {
                  const AssetIcon = assetIcons[asset] || Video
                  return (
                    <div
                      key={asset}
                      className="w-4 h-4 rounded bg-muted/50 flex items-center justify-center"
                      title={asset}
                    >
                      <AssetIcon className="h-2.5 w-2.5 text-muted-foreground" />
                    </div>
                  )
                })}
                <span className="text-xs text-muted-foreground ml-1">
                  {scene.duration_seconds}s
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Credit display with balance context */}
        {estimatedCredits > 0 && (
          <div className={cn(
            "flex items-center justify-between border-t px-3 py-2",
            hasEnoughCredits ? "border-border/40 bg-green-500/5" : "border-red-500/30 bg-red-500/5"
          )}>
            <div className="flex items-center gap-1.5">
              <Coins className={cn("h-4 w-4", hasEnoughCredits ? "text-amber-600" : "text-red-500")} />
              <span className={cn("text-sm font-semibold", hasEnoughCredits ? "text-amber-600" : "text-red-500")}>
                {estimatedCredits.toLocaleString()} credits
              </span>
            </div>
            {creditBalance !== null && (
              <div className="flex items-center gap-1.5 text-xs">
                {hasEnoughCredits ? (
                  <>
                    <CheckCircle2 className="h-3 w-3 text-green-500" />
                    <span className="text-muted-foreground">
                      You have <span className="font-medium text-foreground">{creditBalance.toLocaleString()}</span>
                      {remainingAfter !== null && (
                        <> → <span className="font-medium text-foreground">{remainingAfter.toLocaleString()}</span> after</>
                      )}
                    </span>
                  </>
                ) : (
                  <>
                    <AlertTriangle className="h-3 w-3 text-red-500" />
                    <span className="text-red-500">
                      Need {(estimatedCredits - creditBalance).toLocaleString()} more (have {creditBalance.toLocaleString()})
                    </span>
                  </>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    )
  }

  // Default rendering for other generation types
  return (
    <div className="mt-3 rounded-lg border border-border/60 bg-muted/20 overflow-hidden">
      {/* Preview content */}
      <div className="flex gap-3 p-3">
        {/* Thumbnail placeholder */}
        <div className={cn(
          "flex h-16 w-24 shrink-0 items-center justify-center rounded-md",
          preview.bgColor
        )}>
          <Icon className={cn("h-8 w-8", preview.color)} />
        </div>

        {/* Details */}
        <div className="flex min-w-0 flex-1 flex-col justify-center gap-1">
          <p className="text-sm font-medium leading-tight line-clamp-2">
            {preview.description}
          </p>
          <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
            {preview.duration && (
              <span className="inline-flex items-center gap-1">
                Duration: {preview.duration}
              </span>
            )}
            {preview.model && (
              <span className="inline-flex items-center gap-1">
                {preview.model}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Credit display - prominent */}
      {estimatedCredits > 0 && (
        <div className="flex items-center justify-between border-t border-border/40 bg-amber-500/5 px-3 py-2">
          <span className="text-xs text-muted-foreground">Estimated Cost</span>
          <div className="flex items-center gap-1.5 font-semibold text-amber-600">
            <Coins className="h-4 w-4" />
            <span>{estimatedCredits} credits</span>
          </div>
        </div>
      )}
    </div>
  )
}

export default GenerationPreview
