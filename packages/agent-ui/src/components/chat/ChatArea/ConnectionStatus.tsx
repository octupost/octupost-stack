'use client'

import { motion } from 'framer-motion'
import { Wifi, WifiOff, RefreshCw, AlertCircle } from 'lucide-react'
import { Button } from '../../ui/button'
import useChatActions from '../../../hooks/useChatActions'
import { useStore } from '../../../store'

interface ConnectionStatusProps {
  status: 'connecting' | 'error'
}

// Troubleshooting tips component
const TroubleshootingTips = () => (
  <div className="mt-4 w-full max-w-xs text-left">
    <p className="mb-2 text-xs font-medium text-muted-foreground">
      Troubleshooting:
    </p>
    <ul className="list-inside list-disc space-y-1 text-xs text-muted-foreground">
      <li>Check if the agent server is running</li>
      <li>Verify your network connection</li>
      <li>Try refreshing the page</li>
      <li>Check firewall settings</li>
    </ul>
  </div>
)

const ConnectionStatus = ({ status }: ConnectionStatusProps) => {
  const { initialize } = useChatActions()
  const selectedEndpoint = useStore((s) => s.selectedEndpoint)

  if (status === 'connecting') {
    return (
      <div className="flex h-full items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex flex-col items-center gap-3"
        >
          <div className="relative">
            <div className="flex h-10 w-10 items-center justify-center rounded-full border-2 border-primary/30">
              <Wifi className="h-5 w-5 animate-pulse text-primary" />
            </div>
            <div className="absolute inset-0 h-10 w-10 animate-spin rounded-full border-2 border-l-transparent border-r-transparent border-t-primary border-b-transparent" />
          </div>
          <div className="text-center">
            <p className="text-sm font-medium text-primary">
              Connecting to AI Agent...
            </p>
            <p className="mt-1 font-mono text-xs text-muted-foreground">
              {selectedEndpoint}
            </p>
          </div>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="flex h-full items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex max-w-sm flex-col items-center gap-4 text-center"
      >
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-destructive/10">
          <WifiOff className="h-6 w-6 text-destructive" />
        </div>

        <div className="flex flex-col gap-1">
          <p className="text-sm font-medium text-primary">Connection Failed</p>
          <p className="text-xs text-muted-foreground">
            Unable to reach the AI agent service
          </p>
        </div>

        {/* Endpoint URL display */}
        <div className="flex items-center gap-1.5 rounded-md bg-background-secondary px-3 py-1.5 font-mono text-xs text-muted-foreground">
          <AlertCircle className="h-3 w-3" />
          {selectedEndpoint}
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={() => initialize()}
          className="gap-2"
        >
          <RefreshCw className="h-4 w-4" />
          Retry Connection
        </Button>

        <TroubleshootingTips />
      </motion.div>
    </div>
  )
}

export default ConnectionStatus
