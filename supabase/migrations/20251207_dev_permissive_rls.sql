-- =============================================================================
-- DEVELOPMENT PERMISSIVE RLS POLICIES
-- =============================================================================
-- Created: 2024-12-07
-- Purpose: Allow fast development without RLS restrictions
-- 
-- IMPORTANT: These policies MUST be replaced with proper restrictive 
-- policies before production deployment!
--
-- All dev policies are prefixed with "dev_" for easy identification.
-- See: supabase/RLS_POLICIES.md for production policy checklist
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
-- STEP 1: Enable RLS on all tables
-- -----------------------------------------------------------------------------
-- RLS must be enabled for policies to take effect. Even with permissive
-- policies, having RLS ON ensures the system behaves consistently.

ALTER TABLE octupost.workplaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE octupost.workplace_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE octupost.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE octupost.workplace_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE octupost.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE octupost.assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE octupost.project_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE octupost.workplace_assets ENABLE ROW LEVEL SECURITY;

-- -----------------------------------------------------------------------------
-- STEP 2: Create permissive dev policies
-- -----------------------------------------------------------------------------
-- These policies allow ALL authenticated users to perform ALL operations.
-- This is intentionally insecure for development speed.

-- workplaces: Full access for all authenticated users
CREATE POLICY "dev_workplaces_all" ON octupost.workplaces
  FOR ALL TO authenticated 
  USING (true) 
  WITH CHECK (true);

-- workplace_members: Full access for all authenticated users
CREATE POLICY "dev_workplace_members_all" ON octupost.workplace_members
  FOR ALL TO authenticated 
  USING (true) 
  WITH CHECK (true);

-- projects: Full access for all authenticated users
CREATE POLICY "dev_projects_all" ON octupost.projects
  FOR ALL TO authenticated 
  USING (true) 
  WITH CHECK (true);

-- workplace_projects: Full access for all authenticated users
CREATE POLICY "dev_workplace_projects_all" ON octupost.workplace_projects
  FOR ALL TO authenticated 
  USING (true) 
  WITH CHECK (true);

-- user_profiles: Full access for all authenticated users
CREATE POLICY "dev_user_profiles_all" ON octupost.user_profiles
  FOR ALL TO authenticated 
  USING (true) 
  WITH CHECK (true);

-- assets: Full access for all authenticated users
CREATE POLICY "dev_assets_all" ON octupost.assets
  FOR ALL TO authenticated 
  USING (true) 
  WITH CHECK (true);

-- project_assets: Full access for all authenticated users
CREATE POLICY "dev_project_assets_all" ON octupost.project_assets
  FOR ALL TO authenticated 
  USING (true) 
  WITH CHECK (true);

-- workplace_assets: Full access for all authenticated users
CREATE POLICY "dev_workplace_assets_all" ON octupost.workplace_assets
  FOR ALL TO authenticated 
  USING (true) 
  WITH CHECK (true);

COMMIT;

-- =============================================================================
-- END OF DEVELOPMENT POLICIES
-- =============================================================================
-- 
-- NEXT STEPS BEFORE PRODUCTION:
-- 1. Review supabase/RLS_POLICIES.md for the production checklist
-- 2. Create a new migration to drop dev_* policies
-- 3. Create proper restrictive policies based on your access patterns
-- 
-- To quickly find all dev policies in your database:
--   SELECT policyname FROM pg_policies WHERE policyname LIKE 'dev_%';
--
-- =============================================================================

