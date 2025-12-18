-- Raw Parameters Refactor Migration
-- 
-- This migration restructures model_configs to cleanly separate:
-- 1. raw_parameters: Untouched FAL OpenAPI schema (read-only reference)
-- 2. parameters: Admin customizations (labelKey, displayMode, default)
--
-- Dropped columns (data consolidated into parameters):
-- - inline_params (replaced by displayMode: "inline")
-- - hidden_params (replaced by displayMode: "hidden")
-- - param_mappings (removed - key IS the API mapping)
-- - param_defaults (moved into parameters.default)

-- Step 1: Add raw_parameters column
ALTER TABLE octupost.model_configs 
ADD COLUMN IF NOT EXISTS raw_parameters JSONB DEFAULT '[]'::jsonb;

-- Step 2: Drop deprecated columns
ALTER TABLE octupost.model_configs 
DROP COLUMN IF EXISTS inline_params;

ALTER TABLE octupost.model_configs 
DROP COLUMN IF EXISTS hidden_params;

ALTER TABLE octupost.model_configs 
DROP COLUMN IF EXISTS param_mappings;

ALTER TABLE octupost.model_configs 
DROP COLUMN IF EXISTS param_defaults;

-- Step 3: Update table comment
COMMENT ON TABLE octupost.model_configs IS 
'Model configurations for FAL AI models.

Column Structure:
- raw_parameters: Original FAL OpenAPI schema (read-only reference for admins)
  Contains: key, type, required, enum, minimum, maximum, description, format
  
- parameters: Admin-customized parameter definitions
  Contains: key, type, labelKey, displayMode, default, enum, min, max, step, etc.
  
The labelKey suffix determines the component type:
_textarea, _input, _toggle, _dropdown, _slider, _json, _image, _video, _audio

displayMode options: source, primary, inline, menu, hidden';

-- Step 4: Add column comment for raw_parameters
COMMENT ON COLUMN octupost.model_configs.raw_parameters IS 
'Original FAL OpenAPI parameter schema. Read-only reference showing API constraints.
Updated automatically when syncing from FAL. Admins can reference this to see
original type, enum options, min/max values, descriptions, etc.';

-- Step 5: Update parameters column comment
COMMENT ON COLUMN octupost.model_configs.parameters IS 
'Admin-customized parameter definitions. Each parameter has:
- key: Parameter name (matches raw_parameters key, IS the API mapping)
- labelKey: Registry lookup for component/icon (e.g., "prompt_textarea")
- displayMode: Where to show in UI (source, primary, inline, menu, hidden)
- default: Admin-defined default value
- type, enum, min, max, step: Schema info (synced from FAL, can be overridden)';

