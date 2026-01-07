-- Rename soundtrack to soundeffect in asset_type constraints
-- This standardizes the naming convention between the database and frontend TypeScript

BEGIN;

-- Step 1: Update existing assets with 'soundtrack' to 'soundeffect'
UPDATE octupost.assets
SET asset_type = 'soundeffect'
WHERE asset_type = 'soundtrack';

-- Step 2: Update existing model_configs with 'soundtrack' to 'soundeffect'
UPDATE octupost.model_configs
SET output_asset_type = 'soundeffect'
WHERE output_asset_type = 'soundtrack';

-- Step 3: Drop old constraint and add new one for assets
ALTER TABLE octupost.assets
DROP CONSTRAINT IF EXISTS assets_asset_type_check;

ALTER TABLE octupost.assets
ADD CONSTRAINT assets_asset_type_check
CHECK (asset_type IN ('image', 'video', 'avatar_video', 'avatar_image', 'speech', 'music', 'soundeffect'));

-- Step 4: Drop old constraint and add new one for model_configs (if exists)
ALTER TABLE octupost.model_configs
DROP CONSTRAINT IF EXISTS model_configs_output_asset_type_check;

ALTER TABLE octupost.model_configs
ADD CONSTRAINT model_configs_output_asset_type_check
CHECK (output_asset_type IN ('image', 'video', 'avatar_video', 'avatar_image', 'speech', 'music', 'soundeffect'));

COMMIT;
