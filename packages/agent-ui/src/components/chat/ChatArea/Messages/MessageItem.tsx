'use client'

import { useState, memo } from 'react'
import { motion } from 'framer-motion'
import { Copy, Check } from 'lucide-react'
import Icon from '../../../ui/icon'
import MarkdownRenderer from '../../../ui/typography/MarkdownRenderer'
import { useStore } from '../../../../store'
import type { ChatMessage } from '../../../../types/os'
import Videos from './Multimedia/Videos'
import Images from './Multimedia/Images'
import Audios from './Multimedia/Audios'
import AgentThinkingLoader from './AgentThinkingLoader'
import { formatTimestamp, formatFullDate } from '../../../../lib/utils'

interface MessageProps {
  message: ChatMessage
  index?: number
}

// Copy button component with visual feedback
const CopyButton = ({ content }: { content: string }) => {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  return (
    <button
      onClick={handleCopy}
      className="rounded p-1 opacity-0 transition-all hover:bg-background-secondary group-hover:opacity-100"
      title={copied ? 'Copied!' : 'Copy message'}
    >
      {copied ? (
        <Check className="h-3.5 w-3.5 text-green-500" />
      ) : (
        <Copy className="h-3.5 w-3.5 text-muted-foreground" />
      )}
    </button>
  )
}

// Timestamp component with hover tooltip
const MessageTimestamp = ({ timestamp }: { timestamp: number }) => {
  if (!timestamp) return null

  return (
    <span
      className="cursor-default text-xs text-muted-foreground/60 opacity-0 transition-opacity group-hover:opacity-100"
      title={formatFullDate(timestamp)}
    >
      {formatTimestamp(timestamp)}
    </span>
  )
}

const AgentMessage = memo(({ message, index = 0 }: MessageProps) => {
  const { streamingErrorMessage } = useStore()

  let messageContent
  if (message.streamingError) {
    messageContent = (
      <p className="text-destructive">
        Oops! Something went wrong while streaming.{' '}
        {streamingErrorMessage || 'Please try refreshing the page or try again later.'}
      </p>
    )
  } else if (message.content) {
    messageContent = (
      <div className="flex w-full flex-col gap-4">
        <MarkdownRenderer>{message.content}</MarkdownRenderer>
        {message.videos && message.videos.length > 0 && <Videos videos={message.videos} />}
        {message.images && message.images.length > 0 && <Images images={message.images} />}
        {message.audio && message.audio.length > 0 && <Audios audio={message.audio} />}
      </div>
    )
  } else if (message.response_audio?.transcript) {
    messageContent = (
      <div className="flex w-full flex-col gap-4">
        <MarkdownRenderer>{message.response_audio.transcript}</MarkdownRenderer>
        {message.response_audio.content && <Audios audio={[message.response_audio]} />}
      </div>
    )
  } else {
    messageContent = (
      <div className="mt-1">
        <AgentThinkingLoader />
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.25, delay: Math.min(index * 0.03, 0.15) }}
      className="group flex flex-row items-start gap-3 font-geist"
    >
      {/* Agent avatar */}
      <div className="mt-1 flex-shrink-0">
        <div className="rounded-full bg-primary/10 p-1.5">
          <Icon type="agent" size="xs" className="text-primary" />
        </div>
      </div>

      {/* Message content */}
      <div className="min-w-0 flex-1">
        <div className="rounded-2xl rounded-tl-md bg-background-secondary/50 px-4 py-3">
          {messageContent}
        </div>

        {/* Footer with timestamp and copy button */}
        <div className="mt-1 flex items-center gap-2 px-1">
          <MessageTimestamp timestamp={message.created_at} />
          {message.content && <CopyButton content={message.content} />}
        </div>
      </div>
    </motion.div>
  )
})

const UserMessage = memo(({ message, index = 0 }: MessageProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, x: 10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.25, delay: Math.min(index * 0.03, 0.15) }}
      className="group flex flex-row-reverse items-start gap-3 pt-2 font-geist max-md:break-words"
    >
      {/* User avatar */}
      <div className="mt-1 flex-shrink-0">
        <div className="rounded-full bg-primary/10 p-1.5">
          <Icon type="user" size="xs" className="text-primary" />
        </div>
      </div>

      {/* Message content */}
      <div className="flex min-w-0 max-w-[85%] flex-col items-end">
        <div className="rounded-2xl rounded-tr-md bg-primary px-4 py-3 text-primaryAccent">
          <p className="text-sm">{message.content}</p>
        </div>

        {/* Footer with copy button and timestamp */}
        <div className="mt-1 flex items-center gap-2 px-1">
          {message.content && <CopyButton content={message.content} />}
          <MessageTimestamp timestamp={message.created_at} />
        </div>
      </div>
    </motion.div>
  )
})

AgentMessage.displayName = 'AgentMessage'
UserMessage.displayName = 'UserMessage'
export { AgentMessage, UserMessage }
