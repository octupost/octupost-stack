-- Phase 5: Brand Memory
-- Allows the agent to remember brand-specific preferences and learnings

begin;

-- =============================================================================
-- Add agent_memory column to brand_kits
-- =============================================================================
-- Stores learned preferences, successful patterns, and brand-specific notes
-- that the agent can reference across sessions.

alter table octupost.brand_kits
add column if not exists agent_memory jsonb default '{}'::jsonb;

-- Expected structure:
-- {
--   "style_preferences": {
--     "text_style": "bold headlines with subtle shadows",
--     "color_usage": "prefer primary color for CTAs",
--     "video_style": "fast cuts, energetic pacing"
--   },
--   "learned_patterns": [
--     {"pattern": "always use product image in first scene", "confidence": 0.9},
--     {"pattern": "lower third works best for CTAs", "confidence": 0.85}
--   ],
--   "dos_and_donts": {
--     "do": ["use brand voice consistently", "include logo in outro"],
--     "dont": ["use competitor colors", "exceed 60 second videos"]
--   },
--   "last_updated": "2024-01-15T10:30:00Z",
--   "notes": "Client prefers minimalist approach"
-- }

comment on column octupost.brand_kits.agent_memory is
  'Agent-learned preferences and patterns for this brand. Updated by save_brand_memory tool.';

-- =============================================================================
-- Add project_images column to projects
-- =============================================================================
-- Allows per-project image additions beyond the brand kit.

alter table octupost.projects
add column if not exists project_images jsonb default '[]'::jsonb;

-- Expected structure:
-- [
--   {"url": "https://...", "name": "Product Shot A", "type": "product"},
--   {"url": "https://...", "name": "Background 1", "type": "background"},
-- ]

comment on column octupost.projects.project_images is
  'Project-specific images in addition to brand kit images.';

commit;
