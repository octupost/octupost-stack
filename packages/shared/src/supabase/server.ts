/**
 * Supabase Server Client
 * 
 * Creates a Supabase client for server-side usage (Server Components, Route Handlers).
 * Automatically configures cookie sharing across Octupost subdomains in production.
 * 
 * Usage:
 *   import { createClient } from "@octupost/shared/supabase/server"
 *   const supabase = await createClient()
 */

import { createServerClient } from "@supabase/ssr"
import { cookies } from "next/headers"
import { getCookieDomain } from "../config/constants"

/**
 * Create a Supabase server client with shared cookie configuration.
 * Must be called in an async context (Server Components, Route Handlers).
 * 
 * @returns Supabase server client instance
 */
export async function createClient() {
  const cookieStore = await cookies()

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll()
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, {
                ...options,
                // Share cookies across all subdomains of octupost.com in production
                domain: getCookieDomain(),
              })
            )
          } catch {
            // The `setAll` method was called from a Server Component.
            // This can be ignored if you have middleware refreshing user sessions.
          }
        },
      },
    }
  )
}

