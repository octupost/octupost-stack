/**
 * Supabase utilities barrel export
 * 
 * Note: Prefer importing from specific paths for better tree-shaking:
 *   import { createClient } from "@octupost/shared/supabase/client"
 *   import { createClient } from "@octupost/shared/supabase/server"
 */

export { createClient as createBrowserClient } from "./client"
export { createClient as createServerClient } from "./server"
export {
  createMiddlewareClient,
  updateSession,
  getSignInUrl,
  getSignUpUrl,
  type UpdateSessionConfig,
} from "./middleware"

