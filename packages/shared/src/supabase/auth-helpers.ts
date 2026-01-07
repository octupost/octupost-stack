/**
 * Supabase Auth Helpers
 *
 * Utilities for handling Supabase authentication tokens with automatic refresh.
 *
 * Usage:
 *   import { getValidAccessToken } from "@octupost/shared/supabase/auth-helpers"
 *   const token = await getValidAccessToken(supabase)
 */

import type { SupabaseClient } from "@supabase/supabase-js"

/**
 * Token refresh buffer in milliseconds.
 * Tokens will be refreshed when they expire within this time window.
 */
const REFRESH_BUFFER_MS = 60_000 // 60 seconds

/**
 * Get a valid access token from Supabase, automatically refreshing if needed.
 *
 * This solves the issue where `getSession()` returns a cached token that may be
 * expired, causing "Invalid token" errors on API calls.
 *
 * @param supabase - The Supabase client instance
 * @returns The access token string, or null if no valid session exists
 *
 * @example
 * ```typescript
 * const supabase = createClient()
 * const token = await getValidAccessToken(supabase)
 *
 * if (token) {
 *   const response = await fetch('/api/endpoint', {
 *     headers: { Authorization: `Bearer ${token}` }
 *   })
 * }
 * ```
 */
export async function getValidAccessToken(
  supabase: SupabaseClient
): Promise<string | null> {
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    return null
  }

  // Check if token expires within the buffer window
  const expiresAt = session.expires_at ?? 0
  const expiresAtMs = expiresAt * 1000
  const needsRefresh = expiresAtMs - Date.now() < REFRESH_BUFFER_MS

  if (needsRefresh) {
    const { data, error } = await supabase.auth.refreshSession()

    if (error) {
      console.warn("Failed to refresh Supabase session:", error.message)
      // Return the potentially expired token as a fallback - the API will reject if truly expired
      return session.access_token
    }

    return data.session?.access_token ?? null
  }

  return session.access_token
}

/**
 * Get authorization headers with a valid access token.
 *
 * Convenience wrapper around `getValidAccessToken` that returns a headers object
 * ready to use with fetch or other HTTP clients.
 *
 * @param supabase - The Supabase client instance
 * @returns Headers object with Authorization header, or empty object if no session
 *
 * @example
 * ```typescript
 * const supabase = createClient()
 * const headers = await getAuthHeaders(supabase)
 *
 * const response = await fetch('/api/endpoint', { headers })
 * ```
 */
export async function getAuthHeaders(
  supabase: SupabaseClient
): Promise<HeadersInit> {
  const token = await getValidAccessToken(supabase)

  if (token) {
    return {
      Authorization: `Bearer ${token}`,
    }
  }

  return {}
}
