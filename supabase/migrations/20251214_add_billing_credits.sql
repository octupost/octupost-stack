-- Stripe Billing & Credits Schema
-- Creates tables for subscription management and credit tracking

begin;

-- Create stripe schema for billing-related tables
create schema if not exists stripe;

-- =============================================================================
-- Subscriptions (synced from Stripe)
-- =============================================================================
create table stripe.subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  stripe_customer_id text not null unique,
  stripe_subscription_id text unique,
  plan text not null default 'free' check (plan in ('free', 'pro', 'elite')),
  status text not null default 'active' check (status in ('active', 'canceled', 'past_due', 'incomplete')),
  current_period_end timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index idx_subscriptions_user on stripe.subscriptions(user_id);
create index idx_subscriptions_stripe_customer on stripe.subscriptions(stripe_customer_id);

-- =============================================================================
-- Credit Balances
-- =============================================================================
create table stripe.credit_balances (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade unique,
  balance integer not null default 0 check (balance >= 0),
  updated_at timestamptz not null default now()
);

create index idx_credit_balances_user on stripe.credit_balances(user_id);

-- =============================================================================
-- Credit Transactions (audit log)
-- =============================================================================
create table stripe.credit_transactions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  amount integer not null,  -- positive = add, negative = deduct
  balance_after integer not null,
  type text not null check (type in ('subscription_grant', 'purchase', 'usage', 'refund')),
  description text,
  model_id text,
  job_id text,
  stripe_payment_id text,
  created_at timestamptz not null default now()
);

create index idx_credit_txns_user on stripe.credit_transactions(user_id);
create index idx_credit_txns_created on stripe.credit_transactions(created_at desc);
create index idx_credit_txns_type on stripe.credit_transactions(type);

-- =============================================================================
-- Atomic Credit Deduction Function (prevents race conditions)
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
  v_current_balance integer;
  v_new_balance integer;
begin
  -- Lock the row and get current balance
  select balance into v_current_balance
  from stripe.credit_balances
  where user_id = p_user_id
  for update;

  -- Check if user has balance record
  if v_current_balance is null then
    return false;
  end if;

  -- Check if sufficient balance
  if v_current_balance < p_amount then
    return false;
  end if;

  -- Calculate new balance
  v_new_balance := v_current_balance - p_amount;

  -- Update balance
  update stripe.credit_balances
  set balance = v_new_balance, updated_at = now()
  where user_id = p_user_id;

  -- Record transaction
  insert into stripe.credit_transactions (
    user_id, amount, balance_after, type, model_id, job_id, description
  ) values (
    p_user_id, -p_amount, v_new_balance, 'usage', p_model_id, p_job_id, p_description
  );

  return true;
end;
$$;

-- =============================================================================
-- Add Credits Function
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
  v_new_balance integer;
begin
  -- Upsert credit balance
  insert into stripe.credit_balances (user_id, balance, updated_at)
  values (p_user_id, p_amount, now())
  on conflict (user_id)
  do update set 
    balance = stripe.credit_balances.balance + p_amount,
    updated_at = now()
  returning balance into v_new_balance;

  -- Record transaction
  insert into stripe.credit_transactions (
    user_id, amount, balance_after, type, description, stripe_payment_id
  ) values (
    p_user_id, p_amount, v_new_balance, p_type, p_description, p_stripe_payment_id
  );

  return v_new_balance;
end;
$$;

-- =============================================================================
-- Refund Credits Function
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
  v_new_balance integer;
begin
  -- Add credits back
  update stripe.credit_balances
  set balance = balance + p_amount, updated_at = now()
  where user_id = p_user_id
  returning balance into v_new_balance;

  -- Record refund transaction
  insert into stripe.credit_transactions (
    user_id, amount, balance_after, type, job_id, description
  ) values (
    p_user_id, p_amount, v_new_balance, 'refund', p_job_id, p_description
  );

  return v_new_balance;
end;
$$;

-- =============================================================================
-- Get Credit Balance Function
-- =============================================================================
create or replace function stripe.get_credit_balance(p_user_id uuid)
returns integer
language sql
security definer
stable
as $$
  select coalesce(balance, 0)
  from stripe.credit_balances
  where user_id = p_user_id;
$$;

-- =============================================================================
-- RLS Policies
-- =============================================================================

-- Enable RLS
alter table stripe.subscriptions enable row level security;
alter table stripe.credit_balances enable row level security;
alter table stripe.credit_transactions enable row level security;

-- Subscriptions: users can read their own
create policy "Users can read own subscription"
  on stripe.subscriptions for select
  using (auth.uid() = user_id);

-- Credit balances: users can read their own
create policy "Users can read own credit balance"
  on stripe.credit_balances for select
  using (auth.uid() = user_id);

-- Credit transactions: users can read their own
create policy "Users can read own credit transactions"
  on stripe.credit_transactions for select
  using (auth.uid() = user_id);

-- Service role can do everything (for backend operations)
create policy "Service role full access subscriptions"
  on stripe.subscriptions for all
  using (auth.role() = 'service_role');

create policy "Service role full access credit_balances"
  on stripe.credit_balances for all
  using (auth.role() = 'service_role');

create policy "Service role full access credit_transactions"
  on stripe.credit_transactions for all
  using (auth.role() = 'service_role');

commit;

