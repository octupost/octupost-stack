-- Credit Reservation System Migration
-- Implements a two-phase credit system for models with unknown output duration
-- (e.g., avatar, text-to-speech where duration depends on script length)
--
-- Flow: reserve_credits -> generation -> settle_reservation OR release_reservation

begin;

-- =============================================================================
-- Credit Reservations Table
-- =============================================================================
create table stripe.credit_reservations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  job_id text not null unique,
  reserved_amount integer not null check (reserved_amount > 0),
  estimated_amount integer not null check (estimated_amount > 0),
  actual_amount integer check (actual_amount >= 0),  -- null until settled
  status text not null default 'pending' 
    check (status in ('pending', 'settled', 'released', 'failed')),
  model_id text,
  created_at timestamptz not null default now(),
  settled_at timestamptz
);

create index idx_credit_reservations_user on stripe.credit_reservations(user_id);
create index idx_credit_reservations_job on stripe.credit_reservations(job_id);
create index idx_credit_reservations_status on stripe.credit_reservations(status);

-- =============================================================================
-- Reserve Credits Function
-- Atomically checks balance and creates a reservation
-- Returns reservation_id if successful, null if insufficient credits
-- =============================================================================
create or replace function stripe.reserve_credits(
  p_user_id uuid,
  p_estimated_amount integer,
  p_job_id text,
  p_model_id text default null,
  p_buffer_multiplier numeric default 1.3
)
returns uuid
language plpgsql
security definer
as $$
declare
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
begin
  -- Calculate reserved amount with buffer
  v_reserved_amount := ceil(p_estimated_amount * p_buffer_multiplier)::integer;
  
  -- Lock the row and get current balances
  select monthly_balance, extra_balance
  into v_monthly, v_extra
  from stripe.credit_balances
  where user_id = p_user_id
  for update;

  -- Check if user has balance record
  if v_monthly is null then
    return null;
  end if;

  v_total := v_monthly + v_extra;

  -- Check if sufficient total balance for reserved amount
  if v_total < v_reserved_amount then
    return null;
  end if;

  -- Deduct from monthly first, then extra
  if v_monthly >= v_reserved_amount then
    v_deduct_from_monthly := v_reserved_amount;
    v_deduct_from_extra := 0;
  else
    v_deduct_from_monthly := v_monthly;
    v_deduct_from_extra := v_reserved_amount - v_monthly;
  end if;

  v_new_monthly := v_monthly - v_deduct_from_monthly;
  v_new_extra := v_extra - v_deduct_from_extra;
  v_new_total := v_new_monthly + v_new_extra;

  -- Update balances
  update stripe.credit_balances
  set 
    monthly_balance = v_new_monthly, 
    extra_balance = v_new_extra,
    balance = v_new_total,
    updated_at = now()
  where user_id = p_user_id;

  -- Create reservation record
  insert into stripe.credit_reservations (
    user_id, job_id, reserved_amount, estimated_amount, model_id, status
  ) values (
    p_user_id, p_job_id, v_reserved_amount, p_estimated_amount, p_model_id, 'pending'
  )
  returning id into v_reservation_id;

  -- Record transaction (reservation)
  insert into stripe.credit_transactions (
    user_id, amount, balance_after, type, model_id, job_id, description
  ) values (
    p_user_id, -v_reserved_amount, v_new_total, 'usage', p_model_id, p_job_id, 
    'Credit reservation for generation'
  );

  return v_reservation_id;
end;
$$;

-- =============================================================================
-- Settle Reservation Function
-- Settles a reservation with the actual cost
-- If actual < reserved: refund the difference
-- If actual > reserved: charge the difference from balance
-- Returns JSON with {refunded, charged_extra, final_cost}
-- =============================================================================
create or replace function stripe.settle_reservation(
  p_reservation_id uuid,
  p_actual_amount integer
)
returns jsonb
language plpgsql
security definer
as $$
declare
  v_reservation record;
  v_difference integer;
  v_monthly integer;
  v_extra integer;
  v_new_monthly integer;
  v_new_extra integer;
  v_new_total integer;
  v_charged_extra integer := 0;
  v_refunded integer := 0;
  v_deduct_from_monthly integer;
  v_deduct_from_extra integer;
