-- Update MMAudio models to show in Sound Effect tab
--
-- This migration ensures video-to-audio models (MMAudio, etc.) have 
-- output_asset_type = 'soundtrack' so they appear in the Sound Effect tab
-- while keeping output_media_type = 'video' for correct asset storage.

BEGIN;

-- Update all video-to-audio models to have output_asset_type = 'soundtrack'
-- This ensures they appear in the Sound Effect tab in the composer
UPDATE octupost.model_configs
SET output_asset_type = 'soundtrack'
WHERE model_type = 'video-to-audio';

-- Explicitly update mmaudio-v2 endpoints if they exist
UPDATE octupost.model_configs
SET output_asset_type = 'soundtrack'
WHERE endpoint LIKE '%mmaudio%';

COMMIT;




