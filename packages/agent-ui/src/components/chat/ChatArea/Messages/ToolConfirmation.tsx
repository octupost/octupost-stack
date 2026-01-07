import React, { useState, useCallback } from 'react'
import type { ConfirmationRequirement } from '../../../../types/os'
import { Check, X, Loader2, AlertCircle, Wallet, AlertTriangle } from 'lucide-react'
import { cn } from '../../../../lib/utils'
import { GenerationPreview } from './GenerationPreview'
import { useCreditBalance } from '../../../../hooks/useCreditBalance'

interface ToolConfirmationProps {
  requirements: ConfirmationRequirement[]
  runId: string
  onConfirm: (runId: string, confirmations: ConfirmationDecision[]) => Promise<void>
}

interface ConfirmationDecision {
  requirement_id: string
  confirmed: boolean
  note?: string
}

// Format tool name for display
function formatToolName(name: string): string {
  return name
    .replace(/_/g, ' ')
    .replace(/([A-Z])/g, ' $1')
    .trim()
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')
}

// Format tool args for display
function formatToolArgs(args: Record<string, unknown>): React.ReactNode {
  const entries = Object.entries(args).filter(([key]) =>
    !['model', 'credits', 'user_id', 'project_id'].includes(key)
  )

  if (entries.length === 0) return null

  return (
    <div className="mt-2 space-y-1 text-xs text-muted-foreground">
      {entries.map(([key, value]) => (
        <div key={key} className="flex gap-2">
          <span className="font-medium text-foreground/70">{formatToolName(key)}:</span>
          <span className="truncate max-w-[200px]">
            {typeof value === 'string'
              ? value.length > 50 ? value.slice(0, 50) + '...' : value
              : JSON.stringify(value)}
          </span>
        </div>
      ))}
    </div>
  )
}

// Estimate credits based on tool and args
function estimateCredits(tool_name: string, tool_args: Record<string, unknown>): number {
  if (tool_name === 'generate_scene_video') {
    const duration = Number(tool_args.duration_seconds) || 5
    // Rough estimate: 10 credits per second of video
    return Math.ceil(duration * 10)
  }

  if (tool_name === 'generate_scene_speech') {
    const text = String(tool_args.text || '')
    // Rough estimate: 1 credit per 100 characters
    return Math.max(1, Math.ceil(text.length / 100))
  }

  return 0
}

function ConfirmationCard({
  requirement,
  onApprove,
  onReject,
  isProcessing,
  hasEnoughCredits = true,
}: {
  requirement: ConfirmationRequirement
  onApprove: () => void
  onReject: () => void
  isProcessing: boolean
  hasEnoughCredits?: boolean
}) {
  const credits = requirement.estimated_credits || estimateCredits(requirement.tool_name, requirement.tool_args)
  const isPlan = requirement.tool_name.toLowerCase().includes('video_plan') ||
                 requirement.tool_name.toLowerCase().includes('create_plan')

  // Disable approve button if insufficient credits
  const canApprove = hasEnoughCredits && !isProcessing

  return (
    <div className={cn(
      "rounded-lg border p-3",
      isPlan
        ? "border-primary/30 bg-primary/5"
        : "border-amber-500/30 bg-amber-500/5"
    )}>
      {/* Header */}
      <div className="flex items-center gap-2">
        <AlertCircle className={cn("h-4 w-4", isPlan ? "text-primary" : "text-amber-500")} />
        <span className="font-medium text-sm">
          {isPlan ? "Approve Video Plan" : "Confirmation Required"}
        </span>
        {!isPlan && (
          <div className="ml-auto inline-block rounded-full bg-primary/10 px-2.5 py-1 text-xs font-medium text-primary">
            {formatToolName(requirement.tool_name)}
          </div>
        )}
      </div>

      {/* Visual Preview */}
      <GenerationPreview
        toolName={requirement.tool_name}
        toolArgs={requirement.tool_args}
        estimatedCredits={credits}
      />

      {/* Actions */}
      <div className="mt-4 flex gap-2">
        <button
          onClick={onApprove}
          disabled={!canApprove}
          title={!hasEnoughCredits ? "Insufficient credits" : undefined}
          className={cn(
            "flex flex-1 items-center justify-center gap-1.5 rounded-md px-4 py-2 text-sm font-medium transition-colors",
            isPlan
              ? "bg-primary text-primary-foreground hover:bg-primary/90"
              : "bg-green-600 text-white hover:bg-green-700",
            !canApprove && "opacity-50 cursor-not-allowed",
            !hasEnoughCredits && "!bg-red-500/20 !text-red-500"
          )}
        >
          {isProcessing ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Processing...</span>
            </>
          ) : !hasEnoughCredits ? (
            <>
              <AlertTriangle className="h-4 w-4" />
              <span>Insufficient Credits</span>
            </>
          ) : (
            <>
              <Check className="h-4 w-4" />
              <span>{isPlan ? "Approve & Generate All" : "Generate"}</span>
            </>
          )}
        </button>
        <button
          onClick={onReject}
          disabled={isProcessing}
          className={cn(
            "flex items-center justify-center gap-1.5 rounded-md px-4 py-2 text-sm font-medium transition-colors",
            "bg-muted text-muted-foreground hover:bg-muted/80 border border-border",
            "disabled:opacity-50 disabled:cursor-not-allowed"
          )}
        >
          <X className="h-4 w-4" />
          <span>{isPlan ? "Revise" : "Cancel"}</span>
        </button>
      </div>
    </div>
  )
}

