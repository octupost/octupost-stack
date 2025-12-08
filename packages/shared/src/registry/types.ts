/**
 * Type definitions for the AI Model Registry
 * 
 * This module defines all TypeScript interfaces for the centralized
 * model registry that both frontend and backend consume.
 */

// =============================================================================
// Generation Types
// =============================================================================

export type GenerationType =
  | "text-to-image"
  | "text-to-video"
  | "image-to-video"
  | "text-to-speech"
  | "text-to-audio"
  | "text-to-soundtrack"
  | "text-generation"
  | "video-to-audio"

export type VideoGenerationMode =
  | "text-to-video"
  | "first-frame"
  | "first-last-frame"
  | "components"

// =============================================================================
// Provider Types
// =============================================================================

export type ProviderType = "sdk" | "rest" | "websocket"
export type AuthMethod = "api-key" | "oauth" | "bearer"

export interface Provider {
  /** Display name of the provider */
  name: string
  /** Type of API integration */
  type: ProviderType
  /** NPM package name for SDK-based providers */
  sdkPackage: string | null
  /** Authentication method */
  authMethod: AuthMethod
  /** Environment variable name for API key */
  authEnvVar: string
  /** Base URL for REST APIs (null for SDK-based) */
  baseUrl: string | null
  /** List of generation types this provider supports */
  capabilities: GenerationType[]
  /** Mapping of standard response fields to provider-specific fields */
  responseMapping: Record<string, string>
}

export interface ProviderRegistry {
  providers: Record<string, Provider>
}

// =============================================================================
// Model Types
// =============================================================================

export type PricingUnit = "image" | "second" | "character" | "request" | "generation"

export interface ModelPricing {
  /** Unit of billing */
  unit: PricingUnit
  /** Price per unit in USD */
  pricePerUnit: number
}

export interface DurationRange {
  min: number
  max: number
  /** Step size for duration values (defaults to 1 if not specified) */
  step?: number
}

export interface ModelCapabilities {
  /** Available resolutions (e.g., "1024x1024", "720p") */
  resolutions?: string[]
  /** Available aspect ratios (e.g., "16:9", "1:1") */
  aspectRatios?: string[]
  /** Duration range in seconds for video/audio */
  duration?: DurationRange
  /** Maximum number of outputs per request */
  maxImages?: number
  /** Available voice IDs for TTS */
  voices?: string[]
  /** Human-readable voice labels */
  voiceLabels?: Record<string, string>
  /** Available languages */
  languages?: string[]
  /** Supported video generation modes */
  supportedModes?: VideoGenerationMode[]
  /** Available genres for music generation */
  genres?: string[]
  /** Available categories for soundtrack generation */
  categories?: string[]
  /** Maximum tokens for text generation */
  maxTokens?: number
}

export type ParameterType = "string" | "number" | "integer" | "boolean"

export interface ParameterDefinition {
  /** Data type of the parameter */
  type: ParameterType
  /** Default value if not provided */
  default?: unknown
  /** Minimum value for numeric types */
  min?: number
  /** Maximum value for numeric types */
  max?: number
  /** Maximum length for strings */
  maxLength?: number
  /** Allowed values */
  enum?: string[]
  /** Human-readable description */
  description?: string
}

export interface ModelParameters {
  /** List of required parameter names */
  required: string[]
  /** Optional parameters with their definitions */
  optional: Record<string, ParameterDefinition>
}

export interface ParameterTransform {
  /** Maximum value to clamp to */
  max?: number
  /** Minimum value to clamp to */
  min?: number
  /** Multiply the value by this factor */
  multiply?: number
}

export interface ProviderConfig {
  /** API endpoint path or model identifier */
  endpoint: string
  /** HTTP method for REST APIs */
  method?: "POST" | "GET"
  /** Mapping of standard params to provider-specific params */
  parameterMapping?: Record<string, string>
  /** Transformations to apply to parameters */
  parameterTransforms?: Record<string, ParameterTransform>
  /** Default parameters to always include */
  defaultParams?: Record<string, unknown>
  /** Model identifier for providers with shared endpoints */
  model?: string
}

export interface Model {
  /** Provider identifier (e.g., "fal-ai") */
  provider: string
  /** Type of generation this model performs */
  type: GenerationType
  /** Human-readable model name */
  name: string
  /** Optional description */
  description?: string
  /** Whether this model is currently available */
  enabled: boolean
  /** Pricing information */
  pricing: ModelPricing
  /** Model capabilities and constraints */
  capabilities: ModelCapabilities
  /** Parameter definitions */
  parameters: ModelParameters
  /** Provider-specific configuration */
  providerConfig: ProviderConfig
}

export interface GenerationModeDefinition {
  id: VideoGenerationMode
  label: string
  description: string
}

export interface ModelRegistry {
  models: Record<string, Model>
  generationModes: Record<string, GenerationModeDefinition>
}

// =============================================================================
// Query Result Types
// =============================================================================

/**
 * Flattened model option for UI dropdowns
 */
export interface ModelOption {
  /** Model identifier (e.g., "fal-ai/flux/schnell") */
  id: string
  /** Human-readable model name */
  name: string
  /** Provider identifier */
  provider: string
  /** Provider display name */
  providerName: string
  /** Generation type */
  type: GenerationType
  /** Pricing information */
  pricing: ModelPricing
  /** Model capabilities */
  capabilities: ModelCapabilities
}

/**
 * Validation result for model parameters
 */
export interface ValidationResult {
  /** Whether validation passed */
  valid: boolean
  /** List of validation errors */
  errors: string[]
}

// =============================================================================
// Legacy Type Compatibility
// =============================================================================

/**
 * Video model in the format expected by existing frontend components
 * @deprecated Use ModelOption instead
 */
export interface LegacyVideoModel {
  id: string
  name: string
  provider: string
  resolutions: string[]
  aspectRatios: string[]
  durations: DurationRange
  pricePerSecond: number
  supportedModes: VideoGenerationMode[]
}

/**
 * Image model in the format expected by existing frontend components
 * @deprecated Use ModelOption instead
 */
export interface LegacyImageModel {
  id: string
  name: string
  provider: string
  resolutions: string[]
  aspectRatios: string[]
  pricePerImage: number
}

/**
 * TTS model in the format expected by existing frontend components
 * @deprecated Use ModelOption instead
 */
export interface LegacyTTSModel {
  id: string
  name: string
  provider: string
  voices: string[]
  pricePerCharacter: number
}

/**
 * Audio model in the format expected by existing frontend components
 * @deprecated Use ModelOption instead
 */
export interface LegacyAudioModel {
  id: string
  name: string
  provider: string
  genres: string[]
  durations: DurationRange
  pricePerGeneration: number
}

/**
 * Soundtrack model in the format expected by existing frontend components
 * @deprecated Use ModelOption instead
 */
export interface LegacySoundtrackModel {
  id: string
  name: string
  provider: string
  categories: string[]
  durations: DurationRange
  pricePerGeneration: number
}

