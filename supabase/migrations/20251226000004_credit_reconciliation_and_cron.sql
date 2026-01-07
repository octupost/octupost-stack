-- Credit reconciliation function and pg_cron scheduled jobs
-- Handles orphaned reservations and automatically cleans up stale jobs

BEGIN;

-- =============================================================================
-- Enable pg_cron Extension
-- =============================================================================
CREATE EXTENSION IF NOT EXISTS pg_cron WITH SCHEMA pg_catalog;

-- Grant usage to postgres role (required for cron jobs)
GRANT USAGE ON SCHEMA cron TO postgres;

-- =============================================================================
-- Function: reconcile_stale_reservations
-- Finds pending reservations older than X hours and reconciles them
-- based on the associated job status
-- =============================================================================
CREATE OR REPLACE FUNCTION stripe.reconcile_stale_reservations(
  p_max_age_hours INTEGER DEFAULT 24
)
RETURNS TABLE(
  reservation_id UUID,
  job_id TEXT,
  user_id UUID,
  amount INTEGER,
  action TEXT,
  reason TEXT
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  RETURN QUERY
  WITH stale_reservations AS (
    SELECT
      r.id,
      r.job_id,
      r.user_id,
      r.reserved_amount,
      j.status as job_status
    FROM stripe.credit_reservations r
    LEFT JOIN octupost.jobs j ON r.job_id = j.id
    WHERE r.status = 'pending'
      AND r.created_at < NOW() - (p_max_age_hours || ' hours')::INTERVAL
    FOR UPDATE OF r SKIP LOCKED
  ),
  reconciled AS (
    SELECT
      sr.id,
      sr.job_id,
      sr.user_id,
      sr.reserved_amount,
      CASE
        -- Job completed but reservation not settled - settle it
        WHEN sr.job_status = 'completed' THEN 'settled'
        -- Job failed/cancelled/missing - release credits
        WHEN sr.job_status IN ('failed', 'cancelled') THEN 'released'
        WHEN sr.job_status IS NULL THEN 'released'
        -- Job still processing after 24h - mark as stale and release
        WHEN sr.job_status IN ('pending', 'processing') THEN 'released'
        ELSE 'skipped'
      END as action_type,
      CASE
        WHEN sr.job_status = 'completed' THEN 'missed_settlement'
        WHEN sr.job_status IN ('failed', 'cancelled') THEN 'job_' || sr.job_status
        WHEN sr.job_status IS NULL THEN 'orphaned_reservation'
        WHEN sr.job_status IN ('pending', 'processing') THEN 'job_stale_over_' || p_max_age_hours || 'h'
        ELSE 'unknown'
      END as action_reason
    FROM stale_reservations sr
  ),
  executed AS (
    SELECT
      rec.id,
      rec.job_id,
      rec.user_id,
      rec.reserved_amount,
      rec.action_type,
      rec.action_reason,
      CASE
        WHEN rec.action_type = 'released' THEN
          stripe.release_reservation(rec.id, 'reconciliation: ' || rec.action_reason)
        WHEN rec.action_type = 'settled' THEN
          -- For settled, we use the reserved amount as actual
          (stripe.settle_reservation(rec.id, rec.reserved_amount) IS NOT NULL)
        ELSE FALSE
      END as executed
    FROM reconciled rec
    WHERE rec.action_type IN ('released', 'settled')
  )
  SELECT
    e.id,
    e.job_id,
    e.user_id,
    e.reserved_amount,
    e.action_type,
    e.action_reason
  FROM executed e
  WHERE e.executed = TRUE;
END;
$$;

-- =============================================================================
-- Function: settle_reservation (if not exists)
-- Settles a pending reservation with the actual amount
-- =============================================================================
CREATE OR REPLACE FUNCTION stripe.settle_reservation(
  p_reservation_id UUID,
  p_actual_amount INTEGER
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_reservation RECORD;
  v_difference INTEGER;
  v_user_extra INTEGER;
  v_new_extra INTEGER;
  v_new_total INTEGER;
BEGIN
  -- Get and lock the reservation
  SELECT * INTO v_reservation
  FROM stripe.credit_reservations
  WHERE id = p_reservation_id
  FOR UPDATE;

  IF v_reservation IS NULL THEN
    RETURN jsonb_build_object('error', 'reservation_not_found');
  END IF;

  IF v_reservation.status != 'pending' THEN
    RETURN jsonb_build_object('error', 'already_' || v_reservation.status);
  END IF;

  -- Calculate difference (positive = refund needed, negative = additional charge needed)
  v_difference := v_reservation.reserved_amount - p_actual_amount;

  IF v_difference > 0 THEN
    -- Refund the difference to extra_balance
    SELECT extra_balance INTO v_user_extra
    FROM stripe.credit_balances
    WHERE user_id = v_reservation.user_id
    FOR UPDATE;

    v_new_extra := v_user_extra + v_difference;

    UPDATE stripe.credit_balances
    SET
      extra_balance = v_new_extra,
      balance = monthly_balance + v_new_extra,
      updated_at = NOW()
    WHERE user_id = v_reservation.user_id
    RETURNING balance INTO v_new_total;

    -- Record refund transaction
    INSERT INTO stripe.credit_transactions (
      user_id, amount, balance_after, type, model_id, job_id, description
    ) VALUES (
      v_reservation.user_id,
      v_difference,
      v_new_total,
      'refund',
      v_reservation.model_id,
      v_reservation.job_id,
      'Settlement adjustment: reserved ' || v_reservation.reserved_amount || ', used ' || p_actual_amount
    );
  END IF;

  -- Mark reservation as settled
  UPDATE stripe.credit_reservations
  SET
    status = 'settled',
    settled_at = NOW()
  WHERE id = p_reservation_id;

  RETURN jsonb_build_object(
    'settled', TRUE,
    'reserved_amount', v_reservation.reserved_amount,
    'actual_amount', p_actual_amount,
    'refunded', GREATEST(v_difference, 0)
  );
END;
$$;

-- =============================================================================
-- Schedule Cron Jobs
-- =============================================================================

-- Stale job detection: Run every minute
SELECT cron.schedule(
  'fail-stale-jobs',
  '* * * * *',
  $$SELECT * FROM octupost.fail_stale_jobs()$$
);

-- Credit reconciliation: Run every hour at minute 0
SELECT cron.schedule(
  'reconcile-stale-credits',
  '0 * * * *',
  $$SELECT * FROM stripe.reconcile_stale_reservations(24)$$
);

-- =============================================================================
-- One-time cleanup of existing orphaned reservations
-- This runs immediately to fix any existing stuck reservations
-- =============================================================================
DO $$
DECLARE
  v_result RECORD;
  v_count INTEGER := 0;
BEGIN
  FOR v_result IN SELECT * FROM stripe.reconcile_stale_reservations(24) LOOP
    v_count := v_count + 1;
    RAISE NOTICE 'Reconciled reservation %: % (reason: %)',
      v_result.reservation_id, v_result.action, v_result.reason;
  END LOOP;
  IF v_count > 0 THEN
    RAISE NOTICE 'Total reconciled: % reservations', v_count;
  END IF;
END;
$$;

-- =============================================================================
-- Comments
-- =============================================================================
COMMENT ON FUNCTION stripe.reconcile_stale_reservations(INTEGER) IS 'Finds and reconciles credit reservations older than specified hours. Releases credits for failed/cancelled/orphaned jobs, settles for completed jobs.';
COMMENT ON FUNCTION stripe.settle_reservation(UUID, INTEGER) IS 'Settles a pending credit reservation with the actual amount used. Refunds any difference to extra_balance.';

COMMIT;