export function ToolConfirmation({
  requirements,
  runId,
  onConfirm,
}: ToolConfirmationProps) {
  const [isProcessing, setIsProcessing] = useState(false)
  const [decisions, setDecisions] = useState<Map<string, boolean>>(new Map())
  const { balance } = useCreditBalance({ refreshInterval: 10000 })

  const handleDecision = useCallback(async (requirementId: string, confirmed: boolean) => {
    // Update local state
    const newDecisions = new Map(decisions)
    newDecisions.set(requirementId, confirmed)
    setDecisions(newDecisions)

    // Check if all requirements have decisions
    const allDecided = requirements.every((req) => newDecisions.has(req.id))

    if (allDecided) {
      setIsProcessing(true)
      try {
        const confirmations: ConfirmationDecision[] = requirements.map((req) => ({
          requirement_id: req.id,
          confirmed: newDecisions.get(req.id) ?? false,
        }))
        await onConfirm(runId, confirmations)
      } catch (error) {
        console.error('Failed to confirm:', error)
      } finally {
        setIsProcessing(false)
      }
    }
  }, [decisions, requirements, runId, onConfirm])

  // Calculate total credits
  const totalCredits = requirements.reduce((sum, req) => {
    return sum + (req.estimated_credits || estimateCredits(req.tool_name, req.tool_args))
  }, 0)

  // Check if user has enough credits
  const hasEnoughCredits = balance === null || balance >= totalCredits
  const remainingAfter = balance !== null ? balance - totalCredits : null

  return (
    <div className="space-y-3">
      {/* Credit balance bar */}
      {balance !== null && (
        <div className={cn(
          "flex items-center justify-between rounded-lg border px-3 py-2",
          hasEnoughCredits
            ? "border-border bg-muted/30"
            : "border-red-500/30 bg-red-500/5"
        )}>
          <div className="flex items-center gap-2">
            <Wallet className={cn(
              "h-4 w-4",
              hasEnoughCredits ? "text-muted-foreground" : "text-red-500"
            )} />
            <span className="text-sm text-muted-foreground">Your balance:</span>
            <span className={cn(
              "text-sm font-semibold",
              hasEnoughCredits ? "text-foreground" : "text-red-500"
            )}>
              {balance.toLocaleString()} credits
            </span>
          </div>
          {totalCredits > 0 && (
            <div className="flex items-center gap-2 text-xs">
              {hasEnoughCredits ? (
                <span className="text-muted-foreground">
                  After: <span className="font-medium text-foreground">{remainingAfter?.toLocaleString()}</span>
                </span>
              ) : (
                <span className="flex items-center gap-1 text-red-500">
                  <AlertTriangle className="h-3 w-3" />
                  Need {(totalCredits - balance).toLocaleString()} more
                </span>
              )}
            </div>
          )}
        </div>
      )}

      {/* Summary header for multiple requirements */}
      {requirements.length > 1 && totalCredits > 0 && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span>{requirements.length} actions pending approval</span>
          <span className="text-amber-600">
            (~{totalCredits} total credits)
          </span>
        </div>
      )}

      {/* Confirmation cards */}
      {requirements.map((requirement) => (
        <ConfirmationCard
          key={requirement.id}
          requirement={requirement}
          onApprove={() => handleDecision(requirement.id, true)}
          onReject={() => handleDecision(requirement.id, false)}
          isProcessing={isProcessing || decisions.has(requirement.id)}
          hasEnoughCredits={hasEnoughCredits}
        />
      ))}
    </div>
  )
}

export default ToolConfirmation
