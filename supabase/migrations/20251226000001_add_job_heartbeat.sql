-- Add heartbeat columns for stale job detection
-- last_heartbeat: Updated by Inngest worker during polling
-- stale_at: When job should be considered stale if no heartbeat received

BEGIN;

-- =============================================================================
-- Add Heartbeat Columns
-- =============================================================================
ALTER TABLE octupost.jobs
ADD COLUMN IF NOT EXISTS last_heartbeat TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS stale_at TIMESTAMPTZ;

-- =============================================================================
-- Index for Stale Job Detection
-- Only index active jobs with a stale_at deadline
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_jobs_stale
ON octupost.jobs(stale_at)
WHERE status IN ('pending', 'processing') AND stale_at IS NOT NULL;

-- =============================================================================
-- Comments
-- =============================================================================
COMMENT ON COLUMN octupost.jobs.last_heartbeat IS 'Last heartbeat timestamp from Inngest worker during polling';
COMMENT ON COLUMN octupost.jobs.stale_at IS 'Deadline timestamp - job is stale if no heartbeat received by this time';

COMMIT;
