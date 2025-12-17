/**
 * Pricing Utilities (Minimal)
 *
 * Basic utilities for displaying FAL pricing info.
 * Actual pricing data comes from FAL's Pricing API.
 */

import type { FalPricing } from "./types"

/** Conversion rate: 1 USD = 100 credits */
export const USD_TO_CREDITS = 100

/**
 * Format a price value for display.
 *
 * @param price - Price in USD
 * @returns Formatted price string (e.g., "$0.10", "$0.014")
 */
export function formatPrice(price: number): string {
  if (price === 0) {
    return "$0.00"
  }

  // For very small prices (< $0.001), show 4 decimal places
  if (price < 0.001) {
    return `$${price.toFixed(4)}`
  }

  // For small prices (< $0.01), show 3 decimal places
  if (price < 0.01) {
    return `$${price.toFixed(3)}`
  }

  // For prices < $0.10 that would lose precision with 2 decimals
  if (price < 0.1) {
    const thirdDecimal = Math.round((price * 1000) % 10)
    if (thirdDecimal !== 0) {
      return `$${price.toFixed(3)}`
    }
  }

  // Standard 2 decimal places
  return `$${price.toFixed(2)}`
}

/**
 * Format FAL pricing info for display.
 *
 * @param pricing - Pricing info from FAL API
 * @returns Formatted string (e.g., "$0.04 per generation")
 */
export function formatFalPricing(pricing: FalPricing): string {
  const priceStr = formatPrice(pricing.unit_price)
  const unitStr = pricing.unit.replace(/_/g, " ")
  return `${priceStr} per ${unitStr}`
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
 * Convert USD to credits.
 *
 * @param usd - Amount in USD
 * @returns Credits (1 USD = 100 credits)
 */
export function usdToCredits(usd: number): number {
  return Math.round(usd * USD_TO_CREDITS)
}
