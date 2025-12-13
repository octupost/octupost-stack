-- Migration: Create Agno schema for AI agent data persistence
-- This schema stores Agno agent sessions, memory, metrics, and knowledge

-- Create agno schema for Agno AI agent data
CREATE SCHEMA IF NOT EXISTS agno;

-- Grant permissions to Supabase roles
GRANT USAGE ON SCHEMA agno TO anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA agno TO anon, authenticated, service_role;
GRANT ALL ON ALL ROUTINES IN SCHEMA agno TO anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA agno TO anon, authenticated, service_role;

-- Set default privileges for future tables created by postgres role
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA agno 
  GRANT ALL ON TABLES TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA agno 
  GRANT ALL ON ROUTINES TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA agno 
  GRANT ALL ON SEQUENCES TO anon, authenticated, service_role;

