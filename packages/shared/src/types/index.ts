/**
 * Centralized Type Definitions
 *
 * Single source of truth for media types, asset types, and related mappings.
 * Import from "@octupost/shared/types" in any app.
 *
 * These types are defined in types.json and consumed by both:
 * - Frontend (TypeScript)
 * - Backend (Python via api/app/types.py)
 */

import typesConfig from "./types.json"

// =============================================================================
// Constants (arrays for runtime validation)
// =============================================================================

/** All valid media types */
export const MEDIA_TYPES = typesConfig.mediaTypes as readonly ["image", "video", "audio"]

/** All valid asset types */
export const ASSET_TYPES = typesConfig.assetTypes as readonly [
  "image",
  "video",
  "avatar_video",
  "avatar_image",
  "speech",
  "music",
  "sound_effect"
]

/** All valid composer display sections */
export const COMPOSER_DISPLAY_SECTIONS = typesConfig.composerDisplaySections as readonly [
  "image",
  "video",
  "avatar",
  "speech",
  "music",
  "sound_effect"
]

/** Mapping from asset type to its fundamental media type */
export const ASSET_TYPE_TO_MEDIA_TYPE = typesConfig.assetTypeToMediaType as {
  readonly image: "image"
  readonly video: "video"
  readonly avatar_video: "video"
  readonly avatar_image: "image"
  readonly speech: "audio"
  readonly music: "audio"
  readonly sound_effect: "audio"
}

// =============================================================================
// Type Definitions
// =============================================================================

/** Fundamental media category: image, video, or audio */
export type MediaType = (typeof MEDIA_TYPES)[number]

/** Specific asset type for filtering and display */
export type AssetType = (typeof ASSET_TYPES)[number]

/** Composer display section (which tab the model appears in) */
export type ComposerDisplaySection = (typeof COMPOSER_DISPLAY_SECTIONS)[number]

/** Alias for OutputMediaType (same as MediaType) */
export type OutputMediaType = MediaType

/** Alias for OutputAssetType (same as AssetType) */
export type OutputAssetType = AssetType

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Derive the fundamental media type from a specific asset type.
 *
 * @param assetType - The specific asset type
 * @returns The fundamental media type (image, video, or audio)
 *
 * @example
 * deriveMediaType("avatar_video") // => "video"
 * deriveMediaType("speech") // => "audio"
 */
export function deriveMediaType(assetType: AssetType): MediaType {
  return ASSET_TYPE_TO_MEDIA_TYPE[assetType]
}

/**
 * Check if a string is a valid media type.
 */
export function isValidMediaType(value: string): value is MediaType {
  return (MEDIA_TYPES as readonly string[]).includes(value)
}

/**
 * Check if a string is a valid asset type.
 */
export function isValidAssetType(value: string): value is AssetType {
  return (ASSET_TYPES as readonly string[]).includes(value)
}

/**
 * Check if a string is a valid composer display section.
 */
export function isValidComposerDisplaySection(value: string): value is ComposerDisplaySection {
  return (COMPOSER_DISPLAY_SECTIONS as readonly string[]).includes(value)
}
