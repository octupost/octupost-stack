const { Client } = require('pg');

const connectionString = 'postgresql://postgres.hdqkpswdtcioklcglycz:E2UfqmuYFqvxU7TF@aws-0-us-west-1.pooler.supabase.com:6543/postgres';

const client = new Client({ connectionString });

async function run() {
  await client.connect();

  // Check if table exists
  const checkResult = await client.query(`
    SELECT EXISTS (
      SELECT FROM information_schema.tables
      WHERE table_schema = 'octupost'
      AND table_name = 'api_keys'
    );
  `);

  if (checkResult.rows[0].exists) {
    console.log('Table octupost.api_keys already exists!');
    await client.end();
    return;
  }

  console.log('Creating octupost.api_keys table...');

  const sql = `
    CREATE TABLE octupost.api_keys (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
      key_hash TEXT NOT NULL,
      key_prefix VARCHAR(16) NOT NULL,
      name VARCHAR(100) NOT NULL DEFAULT 'Default',
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      last_used_at TIMESTAMPTZ,
      is_active BOOLEAN NOT NULL DEFAULT true,
      CONSTRAINT unique_key_hash UNIQUE (key_hash)
    );

    CREATE INDEX idx_api_keys_user_id ON octupost.api_keys(user_id);
    CREATE INDEX idx_api_keys_hash_active ON octupost.api_keys(key_hash) WHERE is_active = true;

    ALTER TABLE octupost.api_keys ENABLE ROW LEVEL SECURITY;

    CREATE POLICY "dev_api_keys_all" ON octupost.api_keys
      FOR ALL TO authenticated
      USING (true)
      WITH CHECK (true);

    CREATE POLICY "service_role_api_keys" ON octupost.api_keys
      FOR ALL TO service_role
      USING (true)
      WITH CHECK (true);

    COMMENT ON TABLE octupost.api_keys IS 'API keys for external developer authentication';
    COMMENT ON COLUMN octupost.api_keys.key_hash IS 'SHA-256 hash of the API key (never store plaintext)';
    COMMENT ON COLUMN octupost.api_keys.key_prefix IS 'First 16 chars of key for user identification';
  `;

  await client.query(sql);
  console.log('Table created successfully!');

  await client.end();
}

run().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
