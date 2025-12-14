-- Dual Credit Balance System Migration
-- Separates subscription credits (monthly, expires) from purchased credits (extra, never expires)
--
-- - monthly_balance: Resets each billing cycle, use first
-- - extra_balance: Purchased credits, never expire, use after monthly depleted

begin;

-- =============================================================================
-- Add new columns to credit_balances table
-- =============================================================================
alter table stripe.credit_balances 
add column if not exists monthly_balance integer not null default 0 check (monthly_balance >= 0),
add column if not exists extra_balance integer not null default 0 check (extra_balance >= 0),
add column if not exists monthly_reset_at timestamptz;

-- =============================================================================
-- Updated: Get Credit Balance Function (returns total of both)
-- =============================================================================
create or replace function stripe.get_credit_balance(p_user_id uuid)
returns integer
language sql
security definer
stable
as $$
  select coalesce(monthly_balance, 0) + coalesce(extra_balance, 0)
  from stripe.credit_balances
  where user_id = p_user_id;
$$;

-- =============================================================================
-- New: Get detailed credit balances
-- =============================================================================
create or replace function stripe.get_credit_balances_detail(p_user_id uuid)
returns table (
  total_balance integer,
  monthly_balance integer,
  extra_balance integer,
  monthly_reset_at timestamptz
)
language sql
security definer
stable
as $$
  select 
    coalesce(monthly_balance, 0) + coalesce(extra_balance, 0) as total_balance,
    coalesce(monthly_balance, 0) as monthly_balance,
    coalesce(extra_balance, 0) as extra_balance,
    monthly_reset_at
  from stripe.credit_balances
  where user_id = p_user_id;
$$;

-- =============================================================================
-- Updated: Deduct Credits Function
-- Deducts from monthly_balance first, then extra_balance
-- =============================================================================
create or replace function stripe.deduct_credits(
  p_user_id uuid,
  p_amount integer,
  p_model_id text default null,
  p_job_id text default null,
  p_description text default null
)
returns boolean
language plpgsql
security definer
as $$
declare
  v_monthly integer;
  v_extra integer;
  v_total integer;
  v_new_monthly integer;
  v_new_extra integer;
  v_new_total integer;
  v_deduct_from_monthly integer;
  v_deduct_from_extra integer;
begin
  -- Lock the row and get current balances
  select monthly_balance, extra_balance
  into v_monthly, v_extra
  from stripe.credit_balances
  where user_id = p_user_id
  for update;

  -- Check if user has balance record
  if v_monthly is null then
    return false;
  end if;

  v_total := v_monthly + v_extra;

  -- Check if sufficient total balance
  if v_total < p_amount then
    return false;
  end if;

  -- Deduct from monthly first, then extra
  if v_monthly >= p_amount then
    -- All from monthly
    v_deduct_from_monthly := p_amount;
    v_deduct_from_extra := 0;
  else
    -- Use all monthly, rest from extra
    v_deduct_from_monthly := v_monthly;
    v_deduct_from_extra := p_amount - v_monthly;
  end if;

  v_new_monthly := v_monthly - v_deduct_from_monthly;
  v_new_extra := v_extra - v_deduct_from_extra;
  v_new_total := v_new_monthly + v_new_extra;

  -- Update balances
  update stripe.credit_balances
  set 
    monthly_balance = v_new_monthly, 
    extra_balance = v_new_extra,
    -- Also keep legacy balance field in sync for backwards compatibility
    balance = v_new_total,
    updated_at = now()
  where user_id = p_user_id;

  -- Record transaction
  insert into stripe.credit_transactions (
    user_id, amount, balance_after, type, model_id, job_id, description
  ) values (
    p_user_id, -p_amount, v_new_total, 'usage', p_model_id, p_job_id, p_description
  );

  return true;
end;
$$;

-- =============================================================================
-- Updated: Add Credits Function
-- For purchases, adds to extra_balance
-- For subscription grants, use grant_subscription_credits instead
-- =============================================================================
create or replace function stripe.add_credits(
  p_user_id uuid,
  p_amount integer,
  p_type text,
  p_description text default null,
  p_stripe_payment_id text default null
)
returns integer
language plpgsql
security definer
as $$
declare
  v_new_total integer;
  v_monthly integer;
  v_extra integer;
