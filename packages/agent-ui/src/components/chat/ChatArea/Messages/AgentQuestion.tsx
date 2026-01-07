'use client'

import React, { useState, useCallback, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Check, Loader2, ChevronRight, MessageSquare } from 'lucide-react'
import { cn } from '../../../../lib/utils'
import type { AgentQuestion as AgentQuestionType, QuestionResponse, QuestionOption } from '../../../../types/os'

interface AgentQuestionProps {
  question: AgentQuestionType
  runId: string
  onRespond: (runId: string, response: QuestionResponse) => Promise<void>
}

interface OptionItemProps {
  option: QuestionOption
  isSelected: boolean
  onSelect: () => void
  type: 'single_choice' | 'multi_choice'
  disabled?: boolean
}

const OptionItem: React.FC<OptionItemProps> = ({
  option,
  isSelected,
  onSelect,
  type,
  disabled = false,
}) => {
  return (
    <button
      type="button"
      onClick={onSelect}
      disabled={disabled}
      className={cn(
        'w-full text-left rounded-lg border p-3 transition-all',
        'focus:outline-none focus:ring-2 focus:ring-primary/50',
        isSelected
          ? 'border-primary bg-primary/10'
          : 'border-border bg-background hover:border-primary/40 hover:bg-primary/5',
        disabled && 'opacity-60 cursor-not-allowed hover:border-border hover:bg-background'
      )}
    >
      <div className="flex items-start gap-3">
        {/* Radio/Checkbox indicator */}
        <div
          className={cn(
            'mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full border-2 transition-colors',
            type === 'multi_choice' && 'rounded',
            isSelected
              ? 'border-primary bg-primary'
              : 'border-muted-foreground/40'
          )}
        >
          {isSelected && (
            <Check className="h-2.5 w-2.5 text-primary-foreground" />
          )}
        </div>

        {/* Label and description */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className={cn(
              'text-sm font-medium',
              isSelected ? 'text-primary' : 'text-foreground'
            )}>
              {option.label}
            </span>
            {option.recommended && (
              <span className="text-[10px] font-medium bg-primary/20 text-primary px-1.5 py-0.5 rounded-full">
                Recommended
              </span>
            )}
          </div>
          {option.description && (
            <p className="mt-0.5 text-xs text-muted-foreground">
              {option.description}
            </p>
          )}
        </div>
      </div>
    </button>
  )
}

export function AgentQuestion({ question, runId, onRespond }: AgentQuestionProps) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [isOtherSelected, setIsOtherSelected] = useState(false)
  const [otherText, setOtherText] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isAnswered, setIsAnswered] = useState(question.answered ?? false)
  const [submitError, setSubmitError] = useState<string | null>(null)

  const isSingleChoice = question.type === 'single_choice'

  const handleOptionSelect = useCallback((optionId: string) => {
    if (isAnswered || isSubmitting) return

    setSelectedIds((prev) => {
      const next = new Set(prev)

      if (isSingleChoice) {
        // Single choice: replace selection
        next.clear()
        next.add(optionId)
        setIsOtherSelected(false)
      } else {
        // Multi choice: toggle selection
        if (next.has(optionId)) {
          next.delete(optionId)
        } else {
          next.add(optionId)
        }
      }

      return next
    })
  }, [isSingleChoice, isAnswered, isSubmitting])

  const handleOtherSelect = useCallback(() => {
    if (isAnswered || isSubmitting) return

    if (isSingleChoice) {
      setSelectedIds(new Set())
      setIsOtherSelected(true)
    } else {
      setIsOtherSelected((prev) => !prev)
    }
  }, [isSingleChoice, isAnswered, isSubmitting])

  const canSubmit = useMemo(() => {
    if (isAnswered || isSubmitting) return false

    // Has selected options
    if (selectedIds.size > 0) return true

    // Has "other" selected with text
    if (isOtherSelected && otherText.trim().length > 0) return true

    return false
  }, [selectedIds.size, isOtherSelected, otherText, isAnswered, isSubmitting])

  const handleSubmit = useCallback(async () => {
    if (!canSubmit) return

    setIsSubmitting(true)
    setSubmitError(null)
    try {
      const response: QuestionResponse = {
        question_id: question.question_id,
        selected_ids: Array.from(selectedIds),
        other_text: isOtherSelected && otherText.trim() ? otherText.trim() : undefined,
      }

      await onRespond(runId, response)
      setIsAnswered(true)
    } catch (error) {
      console.error('Failed to submit question response:', error)
      const errorMessage = error instanceof Error ? error.message : 'Failed to submit response. Please try again.'
      setSubmitError(errorMessage)
    } finally {
      setIsSubmitting(false)
    }
  }, [canSubmit, question.question_id, selectedIds, isOtherSelected, otherText, runId, onRespond])

  // Get selected labels for answered state display
  const selectedLabels = useMemo(() => {
    const labels: string[] = []

    for (const id of selectedIds) {
      const option = question.options.find((o) => o.id === id)
      if (option) labels.push(option.label)
    }

    if (isOtherSelected && otherText.trim()) {
      labels.push(`Other: ${otherText.trim()}`)
    }

    return labels
  }, [selectedIds, question.options, isOtherSelected, otherText])

  // If already answered, show compact view
  if (isAnswered) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="rounded-lg border border-green-500/30 bg-green-500/5 p-3"
      >
        <div className="flex items-start gap-2">
          <Check className="mt-0.5 h-4 w-4 text-green-500" />
          <div className="flex-1 min-w-0">
            <p className="text-sm text-muted-foreground">{question.question}</p>
            <div className="mt-1.5 flex flex-wrap gap-1.5">
              {selectedLabels.map((label, i) => (
                <span
                  key={i}
                  className="inline-flex items-center rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary"
                >
                  {label}
                </span>
              ))}
            </div>
          </div>
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="rounded-lg border border-primary/30 bg-primary/5 p-4"
    >
      {/* Question header */}
      <div className="flex items-start gap-2 mb-4">
        <MessageSquare className="mt-0.5 h-4 w-4 text-primary" />
        <p className="text-sm font-medium text-foreground">{question.question}</p>
      </div>

      {/* Options list */}
      <div className="space-y-2">
        {question.options.map((option) => (
          <OptionItem
            key={option.id}
            option={option}
            isSelected={selectedIds.has(option.id)}
            onSelect={() => handleOptionSelect(option.id)}
            type={question.type}
            disabled={isSubmitting}
          />
        ))}

        {/* Other option */}
        {question.allow_other && (
          <div
            className={cn(
              'rounded-lg border p-3 transition-all',
              isOtherSelected
                ? 'border-primary bg-primary/10'
                : 'border-border bg-background'
            )}
          >
            <button
              type="button"
              onClick={handleOtherSelect}
              disabled={isSubmitting}
              className="flex w-full items-start gap-3 text-left focus:outline-none"
            >
              {/* Radio/Checkbox indicator */}
              <div
                className={cn(
                  'mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full border-2 transition-colors',
                  question.type === 'multi_choice' && 'rounded',
                  isOtherSelected
                    ? 'border-primary bg-primary'
                    : 'border-muted-foreground/40'
                )}
              >
                {isOtherSelected && (
                  <Check className="h-2.5 w-2.5 text-primary-foreground" />
                )}
              </div>
              <span className={cn(
                'text-sm font-medium',
                isOtherSelected ? 'text-primary' : 'text-foreground'
              )}>
                Other
              </span>
            </button>

            {/* Other text input */}
            <AnimatePresence>
              {isOtherSelected && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.15 }}
                  className="overflow-hidden"
                >
                  <input
                    type="text"
                    value={otherText}
                    onChange={(e) => setOtherText(e.target.value)}
                    placeholder={question.other_placeholder || 'Type your preference...'}
                    disabled={isSubmitting}
                    className={cn(
                      'mt-2 ml-7 w-[calc(100%-1.75rem)] rounded-md border border-border bg-background px-3 py-2 text-sm',
                      'placeholder:text-muted-foreground',
                      'focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary',
                      'disabled:opacity-60'
                    )}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && canSubmit) {
                        e.preventDefault()
                        handleSubmit()
                      }
                    }}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}
      </div>

      {/* Error message */}
      {submitError && (
        <div className="mt-3 rounded-md bg-red-500/10 border border-red-500/30 px-3 py-2">
          <p className="text-sm text-red-500">{submitError}</p>
        </div>
      )}

      {/* Submit button */}
      <button
        type="button"
        onClick={handleSubmit}
        disabled={!canSubmit}
        className={cn(
          'mt-4 w-full flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-colors',
          'focus:outline-none focus:ring-2 focus:ring-primary/50',
          canSubmit
            ? 'bg-primary text-primary-foreground hover:bg-primary/90'
            : 'bg-muted text-muted-foreground cursor-not-allowed'
        )}
      >
        {isSubmitting ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Submitting...</span>
          </>
        ) : submitError ? (
          <>
            <span>Retry</span>
            <ChevronRight className="h-4 w-4" />
          </>
        ) : (
          <>
            <span>{question.type === 'multi_choice' ? 'Apply' : 'Continue'}</span>
            <ChevronRight className="h-4 w-4" />
          </>
        )}
      </button>
    </motion.div>
  )
}

export default AgentQuestion