begin
  -- Get and lock the reservation
  select * into v_reservation
  from stripe.credit_reservations
  where id = p_reservation_id
  for update;

  if v_reservation is null then
    return jsonb_build_object('error', 'Reservation not found');
  end if;

  if v_reservation.status != 'pending' then
    return jsonb_build_object('error', 'Reservation already ' || v_reservation.status);
  end if;

  -- Lock user's credit balance
  select monthly_balance, extra_balance
  into v_monthly, v_extra
  from stripe.credit_balances
  where user_id = v_reservation.user_id
  for update;

  v_difference := v_reservation.reserved_amount - p_actual_amount;

  if v_difference > 0 then
    -- Actual cost less than reserved - refund the difference
    v_refunded := v_difference;
    
    -- Add refund to extra_balance (refunds never expire)
    v_new_monthly := v_monthly;
    v_new_extra := v_extra + v_refunded;
    v_new_total := v_new_monthly + v_new_extra;

    update stripe.credit_balances
    set 
      extra_balance = v_new_extra,
      balance = v_new_total,
      updated_at = now()
    where user_id = v_reservation.user_id;

    -- Record refund transaction
    insert into stripe.credit_transactions (
      user_id, amount, balance_after, type, model_id, job_id, description
    ) values (
      v_reservation.user_id, v_refunded, v_new_total, 'refund', 
      v_reservation.model_id, v_reservation.job_id,
      'Reservation settlement - refund excess'
    );

  elsif v_difference < 0 then
    -- Actual cost more than reserved - charge the difference
    v_charged_extra := -v_difference;
    
    -- Check if user has enough balance for the extra charge
    if (v_monthly + v_extra) >= v_charged_extra then
      -- Deduct from monthly first, then extra
      if v_monthly >= v_charged_extra then
        v_deduct_from_monthly := v_charged_extra;
        v_deduct_from_extra := 0;
      else
        v_deduct_from_monthly := v_monthly;
        v_deduct_from_extra := v_charged_extra - v_monthly;
      end if;

      v_new_monthly := v_monthly - v_deduct_from_monthly;
      v_new_extra := v_extra - v_deduct_from_extra;
      v_new_total := v_new_monthly + v_new_extra;

      update stripe.credit_balances
      set 
        monthly_balance = v_new_monthly,
        extra_balance = v_new_extra,
        balance = v_new_total,
        updated_at = now()
      where user_id = v_reservation.user_id;

      -- Record extra charge transaction
      insert into stripe.credit_transactions (
        user_id, amount, balance_after, type, model_id, job_id, description
      ) values (
        v_reservation.user_id, -v_charged_extra, v_new_total, 'usage', 
        v_reservation.model_id, v_reservation.job_id,
        'Reservation settlement - additional charge'
      );
    else
      -- Insufficient balance for extra - charge what we can, log the rest
      -- This is a rare edge case - generation already completed
      v_charged_extra := v_monthly + v_extra;
      v_new_monthly := 0;
      v_new_extra := 0;
      v_new_total := 0;

      if v_charged_extra > 0 then
        update stripe.credit_balances
        set 
          monthly_balance = 0,
          extra_balance = 0,
          balance = 0,
          updated_at = now()
        where user_id = v_reservation.user_id;

        insert into stripe.credit_transactions (
          user_id, amount, balance_after, type, model_id, job_id, description
        ) values (
          v_reservation.user_id, -v_charged_extra, 0, 'usage', 
          v_reservation.model_id, v_reservation.job_id,
          'Reservation settlement - partial charge (insufficient balance)'
        );
      end if;
    end if;
  else
    -- Exact match - no adjustment needed
    v_new_total := v_monthly + v_extra;
  end if;

  -- Update reservation to settled
  update stripe.credit_reservations
  set 
    status = 'settled',
    actual_amount = p_actual_amount,
    settled_at = now()
  where id = p_reservation_id;

  return jsonb_build_object(
    'refunded', v_refunded,
    'charged_extra', v_charged_extra,
    'final_cost', p_actual_amount,
    'reserved_amount', v_reservation.reserved_amount
  );
end;
$$;

-- =============================================================================
-- Release Reservation Function
-- Releases a reservation on generation failure, returning credits to user
-- Returns the amount released
-- =============================================================================
create or replace function stripe.release_reservation(
  p_reservation_id uuid,
  p_reason text default 'Generation failed'
)
returns integer
language plpgsql
security definer
as $$
declare
  v_reservation record;
  v_new_total integer;
begin
  -- Get and lock the reservation
  select * into v_reservation
  from stripe.credit_reservations
  where id = p_reservation_id
  for update;

  if v_reservation is null then
    return 0;
  end if;

  if v_reservation.status != 'pending' then
    return 0;
  end if;

  -- Return credits to extra_balance (refunds never expire)
  update stripe.credit_balances
  set 
    extra_balance = extra_balance + v_reservation.reserved_amount,
    balance = monthly_balance + extra_balance + v_reservation.reserved_amount,
    updated_at = now()
  where user_id = v_reservation.user_id
  returning monthly_balance + extra_balance into v_new_total;

  -- Update reservation to released
  update stripe.credit_reservations
  set 
    status = 'released',
    settled_at = now()
  where id = p_reservation_id;

  -- Record refund transaction
  insert into stripe.credit_transactions (
    user_id, amount, balance_after, type, model_id, job_id, description
  ) values (
    v_reservation.user_id, v_reservation.reserved_amount, v_new_total, 'refund', 
    v_reservation.model_id, v_reservation.job_id,
    'Reservation released - ' || p_reason
  );

  return v_reservation.reserved_amount;
end;
$$;

-- =============================================================================
-- Get Reservation Function
-- Gets reservation details by ID or job_id
-- =============================================================================
create or replace function stripe.get_reservation(
  p_reservation_id uuid default null,
  p_job_id text default null
)
returns table (
  id uuid,
  user_id uuid,
  job_id text,
  reserved_amount integer,
  estimated_amount integer,
  actual_amount integer,
  status text,
  model_id text,
  created_at timestamptz,
  settled_at timestamptz
)
language sql
security definer
stable
as $$
  select 
    r.id, r.user_id, r.job_id, r.reserved_amount, r.estimated_amount,
    r.actual_amount, r.status, r.model_id, r.created_at, r.settled_at
  from stripe.credit_reservations r
  where (p_reservation_id is null or r.id = p_reservation_id)
    and (p_job_id is null or r.job_id = p_job_id);
$$;

-- =============================================================================
-- RLS Policies
-- =============================================================================
alter table stripe.credit_reservations enable row level security;

-- Users can view their own reservations
create policy "Users can view own reservations"
  on stripe.credit_reservations for select
  using (auth.uid() = user_id);

-- Service role has full access
create policy "Service role full access credit_reservations"
  on stripe.credit_reservations for all
  using (auth.role() = 'service_role');

commit;

