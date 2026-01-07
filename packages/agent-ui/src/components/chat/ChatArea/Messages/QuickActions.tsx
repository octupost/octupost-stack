'use client'

import { memo, useMemo } from 'react'
import { motion } from 'framer-motion'
import Icon from '../../../ui/icon'
import useAIChatStreamHandler from '../../../../hooks/useAIStreamHandler'
import type { IconType } from '../../../ui/icon/types'
import type { ChatMessage } from '../../../../types/os'

interface QuickAction {
  id: string
  label: string
  prompt: string
  icon: IconType
}

// After agent creates/shows a plan
const PLAN_ACTIONS: QuickAction[] = [
  {
    id: 'generate_all',
    label: 'Generate All',
    prompt: 'Generate all scenes now',
    icon: 'sparkles'
  },
  {
    id: 'review_plan',
    label: 'Review Plan',
    prompt: 'Show me the plan details',
    icon: 'eye'
  },
  {
    id: 'modify_plan',
    label: 'Modify',
    prompt: 'I want to change the plan',
    icon: 'edit'
  }
]

// After scene generation completes
const SCENE_ACTIONS: QuickAction[] = [
  {
    id: 'add_voice',
    label: 'Add Voice',
    prompt: 'Add voiceover to this scene',
    icon: 'mic'
  },
  {
    id: 'add_music',
    label: 'Add Music',
    prompt: 'Add background music',
    icon: 'music'
  },
  {
    id: 'improve',
    label: 'Improve',
    prompt: 'Make this scene more dynamic',
    icon: 'sparkles'
  },
  {
    id: 'remix',
    label: 'Remix',
    prompt: 'Regenerate with a different style',
    icon: 'refresh'
  }
]

// Default/general actions
const DEFAULT_ACTIONS: QuickAction[] = [
  {
    id: 'generate_scene',
    label: 'Generate Scene',
    prompt: 'Generate the next scene',
    icon: 'video'
  },
  {
    id: 'write_script',
    label: 'Write Script',
    prompt: 'Write a video script',
    icon: 'edit'
  },
  {
    id: 'add_text',
    label: 'Add Text',
    prompt: 'Add a text overlay',
    icon: 'type'
  },
  {
    id: 'preview',
    label: 'Preview',
    prompt: 'Preview the current video',
    icon: 'play'
  }
]

type ActionContext = 'plan' | 'scene' | 'default'

function detectContext(message: ChatMessage): ActionContext {
  const content = message.content?.toLowerCase() || ''
  const toolCalls = message.tool_calls || []

  // Check tool calls first - they're most reliable
  const toolNames = toolCalls.map(tc => tc.tool_name.toLowerCase())

  // If there's a plan-related tool or message mentions plan
  if (
    toolNames.some(name => name.includes('plan') || name.includes('create_video_plan')) ||
    content.includes('plan') && (content.includes('scene') || content.includes('created'))
  ) {
    return 'plan'
  }

  // If a scene was generated
  if (
    toolNames.some(name =>
      name.includes('generate_scene') ||
      name.includes('create_scene') ||
      name.includes('text_to_video')
    ) ||
    (content.includes('scene') && (content.includes('generated') || content.includes('created') || content.includes('complete')))
  ) {
    return 'scene'
  }

  return 'default'
}

interface QuickActionsProps {
  message: ChatMessage
  isStreaming?: boolean
}

const QuickActions = memo(({ message, isStreaming = false }: QuickActionsProps) => {
  const { handleStreamResponse } = useAIChatStreamHandler()

  const context = useMemo(() => detectContext(message), [message])

  const actions = useMemo(() => {
    switch (context) {
      case 'plan':
        return PLAN_ACTIONS
      case 'scene':
        return SCENE_ACTIONS
      default:
        return DEFAULT_ACTIONS
    }
  }, [context])

  // Don't show during streaming or if message has an error
  if (isStreaming || message.streamingError) {
    return null
  }

  // Don't show if message is paused waiting for HITL
  if (message.paused && message.requirements?.length) {
    return null
  }

  const handleActionClick = (prompt: string) => {
    handleStreamResponse(prompt)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: 0.1 }}
      className="mt-3 flex flex-wrap gap-2"
    >
      {actions.map((action, index) => (
        <motion.button
          key={action.id}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.15, delay: 0.15 + index * 0.03 }}
          onClick={() => handleActionClick(action.prompt)}
          className="flex items-center gap-1.5 rounded-full border border-border bg-background px-3 py-1.5 text-xs text-muted-foreground transition-all hover:border-primary/40 hover:bg-primary/5 hover:text-primary active:scale-95"
        >
          <Icon type={action.icon} size="xxs" />
          {action.label}
        </motion.button>
      ))}
    </motion.div>
  )
})

QuickActions.displayName = 'QuickActions'

export default QuickActions
