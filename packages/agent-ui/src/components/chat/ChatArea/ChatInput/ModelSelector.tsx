'use client'

import { useEffect, useState } from 'react'
import { Sparkles, Zap, Crown, Gem, Info, ChevronDown } from 'lucide-react'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectSeparator,
  SelectTrigger,
  SelectValue,
} from '../../../ui/select'
import { useStore } from '../../../../store'
import { constructEndpointUrl } from '../../../../lib/constructEndpointUrl'
import { cn } from '../../../../lib/utils'

interface ModelPricing {
  input: number
  output: number
}

interface AgentModel {
  id: string
  name: string
  description: string
  tier: 'free' | 'standard' | 'pro' | 'max'
  supports_tools: boolean
  pricing: ModelPricing
  note?: string
}

interface ModelsResponse {
  models: AgentModel[]
  default: string
}

const tierConfig = {
  free: {
    icon: Zap,
    color: 'text-emerald-500',
    bgColor: 'bg-emerald-500/10',
    borderColor: 'border-emerald-500/20',
    label: 'Free',
    gradient: 'from-emerald-500/20 to-emerald-500/5',
  },
  standard: {
    icon: Sparkles,
    color: 'text-sky-500',
    bgColor: 'bg-sky-500/10',
    borderColor: 'border-sky-500/20',
    label: 'Standard',
    gradient: 'from-sky-500/20 to-sky-500/5',
  },
  pro: {
    icon: Crown,
    color: 'text-violet-500',
    bgColor: 'bg-violet-500/10',
    borderColor: 'border-violet-500/20',
    label: 'Pro',
    gradient: 'from-violet-500/20 to-violet-500/5',
  },
  max: {
    icon: Gem,
    color: 'text-amber-500',
    bgColor: 'bg-amber-500/10',
    borderColor: 'border-amber-500/20',
    label: 'Max',
    gradient: 'from-amber-500/20 to-amber-500/5',
  },
}

/**
 * Format pricing for display
 */
const formatPricing = (pricing: ModelPricing): string => {
  if (pricing.input === 0 && pricing.output === 0) {
    return 'Free'
  }
  if (pricing.input < 1) {
    return `$${pricing.input.toFixed(2)}/M`
  }
  return `$${pricing.input}/M`
}

