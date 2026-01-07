-- Asset Type Refactor Migration
--
-- This migration:
-- 1. Renames assets.type column to assets.asset_type
-- 2. Adds output_asset_type column to model_configs
-- 3. Backfills model_configs.output_asset_type based on model_type

BEGIN;

-- =============================================================================
-- Step 1: Rename assets.type to assets.asset_type
-- =============================================================================

ALTER TABLE octupost.assets 
RENAME COLUMN type TO asset_type;

-- Update column comment
COMMENT ON COLUMN octupost.assets.asset_type IS 
'Specific asset type for categorization: image, video, avatar_video, avatar_image, speech, music, soundtrack';

-- =============================================================================
-- Step 2: Add output_asset_type column to model_configs
-- =============================================================================

ALTER TABLE octupost.model_configs 
ADD COLUMN IF NOT EXISTS output_asset_type TEXT;

-- Add column comment
COMMENT ON COLUMN octupost.model_configs.output_asset_type IS 
'The specific asset type produced by this model. Used to categorize generated assets.
Valid values: image, video, avatar_video, avatar_image, speech, music, soundtrack';

-- =============================================================================
-- Step 3: Backfill output_asset_type based on model_type
-- =============================================================================

UPDATE octupost.model_configs
SET output_asset_type = CASE model_type
    WHEN 'text-to-image' THEN 'image'
    WHEN 'text-to-video' THEN 'video'
    WHEN 'image-to-video' THEN 'video'
    WHEN 'text-to-speech' THEN 'speech'
    WHEN 'text-to-audio' THEN 'soundtrack'
    WHEN 'text-to-music' THEN 'music'
    WHEN 'video-to-audio' THEN 'soundtrack'
    WHEN 'avatar' THEN 'avatar_video'
    WHEN 'reference-to-video' THEN 'video'
    WHEN 'first-last-frame-to-video' THEN 'video'
    WHEN 'retake' THEN 'video'
    WHEN 'lip-sync' THEN 'avatar_video'
    ELSE 'video'  -- Default fallback
END
WHERE output_asset_type IS NULL;

-- =============================================================================
-- Step 4: Add NOT NULL constraint after backfill
-- =============================================================================

ALTER TABLE octupost.model_configs 
ALTER COLUMN output_asset_type SET NOT NULL;

-- Add CHECK constraint for valid values
ALTER TABLE octupost.model_configs
ADD CONSTRAINT model_configs_output_asset_type_check 
CHECK (output_asset_type IN ('image', 'video', 'avatar_video', 'avatar_image', 'speech', 'music', 'soundtrack'));

COMMIT;




