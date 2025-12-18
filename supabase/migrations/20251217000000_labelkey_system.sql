-- LabelKey System Migration
-- 
-- This migration documents the new parameter structure using labelKeys.
-- The actual data transformation is done via script (migrate-to-label-keys.ts)
-- to handle the complex mapping logic.
--
-- New Parameter Structure (inside parameters JSONB array):
-- {
--   "key": "aspect_ratio",           -- Internal identifier
--   "labelKey": "aspect_ratio_dropdown",  -- NEW: Registry lookup key
--   "mapping": "aspect_ratio",       -- API field name (moved from param_mappings)
--   "displayMode": "inline",         -- NEW: primary|inline|menu|hidden
--   "type": "string",
--   "required": false,
--   "default": "16:9",
--   "enum": ["16:9", "9:16", "1:1"],
--   "min": null,                     -- Consolidated from accepted_values
--   "max": null,
--   "step": null,
--   "options": ["16:9", "9:16", "1:1"],  -- Copy of enum for dropdown convenience
--   "count": null,                   -- For image fields (multiple uploads)
--   "mappingType": null,             -- "array" or "indexed" for multiple images
--   "multiplyByFps": null            -- For duration -> frames conversion
-- }
--
-- Deprecated columns (to be removed in future migration):
-- - inline_params (replaced by displayMode: "inline")
-- - hidden_params (replaced by displayMode: "hidden") 
-- - param_mappings (replaced by mapping field in each parameter)
--
-- The columns are kept for backward compatibility during the transition period.

-- Add a comment to the table documenting the new structure
COMMENT ON TABLE octupost.model_configs IS 
'Model configurations for FAL AI models.

Parameters Structure (new labelKey system):
Each parameter in the parameters JSONB array should have:
- key: Internal identifier
- labelKey: Registry lookup (e.g., "prompt_textarea", "duration_slider")
- mapping: API field name for the provider
- displayMode: Where to show in UI (primary, inline, menu, hidden)
- Other fields: type, required, default, enum, min, max, step, etc.

The labelKey suffix determines the component type:
_textarea, _input, _toggle, _dropdown, _slider, _json, _image, _video, _audio

Legacy columns (inline_params, hidden_params, param_mappings) are deprecated
but kept for backward compatibility.';

-- Add comments to deprecated columns
COMMENT ON COLUMN octupost.model_configs.inline_params IS 
'DEPRECATED: Use displayMode: "inline" in parameters array instead.';

COMMENT ON COLUMN octupost.model_configs.hidden_params IS 
'DEPRECATED: Use displayMode: "hidden" in parameters array instead.';

COMMENT ON COLUMN octupost.model_configs.param_mappings IS 
'DEPRECATED: Use mapping and labelKey fields in parameters array instead.';

