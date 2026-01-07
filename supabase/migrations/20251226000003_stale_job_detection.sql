-- Stale job detection function
-- Marks jobs as failed if no heartbeat received by stale_at deadline
-- Releases credit reservations for failed stale jobs

BEGIN;

-- =============================================================================
-- Function: fail_stale_jobs
-- Called by pg_cron every minute to detect and fail stale jobs
-- Returns list of failed jobs and whether their credits were released
-- =============================================================================
CREATE OR REPLACE FUNCTION octupost.fail_stale_jobs()
RETURNS TABLE(job_id TEXT, reservation_id TEXT, reservation_released BOOLEAN)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  RETURN QUERY
  WITH stale_jobs AS (
    -- Find and update stale jobs atomically
    UPDATE octupost.jobs j
    SET
      status = 'failed',
      error = '{"message": "Job timed out - no heartbeat received", "type": "stale_timeout", "is_retryable": true}',
      updated_at = NOW()
    WHERE j.status IN ('pending', 'processing')
      AND j.stale_at IS NOT NULL
      AND j.stale_at < NOW()
    RETURNING j.id, j.reservation_id
  )
  SELECT
    sj.id,
    sj.reservation_id,
    CASE
      WHEN sj.reservation_id IS NOT NULL THEN
        stripe.release_reservation(sj.reservation_id::UUID, 'job_stale_timeout')
      ELSE FALSE
    END as released
  FROM stale_jobs sj;
END;
$$;

-- =============================================================================
-- Comments
-- =============================================================================
COMMENT ON FUNCTION octupost.fail_stale_jobs() IS 'Detects jobs that have not received a heartbeat by their stale_at deadline, marks them as failed, and releases their credit reservations. Called by pg_cron every minute.';

COMMIT;
