/**
 * Provider Pricing Module
 *
 * Centralized price and credit calculation for all provider types.
 * Handles 3 pricing strategies:
 * 1. per_request - Fixed price per request (with optional tier)
 * 2. per_second - Price per second (with optional tier)
 * 3. multiplier - Apply multiplier when certain fields are true
 *
 * Credit System: 1 USD = 100 credits
 *
 * Duration Estimation:
 * For models with unknown output duration (avatar, text-to-speech),
 * duration is estimated from text input using average speaking rates.
 */

import type { Provider, FormValues } from "./types"

/** Conversion rate: 1 USD = 100 credits */
export const USD_TO_CREDITS = 100

/** Buffer multiplier for credit reservations (30% safety buffer) */
export const BUFFER_MULTIPLIER = 1.3

// =============================================================================
// Duration Estimation
// =============================================================================

/**
 * Average speaking rates by model type (characters per second).
 * Based on ~140-150 words per minute, ~5 characters per word.
 */
export const CHARS_PER_SECOND: Record<string, number> = {
  avatar: 14,           // ~14 chars/sec (140 WPM)
  "text-to-speech": 14, // ~14 chars/sec (140 WPM)
}

/** Model types that may require duration estimation */
export const ESTIMATION_MODEL_TYPES = new Set(["avatar", "text-to-speech"])

/**
 * Estimate output duration from input text length.
 *
 * @param text - Input text/script
 * @param modelType - Model type (avatar, text-to-speech)
 * @returns Estimated duration in seconds
 *
 * @example
 * estimateDurationFromText("Hello world!", "avatar") // ~0.86 seconds
 * estimateDurationFromText("A longer script with more words...", "avatar") // ~2.5 seconds
 */
export function estimateDurationFromText(text: string, modelType: string): number {
  if (!text) {
    return 1 // Minimum 1 second
  }

  const charCount = text.length
  const charsPerSec = CHARS_PER_SECOND[modelType] ?? 14

  // Calculate estimated duration
  const estimatedDuration = charCount / charsPerSec

  // Minimum 1 second
  return Math.max(estimatedDuration, 1)
}

/**
 * Extract text from form values (checks common field names).
 *
 * @param formValues - Form values object
 * @returns Text content or empty string
 */
export function getTextFromFormValues(formValues: FormValues): string {
  for (const key of ["prompt", "text", "script", "input_text", "content"]) {
    const value = formValues[key]
    if (value && typeof value === "string") {
      return value
    }
  }
  return ""
}

/**
 * Check if a provider requires duration estimation.
 *
 * Models with per_second pricing and no user-specified duration
 * need estimation because output duration depends on input text length.
 *
 * @param provider - The provider configuration
 * @param formValues - Current form values
 * @returns True if the provider needs duration estimation
 */
export function needsDurationEstimation(
  provider: Provider,
  formValues: FormValues
): boolean {
  const { price, type } = provider
  const { unit } = price

  // Needs estimation if:
  // 1. Model is an avatar/speech type
  // 2. Pricing is per_second
  // 3. User hasn't specified a duration
  return (
    ESTIMATION_MODEL_TYPES.has(type) &&
    unit === "per_second" &&
    formValues.duration === undefined
  )
}

/**
 * Calculate estimated credits including buffer for reservation.
 *
 * @param provider - The provider configuration
 * @param formValues - Current form values
 * @returns Object with estimated credits and reserved amount (with buffer)
 */
export function calculateEstimatedCredits(
  provider: Provider,
  formValues: FormValues
): { estimated: number; reserved: number; duration: number } {
  const needsEstimation = needsDurationEstimation(provider, formValues)
  let duration: number

  if (needsEstimation) {
    const text = getTextFromFormValues(formValues)
    duration = estimateDurationFromText(text, provider.type)
  } else {
    duration = typeof formValues.duration === "number" ? formValues.duration : 1
  }

  // Calculate credits with the estimated/specified duration
  const estimated = calculateCredits(provider, { ...formValues, duration })
  const reserved = Math.round(estimated * BUFFER_MULTIPLIER)

  return { estimated, reserved, duration }
}

// =============================================================================
// Price Calculation
// =============================================================================

/**
 * Calculate the price for a generation request.
 *
 * @param provider - The provider configuration
 * @param formValues - Current form values (duration, resolution, enable_audio, etc.)
 * @returns The calculated price in USD
 *
 * @example
 * // Per second with tier by resolution
 * calculatePrice(provider, { duration: 5, resolution: "1080p" }) // $0.30
 *
 * @example
 * // Per request with tier by duration
 * calculatePrice(provider, { duration: 10 }) // $0.56
 *
 * @example
 * // Per second with audio multiplier
 * calculatePrice(provider, { duration: 4, enable_audio: true }) // $0.60 (0.1 × 4 × 1.5)
 */