begin
  -- For purchases, add to extra_balance (never expires)
  -- For subscription_grant, this function now redirects to proper handling
  if p_type = 'purchase' then
    insert into stripe.credit_balances (user_id, monthly_balance, extra_balance, balance, updated_at)
    values (p_user_id, 0, p_amount, p_amount, now())
    on conflict (user_id)
    do update set 
      extra_balance = stripe.credit_balances.extra_balance + p_amount,
      balance = stripe.credit_balances.monthly_balance + stripe.credit_balances.extra_balance + p_amount,
      updated_at = now()
    returning monthly_balance + extra_balance into v_new_total;
  else
    -- For refunds and other types, add to extra_balance as well
    insert into stripe.credit_balances (user_id, monthly_balance, extra_balance, balance, updated_at)
    values (p_user_id, 0, p_amount, p_amount, now())
    on conflict (user_id)
    do update set 
      extra_balance = stripe.credit_balances.extra_balance + p_amount,
      balance = stripe.credit_balances.monthly_balance + stripe.credit_balances.extra_balance + p_amount,
      updated_at = now()
    returning monthly_balance + extra_balance into v_new_total;
  end if;

  -- Record transaction
  insert into stripe.credit_transactions (
    user_id, amount, balance_after, type, description, stripe_payment_id
  ) values (
    p_user_id, p_amount, v_new_total, p_type, p_description, p_stripe_payment_id
  );

  return v_new_total;
end;
$$;

-- =============================================================================
-- New: Grant Subscription Credits Function
-- RESETS monthly_balance (doesn't add), preserves extra_balance
-- =============================================================================
create or replace function stripe.grant_subscription_credits(
  p_user_id uuid,
  p_amount integer,
  p_description text default null,
  p_stripe_subscription_id text default null
)
returns integer
language plpgsql
security definer
as $$
declare
  v_old_monthly integer;
  v_extra integer;
  v_new_total integer;
begin
  -- Get current extra balance (preserve it)
  select extra_balance into v_extra
  from stripe.credit_balances
  where user_id = p_user_id;

  if v_extra is null then
    v_extra := 0;
  end if;

  -- Reset monthly balance to the subscription amount (don't add)
  insert into stripe.credit_balances (user_id, monthly_balance, extra_balance, balance, monthly_reset_at, updated_at)
  values (p_user_id, p_amount, 0, p_amount, now(), now())
  on conflict (user_id)
  do update set 
    monthly_balance = p_amount,  -- RESET, not add
    balance = p_amount + stripe.credit_balances.extra_balance,
    monthly_reset_at = now(),
    updated_at = now()
  returning monthly_balance + extra_balance into v_new_total;

  -- Record transaction
  insert into stripe.credit_transactions (
    user_id, amount, balance_after, type, description, stripe_payment_id
  ) values (
    p_user_id, p_amount, v_new_total, 'subscription_grant', p_description, p_stripe_subscription_id
  );

  return v_new_total;
end;
$$;

-- =============================================================================
-- Updated: Refund Credits Function
-- Refunds go to extra_balance (they never expire)
-- =============================================================================
create or replace function stripe.refund_credits(
  p_user_id uuid,
  p_amount integer,
  p_job_id text,
  p_description text default 'Generation failed - credits refunded'
)
returns integer
language plpgsql
security definer
as $$
declare
  v_new_total integer;
begin
  -- Add refunded credits to extra_balance (they never expire)
  update stripe.credit_balances
  set 
    extra_balance = extra_balance + p_amount, 
    balance = monthly_balance + extra_balance + p_amount,
    updated_at = now()
  where user_id = p_user_id
  returning monthly_balance + extra_balance into v_new_total;

  -- Record refund transaction
  insert into stripe.credit_transactions (
    user_id, amount, balance_after, type, job_id, description
  ) values (
    p_user_id, p_amount, v_new_total, 'refund', p_job_id, p_description
  );

  return v_new_total;
end;
$$;

-- =============================================================================
-- Data Migration: Move existing balance to extra_balance
-- This preserves all existing credits as "purchased" (never expire)
-- =============================================================================
update stripe.credit_balances
set 
  extra_balance = balance,
  monthly_balance = 0
where balance > 0 and extra_balance = 0 and monthly_balance = 0;

commit;

