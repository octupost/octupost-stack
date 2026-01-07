-- Add idempotency key for duplicate request prevention
-- Prevents double-charges from network retries or double-clicks

BEGIN;

-- =============================================================================
-- Add Idempotency Key Column
-- =============================================================================
ALTER TABLE octupost.jobs
ADD COLUMN IF NOT EXISTS idempotency_key TEXT;

-- =============================================================================
-- Unique Index for Idempotency
-- Ensures only one job per (owner_id, idempotency_key) combination
-- NULL idempotency_keys are excluded (normal behavior for requests without key)
-- =============================================================================
CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_idempotency
ON octupost.jobs(owner_id, idempotency_key)
WHERE idempotency_key IS NOT NULL;

-- =============================================================================
-- Comments
-- =============================================================================
COMMENT ON COLUMN octupost.jobs.idempotency_key IS 'Client-provided key for request deduplication. Same key returns existing job instead of creating new one.';

COMMIT;
