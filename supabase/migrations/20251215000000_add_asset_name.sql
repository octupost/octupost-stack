-- Add name column to assets table for user-friendly asset identification
-- Names are auto-generated on creation but can be edited by users

BEGIN;

-- Add nullable name column
ALTER TABLE octupost.assets 
ADD COLUMN IF NOT EXISTS name TEXT;

-- Add comment for documentation
COMMENT ON COLUMN octupost.assets.name IS 'User-friendly display name for the asset. Auto-generated on creation, editable by user.';

COMMIT;
