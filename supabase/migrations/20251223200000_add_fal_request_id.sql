-- Add fal_request_id column to jobs table
-- This links our job_id to Fal's request_id for webhook lookups

BEGIN;

-- Add column to store Fal's request_id
ALTER TABLE octupost.jobs
ADD COLUMN IF NOT EXISTS fal_request_id TEXT;

-- Index for webhook lookup by fal_request_id
CREATE INDEX IF NOT EXISTS idx_jobs_fal_request_id
ON octupost.jobs(fal_request_id)
WHERE fal_request_id IS NOT NULL;

-- Comment
COMMENT ON COLUMN octupost.jobs.fal_request_id IS 'Fal API request_id for webhook callback matching';

COMMIT;
