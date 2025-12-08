/**
 * Supabase Middleware Utilities
 * 
 * Provides middleware helpers for session management and authentication.
 * Automatically configures cookie sharing across Octupost subdomains in production.
 * 
 * Usage:
 *   import { createMiddlewareClient, updateSession } from "@octupost/shared/supabase/middleware"
 */

import { createServerClient } from "@supabase/ssr"
import { NextResponse, type NextRequest } from "next/server"
import { getCookieDomain, getAppUrl } from "../config/constants"

/**
 * Create a Supabase client for middleware usage.
 * Returns both the client and the response object for cookie handling.
 * 
 * @param request - The incoming Next.js request
 * @returns Object containing supabase client and response
 */
export function createMiddlewareClient(request: NextRequest) {
  let supabaseResponse = NextResponse.next({ request })
  
  // Extract hostname for localhost detection
  const hostname = request.nextUrl.hostname

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll()
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value)
          )
          supabaseResponse = NextResponse.next({ request })
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, {
              ...options,
              // Share cookies across all subdomains, or undefined for localhost
              domain: getCookieDomain(undefined, hostname),
            })
          )
        },
      },
    }
  )

  return { supabase, response: supabaseResponse, setResponse: (r: NextResponse) => { supabaseResponse = r } }
}

/**
 * Configuration for updateSession middleware.
 */
export interface UpdateSessionConfig {
  /** Routes that don't require authentication */
  publicRoutes?: string[]
  /** URL to redirect unauthenticated users to (defaults to main app sign-in) */
  signInUrl?: string
  /** Whether to include return URL in redirect */
  includeReturnUrl?: boolean
  /** Custom handler for authenticated users */
  onAuthenticated?: (user: unknown, request: NextRequest) => Promise<NextResponse | null>
}

/**
 * Update the Supabase session and optionally handle authentication redirects.
 * 
 * This is a flexible middleware helper that:
 * 1. Refreshes the auth token
 * 2. Optionally redirects unauthenticated users
 * 3. Allows custom handling via callbacks
 * 
 * @param request - The incoming Next.js request
 * @param config - Optional configuration for auth handling
 * @returns NextResponse with updated session cookies
 */
export async function updateSession(
  request: NextRequest,
  config: UpdateSessionConfig = {}
): Promise<NextResponse> {
  const {
    publicRoutes = [],
    signInUrl,
    includeReturnUrl = true,
    onAuthenticated,
  } = config

  let supabaseResponse = NextResponse.next({ request })
  
  // Extract hostname for localhost detection
  const hostname = request.nextUrl.hostname

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll()
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value)
          )
          supabaseResponse = NextResponse.next({ request })
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, {
              ...options,
              // Share cookies across all subdomains, or undefined for localhost
              domain: getCookieDomain(undefined, hostname),
            })
          )
        },
      },
    }
  )

  // Refreshing the auth token
  const {
    data: { user },
  } = await supabase.auth.getUser()

  const pathname = request.nextUrl.pathname

  // Check if current route is public
  const isPublicRoute = publicRoutes.some(
    (route) => pathname === route || pathname.startsWith(route)
  )

  // If user is not logged in and trying to access protected route
  if (!user && !isPublicRoute && signInUrl) {
    const redirectUrl = new URL(signInUrl)
    
    if (includeReturnUrl) {
      redirectUrl.searchParams.set("returnTo", request.nextUrl.toString())
    }
    
    return NextResponse.redirect(redirectUrl)
  }

  // Custom authenticated handler
  if (user && onAuthenticated) {
    const customResponse = await onAuthenticated(user, request)
    if (customResponse) {
      return customResponse
    }
  }

  return supabaseResponse
}

/**
 * Get the default sign-in URL based on environment.
 * Points to the main Octupost app's auth pages.
 */
export function getSignInUrl(): string {
  return `${getAppUrl("app")}/auth/sign-in`
}

/**
 * Get the default sign-up URL based on environment.
 */
export function getSignUpUrl(): string {
  return `${getAppUrl("app")}/auth/sign-up`
}

