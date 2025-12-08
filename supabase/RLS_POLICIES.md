# RLS Policies Tracking

> **Current Status: DEVELOPMENT MODE**  
> All tables have permissive `dev_*` policies. These MUST be replaced before production.

---

## Pre-Production Checklist

Before deploying to production, complete these steps:

- [ ] Review access patterns for each table
- [ ] Define proper policies for each table (see templates below)
- [ ] Create production migration to drop dev policies and add restrictive ones
- [ ] Test all features with restrictive policies enabled
- [ ] Run security advisor check in Supabase Dashboard

---

## Current Policy Status

| Table | Schema | RLS Enabled | Current Policy | Production Ready |
|-------|--------|-------------|----------------|------------------|
| workplaces | octupost | ✅ | `dev_workplaces_all` | ❌ |
| workplace_members | octupost | ✅ | `dev_workplace_members_all` | ❌ |
| projects | octupost | ✅ | `dev_projects_all` | ❌ |
| workplace_projects | octupost | ✅ | `dev_workplace_projects_all` | ❌ |
| user_profiles | octupost | ✅ | `dev_user_profiles_all` | ❌ |
| assets | octupost | ✅ | `dev_assets_all` | ❌ |
| project_assets | octupost | ✅ | `dev_project_assets_all` | ❌ |
| workplace_assets | octupost | ✅ | `dev_workplace_assets_all` | ❌ |

---

## Production Migration Template

When ready for production, create a new migration file (e.g., `20251231_production_rls.sql`) with the following structure:

```sql
-- =============================================================================
-- PRODUCTION RLS POLICIES
-- =============================================================================
-- Replaces dev policies with proper restrictive policies
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
-- STEP 1: Drop all dev policies
-- -----------------------------------------------------------------------------

DROP POLICY IF EXISTS "dev_workplaces_all" ON octupost.workplaces;
DROP POLICY IF EXISTS "dev_workplace_members_all" ON octupost.workplace_members;
DROP POLICY IF EXISTS "dev_projects_all" ON octupost.projects;
DROP POLICY IF EXISTS "dev_workplace_projects_all" ON octupost.workplace_projects;
DROP POLICY IF EXISTS "dev_user_profiles_all" ON octupost.user_profiles;
DROP POLICY IF EXISTS "dev_assets_all" ON octupost.assets;
DROP POLICY IF EXISTS "dev_project_assets_all" ON octupost.project_assets;
DROP POLICY IF EXISTS "dev_workplace_assets_all" ON octupost.workplace_assets;

-- -----------------------------------------------------------------------------
-- STEP 2: Create production policies
-- -----------------------------------------------------------------------------

-- Add your production policies below...

COMMIT;
```

---

## Production Policy Templates

### user_profiles
Users should only access their own profile.

```sql
-- SELECT: Users can view their own profile
CREATE POLICY "user_profiles_select_own" ON octupost.user_profiles
  FOR SELECT TO authenticated
  USING (user_id = auth.uid());

-- INSERT: Users can create their own profile
CREATE POLICY "user_profiles_insert_own" ON octupost.user_profiles
  FOR INSERT TO authenticated
  WITH CHECK (user_id = auth.uid());

-- UPDATE: Users can update their own profile
CREATE POLICY "user_profiles_update_own" ON octupost.user_profiles
  FOR UPDATE TO authenticated
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());
```

### workplaces
Users can only see workplaces they are members of.

```sql
-- SELECT: Users can view workplaces they belong to
CREATE POLICY "workplaces_select_member" ON octupost.workplaces
  FOR SELECT TO authenticated
  USING (
    id IN (
      SELECT workplace_id FROM octupost.workplace_members
      WHERE user_id = auth.uid()
    )
  );

-- INSERT: Any authenticated user can create a workplace
CREATE POLICY "workplaces_insert_authenticated" ON octupost.workplaces
  FOR INSERT TO authenticated
  WITH CHECK (true);

-- UPDATE: Only workspace owners/admins can update
CREATE POLICY "workplaces_update_admin" ON octupost.workplaces
  FOR UPDATE TO authenticated
  USING (
    id IN (
      SELECT workplace_id FROM octupost.workplace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );

-- DELETE: Only workspace owners can delete
CREATE POLICY "workplaces_delete_owner" ON octupost.workplaces
  FOR DELETE TO authenticated
  USING (
    id IN (
      SELECT workplace_id FROM octupost.workplace_members
      WHERE user_id = auth.uid() AND role = 'owner'
    )
  );
```

### workplace_members
Users can see members of workplaces they belong to.

```sql
-- SELECT: Users can view members of their workplaces
CREATE POLICY "workplace_members_select" ON octupost.workplace_members
  FOR SELECT TO authenticated
  USING (
    workplace_id IN (
      SELECT workplace_id FROM octupost.workplace_members
      WHERE user_id = auth.uid()
    )
  );

-- INSERT: Only admins/owners can add members
CREATE POLICY "workplace_members_insert_admin" ON octupost.workplace_members
  FOR INSERT TO authenticated
  WITH CHECK (
    workplace_id IN (
      SELECT workplace_id FROM octupost.workplace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );

-- DELETE: Admins can remove members, users can remove themselves
CREATE POLICY "workplace_members_delete" ON octupost.workplace_members
  FOR DELETE TO authenticated
  USING (
    user_id = auth.uid() OR
    workplace_id IN (
      SELECT workplace_id FROM octupost.workplace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );
```

