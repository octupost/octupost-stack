'use client'

import { motion } from 'framer-motion'
import Icon from '../../../ui/icon'
import useAIChatStreamHandler from '../../../../hooks/useAIStreamHandler'
import type { IconType } from '../../../ui/icon/types'

interface SuggestionChip {
  label: string
  prompt: string
  icon: IconType
  description?: string
}

const SUGGESTION_CHIPS: SuggestionChip[] = [
  {
    label: 'Product video',
    prompt: 'I want to create a product video to showcase and sell my product',
    icon: 'video',
    description: 'Showcase & sell'
  },
  {
    label: 'Avatar video',
    prompt: 'I want to create an avatar talking head video where an AI presenter explains my content',
    icon: 'agent',
    description: 'AI presenter'
  },
  {
    label: 'Social media ad',
    prompt: 'I want to create a short, engaging ad for TikTok or Instagram Reels',
    icon: 'sparkles',
    description: 'TikTok & Reels'
  },
  {
    label: 'Explainer video',
    prompt: 'I want to create an explainer video that teaches my audience about a topic or how my product works',
    icon: 'subtitles',
    description: 'Educate & inform'
  }
]

const ChatBlankState = () => {
  const { handleStreamResponse } = useAIChatStreamHandler()

  const handleSuggestionClick = (prompt: string) => {
    handleStreamResponse(prompt)
  }

  return (
    <section
      className="flex flex-1 flex-col items-center justify-center gap-6 overflow-hidden px-4"
      aria-label="Welcome"
    >
      {/* Welcome message */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="flex flex-col items-center gap-3"
      >
        <div className="rounded-full bg-primary/10 p-3">
          <Icon type="agent" size="md" className="text-primary" />
        </div>
        <div className="w-full max-w-sm px-2 text-center">
          <h2 className="text-lg font-semibold text-primary">
            What video do you want to create?
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Pick a format or describe your idea
          </p>
        </div>
      </motion.div>

      {/* Suggestion cards */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.15 }}
        className="grid w-full max-w-sm grid-cols-2 gap-2 px-2"
      >
        {SUGGESTION_CHIPS.map((chip, index) => (
          <motion.button
            key={chip.label}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.2, delay: 0.2 + index * 0.05 }}
            onClick={() => handleSuggestionClick(chip.prompt)}
            className="flex flex-col items-start gap-1.5 rounded-lg border border-border bg-background p-3 text-left transition-all hover:border-primary/40 hover:bg-primary/5 group"
          >
            <div className="flex items-center gap-2">
              <div className="rounded-md bg-primary/10 p-1.5 group-hover:bg-primary/20 transition-colors">
                <Icon type={chip.icon} size="xs" className="text-primary" />
              </div>
              <span className="text-sm font-medium text-foreground group-hover:text-primary transition-colors">
                {chip.label}
              </span>
            </div>
            {chip.description && (
              <span className="text-xs text-muted-foreground pl-8">
                {chip.description}
              </span>
            )}
          </motion.button>
        ))}
      </motion.div>
    </section>
  )
}

export default ChatBlankState
