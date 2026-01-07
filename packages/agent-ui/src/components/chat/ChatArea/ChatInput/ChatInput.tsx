'use client'

import { useState, useCallback } from 'react'
import { toast } from 'sonner'
import { Square, Send, Keyboard } from 'lucide-react'
import { TextArea } from '../../../ui/textarea'
import { useStore } from '../../../../store'
import useAIChatStreamHandler from '../../../../hooks/useAIStreamHandler'
import { useQueryState } from 'nuqs'
import { CHARACTER_LIMIT, cn } from '../../../../lib/utils'
import ModelSelector from './ModelSelector'

const ChatInput = () => {
  const { chatInputRef, abortController, setAbortController } = useStore()

  const { handleStreamResponse } = useAIChatStreamHandler()
  const [selectedAgent] = useQueryState('agent')
  const [teamId] = useQueryState('team')
  const [inputMessage, setInputMessage] = useState('')
  const isStreaming = useStore((state) => state.isStreaming)

  const handleSubmit = async () => {
    if (!inputMessage.trim()) return

    const currentMessage = inputMessage
    setInputMessage('')

    try {
      await handleStreamResponse(currentMessage)
    } catch (error) {
      toast.error(
        `Error in handleSubmit: ${
          error instanceof Error ? error.message : String(error)
        }`
      )
    }
  }

  const handleStopStreaming = useCallback(() => {
    if (abortController) {
      abortController.abort()
      setAbortController(null)
    }
  }, [abortController, setAbortController])

  const isDisabled = !(selectedAgent || teamId)
  const characterCount = inputMessage.length
  const isNearLimit = characterCount > CHARACTER_LIMIT * 0.9
  const isOverLimit = characterCount > CHARACTER_LIMIT
  // Block submit if over character limit
  const canSubmit = !isDisabled && inputMessage.trim() && !isStreaming && !isOverLimit

  return (
    <div className="relative mx-auto w-full max-w-2xl font-geist">
      <div
        className={cn(
          'relative flex flex-col rounded-xl border bg-background-secondary transition-all',
          isDisabled
            ? 'border-border opacity-60'
            : 'border-border focus-within:border-primary/50 focus-within:ring-1 focus-within:ring-primary/20'
        )}
      >
        {/* Input area */}
        <div className="relative flex items-end">
          <TextArea
            placeholder={
              isDisabled
                ? 'Select an AI model to start chatting'
                : 'Ask anything...'
            }
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={(e) => {
              if (
                e.key === 'Enter' &&
                !e.nativeEvent.isComposing &&
                !e.shiftKey &&
                !isStreaming
              ) {
                e.preventDefault()
                handleSubmit()
              }
            }}
            className="flex-1 border-0 bg-transparent pr-12 text-sm text-primary focus-visible:border-transparent focus-visible:ring-0"
            disabled={isDisabled}
            ref={chatInputRef}
          />

          {/* Submit/Stop button */}
          {isStreaming ? (
            <button
              onClick={handleStopStreaming}
              className="absolute bottom-2 right-2 flex h-8 w-8 items-center justify-center rounded-lg bg-destructive text-white transition-all hover:bg-destructive/90"
              title="Stop generating"
            >
              <Square className="h-4 w-4 fill-current" />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={!canSubmit}
              className={cn(
                'absolute bottom-2 right-2 flex h-8 w-8 items-center justify-center rounded-lg transition-all',
                canSubmit
                  ? 'bg-primary text-primaryAccent hover:bg-primary/90'
                  : 'cursor-not-allowed bg-muted text-muted-foreground'
              )}
              title="Send message"
            >
              <Send className="h-4 w-4" />
            </button>
          )}
        </div>

        {/* Footer with model selector, keyboard hint, and character count */}
        <div className="flex items-center justify-between border-t border-border/30 px-2 py-1 text-xs text-muted-foreground">
          <div className="flex items-center gap-2">
            {/* Model Selector - like Cursor's model picker */}
            <ModelSelector />
            <div className="h-4 w-px bg-border/50" />
            <div className="flex items-center gap-1.5">
              <Keyboard className="h-3 w-3" />
              <span className="hidden sm:inline">Enter to send</span>
            </div>
          </div>
          <div
            className={cn(
              'transition-colors',
              isOverLimit && 'font-medium text-destructive',
              isNearLimit && !isOverLimit && 'text-yellow-500'
            )}
          >
            {characterCount.toLocaleString()} / {CHARACTER_LIMIT.toLocaleString()}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatInput
