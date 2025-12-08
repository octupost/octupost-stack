/**
 * Supabase Browser Client
 * 
 * Creates a Supabase client for browser/client-side usage.
 * Automatically configures cookie sharing across Octupost subdomains in production.
 * 
 * Usage:
 *   import { createClient } from "@octupost/shared/supabase/client"
 *   const supabase = createClient()
 */

import { createBrowserClient } from "@supabase/ssr"
import { getCookieDomain, isProduction } from "../config/constants"

/**
 * Create a Supabase browser client with shared cookie configuration.
 * 
 * @returns Supabase browser client instance
 */
export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookieOptions: {
        // Share cookies across all subdomains of octupost.com in production
        domain: getCookieDomain(),
        path: "/",
        sameSite: "lax",
        secure: isProduction(),
      },
    }
  )
}

