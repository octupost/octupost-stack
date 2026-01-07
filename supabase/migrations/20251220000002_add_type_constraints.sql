-- Add CHECK constraints for media_type and asset_type columns
--
-- This migration ensures consistency between:
-- - assets.media_type / assets.asset_type
-- - model_configs.output_media_type / model_configs.output_asset_type
--
-- Valid values:
-- - media_type / output_media_type: image, video, audio
-- - asset_type / output_asset_type: image, video, avatar_video, avatar_image, speech, music, soundtrack

BEGIN;

-- =============================================================================
-- Step 1: Add CHECK constraint for model_configs.output_media_type
-- =============================================================================

ALTER TABLE octupost.model_configs
ADD CONSTRAINT model_configs_output_media_type_check 
CHECK (output_media_type IN ('image', 'video', 'audio'));

-- =============================================================================
-- Step 2: Add CHECK constraint for assets.media_type
-- =============================================================================

ALTER TABLE octupost.assets
ADD CONSTRAINT assets_media_type_check 
CHECK (media_type IN ('image', 'video', 'audio'));

-- =============================================================================
-- Step 3: Add CHECK constraint for assets.asset_type
-- =============================================================================

ALTER TABLE octupost.assets
ADD CONSTRAINT assets_asset_type_check 
CHECK (asset_type IN ('image', 'video', 'avatar_video', 'avatar_image', 'speech', 'music', 'soundtrack'));

COMMIT;




