-- Drop React Video Editor tables and columns
-- These tables/columns were used by the old React Video Editor which is being removed
-- We're starting fresh with a new video editing approach

-- Remove overlays column from projects table
ALTER TABLE octupost.projects DROP COLUMN IF EXISTS overlays;

-- Drop tables in order of dependencies (children first)

-- Drop project_tasks (depends on project_video_plans, project_scenes)
DROP TABLE IF EXISTS octupost.project_tasks CASCADE;

-- Drop project_video_plans (depends on projects)
DROP TABLE IF EXISTS octupost.project_video_plans CASCADE;

-- Drop project_overlays (depends on project_scenes, projects)
DROP TABLE IF EXISTS octupost.project_overlays CASCADE;

-- Drop project_scenes (depends on projects)
DROP TABLE IF EXISTS octupost.project_scenes CASCADE;

-- Drop video_templates (depends on workplaces, users)
DROP TABLE IF EXISTS octupost.video_templates CASCADE;

-- Drop overlay_style_templates (depends on brand_kits)
DROP TABLE IF EXISTS octupost.overlay_style_templates CASCADE;

-- Drop agent_paused_runs (depends on projects)
DROP TABLE IF EXISTS octupost.agent_paused_runs CASCADE;

-- Remove realtime publications for dropped tables
DO $$
BEGIN
    -- These may fail if tables weren't in the publication, that's ok
    BEGIN
        ALTER PUBLICATION supabase_realtime DROP TABLE IF EXISTS octupost.project_overlays;
    EXCEPTION WHEN OTHERS THEN NULL;
    END;
    BEGIN
        ALTER PUBLICATION supabase_realtime DROP TABLE IF EXISTS octupost.project_scenes;
    EXCEPTION WHEN OTHERS THEN NULL;
    END;
    BEGIN
        ALTER PUBLICATION supabase_realtime DROP TABLE IF EXISTS octupost.project_video_plans;
    EXCEPTION WHEN OTHERS THEN NULL;
    END;
    BEGIN
        ALTER PUBLICATION supabase_realtime DROP TABLE IF EXISTS octupost.project_tasks;
    EXCEPTION WHEN OTHERS THEN NULL;
    END;
END $$;
