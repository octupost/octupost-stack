'use client'

import { motion } from 'framer-motion'
import { useStore } from '../../../../store'

interface AgentThinkingLoaderProps {
  agentName?: string
}

const AgentThinkingLoader = ({ agentName }: AgentThinkingLoaderProps) => {
  const activeAgent = useStore((s) => s.activeAgent)
  const displayAgent = agentName || activeAgent

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex items-center gap-3"
    >
      {/* Animated dots */}
      <div className="flex items-center gap-1">
        <div className="size-2 animate-bounce rounded-full bg-primary/60 [animation-delay:-0.3s] [animation-duration:0.70s]" />
        <div className="size-2 animate-bounce rounded-full bg-primary/60 [animation-delay:-0.15s] [animation-duration:0.70s]" />
        <div className="size-2 animate-bounce rounded-full bg-primary/60 [animation-duration:0.70s]" />
      </div>

      {/* Text label */}
      <span className="text-sm text-muted-foreground">
        {displayAgent ? (
          <>
            <span className="font-medium text-primary">{displayAgent}</span>
            {' is thinking...'}
          </>
        ) : (
          'Thinking...'
        )}
      </span>
    </motion.div>
  )
}

export default AgentThinkingLoader
