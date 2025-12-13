/**
 * @octupost/shared
 * 
 * Centralized configuration and utilities for the Octupost platform.
 * 
 * Recommended imports:
 *   // Configuration
 *   import { URLS, getAppUrl, getCookieDomain } from "@octupost/shared/config"
 * 
 *   // Supabase clients (import from specific paths for tree-shaking)
 *   import { createClient } from "@octupost/shared/supabase/client"
 *   import { createClient } from "@octupost/shared/supabase/server"
 *   import { updateSession } from "@octupost/shared/supabase/middleware"
 */

// Re-export everything for convenience
export * from "./config"
export * from "./supabase"
export * from "./library"
