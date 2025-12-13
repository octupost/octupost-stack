/**
 * Provider Registry
 *
 * Centralized provider configuration and query helpers.
 * Import from "@octupost/shared/registry"
 */

import providersData from "./provider.json"
import type {
  Provider,
  ProviderParameter,
  ProviderParentType,
  ProviderType,
  ProviderTier,
  ParameterEntry,
  DurationRange,
  SpeedRange,
  AcceptedValues,
  FormValues,
} from "./types"
import {
  isDefaultValuesEntry,
  isDurationAcceptedValues,
  isSpeedAcceptedValues,
  isArrayAcceptedValues,
} from "./types"

// =============================================================================
// Re-exports
// =============================================================================

export * from "./types"
export * from "./pricing"

// =============================================================================
// Provider Data
// =============================================================================

/** All providers from the registry */
export const providers: Provider[] = providersData as Provider[]

// =============================================================================
// Provider Queries
// =============================================================================

/**
 * Get a provider by its endpoint identifier.
 */
export function getProviderByEndpoint(endpoint: string): Provider | undefined {
  return providers.find((p) => p.endpoint === endpoint)
}

/**
 * Get all providers of a specific type.
 */
export function getProvidersByType(type: ProviderType): Provider[] {
  return providers.filter((p) => p.type === type && p.is_active)
}

/**
 * Get all providers of a specific parent type.
 */
export function getProvidersByParentType(parentType: ProviderParentType): Provider[] {
  return providers.filter((p) => p.parent_type === parentType && p.is_active)
}

/**
 * Get all active providers.
 */
export function getActiveProviders(): Provider[] {
  return providers.filter((p) => p.is_active)
}

/**
 * Get all providers of a specific tier.
 */
export function getProvidersByTier(tier: ProviderTier): Provider[] {
  return providers.filter((p) => p.tier === tier && p.is_active)
}

// =============================================================================
// Parameter Helpers
// =============================================================================

/**
 * Get displayable parameters (excludes default_values entries).
 */
export function getProviderParameters(provider: Provider): ProviderParameter[] {
  return provider.parameters.filter(
    (p): p is ProviderParameter => !isDefaultValuesEntry(p)
  )
}

/**
 * Get the default values object for a provider.
 */
export function getProviderDefaultValues(provider: Provider): Record<string, unknown> {
  const entry = provider.parameters.find(isDefaultValuesEntry)
  return entry?.default_values ?? {}
}

/**
 * Get a specific parameter by key.
 */
export function getParameter(provider: Provider, key: string): ProviderParameter | undefined {
  return getProviderParameters(provider).find((p) => p.key === key)
}

/**
 * Check if a provider has a specific parameter.
 */
export function hasParameter(provider: Provider, key: string): boolean {
  return getParameter(provider, key) !== undefined
}

// =============================================================================
// Parameter Value Helpers
// =============================================================================

/**
 * Get duration range from a provider.
 * Returns null if provider doesn't have a duration parameter.
 */
export function getDurationRange(provider: Provider): DurationRange | null {
  const param = getParameter(provider, "duration")
  if (!param?.accepted_values) return null

  if (isDurationAcceptedValues(param.accepted_values)) {
    return {
      min: param.accepted_values.min_duration,
      max: param.accepted_values.max_duration,
      step: param.accepted_values.steps || 1,
    }
  }

  return null
}

/**
 * Get speed range from a provider.
 * Returns null if provider doesn't have a speed parameter.
 */
export function getSpeedRange(provider: Provider): SpeedRange | null {
  const param = getParameter(provider, "speech_speed")
  if (!param?.accepted_values) return null

  if (isSpeedAcceptedValues(param.accepted_values)) {
    return {
      min: param.accepted_values.min_speed,
      max: param.accepted_values.max_speed,
      step: param.accepted_values.steps || 0.1,
    }
  }

  return null
}

/**
 * Get accepted values array for a parameter.
 * Returns empty array if not an array type.
 */
export function getAcceptedValuesArray(
  acceptedValues: AcceptedValues | undefined
): (string | number)[] {
  if (!acceptedValues) return []
  if (isArrayAcceptedValues(acceptedValues)) return acceptedValues
  return []
}

/**
 * Get resolution options from a provider.
 */
