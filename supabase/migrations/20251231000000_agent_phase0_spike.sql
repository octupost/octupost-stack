-- Phase 0 Agent Spike: HITL Support
-- Creates agent_paused_runs table for HITL recovery and adds job_id index to overlays
--
-- This migration supports the agent video creation system:
-- 1. agent_paused_runs: Stores paused run state for browser refresh recovery
-- 2. job_id index on overlays: Enables Inngest to update overlays when jobs complete

BEGIN;

-- =============================================================================
-- Agent Paused Runs Table
-- =============================================================================
-- Stores Agno run state when agent pauses for HITL confirmation
-- Enables recovery when user refreshes browser during HITL pause

CREATE TABLE IF NOT EXISTS octupost.agent_paused_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES octupost.projects(id) ON DELETE CASCADE,

  -- Agno run identification
  run_id TEXT NOT NULL UNIQUE,

  -- Serialized Agno requirements (for continue_run)
  requirements JSONB NOT NULL,

  -- Timestamps
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMPTZ NOT NULL DEFAULT NOW() + INTERVAL '24 hours'
);

-- Index for project lookups (find paused run when user returns to project)
CREATE INDEX IF NOT EXISTS idx_agent_paused_runs_project
  ON octupost.agent_paused_runs(project_id);

-- Index for expiration cleanup
CREATE INDEX IF NOT EXISTS idx_agent_paused_runs_expires
  ON octupost.agent_paused_runs(expires_at);

-- =============================================================================
-- RLS Policies
-- =============================================================================
ALTER TABLE octupost.agent_paused_runs ENABLE ROW LEVEL SECURITY;

-- Dev policy (permissive for development)
CREATE POLICY "dev_agent_paused_runs_all"
  ON octupost.agent_paused_runs FOR ALL TO authenticated
  USING (true)
  WITH CHECK (true);

-- =============================================================================
-- Cleanup Job (pg_cron)
-- =============================================================================
-- Clean up expired paused runs every hour
-- Note: Requires pg_cron extension to be enabled

DO $$
BEGIN
  -- Check if pg_cron is available before scheduling
  IF EXISTS (
    SELECT 1 FROM pg_extension WHERE extname = 'pg_cron'
  ) THEN
    -- Unschedule if exists (idempotent)
    PERFORM cron.unschedule('cleanup-expired-paused-runs');

    -- Schedule hourly cleanup
    PERFORM cron.schedule(
      'cleanup-expired-paused-runs',
      '0 * * * *',  -- Every hour at minute 0
      $$DELETE FROM octupost.agent_paused_runs WHERE expires_at < NOW()$$
    );
  END IF;
EXCEPTION
  WHEN OTHERS THEN
    -- pg_cron not available, skip scheduling
    RAISE NOTICE 'pg_cron not available, skipping paused runs cleanup scheduling';
END
$$;

-- =============================================================================
-- Job ID Index on Overlays
-- =============================================================================
-- Enables fast lookup of overlays by job_id when Inngest job completes
-- Only indexes rows where job_id exists (sparse index)

CREATE INDEX IF NOT EXISTS idx_project_overlays_job_id
  ON octupost.project_overlays ((data->>'job_id'))
  WHERE data->>'job_id' IS NOT NULL;

-- =============================================================================
-- Comments
-- =============================================================================
COMMENT ON TABLE octupost.agent_paused_runs IS
  'Stores Agno run state during HITL pauses. Enables recovery when user refreshes browser.';

COMMENT ON COLUMN octupost.agent_paused_runs.run_id IS
  'Agno run_id - unique identifier for the paused run';

COMMENT ON COLUMN octupost.agent_paused_runs.requirements IS
  'Serialized Agno requirements including pending confirmations';

COMMENT ON COLUMN octupost.agent_paused_runs.expires_at IS
  'Auto-cleanup time. Paused runs expire after 24 hours.';

COMMIT;
