-- Add agent_session_id column to projects table
-- This stores the AgentOS session ID for the AI chat associated with each project

ALTER TABLE octupost.projects
ADD COLUMN IF NOT EXISTS agent_session_id TEXT DEFAULT NULL;

COMMENT ON COLUMN octupost.projects.agent_session_id IS
'AgentOS session ID for the AI chat associated with this project. Each project has one persistent chat session.';