const ModelSelector = () => {
  const selectedEndpoint = useStore((state) => state.selectedEndpoint)
  const selectedModel = useStore((state) => state.selectedModel)
  const setSelectedModel = useStore((state) => state.setSelectedModel)
  const isStreaming = useStore((state) => state.isStreaming)

  const [models, setModels] = useState<AgentModel[]>([])
  const [defaultModel, setDefaultModel] = useState<string>('')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [hoveredModel, setHoveredModel] = useState<string | null>(null)

  // Fetch available models on mount
  useEffect(() => {
    const fetchModels = async () => {
      try {
        setIsLoading(true)
        setError(null)

        const endpointUrl = constructEndpointUrl(selectedEndpoint)
        const response = await fetch(`${endpointUrl}/api/agents/video-creator/models`)

        if (!response.ok) {
          throw new Error('Failed to fetch models')
        }

        const data: ModelsResponse = await response.json()
        setModels(data.models)
        setDefaultModel(data.default)

        // Set default model if none selected
        if (!selectedModel && data.default) {
          setSelectedModel(data.default)
        }
      } catch (err) {
        console.error('Failed to fetch models:', err)
        setError('Failed to load models')
        // Set fallback models if API fails
        setModels([
          { id: 'xiaomi/mimo-v2-flash:free', name: 'MiMo V2 Flash', description: 'Sonnet-level, free', tier: 'free', supports_tools: true, pricing: { input: 0, output: 0 } },
          { id: 'anthropic/claude-3.5-haiku', name: 'Claude 3.5 Haiku', description: 'Fast, great for coding', tier: 'standard', supports_tools: true, pricing: { input: 0.80, output: 4.00 } },
        ])
        if (!selectedModel) {
          setSelectedModel('xiaomi/mimo-v2-flash:free')
        }
      } finally {
        setIsLoading(false)
      }
    }

    fetchModels()
  }, [selectedEndpoint, selectedModel, setSelectedModel])

  // Group models by tier
  const groupedModels = models.reduce((acc, model) => {
    if (!acc[model.tier]) {
      acc[model.tier] = []
    }
    acc[model.tier].push(model)
    return acc
  }, {} as Record<string, AgentModel[]>)

  const currentModel = models.find((m) => m.id === selectedModel)
  const currentTier = currentModel?.tier || 'free'
  const TierIcon = tierConfig[currentTier].icon

  if (isLoading) {
    return (
      <div className="flex h-7 w-36 animate-pulse items-center gap-2 rounded-lg bg-muted/30 px-2">
        <div className="h-3 w-3 rounded-full bg-muted/50" />
        <div className="h-3 w-20 rounded bg-muted/50" />
      </div>
    )
  }

  const pricingLabel = currentModel ? formatPricing(currentModel.pricing) : ''

  return (
    <Select
      value={selectedModel}
      onValueChange={setSelectedModel}
      disabled={isStreaming}
    >
      <SelectTrigger
        className={cn(
          'group h-7 w-auto min-w-[160px] gap-1.5 rounded-lg border px-2.5 py-1 text-xs font-medium transition-all duration-200',
          'border-border/50 bg-background/50 backdrop-blur-sm',
          'hover:border-border hover:bg-muted/50 hover:shadow-sm',
          'focus:ring-1 focus:ring-primary/20',
          isStreaming && 'cursor-not-allowed opacity-50'
        )}
      >
        <div className={cn(
          'flex h-4 w-4 items-center justify-center rounded-md transition-colors',
          tierConfig[currentTier].bgColor
        )}>
          <TierIcon className={cn('h-2.5 w-2.5', tierConfig[currentTier].color)} />
        </div>
        <SelectValue placeholder="Select model">
          <span className="flex items-center gap-2">
            <span className="font-medium">{currentModel?.name || 'Select model'}</span>
            {currentModel && (
              <span
                className={cn(
                  'rounded-md px-1.5 py-0.5 text-[10px] font-semibold transition-colors',
                  currentModel.pricing.input === 0
                    ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400'
                    : 'bg-muted text-muted-foreground'
                )}
              >
                {pricingLabel}
              </span>
            )}
          </span>
        </SelectValue>
        <ChevronDown className="ml-auto h-3 w-3 opacity-50 transition-transform group-data-[state=open]:rotate-180" />
      </SelectTrigger>

      <SelectContent
        className="min-w-[320px] overflow-hidden rounded-xl border border-border/50 bg-background/95 p-0 shadow-xl backdrop-blur-xl"
      >
        {(['free', 'standard', 'pro', 'max'] as const).map((tier, tierIndex) => {
          const tierModels = groupedModels[tier]
          if (!tierModels?.length) return null

          const config = tierConfig[tier]
          const TierLabelIcon = config.icon

          return (
            <div key={tier}>
              {tierIndex > 0 && <SelectSeparator className="my-0" />}
              <SelectGroup>
                {/* Tier Header */}
                <SelectLabel
                  className={cn(
                    'flex items-center gap-2 px-3 py-2 text-xs font-semibold uppercase tracking-wider',
                    'bg-gradient-to-r',
                    config.gradient
                  )}
                >
                  <div className={cn(
                    'flex h-5 w-5 items-center justify-center rounded-md',
                    config.bgColor
                  )}>
                    <TierLabelIcon className={cn('h-3 w-3', config.color)} />
                  </div>
                  <span className={config.color}>{config.label}</span>
                  <span className="ml-auto text-[10px] font-normal normal-case text-muted-foreground">
                    {tierModels.length} model{tierModels.length > 1 ? 's' : ''}
                  </span>
                </SelectLabel>

                {/* Model Items */}
                {tierModels.map((model) => (
                  <SelectItem
                    key={model.id}
                    value={model.id}
                    className={cn(
                      'group/item relative mx-1 my-0.5 cursor-pointer rounded-lg px-3 py-2.5 transition-all duration-150',
                      'hover:bg-muted/80',
                      'focus:bg-muted',
                      'data-[state=checked]:bg-primary/10'
                    )}
                    onMouseEnter={() => setHoveredModel(model.id)}
                    onMouseLeave={() => setHoveredModel(null)}
                  >
                    <div className="flex w-full items-start justify-between gap-3">
                      <div className="flex flex-col gap-0.5">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-foreground">
                            {model.name}
                          </span>
                          {model.note && (
                            <div className="group/tooltip relative">
                              <Info className="h-3 w-3 text-muted-foreground/50 transition-colors hover:text-muted-foreground" />
                              {/* Tooltip */}
                              <div className={cn(
                                'absolute bottom-full left-1/2 z-50 mb-2 -translate-x-1/2 whitespace-nowrap rounded-lg px-2.5 py-1.5',
                                'bg-foreground text-background text-xs font-medium shadow-lg',
                                'pointer-events-none opacity-0 transition-opacity',
                                'group-hover/tooltip:opacity-100'
                              )}>
                                {model.note}
                                <div className="absolute left-1/2 top-full -translate-x-1/2 border-4 border-transparent border-t-foreground" />
                              </div>
                            </div>
                          )}
                        </div>
                        <span className="text-xs text-muted-foreground">
                          {model.description}
                        </span>
                      </div>

                      {/* Pricing Badge */}
                      <span
                        className={cn(
                          'shrink-0 rounded-md px-2 py-1 text-xs font-bold tabular-nums transition-all',
                          model.pricing.input === 0
                            ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400'
                            : 'bg-muted/80 text-muted-foreground',
                          hoveredModel === model.id && model.pricing.input === 0 && 'bg-emerald-500/25'
                        )}
                      >
                        {formatPricing(model.pricing)}
                      </span>
                    </div>

                    {/* Hover indicator line */}
                    <div
                      className={cn(
                        'absolute inset-y-1 left-0 w-0.5 rounded-full transition-all duration-200',
                        config.bgColor,
                        'opacity-0 group-hover/item:opacity-100',
                        'group-data-[state=checked]/item:opacity-100',
                        config.color.replace('text-', 'bg-')
                      )}
                    />
                  </SelectItem>
                ))}
              </SelectGroup>
            </div>
          )
        })}

        {error && (
          <div className="border-t border-destructive/20 bg-destructive/5 px-3 py-2 text-xs text-destructive">
            {error}
          </div>
        )}

        {/* Footer */}
        <div className="border-t border-border/50 bg-muted/30 px-3 py-2">
          <p className="text-[10px] text-muted-foreground">
            Pricing shown is per million input tokens via OpenRouter
          </p>
        </div>
      </SelectContent>
    </Select>
  )
}

export default ModelSelector
