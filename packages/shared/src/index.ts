/**
 * @octupost/shared
 * 
 * Centralized configuration and utilities for the Octupost platform.
 * 
 * Recommended imports:
 *   // Configuration
 *   import { URLS, getAppUrl, getCookieDomain } from "@octupost/shared/config"
 * 
 *   // AI Model Registry
 *   import { getModel, getModelsByType, getModelOptionsForType } from "@octupost/shared/registry"
 * 
 *   // Supabase clients (import from specific paths for tree-shaking)
 *   import { createClient } from "@octupost/shared/supabase/client"
 *   import { createClient } from "@octupost/shared/supabase/server"
 *   import { updateSession } from "@octupost/shared/supabase/middleware"
 */

// Re-export everything for convenience
export * from "./config"
export * from "./supabase"
export * from "./registry"
export * from "./library"
