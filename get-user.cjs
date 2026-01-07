const { Client } = require('pg');

const connectionString = 'postgresql://postgres:E2UfqmuYFqvxU7TF@db.hdqkpswdtcioklcglycz.supabase.co:5432/postgres';

const client = new Client({ connectionString });

async function run() {
  await client.connect();
  const result = await client.query('SELECT id, email FROM auth.users LIMIT 5');
  console.log(JSON.stringify(result.rows, null, 2));
  await client.end();
}

run().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
