/**
 * Provider Registry Types
 *
 * TypeScript types for the provider.json registry.
 * These types define the structure for AI generation providers/models.
 */

// =============================================================================
// Price Types
// =============================================================================

/** Unit of pricing */
export type PriceUnit = "per_second" | "per_request" | "per_char"

/** Billing strategy: direct deduction or reservation system */
export type BillingStrategy = "direct" | "reservation"

/** Tier-based pricing lookup (e.g., resolution -> price or duration -> price) */
export type PriceTier = Record<string, number>

/** Provider pricing configuration */
export interface ProviderPrice {
  /** Unit of pricing */
  unit: PriceUnit
  /** Price per unit in USD (used when no tier pricing) */
  price_per_unit?: number
  /** Credits per unit (1 USD = 100 credits). Auto-calculated if not provided. */
  credits_per_unit?: number
  /** Billing unit size (e.g., 1000 for per 1000 chars) */
  billing_unit_size?: number
  /** Tier-based pricing lookup (USD values) */
  tier?: PriceTier
  /** Tier-based credits lookup (credits values) */
  credits_tier?: PriceTier
  /** Field key to look up in tier (e.g., "resolution" or "duration") */
  tier_field_key?: string
  /** Field key to check for multiplier (e.g., "enable_audio") */
  multiplier_field_key?: string
  /** Multiplier value when multiplier_field_key is true */
  multiplier_value?: number
}

// =============================================================================
// Parameter Types
// =============================================================================

/** Parameter data type */
export type ParameterType = "string" | "integer" | "float" | "boolean" | "image" | "image_array"

/** Mapping type for API payload */
export type MappingType = "string" | "integer" | "float" | "boolean" | "image" | "image_array"

/** Accepted values for duration parameters */
export interface DurationAcceptedValues {
  /** Step increment for slider */
  steps: number
  /** Maximum duration in seconds */
  max_duration: number
  /** Minimum duration in seconds */
  min_duration: number
}

/** Accepted values for speed parameters */
export interface SpeedAcceptedValues {
  /** Step increment for slider */
  steps: number
  /** Maximum speed */
  max_speed: number
  /** Minimum speed */
  min_speed: number
}

/** Avatar option with metadata (for providers with built-in avatars like Argil) */
export interface AvatarAcceptedValue {
  /** Display name (sent to API) */
  name: string
  /** Image URL for avatar preview */
  imageUrl: string
}

/** Type guard for duration accepted values */
export function isDurationAcceptedValues(value: unknown): value is DurationAcceptedValues {
  return (
    typeof value === "object" &&
    value !== null &&
    "max_duration" in value &&
    "min_duration" in value
  )
}

/** Type guard for speed accepted values */
export function isSpeedAcceptedValues(value: unknown): value is SpeedAcceptedValues {
  return (
    typeof value === "object" &&
    value !== null &&
    "max_speed" in value &&
    "min_speed" in value
  )
}

/** Type guard for array accepted values */
export function isArrayAcceptedValues(value: unknown): value is (string | number)[] {
  return Array.isArray(value) && (value.length === 0 || typeof value[0] !== "object")
}

/** Type guard for avatar accepted values (array of objects with name property) */
export function isAvatarAcceptedValues(value: unknown): value is AvatarAcceptedValue[] {
  return (
    Array.isArray(value) &&
    value.length > 0 &&
    typeof value[0] === "object" &&
    value[0] !== null &&
    "name" in value[0]
  )
}

/** Union type for all accepted values */
export type AcceptedValues = (string | number)[] | DurationAcceptedValues | SpeedAcceptedValues | AvatarAcceptedValue[]

/** Parameter definition */
export interface ProviderParameter {
  /** Parameter key (UI field name) */
  key: string
  /** Data type */
  type: ParameterType
  /** Notes about the parameter */
  notes?: string
  /** Default value */
  default?: string | number | boolean
  /** API field mapping */
  mapping: string
  /** Whether the parameter is required */
  required: boolean
  /** Type for API payload mapping */
  mapping_type: MappingType
  /** Accepted values (array for select, object for slider) */
  accepted_values?: AcceptedValues
  /** Maximum character length for text parameters */
  max_length?: number
}

/** Default values object (merged into API payload) */
export interface DefaultValuesEntry {
  default_values: Record<string, unknown>
}

/** Type guard for default values entry */
export function isDefaultValuesEntry(value: unknown): value is DefaultValuesEntry {
  return (
    typeof value === "object" &&
    value !== null &&
    "default_values" in value
  )
}

/** Union type for parameters array items */
export type ParameterEntry = ProviderParameter | DefaultValuesEntry

// =============================================================================
// Provider Types
// =============================================================================

/** Provider tier (quality/speed tier) */
export type ProviderTier = "Basic" | "Standard" | "Plus" | "Pro" | "Elite"

/** Parent type category */
export type ProviderParentType =
  | "avatar"
  | "text-to-video"
  | "image-to-video"
  | "text-to-image"
  | "text-to-audio"
  | "text-to-music"
  | "text-to-speech"
  | "video-to-audio"
  | "retake"

/** Provider type (more specific than parent_type) */
export type ProviderType =
  | "avatar"
  | "text-to-video"
  | "image-to-video"
  | "text-to-image"
  | "text-to-audio"
  | "text-to-music"
  | "text-to-speech"
  | "video-to-audio"
  | "retake"
  | "reference-to-video"
  | "first-last-frame-to-video"

/** Full provider definition */
export interface Provider {
  /** Frames per second (null for non-video providers) */
  fps: number | null
  /** Link to provider documentation */
  link: string
  /** Quality/speed tier */
  tier: ProviderTier
  /** Specific provider type */
  type: ProviderType
  /** Pricing configuration */
  price: ProviderPrice
  /** API endpoint identifier */
  endpoint: string
  /** Display name */
  provider: string
  /** Whether the provider is active */
  is_active: boolean
  /** Parameter definitions */
  parameters: ParameterEntry[]
  /** Parent type category */
  parent_type: ProviderParentType
  /** Billing strategy: direct deduction or reservation system. Defaults to "direct". */
  billing_strategy?: BillingStrategy
}

// =============================================================================
// Helper Types for Forms
// =============================================================================

/** Form values object (key -> value) */
export type FormValues = Record<string, string | number | boolean | undefined>

/** Duration range for UI components */
export interface DurationRange {
  min: number
  max: number
  step: number
}

/** Speed range for UI components */
export interface SpeedRange {
  min: number
  max: number
  step: number
}



