-- =============================================================================
-- PRODUCTION RLS POLICIES
-- =============================================================================
-- Replaces permissive dev_* policies with proper restrictive policies
-- Based on templates from supabase/RLS_POLICIES.md
--
-- IMPORTANT: Test all features after applying this migration!
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
-- STEP 1: Drop all dev policies
-- -----------------------------------------------------------------------------

-- Core tables
DROP POLICY IF EXISTS "dev_workplaces_all" ON octupost.workplaces;
DROP POLICY IF EXISTS "dev_workplace_members_all" ON octupost.workplace_members;
DROP POLICY IF EXISTS "dev_projects_all" ON octupost.projects;
DROP POLICY IF EXISTS "dev_workplace_projects_all" ON octupost.workplace_projects;
DROP POLICY IF EXISTS "dev_user_profiles_all" ON octupost.user_profiles;
DROP POLICY IF EXISTS "dev_assets_all" ON octupost.assets;
DROP POLICY IF EXISTS "dev_project_assets_all" ON octupost.project_assets;
DROP POLICY IF EXISTS "dev_workplace_assets_all" ON octupost.workplace_assets;

-- Additional tables with dev policies
DROP POLICY IF EXISTS "dev_agent_paused_runs_all" ON octupost.agent_paused_runs;
DROP POLICY IF EXISTS "dev_api_keys_all" ON octupost.api_keys;
DROP POLICY IF EXISTS "dev_jobs_all" ON octupost.jobs;
DROP POLICY IF EXISTS "dev_project_scenes_all" ON octupost.project_scenes;
DROP POLICY IF EXISTS "dev_insert_rendered_videos" ON octupost.rendered_videos;
DROP POLICY IF EXISTS "dev_update_rendered_videos" ON octupost.rendered_videos;
DROP POLICY IF EXISTS "dev_select_rendered_videos" ON octupost.rendered_videos;
DROP POLICY IF EXISTS "dev_delete_rendered_videos" ON octupost.rendered_videos;

-- -----------------------------------------------------------------------------
-- STEP 2: user_profiles - Users can only access their own profile
-- -----------------------------------------------------------------------------

CREATE POLICY "user_profiles_select_own" ON octupost.user_profiles
  FOR SELECT TO authenticated
  USING (user_id = auth.uid());

CREATE POLICY "user_profiles_insert_own" ON octupost.user_profiles
  FOR INSERT TO authenticated
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "user_profiles_update_own" ON octupost.user_profiles
  FOR UPDATE TO authenticated
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- -----------------------------------------------------------------------------
-- STEP 3: workplaces - Users can see workplaces they are members of
-- -----------------------------------------------------------------------------

