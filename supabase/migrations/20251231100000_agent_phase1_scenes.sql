-- Phase 1: Agent Video Creation - project_scenes table
-- Creates scene structure for agent-based video generation

BEGIN;

-- =============================================================================
-- Project Scenes Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS octupost.project_scenes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES octupost.projects(id) ON DELETE CASCADE,

  -- Ordering (with gaps for easy insertion)
  order_index INTEGER NOT NULL,

  -- Scene definition
  name TEXT,                           -- "Hook", "Feature Demo", "CTA"
  description TEXT,                    -- What happens in this scene

  -- Timing (in FRAMES - FPS=30)
  -- NOTE: start_frame is COMPUTED, not stored. Calculated from order_index and previous scene durations.
  duration_frames INTEGER,             -- Target duration in frames

  -- Status
  status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'planned', 'generating', 'complete', 'failed')),

  -- Locking (scene-level) for AI edits
  editing_by TEXT,                     -- null | 'ai' | user_id
  editing_started_at TIMESTAMPTZ,      -- For timeout detection (unlock if stale > 15 min)

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  UNIQUE(project_id, order_index)
);

-- =============================================================================
-- Updated_at Trigger
-- =============================================================================
CREATE OR REPLACE FUNCTION octupost.update_project_scenes_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER project_scenes_updated_at_trigger
  BEFORE UPDATE ON octupost.project_scenes
  FOR EACH ROW
  EXECUTE FUNCTION octupost.update_project_scenes_updated_at();

-- =============================================================================
-- Indexes
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_project_scenes_project_order
  ON octupost.project_scenes(project_id, order_index);

CREATE INDEX IF NOT EXISTS idx_project_scenes_status
  ON octupost.project_scenes(status)
  WHERE status IN ('generating', 'failed');

-- =============================================================================
-- RLS Policies
-- =============================================================================
ALTER TABLE octupost.project_scenes ENABLE ROW LEVEL SECURITY;

-- Dev policy for development (permissive) - matches project_overlays pattern
CREATE POLICY "dev_project_scenes_all"
  ON octupost.project_scenes FOR ALL TO authenticated
  USING (true)
  WITH CHECK (true);

-- =============================================================================
-- Enable Realtime
-- =============================================================================
ALTER PUBLICATION supabase_realtime ADD TABLE octupost.project_scenes;

-- =============================================================================
-- Add scene_id to project_overlays for scene association
-- =============================================================================
ALTER TABLE octupost.project_overlays
ADD COLUMN IF NOT EXISTS scene_id UUID REFERENCES octupost.project_scenes(id) ON DELETE SET NULL;

-- scene_id is NULLABLE:
-- - NULL = project-level overlay (e.g., background music spanning all scenes)
-- - UUID = scene-specific overlay

-- Index for scene queries
CREATE INDEX IF NOT EXISTS idx_overlays_scene
  ON octupost.project_overlays(scene_id)
  WHERE scene_id IS NOT NULL;

-- =============================================================================
-- Add job_id index on project_overlays.data for fast lookup
-- Used by Inngest worker to update overlays when jobs complete
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_overlays_job_id
  ON octupost.project_overlays ((data->>'job_id'))
  WHERE data->>'job_id' IS NOT NULL;

-- =============================================================================
-- Comments
-- =============================================================================
COMMENT ON TABLE octupost.project_scenes IS
  'Scene structure for agent-based video generation. Scenes organize overlays into logical segments with timing.';

COMMENT ON COLUMN octupost.project_scenes.order_index IS
  'Ordering with gaps (10, 20, 30...) for easy insertion between scenes';

COMMENT ON COLUMN octupost.project_scenes.duration_frames IS
  'Target duration in frames (FPS=30). start_frame is computed from order_index and previous durations.';

COMMENT ON COLUMN octupost.project_scenes.status IS
  'Scene status: draft | planned | generating | complete | failed';

COMMENT ON COLUMN octupost.project_scenes.editing_by IS
  'Lock indicator: null = available, ai = AI is editing, user_id = user is editing';

COMMENT ON COLUMN octupost.project_overlays.scene_id IS
  'Scene this overlay belongs to. NULL for project-level overlays (e.g., background music).';

COMMIT;
