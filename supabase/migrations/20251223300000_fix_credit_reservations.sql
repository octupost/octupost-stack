-- Fix Critical Credit Reservation Issues
--
-- C1: release_reservation() was not refunding credits back to user balance
-- C2: reserve_credits() had hidden buffer multiplier, now reserves exact amount

BEGIN;

-- =============================================================================
-- Fix 1: release_reservation must refund credits
--
-- BEFORE: Only marked status as 'released' but never returned credits
-- AFTER:  Refunds reserved_amount to extra_balance and records transaction
-- =============================================================================
CREATE OR REPLACE FUNCTION stripe.release_reservation(
  p_reservation_id uuid,
  p_reason text DEFAULT 'generation_failed'
)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_reservation record;
  v_monthly integer;
  v_extra integer;
  v_new_extra integer;
  v_new_total integer;
BEGIN
  -- Get and lock the reservation
  SELECT * INTO v_reservation
  FROM stripe.credit_reservations
  WHERE id = p_reservation_id
  FOR UPDATE;

  IF v_reservation IS NULL THEN
    RETURN false;
  END IF;

  IF v_reservation.status != 'pending' THEN
    RETURN false;
  END IF;

  -- Lock user's balance
  SELECT monthly_balance, extra_balance
  INTO v_monthly, v_extra
  FROM stripe.credit_balances
  WHERE user_id = v_reservation.user_id
  FOR UPDATE;

  -- Refund reserved amount to extra_balance (refunds never expire)
  v_new_extra := v_extra + v_reservation.reserved_amount;
  v_new_total := v_monthly + v_new_extra;

  UPDATE stripe.credit_balances
  SET
    extra_balance = v_new_extra,
    balance = v_new_total,
    updated_at = now()
  WHERE user_id = v_reservation.user_id;

  -- Record refund transaction
  INSERT INTO stripe.credit_transactions (
    user_id, amount, balance_after, type, model_id, job_id, description
  ) VALUES (
    v_reservation.user_id,
    v_reservation.reserved_amount,  -- positive = credit added
    v_new_total,
    'refund',
    v_reservation.model_id,
    v_reservation.job_id,
    'Reservation released: ' || p_reason
  );

  -- Mark reservation as released
  UPDATE stripe.credit_reservations
  SET
    status = 'released',
    settled_at = now()
  WHERE id = p_reservation_id;

  RETURN true;
END;
$$;

-- =============================================================================
-- Fix 2: Remove buffer multiplier from reserve_credits
--
-- BEFORE: v_reserved_amount := ceil(p_estimated_amount * p_buffer_multiplier)
-- AFTER:  v_reserved_amount := p_estimated_amount (exact, no buffer)
-- =============================================================================
CREATE OR REPLACE FUNCTION stripe.reserve_credits(
  p_user_id uuid,
  p_estimated_amount integer,
  p_job_id text,
  p_model_id text DEFAULT NULL
)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_monthly integer;
  v_extra integer;
  v_total integer;
  v_reserved_amount integer;
  v_new_monthly integer;
  v_new_extra integer;
  v_new_total integer;
  v_deduct_from_monthly integer;
  v_deduct_from_extra integer;
  v_reservation_id uuid;
BEGIN
  -- No buffer - reserve exactly what was estimated
  v_reserved_amount := p_estimated_amount;

  -- Lock the row and get current balances
  SELECT monthly_balance, extra_balance
  INTO v_monthly, v_extra
  FROM stripe.credit_balances
  WHERE user_id = p_user_id
  FOR UPDATE;

  -- Check if user has balance record
  IF v_monthly IS NULL THEN
    RETURN NULL;
  END IF;

  v_total := v_monthly + v_extra;

  -- Check if sufficient total balance
  IF v_total < v_reserved_amount THEN
    RETURN NULL;
  END IF;

  -- Deduct from monthly first, then extra
  IF v_monthly >= v_reserved_amount THEN
    v_deduct_from_monthly := v_reserved_amount;
    v_deduct_from_extra := 0;
  ELSE
    v_deduct_from_monthly := v_monthly;
    v_deduct_from_extra := v_reserved_amount - v_monthly;
  END IF;

  v_new_monthly := v_monthly - v_deduct_from_monthly;
  v_new_extra := v_extra - v_deduct_from_extra;
  v_new_total := v_new_monthly + v_new_extra;

  -- Update balances
  UPDATE stripe.credit_balances
  SET
    monthly_balance = v_new_monthly,
    extra_balance = v_new_extra,
    balance = v_new_total,
    updated_at = now()
  WHERE user_id = p_user_id;

  -- Create reservation record
  INSERT INTO stripe.credit_reservations (
    user_id, job_id, reserved_amount, estimated_amount, model_id, status
  ) VALUES (
    p_user_id, p_job_id, v_reserved_amount, p_estimated_amount, p_model_id, 'pending'
  )
  RETURNING id INTO v_reservation_id;

  -- Record transaction
  INSERT INTO stripe.credit_transactions (
    user_id, amount, balance_after, type, model_id, job_id, description
  ) VALUES (
    p_user_id, -v_reserved_amount, v_new_total, 'usage', p_model_id, p_job_id,
    'Credit reservation for generation'
  );

  RETURN v_reservation_id;
END;
$$;

-- Drop the old overloaded function with buffer parameter
DROP FUNCTION IF EXISTS stripe.reserve_credits(uuid, integer, text, text, numeric);

COMMIT;
