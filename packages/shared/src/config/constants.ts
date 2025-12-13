/**
 * Centralized Configuration Constants
 * 
 * All domain, URL, and port configurations for the Octupost platform.
 * Import from "@octupost/shared/config" in any app.
 */

// =============================================================================
// Domain Configuration
// =============================================================================

export const DOMAIN = "octupost.com"
export const DEV_DOMAIN = "octupost.local"
export const COOKIE_DOMAIN = `.${DOMAIN}` as const
export const DEV_COOKIE_DOMAIN = `.${DEV_DOMAIN}` as const

// =============================================================================
// Port Configuration
// =============================================================================

export const PORTS = {
  app: 3000,
  social: 3002,  // Mixpost runs here
  api: 8000,
} as const

// =============================================================================
// URL Configuration
// =============================================================================

export const URLS = {
  app: {
    prod: `https://app.${DOMAIN}`,
    dev: `http://localhost:${PORTS.app}`,
  },
  social: {
    prod: `https://social.${DOMAIN}`,
    dev: `http://localhost:${PORTS.social}`,
  },
  api: {
    prod: `https://api.${DOMAIN}`,
    dev: `http://localhost:${PORTS.api}`,
  },
} as const

// =============================================================================
// Type Exports
// =============================================================================

export type AppName = keyof typeof URLS
export type UrlConfig = typeof URLS[AppName]

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Get the appropriate URL for an app based on the current environment.
 * 
 * @param app - The app name (app, social, api)
 * @param env - Optional environment override. Defaults to NODE_ENV.
 * @returns The URL for the specified app in the given environment
 */
export function getAppUrl(app: AppName, env?: string): string {
  const environment = env ?? process.env.NODE_ENV
  return environment === "production" ? URLS[app].prod : URLS[app].dev
}

/**
 * Get the cookie domain based on the current environment.
 * Returns undefined for localhost (allows cookie sharing between ports),
 * .octupost.local for subdomain-based local development,
 * and .octupost.com for production.
 * 
 * @param env - Optional environment override. Defaults to NODE_ENV.
 * @param hostname - Optional hostname for server-side detection.
 * @returns The cookie domain for the current environment, or undefined for localhost
 */
export function getCookieDomain(env?: string, hostname?: string): string | undefined {
  const environment = env ?? process.env.NODE_ENV
  
  if (environment === "production") {
    return COOKIE_DOMAIN
  }
  
  // Check hostname (server-side when passed, client-side via window)
  const currentHostname = hostname ?? (typeof window !== "undefined" ? window.location.hostname : undefined)
  
  // For localhost, return undefined to allow cookie sharing between different ports
  if (currentHostname === "localhost" || currentHostname === "127.0.0.1") {
    return undefined
  }
  
  // For subdomain-based local development (octupost.local)
  return DEV_COOKIE_DOMAIN
}

/**
 * Check if the current environment is production.
 */
export function isProduction(env?: string): boolean {
  const environment = env ?? process.env.NODE_ENV
  return environment === "production"
}

/**
 * Check if the current environment is development.
 */
export function isDevelopment(env?: string): boolean {
  const environment = env ?? process.env.NODE_ENV
  return environment === "development"
}

// =============================================================================
// CORS Origins (for API)
// =============================================================================

/**
 * Get CORS origins list for the API server.
 * Includes both production and development URLs.
 */
export function getCorsOrigins(): string[] {
  return [
    URLS.app.prod,
    URLS.app.dev,
    URLS.social.prod,
    URLS.social.dev,
  ]
}

/**
 * Get CORS origins as comma-separated string (for env vars).
 */
export function getCorsOriginsString(): string {
  return getCorsOrigins().join(",")
}

