-- Phase 3: Agent Video Creation - Project Settings for Agent
-- Adds video_type, brand_kit_id, and selected_models to projects table

BEGIN;

-- =============================================================================
-- Add video_type column
-- =============================================================================
ALTER TABLE octupost.projects
ADD COLUMN IF NOT EXISTS video_type TEXT;

COMMENT ON COLUMN octupost.projects.video_type IS
  'Video type for agent workflow: product, avatar, saas, etc. Extensible text field.';

-- =============================================================================
-- Add brand_kit_id column with FK to brand_kits
-- =============================================================================
ALTER TABLE octupost.projects
ADD COLUMN IF NOT EXISTS brand_kit_id UUID REFERENCES octupost.brand_kits(id) ON DELETE SET NULL;

COMMENT ON COLUMN octupost.projects.brand_kit_id IS
  'Selected brand kit for this project. Agent uses brand colors, fonts, logos, and product images.';

-- =============================================================================
-- Add selected_models column (JSONB)
-- =============================================================================
ALTER TABLE octupost.projects
ADD COLUMN IF NOT EXISTS selected_models JSONB DEFAULT '{}';

COMMENT ON COLUMN octupost.projects.selected_models IS
  'Model selections for generation: {video, image, tts, voice_id, avatar, music, sound_effects}';

-- =============================================================================
-- Add project_images column for additional images beyond brand kit
-- =============================================================================
ALTER TABLE octupost.projects
ADD COLUMN IF NOT EXISTS project_images JSONB DEFAULT '[]';

COMMENT ON COLUMN octupost.projects.project_images IS
  'Project-specific images beyond brand kit: [{id, url, name, description}]';

-- =============================================================================
-- Add default_voice_id to brand_kits (used as default when creating new project)
-- =============================================================================
ALTER TABLE octupost.brand_kits
ADD COLUMN IF NOT EXISTS default_voice_id TEXT;

COMMENT ON COLUMN octupost.brand_kits.default_voice_id IS
  'Default ElevenLabs voice ID for new projects using this brand kit';

-- =============================================================================
-- Add agent_memory to brand_kits for brand-level AI preferences
-- =============================================================================
ALTER TABLE octupost.brand_kits
ADD COLUMN IF NOT EXISTS agent_memory JSONB DEFAULT '[]';

COMMENT ON COLUMN octupost.brand_kits.agent_memory IS
  'Agent-learned brand preferences: [{memory, created_at, created_by}]';

-- =============================================================================
-- Indexes for common queries
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_projects_brand_kit
  ON octupost.projects(brand_kit_id)
  WHERE brand_kit_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_projects_video_type
  ON octupost.projects(video_type)
  WHERE video_type IS NOT NULL;

COMMIT;
