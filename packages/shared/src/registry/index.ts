/**
 * AI Model Registry
 * 
 * Centralized configuration for all AI models across the Octupost platform.
 * This module provides query functions to access model and provider information.
 * 
 * @example
 * ```typescript
 * import { getModel, getModelsByType, getModelOptionsForType } from "@octupost/shared/registry"
 * 
 * // Get a specific model
 * const model = getModel("fal-ai/flux/schnell")
 * 
 * // Get all image models for a dropdown
 * const imageModels = getModelOptionsForType("text-to-image")
 * ```
 */

import modelsData from "./models.json"
import providersData from "./providers.json"
import type {
  Model,
  Provider,
  GenerationType,
  ModelRegistry,
  ProviderRegistry,
  ModelOption,
  ValidationResult,
  VideoGenerationMode,
  GenerationModeDefinition,
  LegacyVideoModel,
  LegacyImageModel,
  LegacyTTSModel,
  LegacyAudioModel,
  LegacySoundtrackModel,
  DurationRange,
} from "./types"

// Re-export types
export * from "./types"

// Type assertions for JSON imports
const models = modelsData as unknown as ModelRegistry
const providers = providersData as ProviderRegistry

// =============================================================================
// Model Queries
// =============================================================================

/**
 * Get a model by its ID
 */
export function getModel(modelId: string): Model | undefined {
  return models.models[modelId]
}

/**
 * Get all models (including disabled ones)
 */
export function getAllModels(): Record<string, Model> {
  return models.models
}

/**
 * Get only enabled models
 */
export function getEnabledModels(): Record<string, Model> {
  return Object.fromEntries(
    Object.entries(models.models).filter(([, model]) => model.enabled)
  )
}

/**
 * Get enabled models filtered by generation type
 */
export function getModelsByType(type: GenerationType): Record<string, Model> {
  return Object.fromEntries(
    Object.entries(models.models).filter(
      ([, model]) => model.type === type && model.enabled
    )
  )
}

/**
 * Get enabled models filtered by provider
 */
export function getModelsByProvider(providerId: string): Record<string, Model> {
  return Object.fromEntries(
    Object.entries(models.models).filter(
      ([, model]) => model.provider === providerId && model.enabled
    )
  )
}

/**
 * Get model IDs for a specific generation type
 */
export function getModelIds(type: GenerationType): string[] {
  return Object.keys(getModelsByType(type))
}

// =============================================================================
// Provider Queries
// =============================================================================

/**
 * Get a provider by its ID
 */
export function getProvider(providerId: string): Provider | undefined {
  return providers.providers[providerId]
}

/**
 * Get all providers
 */
export function getAllProviders(): Record<string, Provider> {
  return providers.providers
}

/**
 * Get the provider for a specific model
 */
export function getProviderForModel(modelId: string): Provider | undefined {
  const model = getModel(modelId)
  if (!model) return undefined
  return getProvider(model.provider)
}

// =============================================================================
// Generation Mode Queries
// =============================================================================

/**
 * Get all video generation modes
 */
export function getGenerationModes(): GenerationModeDefinition[] {
  return Object.values(models.generationModes)
}

/**
 * Get a specific generation mode by ID
 */
export function getGenerationMode(modeId: VideoGenerationMode): GenerationModeDefinition | undefined {
  return models.generationModes[modeId]
}

// =============================================================================
// Validation
// =============================================================================

/**
 * Check if a model ID is valid and enabled
 */
export function isValidModel(modelId: string): boolean {
  const model = getModel(modelId)
  return model !== undefined && model.enabled
}

/**
 * Validate parameters against a model's schema
 */
export function validateModelParameters(
  modelId: string,
  params: Record<string, unknown>
): ValidationResult {
  const model = getModel(modelId)
  if (!model) {
    return { valid: false, errors: [`Unknown model: ${modelId}`] }
  }

  const errors: string[] = []

  // Check required parameters
  for (const required of model.parameters.required) {
    if (!(required in params) || params[required] === undefined || params[required] === null) {
      errors.push(`Missing required parameter: ${required}`)
    }
  }

  // Validate optional parameters
  for (const [key, value] of Object.entries(params)) {
    if (model.parameters.required.includes(key)) continue
    
    const def = model.parameters.optional[key]
    if (!def) continue // Unknown parameter, allow it to pass through

    // Type checking
    if (def.type === "integer" || def.type === "number") {
      if (typeof value !== "number") {
        errors.push(`${key} must be a number`)
        continue
      }
      if (def.min !== undefined && value < def.min) {
        errors.push(`${key} must be >= ${def.min}`)
      }
      if (def.max !== undefined && value > def.max) {
        errors.push(`${key} must be <= ${def.max}`)
      }
    }

    if (def.type === "string") {
      if (typeof value !== "string") {
        errors.push(`${key} must be a string`)
        continue
      }
      if (def.maxLength !== undefined && value.length > def.maxLength) {
        errors.push(`${key} must be <= ${def.maxLength} characters`)
      }
      if (def.enum !== undefined && !def.enum.includes(value)) {
        errors.push(`${key} must be one of: ${def.enum.join(", ")}`)
      }
    }

    if (def.type === "boolean" && typeof value !== "boolean") {
      errors.push(`${key} must be a boolean`)
    }
  }

  return { valid: errors.length === 0, errors }
}

