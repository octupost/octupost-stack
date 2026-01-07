-- Generation Cost Log Table
-- Tracks all generation charges for cost monitoring and price tuning
-- Cross-reference with Fal Usage API to verify pricing accuracy

BEGIN;

CREATE TABLE octupost.generation_cost_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  job_id text NOT NULL,
  
  -- Model info
  model_id text NOT NULL,
  generation_type text NOT NULL,
  
  -- What we charged
  credits_charged integer NOT NULL CHECK (credits_charged >= 0),
  
  -- Input parameters that affect pricing
  input_params jsonb NOT NULL DEFAULT '{}'::jsonb,
  
  -- Timestamp
  created_at timestamptz NOT NULL DEFAULT now()
);

-- Indexes for querying
CREATE INDEX idx_generation_cost_log_user ON octupost.generation_cost_log(user_id);
CREATE INDEX idx_generation_cost_log_model ON octupost.generation_cost_log(model_id);
CREATE INDEX idx_generation_cost_log_created ON octupost.generation_cost_log(created_at);
CREATE INDEX idx_generation_cost_log_job ON octupost.generation_cost_log(job_id);

-- RLS
ALTER TABLE octupost.generation_cost_log ENABLE ROW LEVEL SECURITY;

-- Users can view their own logs (for debugging/transparency)
CREATE POLICY "Users can view own generation logs"
  ON octupost.generation_cost_log FOR SELECT
  USING (auth.uid() = user_id);

-- Service role has full access
CREATE POLICY "Service role full access generation_cost_log"
  ON octupost.generation_cost_log FOR ALL
  USING (auth.role() = 'service_role');

COMMIT;




