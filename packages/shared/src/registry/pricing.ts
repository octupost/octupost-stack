/**
 * Provider Pricing Module
 *
 * Centralized price calculation for all provider types.
 * Handles 3 pricing strategies:
 * 1. per_request - Fixed price per request (with optional tier)
 * 2. per_second - Price per second (with optional tier)
 * 3. multiplier - Apply multiplier when certain fields are true
 */

import type { Provider, FormValues } from "./types"

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

  // Calculate price based on billing unit size
  // e.g., $0.1 per 1000 chars, 500 chars = $0.05
  return (textLength / unitSize) * pricePerUnit
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

