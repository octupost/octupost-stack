-- Migration: Auto-initialize billing records for new users
-- This ensures all users have stripe.subscriptions and stripe.credit_balances records

-- First, make stripe_customer_id nullable since free users don't have a Stripe customer yet
ALTER TABLE stripe.subscriptions ALTER COLUMN stripe_customer_id DROP NOT NULL;

-- Create trigger function to initialize billing records for new users
CREATE OR REPLACE FUNCTION stripe.initialize_user_billing()
RETURNS TRIGGER AS $$
BEGIN
    -- Create subscription record (free plan by default, no stripe_customer_id yet)
    INSERT INTO stripe.subscriptions (user_id, plan, status)
    VALUES (NEW.id, 'free', 'active')
    ON CONFLICT (user_id) DO NOTHING;

    -- Create credit balance record
    INSERT INTO stripe.credit_balances (user_id, balance, monthly_balance, extra_balance)
    VALUES (NEW.id, 0, 0, 0)
    ON CONFLICT (user_id) DO NOTHING;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger on auth.users
DROP TRIGGER IF EXISTS on_auth_user_created_init_billing ON auth.users;
CREATE TRIGGER on_auth_user_created_init_billing
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION stripe.initialize_user_billing();

-- Backfill: Create subscription records for existing users who don't have them
INSERT INTO stripe.subscriptions (user_id, plan, status)
SELECT id, 'free', 'active'
FROM auth.users u
WHERE NOT EXISTS (
    SELECT 1 FROM stripe.subscriptions s WHERE s.user_id = u.id
)
ON CONFLICT (user_id) DO NOTHING;

-- Backfill: Create credit balance records for existing users who don't have them
INSERT INTO stripe.credit_balances (user_id, balance, monthly_balance, extra_balance)
SELECT id, 0, 0, 0
FROM auth.users u
WHERE NOT EXISTS (
    SELECT 1 FROM stripe.credit_balances cb WHERE cb.user_id = u.id
)
ON CONFLICT (user_id) DO NOTHING;
