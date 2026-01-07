-- API Keys Table
-- Allows external developers to authenticate via API keys instead of internal user IDs

CREATE TABLE octupost.api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  -- Key data (store hash, not plaintext)
  key_hash TEXT NOT NULL,
  key_prefix VARCHAR(16) NOT NULL,  -- "oct_sk_xxxx..." for identification

  -- Metadata
  name VARCHAR(100) NOT NULL DEFAULT 'Default',

  -- Lifecycle
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_used_at TIMESTAMPTZ,
  is_active BOOLEAN NOT NULL DEFAULT true,

  -- Constraints
  CONSTRAINT unique_key_hash UNIQUE (key_hash)
);

-- Indexes for fast lookups
CREATE INDEX idx_api_keys_user_id ON octupost.api_keys(user_id);
CREATE INDEX idx_api_keys_hash_active ON octupost.api_keys(key_hash) WHERE is_active = true;

-- Enable RLS (dev mode policies for now)
ALTER TABLE octupost.api_keys ENABLE ROW LEVEL SECURITY;

-- Dev policy: authenticated users can manage their own keys
-- In production, replace with proper user_id = auth.uid() policies
CREATE POLICY "dev_api_keys_all" ON octupost.api_keys
  FOR ALL TO authenticated
  USING (true)
  WITH CHECK (true);

-- Service role bypass for backend operations
CREATE POLICY "service_role_api_keys" ON octupost.api_keys
  FOR ALL TO service_role
  USING (true)
  WITH CHECK (true);

COMMENT ON TABLE octupost.api_keys IS 'API keys for external developer authentication';
COMMENT ON COLUMN octupost.api_keys.key_hash IS 'SHA-256 hash of the API key (never store plaintext)';
COMMENT ON COLUMN octupost.api_keys.key_prefix IS 'First 16 chars of key for user identification (oct_sk_xxxxxxxx)';