// =============================================================================
// UI Helpers
// =============================================================================

/**
 * Get model options formatted for UI dropdowns
 */
export function getModelOptionsForType(type: GenerationType): ModelOption[] {
  const typeModels = getModelsByType(type)

  return Object.entries(typeModels).map(([id, model]) => ({
    id,
    name: model.name,
    provider: model.provider,
    providerName: getProvider(model.provider)?.name || model.provider,
    type: model.type,
    pricing: model.pricing,
    capabilities: model.capabilities,
  }))
}

/**
 * Calculate estimated cost for a generation request
 */
export function calculateCost(modelId: string, quantity: number = 1): number {
  const model = getModel(modelId)
  if (!model) return 0

  return model.pricing.pricePerUnit * quantity
}

/**
 * Format price for display
 */
export function formatPrice(price: number): string {
  if (price < 0.01) {
    return `$${price.toFixed(5)}`
  }
  return `$${price.toFixed(2)}`
}

// =============================================================================
// Legacy Format Converters (for backward compatibility)
// =============================================================================

/**
 * Convert registry models to legacy VideoModel format
 * @deprecated Use getModelOptionsForType("text-to-video") instead
 */
export function getLegacyVideoModels(): LegacyVideoModel[] {
  const videoModels = getModelsByType("text-to-video")
  const i2vModels = getModelsByType("image-to-video")
  const allModels = { ...videoModels, ...i2vModels }

  return Object.entries(allModels).map(([id, model]) => ({
    id,
    name: model.name,
    provider: getProvider(model.provider)?.name || model.provider,
    resolutions: model.capabilities.resolutions || [],
    aspectRatios: model.capabilities.aspectRatios || [],
    durations: model.capabilities.duration || { min: 4, max: 8 },
    pricePerSecond: model.pricing.pricePerUnit,
    supportedModes: model.capabilities.supportedModes || ["text-to-video"],
  }))
}

/**
 * Convert registry models to legacy ImageModel format
 * @deprecated Use getModelOptionsForType("text-to-image") instead
 */
export function getLegacyImageModels(): LegacyImageModel[] {
  const imageModels = getModelsByType("text-to-image")

  return Object.entries(imageModels).map(([id, model]) => ({
    id,
    name: model.name,
    provider: getProvider(model.provider)?.name || model.provider,
    resolutions: model.capabilities.resolutions || [],
    aspectRatios: model.capabilities.aspectRatios || [],
    pricePerImage: model.pricing.pricePerUnit,
  }))
}

/**
 * Convert registry models to legacy TTSModel format
 * @deprecated Use getModelOptionsForType("text-to-speech") instead
 */
export function getLegacyTTSModels(): LegacyTTSModel[] {
  const ttsModels = getModelsByType("text-to-speech")

  return Object.entries(ttsModels).map(([id, model]) => ({
    id,
    name: model.name,
    provider: getProvider(model.provider)?.name || model.provider,
    voices: model.capabilities.voices || [],
    pricePerCharacter: model.pricing.pricePerUnit,
  }))
}

/**
 * Convert registry models to legacy AudioModel format
 * @deprecated Use getModelOptionsForType("text-to-audio") instead
 */
export function getLegacyAudioModels(): LegacyAudioModel[] {
  const audioModels = getModelsByType("text-to-audio")

  return Object.entries(audioModels).map(([id, model]) => ({
    id,
    name: model.name,
    provider: getProvider(model.provider)?.name || model.provider,
    genres: model.capabilities.genres || [],
    durations: model.capabilities.duration || { min: 30, max: 120 },
    pricePerGeneration: model.pricing.pricePerUnit,
  }))
}

/**
 * Convert registry models to legacy SoundtrackModel format
 * @deprecated Use getModelOptionsForType("text-to-soundtrack") instead
 */
export function getLegacySoundtrackModels(): LegacySoundtrackModel[] {
  const soundtrackModels = getModelsByType("text-to-soundtrack")

  return Object.entries(soundtrackModels).map(([id, model]) => ({
    id,
    name: model.name,
    provider: getProvider(model.provider)?.name || model.provider,
    categories: model.capabilities.categories || [],
    durations: model.capabilities.duration || { min: 5, max: 60 },
    pricePerGeneration: model.pricing.pricePerUnit,
  }))
}

/**
 * Get voice display names for TTS models
 */
export function getVoiceDisplayNames(): Record<string, string> {
  const ttsModels = getModelsByType("text-to-speech")
  const voiceLabels: Record<string, string> = {}

  for (const model of Object.values(ttsModels)) {
    if (model.capabilities.voiceLabels) {
      Object.assign(voiceLabels, model.capabilities.voiceLabels)
    }
  }

  return voiceLabels
}

/**
 * Get video generation modes in legacy format
 */
export function getLegacyVideoGenerationModes(): { id: VideoGenerationMode; label: string; description: string }[] {
  return getGenerationModes()
}

