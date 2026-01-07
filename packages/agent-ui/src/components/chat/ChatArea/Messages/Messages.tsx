import type { ChatMessage, ConfirmationRequirement, QuestionResponse } from '../../../../types/os'

import { AgentMessage, UserMessage } from './MessageItem'
import Tooltip from '../../../ui/tooltip'
import { memo, useCallback } from 'react'
import {
  ToolCallProps,
  ReasoningStepProps,
  ReasoningProps,
  ReferenceData,
  Reference
} from '../../../../types/os'
import React, { type FC } from 'react'

import Icon from '../../../ui/icon'
import ChatBlankState from './ChatBlankState'
import { ToolConfirmation } from './ToolConfirmation'
import QuickActions from './QuickActions'
import AgentQuestion from './AgentQuestion'
import { useStore } from '../../../../store'

interface MessageListProps {
  messages: ChatMessage[]
}

interface MessageWrapperProps {
  message: ChatMessage
  isLastMessage: boolean
  index?: number
}

interface ReferenceProps {
  references: ReferenceData[]
}

interface ReferenceItemProps {
  reference: Reference
}

const ReferenceItem: FC<ReferenceItemProps> = ({ reference }) => (
  <div className="relative flex h-[63px] w-[190px] cursor-default flex-col justify-between overflow-hidden rounded-md bg-background-secondary p-3 transition-colors hover:bg-background-secondary/80">
    <p className="text-sm font-medium text-primary">{reference.name}</p>
    <p className="truncate text-xs text-primary/40">{reference.content}</p>
  </div>
)

const References: FC<ReferenceProps> = ({ references }) => (
  <div className="flex flex-col gap-4">
    {references.map((referenceData, index) => (
      <div
        key={`${referenceData.query}-${index}`}
        className="flex flex-col gap-3"
      >
        <div className="flex flex-wrap gap-3">
          {referenceData.references.map((reference, refIndex) => (
            <ReferenceItem
              key={`${reference.name}-${reference.meta_data.chunk}-${refIndex}`}
              reference={reference}
            />
          ))}
        </div>
      </div>
    ))}
  </div>
)

