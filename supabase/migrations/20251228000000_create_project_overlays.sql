-- Create project_overlays table for real-time AI agent collaboration
-- This normalized table allows granular real-time updates per overlay
-- Enables AI agents to edit video projects with changes appearing instantly in the UI

BEGIN;

-- =============================================================================
-- Project Overlays Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS octupost.project_overlays (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES octupost.projects(id) ON DELETE CASCADE,

  -- Overlay identity (matches editor's internal ID)
  overlay_id INTEGER NOT NULL,

  -- Type: 'video' | 'audio' | 'image' | 'text'
  type TEXT NOT NULL CHECK (type IN ('video', 'audio', 'image', 'text')),

  -- Timeline positioning
  row_index INTEGER NOT NULL,
  from_frame INTEGER NOT NULL,
  duration_frames INTEGER NOT NULL,

  -- Canvas positioning
  left_position FLOAT NOT NULL,
  top_position FLOAT NOT NULL,
  width FLOAT NOT NULL,
  height FLOAT NOT NULL,
  rotation FLOAT NOT NULL DEFAULT 0,

  -- Type-specific data (styles, content, src, etc.)
  data JSONB NOT NULL DEFAULT '{}',

  -- Locking for AI edits: null = available, 'ai' = AI is editing
  editing_by TEXT,

  -- Timestamps
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- Constraints
  UNIQUE(project_id, overlay_id)
);

-- =============================================================================
-- Indexes
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_project_overlays_project_id
  ON octupost.project_overlays(project_id);

CREATE INDEX IF NOT EXISTS idx_project_overlays_editing_by
  ON octupost.project_overlays(editing_by)
  WHERE editing_by IS NOT NULL;

-- =============================================================================
-- Updated_at Trigger
-- =============================================================================
CREATE OR REPLACE FUNCTION octupost.update_project_overlays_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER project_overlays_updated_at_trigger
  BEFORE UPDATE ON octupost.project_overlays
  FOR EACH ROW
  EXECUTE FUNCTION octupost.update_project_overlays_updated_at();

-- =============================================================================
-- RLS Policies
-- =============================================================================
ALTER TABLE octupost.project_overlays ENABLE ROW LEVEL SECURITY;

-- Dev policy for development (permissive)
CREATE POLICY "dev_project_overlays_all"
  ON octupost.project_overlays FOR ALL TO authenticated
  USING (true)
  WITH CHECK (true);

-- =============================================================================
-- Enable Realtime
-- =============================================================================
ALTER PUBLICATION supabase_realtime ADD TABLE octupost.project_overlays;

-- =============================================================================
-- Comments
-- =============================================================================
COMMENT ON TABLE octupost.project_overlays IS
  'Normalized overlay storage for real-time AI agent collaboration. Supports Realtime subscriptions for instant UI updates.';

COMMENT ON COLUMN octupost.project_overlays.overlay_id IS
  'Editor internal ID (integer), unique per project';

COMMENT ON COLUMN octupost.project_overlays.type IS
  'Overlay type: video, audio, image, text';

COMMENT ON COLUMN octupost.project_overlays.data IS
  'Type-specific properties: src, content, styles, greenscreen config, etc.';

COMMENT ON COLUMN octupost.project_overlays.editing_by IS
  'Lock indicator: null = available, ai = AI is editing';

COMMIT;