export function calculatePrice(provider: Provider, formValues: FormValues): number {
  const { price } = provider
  const { unit, price_per_unit, tier, tier_field_key, multiplier_field_key, multiplier_value } = price

  // Get duration from form values (default to 1 for per_request)
  const duration = typeof formValues.duration === "number" ? formValues.duration : 1

  // Step 1: Determine base price per unit
  let basePrice = price_per_unit ?? 0

  // If tier pricing exists, look up the price based on tier_field_key
  if (tier && tier_field_key) {
    const tierValue = formValues[tier_field_key]
    if (tierValue !== undefined) {
      const tierKey = String(tierValue)
      if (tier[tierKey] !== undefined) {
        basePrice = tier[tierKey]
      }
    }
  }

  // Step 2: Calculate total based on unit type
  let totalPrice: number

  switch (unit) {
    case "per_request":
      // Flat fee per request
      totalPrice = basePrice
      break

    case "per_second":
      // Standard per-second pricing
      totalPrice = basePrice * duration
      break

    case "per_char":
      // Per character pricing (for TTS)
      // We don't know character count from form values, return base price
      // The actual calculation should be done when we know the text length
      totalPrice = basePrice
      break

    default:
      totalPrice = basePrice
  }

  // Step 3: Apply multiplier if applicable
  if (multiplier_field_key && multiplier_value) {
    const shouldApplyMultiplier = formValues[multiplier_field_key] === true
    if (shouldApplyMultiplier) {
      totalPrice *= multiplier_value
    }
  }

  return totalPrice
}

/**
 * Calculate price for per_char providers based on text length.
 *
 * Rounds UP to the nearest billing unit (minimum 1 unit).
 * e.g., billing_unit_size=1000, price_per_unit=$0.1:
 *   - 1-1000 chars = 1 unit = $0.10
 *   - 1001-2000 chars = 2 units = $0.20
 *
 * @param provider - The provider configuration
 * @param textLength - Number of characters in the text
 * @returns The calculated price in USD
 */
export function calculateCharPrice(provider: Provider, textLength: number): number {
  const { price } = provider
  const { price_per_unit, billing_unit_size } = price

  if (price.unit !== "per_char") {
    return calculatePrice(provider, {})
  }

  const pricePerUnit = price_per_unit ?? 0
  const unitSize = billing_unit_size ?? 1

  // Round UP to nearest billing unit (minimum 1 unit if textLength > 0)
  const billingUnits = textLength > 0 ? Math.ceil(textLength / unitSize) : 0
  return billingUnits * pricePerUnit
}

// =============================================================================
// Credit Calculation
// =============================================================================

/**
 * Calculate credits for a generation request.
 *
 * @param provider - The provider configuration
 * @param formValues - Current form values (duration, resolution, enable_audio, etc.)
 * @returns The calculated credits (1 USD = 100 credits)
 *
 * @example
 * // Per second at 4 credits/sec for 5 seconds
 * calculateCredits(provider, { duration: 5 }) // 20 credits
 *
 * @example
 * // With audio multiplier (1.5x)
 * calculateCredits(provider, { duration: 4, enable_audio: true }) // 60 credits
 */
export function calculateCredits(provider: Provider, formValues: FormValues): number {
  const { price } = provider
  const { unit, credits_per_unit, price_per_unit, credits_tier, tier, tier_field_key, multiplier_field_key, multiplier_value } = price

  // Get duration from form values (default to 1 for per_request)
  const duration = typeof formValues.duration === "number" ? formValues.duration : 1

  // Step 1: Determine base credits per unit
  // Use credits_per_unit if provided, otherwise derive from price_per_unit
  let baseCredits = credits_per_unit ?? Math.round((price_per_unit ?? 0) * USD_TO_CREDITS)

  // If tier pricing exists, look up the credits based on tier_field_key
  if (tier_field_key) {
    const tierValue = formValues[tier_field_key]
    if (tierValue !== undefined) {
      const tierKey = String(tierValue)
      
      // Try credits_tier first, then derive from tier
      if (credits_tier && credits_tier[tierKey] !== undefined) {
        baseCredits = credits_tier[tierKey]
      } else if (tier && tier[tierKey] !== undefined) {
        baseCredits = Math.round(tier[tierKey] * USD_TO_CREDITS)
      }
    }
  }

  // Step 2: Calculate total based on unit type
  let totalCredits: number

  switch (unit) {
    case "per_request":
      // Flat fee per request
      totalCredits = baseCredits
      break

    case "per_second":
      // Per-second pricing
      totalCredits = baseCredits * duration
      break

    case "per_char":
      // Per character - return base, actual calc needs text length
      totalCredits = baseCredits
      break

    default:
      totalCredits = baseCredits
  }

  // Step 3: Apply multiplier if applicable
  if (multiplier_field_key && multiplier_value) {
    const shouldApplyMultiplier = formValues[multiplier_field_key] === true
    if (shouldApplyMultiplier) {
      totalCredits = Math.round(totalCredits * multiplier_value)
    }
  }

  return Math.round(totalCredits)
}