export function getResolutions(provider: Provider): string[] {
  const param = getParameter(provider, "resolution")
  if (!param?.accepted_values) return []
  return getAcceptedValuesArray(param.accepted_values) as string[]
}

/**
 * Get aspect ratio options from a provider.
 */
export function getAspectRatios(provider: Provider): string[] {
  const param = getParameter(provider, "aspect_ratio")
  if (!param?.accepted_values) return []
  return getAcceptedValuesArray(param.accepted_values) as string[]
}

/**
 * Get voice options from a provider.
 */
export function getVoices(provider: Provider): string[] {
  const param = getParameter(provider, "voice")
  if (!param?.accepted_values) return []
  return getAcceptedValuesArray(param.accepted_values) as string[]
}

/**
 * Get voice emotion options from a provider.
 */
export function getVoiceEmotions(provider: Provider): string[] {
  const param = getParameter(provider, "voice_emotion")
  if (!param?.accepted_values) return []
  return getAcceptedValuesArray(param.accepted_values) as string[]
}

/**
 * Get avatar options from a provider.
 */
export function getAvatars(provider: Provider): string[] {
  const param = getParameter(provider, "avatar")
  if (!param?.accepted_values) return []
  return getAcceptedValuesArray(param.accepted_values) as string[]
}

/**
 * Get FPS options from a provider.
 */
export function getFpsOptions(provider: Provider): number[] {
  const param = getParameter(provider, "fps")
  if (!param?.accepted_values) return []
  return getAcceptedValuesArray(param.accepted_values) as number[]
}

// =============================================================================
// Form Initialization
// =============================================================================

/**
 * Get initial form values for a provider (uses defaults from parameters).
 */
export function getInitialFormValues(provider: Provider): FormValues {
  const values: FormValues = {}
  const params = getProviderParameters(provider)

  for (const param of params) {
    if (param.default !== undefined) {
      values[param.key] = param.default
    }
  }

  return values
}

// =============================================================================
// Provider Display Helpers
// =============================================================================

/**
 * Get display name for a provider.
 */
export function getDisplayName(provider: Provider): string {
  return provider.provider
}

/**
 * Get the FPS value for a provider (null for non-video providers).
 */
export function getFps(provider: Provider): number | null {
  return provider.fps
}

/**
 * Check if provider supports audio generation.
 */
export function supportsAudio(provider: Provider): boolean {
  return hasParameter(provider, "enable_audio")
}

/**
 * Check if provider supports prompt enhancement.
 */
export function supportsPromptEnhancement(provider: Provider): boolean {
  return hasParameter(provider, "enhance_prompt")
}

/**
 * Get tier badge color class.
 */
export function getTierBadgeClass(tier: ProviderTier): string {
  switch (tier) {
    case "Elite":
      return "bg-purple-500/10 text-purple-500 border-purple-500/20"
    case "Pro":
      return "bg-blue-500/10 text-blue-500 border-blue-500/20"
    case "Plus":
      return "bg-green-500/10 text-green-500 border-green-500/20"
    case "Standard":
      return "bg-yellow-500/10 text-yellow-500 border-yellow-500/20"
    case "Basic":
      return "bg-gray-500/10 text-gray-500 border-gray-500/20"
    default:
      return "bg-gray-500/10 text-gray-500 border-gray-500/20"
  }
}

// =============================================================================
// Generation Mode Support
// =============================================================================

/** Video generation mode (maps to provider types) */
export type VideoGenerationMode = "text-to-video" | "first-frame" | "first-last-frame" | "components"

/**
 * Check if a provider supports a specific video generation mode.
 */
export function supportsVideoMode(provider: Provider, mode: VideoGenerationMode): boolean {
  const { parent_type, type } = provider

  switch (mode) {
    case "text-to-video":
      return parent_type === "text-to-video" && type === "text-to-video"
    case "first-frame":
      return parent_type === "image-to-video" && type === "image-to-video"
    case "first-last-frame":
      return parent_type === "image-to-video" && type === "first-last-frame-to-video"
    case "components":
      return parent_type === "image-to-video" && type === "reference-to-video"
    default:
      return false
  }
}

/**
 * Get providers that support a specific video generation mode.
 */
export function getProvidersForVideoMode(mode: VideoGenerationMode): Provider[] {
  return getActiveProviders().filter((p) => supportsVideoMode(p, mode))
}


