/**
 * Provider Registry (Minimal)
 *
 * Centralized provider configuration with minimal business logic.
 * Parameter schemas are fetched dynamically from FAL's OpenAPI endpoint.
 * Import from "@octupost/shared/registry"
 */

import providersData from "./provider.json"
import type {
  Provider,
  ProviderType,
  ProviderTier,
  OutputMediaType,
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
 * Get all active providers that produce one of the specified output media types.
 */
export function getProvidersByOutputMediaType(types: OutputMediaType[]): Provider[] {
  return providers.filter((p) => types.includes(p.output_media_type) && p.is_active)
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
  const { type } = provider

  switch (mode) {
    case "text-to-video":
      return type === "text-to-video"
    case "first-frame":
      return type === "image-to-video"
    case "first-last-frame":
      return type === "first-last-frame-to-video"
    case "components":
      return type === "reference-to-video"
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
