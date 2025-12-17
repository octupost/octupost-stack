/**
 * Provider Registry Types (Minimal)
 *
 * TypeScript types for the minimal provider.json registry.
 * Parameter schemas are fetched dynamically from FAL's OpenAPI endpoint.
 */

// =============================================================================
// Provider Types
// =============================================================================

/** Provider tier (quality/speed tier) */
export type ProviderTier = "Basic" | "Standard" | "Plus" | "Pro" | "Elite"

/** Output media type - what the model produces */
export type OutputMediaType = "video" | "image" | "music" | "audio" | "avatar"

/** Provider type (specific capability/mode) */
export type ProviderType =
  // Video generation modes
  | "text-to-video"
  | "image-to-video"
  | "first-last-frame-to-video"
  | "reference-to-video"
  | "extend-video"
  | "retake-video"
  | "remix-video"
  // Image generation modes
  | "text-to-image"
  | "image-to-image"
  // Audio/Music generation modes
  | "text-to-audio"
  | "text-to-music"
  | "text-to-speech"
  | "video-to-audio"
  // Avatar
  | "avatar"

/** Minimal provider definition (business logic only) */
export interface Provider {
  /** FAL endpoint identifier */
  endpoint: string
  /** Display name */
  provider: string
  /** Specific provider type/mode - used for capability detection */
  type: ProviderType
  /** Quality/speed tier */
  tier: ProviderTier
  /** Whether the provider is active */
  is_active: boolean
  /** Link to provider documentation */
  link: string
  /** Frames per second (null for non-video providers) */
  fps: number | null
  /** Output media type - what the model produces */
  output_media_type: OutputMediaType
}

// =============================================================================
// FAL OpenAPI Schema Types (Parsed)
// =============================================================================

/** Field type for dynamic form rendering */
export type DynamicFieldType =
  | "text"
  | "textarea"
  | "number"
  | "select"
  | "toggle"
  | "url"
  | "file"

/** Parsed parameter from OpenAPI schema */
export interface ParsedParameter {
  /** Parameter key/name from OpenAPI */
  key: string
  /** Field type for rendering */
  fieldType: DynamicFieldType
  /** Original OpenAPI type */
  openApiType: string
  /** Whether parameter is required */
  required: boolean
  /** Default value if any */
  default?: string | number | boolean
  /** Description from OpenAPI */
  description?: string
  /** Enum values for select fields */
  enum?: (string | number)[]
  /** Minimum value for numbers */
  minimum?: number
  /** Maximum value for numbers */
  maximum?: number
  /** Min length for strings */
  minLength?: number
  /** Max length for strings */
  maxLength?: number
  /** Format hint (e.g., "uri") */
  format?: string
}

/** Parsed schema response from FAL */
export interface ParsedSchema {
  /** Endpoint ID */
  endpoint: string
  /** List of parsed parameters */
  parameters: ParsedParameter[]
}

// =============================================================================
// FAL Pricing Types
// =============================================================================

/** Pricing info from FAL API */
export interface FalPricing {
  /** Endpoint ID */
  endpoint_id: string
  /** Unit price in USD */
  unit_price: number
  /** Pricing unit (e.g., "generations", "seconds") */
  unit: string
  /** Currency (always USD) */
  currency: string
}

// =============================================================================
// Combined Model Data (Provider + Schema + Pricing)
// =============================================================================

/** Complete model data for UI */
export interface ModelData {
  /** Provider config from provider.json */
  provider: Provider
  /** Parsed schema from OpenAPI (null if loading/error) */
  schema: ParsedSchema | null
  /** Pricing info from FAL (null if loading/error) */
  pricing: FalPricing | null
}

// =============================================================================
// Form Types
// =============================================================================

/** Form values object (key -> value) */
export type FormValues = Record<string, string | number | boolean | undefined>