/**
 * Calculate credits for per_char providers based on text length.
 *
 * Rounds UP to the nearest billing unit (minimum 1 unit).
 * e.g., billing_unit_size=1000, credits_per_unit=10:
 *   - 1-1000 chars = 1 unit = 10 credits
 *   - 1001-2000 chars = 2 units = 20 credits
 *
 * @param provider - The provider configuration
 * @param textLength - Number of characters in the text
 * @returns The calculated credits
 */
export function calculateCharCredits(provider: Provider, textLength: number): number {
  const { price } = provider
  const { credits_per_unit, price_per_unit, billing_unit_size } = price

  if (price.unit !== "per_char") {
    return calculateCredits(provider, {})
  }

  const creditsPerUnit = credits_per_unit ?? Math.round((price_per_unit ?? 0) * USD_TO_CREDITS)
  const unitSize = billing_unit_size ?? 1

  // Round UP to nearest billing unit (minimum 1 unit if textLength > 0)
  const billingUnits = textLength > 0 ? Math.ceil(textLength / unitSize) : 0
  return billingUnits * creditsPerUnit
}

/**
 * Format credits for display.
 *
 * @param credits - Number of credits
 * @returns Formatted string (e.g., "20 credits")
 */
export function formatCredits(credits: number): string {
  return `${credits} credits`
}

/**
 * Get display credits string for a provider (shows range for tiered pricing).
 *
 * @param provider - The provider configuration
 * @returns Display string (e.g., "4 cr/sec" or "6 - 24 cr/sec")
 */
export function getDisplayCredits(provider: Provider): string {
  const { price } = provider
  const { unit, credits_per_unit, price_per_unit, credits_tier, tier } = price

  const unitLabel = unit === "per_second" ? " cr/sec" : unit === "per_char" ? " cr/char" : " cr"

  // Tiered pricing - show range
  const tierValues = credits_tier ?? tier
  if (tierValues) {
    const prices = Object.values(tierValues)
    if (prices.length > 0) {
      // Convert to credits if using price tier
      const credits = credits_tier 
        ? prices 
        : prices.map(p => Math.round(p * USD_TO_CREDITS))
      
      const min = Math.min(...credits)
      const max = Math.max(...credits)
      if (min === max) {
        return `${min}${unitLabel}`
      }
      return `${min} - ${max}${unitLabel}`
    }
  }

  // Simple pricing
  const creditsPerUnit = credits_per_unit ?? Math.round((price_per_unit ?? 0) * USD_TO_CREDITS)
  if (creditsPerUnit > 0) {
    return `${creditsPerUnit}${unitLabel}`
  }

  return "Free"
}

// =============================================================================
// Price Formatting
// =============================================================================

/**
 * Format price for display.
 *
 * @param price - Price in USD
 * @returns Formatted price string (e.g., "$0.10" or "$0.0050")
 */
export function formatPrice(price: number): string {
  if (price < 0.01) {
    return `$${price.toFixed(4)}`
  }
  return `$${price.toFixed(2)}`
}

/**
 * Get display price string for a provider (shows range for tiered pricing).
 *
 * @param provider - The provider configuration
 * @returns Display string (e.g., "$0.10/sec" or "$0.06 - $0.24/sec")
 */
export function getDisplayPrice(provider: Provider): string {
  const { price } = provider
  const { unit, price_per_unit, tier } = price

  const unitLabel = unit === "per_second" ? "/sec" : unit === "per_char" ? "/char" : ""

  // Tiered pricing - show range
  if (tier) {
    const prices = Object.values(tier)
    if (prices.length > 0) {
      const min = Math.min(...prices)
      const max = Math.max(...prices)
      if (min === max) {
        return `${formatPrice(min)}${unitLabel}`
      }
      return `${formatPrice(min)} - ${formatPrice(max)}${unitLabel}`
    }
  }

  // Simple pricing
  if (price_per_unit !== undefined) {
    return `${formatPrice(price_per_unit)}${unitLabel}`
  }

  return "Free"
}

// =============================================================================
// Price Estimation
// =============================================================================

/**
 * Get estimated price range for a provider.
 * Uses min and max duration to calculate range.
 *
 * @param provider - The provider configuration
 * @returns Object with min and max estimated prices
 */
export function getEstimatedPriceRange(
  provider: Provider
): { min: number; max: number } | null {
  // Find duration parameter to get min/max
  const durationParam = provider.parameters.find(
    (p) => "key" in p && p.key === "duration"
  )

  if (!durationParam || !("accepted_values" in durationParam)) {
    return null
  }

  const acceptedValues = durationParam.accepted_values
  if (
    !acceptedValues ||
    typeof acceptedValues !== "object" ||
    Array.isArray(acceptedValues)
  ) {
    return null
  }

  if (!("min_duration" in acceptedValues) || !("max_duration" in acceptedValues)) {
    return null
  }

  const minDuration = acceptedValues.min_duration
  const maxDuration = acceptedValues.max_duration

  const minPrice = calculatePrice(provider, { duration: minDuration })
  const maxPrice = calculatePrice(provider, { duration: maxDuration })

  return { min: minPrice, max: maxPrice }
}