### projects
Users can access projects in their workplaces.

```sql
-- SELECT: Users can view projects in their workplaces
CREATE POLICY "projects_select_member" ON octupost.projects
  FOR SELECT TO authenticated
  USING (
    id IN (
      SELECT project_id FROM octupost.workplace_projects wp
      JOIN octupost.workplace_members wm ON wp.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid()
    )
  );

-- INSERT: Members can create projects
CREATE POLICY "projects_insert_member" ON octupost.projects
  FOR INSERT TO authenticated
  WITH CHECK (true);

-- UPDATE: Members can update projects in their workplaces
CREATE POLICY "projects_update_member" ON octupost.projects
  FOR UPDATE TO authenticated
  USING (
    id IN (
      SELECT project_id FROM octupost.workplace_projects wp
      JOIN octupost.workplace_members wm ON wp.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid()
    )
  );

-- DELETE: Only admins/owners can delete projects
CREATE POLICY "projects_delete_admin" ON octupost.projects
  FOR DELETE TO authenticated
  USING (
    id IN (
      SELECT project_id FROM octupost.workplace_projects wp
      JOIN octupost.workplace_members wm ON wp.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid() AND wm.role IN ('owner', 'admin')
    )
  );
```

### workplace_projects
Link table - access based on workspace membership.

```sql
-- SELECT: Users can view project-workspace links for their workplaces
CREATE POLICY "workplace_projects_select" ON octupost.workplace_projects
  FOR SELECT TO authenticated
  USING (
    workplace_id IN (
      SELECT workplace_id FROM octupost.workplace_members
      WHERE user_id = auth.uid()
    )
  );

-- INSERT: Members can link projects to their workplaces
CREATE POLICY "workplace_projects_insert" ON octupost.workplace_projects
  FOR INSERT TO authenticated
  WITH CHECK (
    workplace_id IN (
      SELECT workplace_id FROM octupost.workplace_members
      WHERE user_id = auth.uid()
    )
  );

-- DELETE: Admins can unlink projects
CREATE POLICY "workplace_projects_delete" ON octupost.workplace_projects
  FOR DELETE TO authenticated
  USING (
    workplace_id IN (
      SELECT workplace_id FROM octupost.workplace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );
```

### assets
Users can access assets in their workplaces.

```sql
-- SELECT: Users can view assets in their workplaces
CREATE POLICY "assets_select_member" ON octupost.assets
  FOR SELECT TO authenticated
  USING (
    id IN (
      SELECT asset_id FROM octupost.workplace_assets wa
      JOIN octupost.workplace_members wm ON wa.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid()
    )
  );

-- INSERT: Members can upload assets
CREATE POLICY "assets_insert_member" ON octupost.assets
  FOR INSERT TO authenticated
  WITH CHECK (true);

-- UPDATE: Members can update assets in their workplaces
CREATE POLICY "assets_update_member" ON octupost.assets
  FOR UPDATE TO authenticated
  USING (
    id IN (
      SELECT asset_id FROM octupost.workplace_assets wa
      JOIN octupost.workplace_members wm ON wa.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid()
    )
  );

-- DELETE: Admins can delete assets
CREATE POLICY "assets_delete_admin" ON octupost.assets
  FOR DELETE TO authenticated
  USING (
    id IN (
      SELECT asset_id FROM octupost.workplace_assets wa
      JOIN octupost.workplace_members wm ON wa.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid() AND wm.role IN ('owner', 'admin')
    )
  );
```

### project_assets & workplace_assets
Link tables - similar pattern to workplace_projects.

```sql
-- project_assets: SELECT based on project access
CREATE POLICY "project_assets_select" ON octupost.project_assets
  FOR SELECT TO authenticated
  USING (
    project_id IN (
      SELECT project_id FROM octupost.workplace_projects wp
      JOIN octupost.workplace_members wm ON wp.workplace_id = wm.workplace_id
      WHERE wm.user_id = auth.uid()
    )
  );

-- workplace_assets: SELECT based on workspace membership
CREATE POLICY "workplace_assets_select" ON octupost.workplace_assets
  FOR SELECT TO authenticated
  USING (
    workplace_id IN (
      SELECT workplace_id FROM octupost.workplace_members
      WHERE user_id = auth.uid()
    )
  );
```

---

## Quick Reference: Find Dev Policies

Run this query to see all dev policies currently in the database:

```sql
SELECT schemaname, tablename, policyname, cmd, qual
FROM pg_policies 
WHERE policyname LIKE 'dev_%'
ORDER BY tablename;
```

---

## Notes

- The templates above are starting points. Adjust based on your actual access requirements.
- Consider adding policies for the `anon` role if you have public-facing features.
- Use Supabase Dashboard > Database > Policies to visually manage policies.
- Run `SELECT * FROM pg_policies WHERE schemaname = 'octupost';` to see all active policies.