CREATE POLICY "workplaces_select_member" ON octupost.workplaces
  FOR SELECT TO authenticated
  USING (
    id IN (
      SELECT workplace_id FROM octupost.workplace_members
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "workplaces_insert_authenticated" ON octupost.workplaces
  FOR INSERT TO authenticated
  WITH CHECK (true);

CREATE POLICY "workplaces_update_admin" ON octupost.workplaces
  FOR UPDATE TO authenticated
  USING (
    id IN (
      SELECT workplace_id FROM octupost.workplace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );

CREATE POLICY "workplaces_delete_owner" ON octupost.workplaces
  FOR DELETE TO authenticated
  USING (
    id IN (
      SELECT workplace_id FROM octupost.workplace_members
      WHERE user_id = auth.uid() AND role = 'owner'
    )
  );

-- -----------------------------------------------------------------------------
-- STEP 4: workplace_members - Users can see members of their workplaces
-- -----------------------------------------------------------------------------

CREATE POLICY "workplace_members_select" ON octupost.workplace_members
  FOR SELECT TO authenticated
  USING (
    workplace_id IN (
      SELECT workplace_id FROM octupost.workplace_members
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "workplace_members_insert_admin" ON octupost.workplace_members
  FOR INSERT TO authenticated
  WITH CHECK (
    workplace_id IN (
      SELECT workplace_id FROM octupost.workplace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );

CREATE POLICY "workplace_members_delete" ON octupost.workplace_members
  FOR DELETE TO authenticated
  USING (
    user_id = auth.uid() OR
    workplace_id IN (
      SELECT workplace_id FROM octupost.workplace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );

-- -----------------------------------------------------------------------------
-- STEP 5: projects - Users can access projects in their workplaces
-- -----------------------------------------------------------------------------

CREATE POLICY "projects_select_member" ON octupost.projects
  FOR SELECT TO authenticated
  USING (
    id IN (
      SELECT project_id FROM octupost.workplace_projects wp
      JOIN octupost.workplace_members wm ON wp.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid()
    )
  );

CREATE POLICY "projects_insert_member" ON octupost.projects
  FOR INSERT TO authenticated
  WITH CHECK (true);

CREATE POLICY "projects_update_member" ON octupost.projects
  FOR UPDATE TO authenticated
  USING (
    id IN (
      SELECT project_id FROM octupost.workplace_projects wp
      JOIN octupost.workplace_members wm ON wp.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid()
    )
  );

CREATE POLICY "projects_delete_admin" ON octupost.projects
  FOR DELETE TO authenticated
  USING (
    id IN (
      SELECT project_id FROM octupost.workplace_projects wp
      JOIN octupost.workplace_members wm ON wp.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid() AND wm.role IN ('owner', 'admin')
    )
  );

-- -----------------------------------------------------------------------------
-- STEP 6: workplace_projects - Link table access
-- -----------------------------------------------------------------------------

CREATE POLICY "workplace_projects_select" ON octupost.workplace_projects
  FOR SELECT TO authenticated
  USING (
    workplace_id IN (
      SELECT workplace_id FROM octupost.workplace_members
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "workplace_projects_insert" ON octupost.workplace_projects
  FOR INSERT TO authenticated
  WITH CHECK (
    workplace_id IN (
      SELECT workplace_id FROM octupost.workplace_members
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "workplace_projects_delete" ON octupost.workplace_projects
  FOR DELETE TO authenticated
  USING (
    workplace_id IN (
      SELECT workplace_id FROM octupost.workplace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );

-- -----------------------------------------------------------------------------
-- STEP 7: assets - Users can access assets in their workplaces
-- -----------------------------------------------------------------------------

CREATE POLICY "assets_select_member" ON octupost.assets
  FOR SELECT TO authenticated
  USING (
    id IN (
      SELECT asset_id FROM octupost.workplace_assets wa
      JOIN octupost.workplace_members wm ON wa.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid()
    )
  );

CREATE POLICY "assets_insert_member" ON octupost.assets
  FOR INSERT TO authenticated
  WITH CHECK (true);

CREATE POLICY "assets_update_member" ON octupost.assets
  FOR UPDATE TO authenticated
  USING (
    id IN (
      SELECT asset_id FROM octupost.workplace_assets wa
      JOIN octupost.workplace_members wm ON wa.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid()
    )
  );

CREATE POLICY "assets_delete_admin" ON octupost.assets
  FOR DELETE TO authenticated
  USING (
    id IN (
      SELECT asset_id FROM octupost.workplace_assets wa
      JOIN octupost.workplace_members wm ON wa.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid() AND wm.role IN ('owner', 'admin')
    )
  );

-- -----------------------------------------------------------------------------
-- STEP 8: project_assets - Link table access
-- -----------------------------------------------------------------------------

CREATE POLICY "project_assets_select" ON octupost.project_assets
  FOR SELECT TO authenticated
  USING (
    project_id IN (
      SELECT project_id FROM octupost.workplace_projects wp
      JOIN octupost.workplace_members wm ON wp.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid()
    )
  );

CREATE POLICY "project_assets_insert" ON octupost.project_assets
  FOR INSERT TO authenticated
  WITH CHECK (
    project_id IN (
      SELECT project_id FROM octupost.workplace_projects wp
      JOIN octupost.workplace_members wm ON wp.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid()
    )
  );

CREATE POLICY "project_assets_delete" ON octupost.project_assets
  FOR DELETE TO authenticated
  USING (
    project_id IN (
      SELECT project_id FROM octupost.workplace_projects wp
      JOIN octupost.workplace_members wm ON wp.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid() AND wm.role IN ('owner', 'admin')
    )
  );

-- -----------------------------------------------------------------------------
-- STEP 9: workplace_assets - Link table access
-- -----------------------------------------------------------------------------

CREATE POLICY "workplace_assets_select" ON octupost.workplace_assets
  FOR SELECT TO authenticated
  USING (
    workplace_id IN (
      SELECT workplace_id FROM octupost.workplace_members
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "workplace_assets_insert" ON octupost.workplace_assets
  FOR INSERT TO authenticated
  WITH CHECK (
    workplace_id IN (
      SELECT workplace_id FROM octupost.workplace_members
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "workplace_assets_delete" ON octupost.workplace_assets
  FOR DELETE TO authenticated
  USING (
    workplace_id IN (
      SELECT workplace_id FROM octupost.workplace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );

-- -----------------------------------------------------------------------------
-- STEP 10: jobs - Users can access jobs for their projects
-- -----------------------------------------------------------------------------

CREATE POLICY "jobs_select_member" ON octupost.jobs
  FOR SELECT TO authenticated
  USING (
    project_id IN (
      SELECT project_id FROM octupost.workplace_projects wp
      JOIN octupost.workplace_members wm ON wp.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid()
    )
  );

CREATE POLICY "jobs_insert_member" ON octupost.jobs
  FOR INSERT TO authenticated
  WITH CHECK (
    project_id IN (
      SELECT project_id FROM octupost.workplace_projects wp
      JOIN octupost.workplace_members wm ON wp.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid()
    )
  );

CREATE POLICY "jobs_update_member" ON octupost.jobs
  FOR UPDATE TO authenticated
  USING (
    project_id IN (
      SELECT project_id FROM octupost.workplace_projects wp
      JOIN octupost.workplace_members wm ON wp.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid()
    )
  );

-- -----------------------------------------------------------------------------
-- STEP 11: project_scenes - Users can access scenes for their projects
-- -----------------------------------------------------------------------------

CREATE POLICY "project_scenes_select_member" ON octupost.project_scenes
  FOR SELECT TO authenticated
  USING (
    project_id IN (
      SELECT project_id FROM octupost.workplace_projects wp
      JOIN octupost.workplace_members wm ON wp.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid()
    )
  );

CREATE POLICY "project_scenes_insert_member" ON octupost.project_scenes
  FOR INSERT TO authenticated
  WITH CHECK (
    project_id IN (
      SELECT project_id FROM octupost.workplace_projects wp
      JOIN octupost.workplace_members wm ON wp.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid()
    )
  );

CREATE POLICY "project_scenes_update_member" ON octupost.project_scenes
  FOR UPDATE TO authenticated
  USING (
    project_id IN (
      SELECT project_id FROM octupost.workplace_projects wp
      JOIN octupost.workplace_members wm ON wp.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid()
    )
  );

CREATE POLICY "project_scenes_delete_admin" ON octupost.project_scenes
  FOR DELETE TO authenticated
  USING (
    project_id IN (
      SELECT project_id FROM octupost.workplace_projects wp
      JOIN octupost.workplace_members wm ON wp.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid() AND wm.role IN ('owner', 'admin')
    )
  );

-- -----------------------------------------------------------------------------
-- STEP 12: rendered_videos - Users can access rendered videos for their projects
-- -----------------------------------------------------------------------------

CREATE POLICY "rendered_videos_select_member" ON octupost.rendered_videos
  FOR SELECT TO authenticated
  USING (
    project_id IN (
      SELECT project_id FROM octupost.workplace_projects wp
      JOIN octupost.workplace_members wm ON wp.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid()
    )
  );

CREATE POLICY "rendered_videos_insert_member" ON octupost.rendered_videos
  FOR INSERT TO authenticated
  WITH CHECK (
    project_id IN (
      SELECT project_id FROM octupost.workplace_projects wp
      JOIN octupost.workplace_members wm ON wp.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid()
    )
  );

CREATE POLICY "rendered_videos_update_member" ON octupost.rendered_videos
  FOR UPDATE TO authenticated
  USING (
    project_id IN (
      SELECT project_id FROM octupost.workplace_projects wp
      JOIN octupost.workplace_members wm ON wp.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid()
    )
  );

CREATE POLICY "rendered_videos_delete_admin" ON octupost.rendered_videos
  FOR DELETE TO authenticated
  USING (
    project_id IN (
      SELECT project_id FROM octupost.workplace_projects wp
      JOIN octupost.workplace_members wm ON wp.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid() AND wm.role IN ('owner', 'admin')
    )
  );

-- -----------------------------------------------------------------------------
-- STEP 13: agent_paused_runs - Users can access paused runs for their projects
-- -----------------------------------------------------------------------------

CREATE POLICY "agent_paused_runs_select_member" ON octupost.agent_paused_runs
  FOR SELECT TO authenticated
  USING (
    project_id IN (
      SELECT project_id FROM octupost.workplace_projects wp
      JOIN octupost.workplace_members wm ON wp.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid()
    )
  );

CREATE POLICY "agent_paused_runs_insert_member" ON octupost.agent_paused_runs
  FOR INSERT TO authenticated
  WITH CHECK (
    project_id IN (
      SELECT project_id FROM octupost.workplace_projects wp
      JOIN octupost.workplace_members wm ON wp.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid()
    )
  );

CREATE POLICY "agent_paused_runs_update_member" ON octupost.agent_paused_runs
  FOR UPDATE TO authenticated
  USING (
    project_id IN (
      SELECT project_id FROM octupost.workplace_projects wp
      JOIN octupost.workplace_members wm ON wp.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid()
    )
  );

CREATE POLICY "agent_paused_runs_delete_member" ON octupost.agent_paused_runs
  FOR DELETE TO authenticated
  USING (
    project_id IN (
      SELECT project_id FROM octupost.workplace_projects wp
      JOIN octupost.workplace_members wm ON wp.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid()
    )
  );

-- -----------------------------------------------------------------------------
-- STEP 14: api_keys - Users can only access their own API keys
-- -----------------------------------------------------------------------------

CREATE POLICY "api_keys_select_own" ON octupost.api_keys
  FOR SELECT TO authenticated
  USING (user_id = auth.uid());

CREATE POLICY "api_keys_insert_own" ON octupost.api_keys
  FOR INSERT TO authenticated
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "api_keys_update_own" ON octupost.api_keys
  FOR UPDATE TO authenticated
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "api_keys_delete_own" ON octupost.api_keys
  FOR DELETE TO authenticated
  USING (user_id = auth.uid());

COMMIT;
