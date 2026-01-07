-- Add question_data column to agent_paused_runs for structured questions
-- This supports the ask_user_question tool which pauses the agent for user input

ALTER TABLE octupost.agent_paused_runs
ADD COLUMN IF NOT EXISTS question_data JSONB DEFAULT NULL;

-- Add a comment explaining the column
COMMENT ON COLUMN octupost.agent_paused_runs.question_data IS
'Stores structured question data when agent is paused for user input via ask_user_question tool. Contains question_id, question text, options, and response.';