const AgentMessageWrapper = ({ message, isLastMessage, index = 0 }: MessageWrapperProps) => {
  const selectedEndpoint = useStore((s) => s.selectedEndpoint)
  const setMessages = useStore((s) => s.setMessages)
  const setPausedRun = useStore((s) => s.setPausedRun)
  const isStreaming = useStore((s) => s.isStreaming)

  // Handle HITL confirmation
  const handleConfirm = useCallback(async (
    runId: string,
    confirmations: { requirement_id: string; confirmed: boolean; note?: string }[]
  ) => {
    try {
      // Build the API URL - use the agent routes endpoint
      const baseUrl = selectedEndpoint.replace('/v1', '')
      const response = await fetch(`${baseUrl}/api/agents/video-creator/runs/${runId}/continue`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirmations }),
      })

      if (!response.ok) {
        throw new Error('Failed to continue run')
      }

      // Clear the paused state immediately
      setPausedRun(null)

      // Update the message to remove paused state
      setMessages((prevMessages) =>
        prevMessages.map((msg) =>
          msg.run_id === runId
            ? { ...msg, paused: false, requirements: undefined }
            : msg
        )
      )

      // Consume the SSE stream and update messages with results
      if (!response.body) return

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })

        // Parse SSE events from buffer (format: "data: {...}\n\n")
        const events = buffer.split('\n\n')
        buffer = events.pop() || '' // Keep incomplete event in buffer

        for (const eventStr of events) {
          if (!eventStr.startsWith('data: ')) continue
          const jsonStr = eventStr.slice(6) // Remove "data: " prefix

          try {
            const chunk = JSON.parse(jsonStr)

            if (chunk.type === 'content' && chunk.content) {
              // Append content to the last agent message
              setMessages((prevMessages) => {
                const newMessages = [...prevMessages]
                const lastMessage = newMessages[newMessages.length - 1]
                if (lastMessage && lastMessage.role === 'agent') {
                  lastMessage.content += chunk.content
                }
                return newMessages
              })
            } else if (chunk.type === 'tool_call' && chunk.tool_call) {
              // Add tool call to the last agent message
              setMessages((prevMessages) => {
                const newMessages = [...prevMessages]
                const lastMessage = newMessages[newMessages.length - 1]
                if (lastMessage && lastMessage.role === 'agent') {
                  lastMessage.tool_calls = [
                    ...(lastMessage.tool_calls || []),
                    {
                      tool_call_id: chunk.tool_call.tool_call_id,
                      tool_name: chunk.tool_call.tool_name,
                      tool_args: chunk.tool_call.tool_args,
                      role: 'tool',
                      content: null,
                      tool_call_error: false,
                      metrics: { time: 0 },
                      created_at: Date.now(),
                    }
                  ]
                }
                return newMessages
              })
            } else if (chunk.type === 'question' && chunk.question) {
              // Structured question from ask_user_question tool
              setMessages((prevMessages) => {
                const newMessages = [...prevMessages]
                const lastMessage = newMessages[newMessages.length - 1]
                if (lastMessage && lastMessage.role === 'agent') {
                  lastMessage.run_id = chunk.run_id
                  lastMessage.question = {
                    question_id: chunk.question.question_id,
                    question: chunk.question.question,
                    type: chunk.question.type || 'single_choice',
                    options: chunk.question.options || [],
                    allow_other: chunk.question.allow_other ?? true,
                    other_placeholder: chunk.question.other_placeholder,
                    answered: false,
                  }
                }
                return newMessages
              })
            } else if (chunk.type === 'paused' && chunk.requirements) {
              // New pause - update message with new requirements
              setMessages((prevMessages) => {
                const newMessages = [...prevMessages]
                const lastMessage = newMessages[newMessages.length - 1]
                if (lastMessage && lastMessage.role === 'agent') {
                  lastMessage.paused = true
                  lastMessage.run_id = chunk.run_id
                  lastMessage.requirements = chunk.requirements
                }
                return newMessages
              })
              setPausedRun({
                run_id: chunk.run_id,
                requirements: chunk.requirements,
                created_at: new Date().toISOString()
              })
            } else if (chunk.type === 'blocked') {
              // Insufficient credits - show error in message
              setMessages((prevMessages) => {
                const newMessages = [...prevMessages]
                const lastMessage = newMessages[newMessages.length - 1]
                if (lastMessage && lastMessage.role === 'agent') {
                  lastMessage.content += `\n\n⚠️ ${chunk.message || 'Insufficient credits to continue.'}`
                }
                return newMessages
              })
            } else if (chunk.type === 'error') {
              // Error occurred
              console.error('Continue run error:', chunk.error)
              setMessages((prevMessages) => {
                const newMessages = [...prevMessages]
                const lastMessage = newMessages[newMessages.length - 1]
                if (lastMessage && lastMessage.role === 'agent') {
                  lastMessage.content += `\n\n❌ Error: ${chunk.error}`
                }
                return newMessages
              })
            }
            // 'done' type means completion - no special handling needed
          } catch {
            // Skip malformed JSON
          }
        }
      }
    } catch (error) {
      console.error('Failed to confirm:', error)
    }
  }, [selectedEndpoint, setMessages, setPausedRun])

  // Handle structured question response
  const handleQuestionResponse = useCallback(async (
    runId: string,
    response: QuestionResponse
  ) => {
    try {
      const baseUrl = selectedEndpoint.replace('/v1', '')

      // Mark question as answered immediately
      setMessages((prevMessages) =>
        prevMessages.map((msg) =>
          msg.run_id === runId && msg.question
            ? { ...msg, question: { ...msg.question, answered: true } }
            : msg
        )
      )

      // Add a new agent message for the continuing response
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          role: 'agent' as const,
          content: '',
          tool_calls: [],
          created_at: Math.floor(Date.now() / 1000),
        }
      ])

      const result = await fetch(`${baseUrl}/api/agents/video-creator/runs/${runId}/continue`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question_response: response }),
      })

      if (!result.ok) {
        throw new Error('Failed to submit question response')
      }

      // Consume the SSE stream and update messages with results
      if (!result.body) return

      const reader = result.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })

        // Parse SSE events from buffer (format: "data: {...}\n\n")
        const events = buffer.split('\n\n')
        buffer = events.pop() || '' // Keep incomplete event in buffer

        for (const eventStr of events) {
          if (!eventStr.startsWith('data: ')) continue
          const jsonStr = eventStr.slice(6) // Remove "data: " prefix

          try {
            const chunk = JSON.parse(jsonStr)

            if (chunk.type === 'content' && chunk.content) {
              // Append content to the last agent message
              setMessages((prevMessages) => {
                const newMessages = [...prevMessages]
                const lastMessage = newMessages[newMessages.length - 1]
                if (lastMessage && lastMessage.role === 'agent') {
                  lastMessage.content += chunk.content
                }
                return newMessages
              })
            } else if (chunk.type === 'tool_call' && chunk.tool_call) {
              // Add tool call to the last agent message
              setMessages((prevMessages) => {
                const newMessages = [...prevMessages]
                const lastMessage = newMessages[newMessages.length - 1]
                if (lastMessage && lastMessage.role === 'agent') {
                  lastMessage.tool_calls = [
                    ...(lastMessage.tool_calls || []),
                    {
                      tool_call_id: chunk.tool_call.tool_call_id,
                      tool_name: chunk.tool_call.tool_name,
                      tool_args: chunk.tool_call.tool_args,
                      role: 'tool',
                      content: null,
                      tool_call_error: false,
                      metrics: { time: 0 },
                      created_at: Date.now(),
                    }
                  ]
                }
                return newMessages
              })
            } else if (chunk.type === 'question' && chunk.question) {
              // Another structured question
              setMessages((prevMessages) => {
                const newMessages = [...prevMessages]
                const lastMessage = newMessages[newMessages.length - 1]
                if (lastMessage && lastMessage.role === 'agent') {
                  lastMessage.run_id = chunk.run_id
                  lastMessage.question = {
                    question_id: chunk.question.question_id,
                    question: chunk.question.question,
                    type: chunk.question.type || 'single_choice',
                    options: chunk.question.options || [],
                    allow_other: chunk.question.allow_other ?? true,
                    other_placeholder: chunk.question.other_placeholder,
                    answered: false,
                  }
                }
                return newMessages
              })
            } else if (chunk.type === 'paused' && chunk.requirements) {
              // HITL confirmation needed
              setMessages((prevMessages) => {
                const newMessages = [...prevMessages]
                const lastMessage = newMessages[newMessages.length - 1]
                if (lastMessage && lastMessage.role === 'agent') {
                  lastMessage.paused = true
                  lastMessage.run_id = chunk.run_id
                  lastMessage.requirements = chunk.requirements
                }
                return newMessages
              })
              setPausedRun({
                run_id: chunk.run_id,
                requirements: chunk.requirements,
                created_at: new Date().toISOString()
              })
            }
          } catch {
            // Skip malformed JSON
          }
        }
      }
    } catch (error) {
      console.error('Failed to submit question response:', error)
    }
  }, [selectedEndpoint, setMessages, setPausedRun])

  return (
    <div className="flex flex-col gap-y-9">
      {message.extra_data?.reasoning_steps &&
        message.extra_data.reasoning_steps.length > 0 && (
          <div className="flex items-start gap-4">
            <Tooltip
              delayDuration={0}
              content={<p className="text-accent">Reasoning</p>}
              side="top"
            >
              <Icon type="reasoning" size="sm" />
            </Tooltip>
            <div className="flex flex-col gap-3">
              <p className="text-xs uppercase">Reasoning</p>
              <Reasonings reasoning={message.extra_data.reasoning_steps} />
            </div>
          </div>
        )}
      {message.extra_data?.references &&
        message.extra_data.references.length > 0 && (
          <div className="flex items-start gap-4">
            <Tooltip
              delayDuration={0}
              content={<p className="text-accent">References</p>}
              side="top"
            >
              <Icon type="references" size="sm" />
            </Tooltip>
            <div className="flex flex-col gap-3">
              <References references={message.extra_data.references} />
            </div>
          </div>
        )}
      {message.tool_calls && message.tool_calls.length > 0 && (
        <div className="flex items-start gap-3">
          <Tooltip
            delayDuration={0}
            content={<p className="text-accent">Tool Calls</p>}
            side="top"
          >
            <Icon
              type="hammer"
              className="rounded-lg bg-background-secondary p-1"
              size="sm"
              color="secondary"
            />
          </Tooltip>

          <div className="flex flex-wrap gap-2">
            {message.tool_calls.map((toolCall, toolIndex) => (
              <ToolComponent
                key={
                  toolCall.tool_call_id ||
                  `${toolCall.tool_name}-${toolCall.created_at}-${toolIndex}`
                }
                tools={toolCall}
              />
            ))}
          </div>
        </div>
      )}
      <AgentMessage message={message} index={index} />

      {/* HITL Confirmation UI */}
      {message.paused && message.requirements && message.requirements.length > 0 && message.run_id && (
        <ToolConfirmation
          requirements={message.requirements}
          runId={message.run_id}
          onConfirm={handleConfirm}
        />
      )}

      {/* Structured Question UI */}
      {message.question && message.run_id && (
        <AgentQuestion
          question={message.question}
          runId={message.run_id}
          onRespond={handleQuestionResponse}
        />
      )}

      {/* Quick Actions - show after last agent message when not streaming, not when question is pending */}
      {isLastMessage && !isStreaming && message.content && !(message.question && !message.question.answered) && (
        <QuickActions message={message} isStreaming={isStreaming} />
      )}
    </div>
  )
}
const Reasoning: FC<ReasoningStepProps> = ({ index, stepTitle }) => (
  <div className="flex items-center gap-2 text-secondary">
    <div className="flex h-[20px] items-center rounded-md bg-background-secondary p-2">
      <p className="text-xs">STEP {index + 1}</p>
    </div>
    <p className="text-xs">{stepTitle}</p>
  </div>
)
const Reasonings: FC<ReasoningProps> = ({ reasoning }) => (
  <div className="flex flex-col items-start justify-center gap-2">
    {reasoning.map((title, index) => (
      <Reasoning
        key={`${title.title}-${title.action}-${index}`}
        stepTitle={title.title}
        index={index}
      />
    ))}
  </div>
)

const ToolComponent = memo(({ tools }: ToolCallProps) => (
  <div className="cursor-default rounded-full bg-accent px-2 py-1.5 text-xs">
    <p className="font-dmmono uppercase text-primary/80">{tools.tool_name}</p>
  </div>
))
ToolComponent.displayName = 'ToolComponent'
const Messages = ({ messages }: MessageListProps) => {
  if (messages.length === 0) {
    return <ChatBlankState />
  }

  return (
    <>
      {messages.map((message, index) => {
        const key = `${message.role}-${message.created_at}-${index}`
        const isLastMessage = index === messages.length - 1

        if (message.role === 'agent') {
          return (
            <AgentMessageWrapper
              key={key}
              message={message}
              isLastMessage={isLastMessage}
              index={index}
            />
          )
        }
        return <UserMessage key={key} message={message} index={index} />
      })}
    </>
  )
}

export default Messages
