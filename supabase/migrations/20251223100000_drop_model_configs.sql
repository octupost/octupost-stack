-- Migration: Drop model_configs table
--
-- IMPORTANT: This table is no longer used - registry.py is the single source of truth
-- for model configurations, pricing, and frontend metadata.
--
-- Before running this migration, ensure:
-- 1. The frontend is using /api/capabilities/model-configs instead of /api/admin/model-configs
-- 2. Billing is using registry.py for pricing (get_pricing_config_for_model in billing.py)
-- 3. Generation requests use registry.py for validation (_create_generation_job in main.py)
-- 4. All admin model CRUD pages have been removed

-- Drop the model_configs table
DROP TABLE IF EXISTS octupost.model_configs;
