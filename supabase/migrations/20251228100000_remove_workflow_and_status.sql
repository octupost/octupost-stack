-- Migration: Remove workflow_step and project_status columns from projects table
-- These features are being removed from the application

-- Drop workflow_step column from projects table
ALTER TABLE octupost.projects DROP COLUMN IF EXISTS workflow_step;

-- Drop project_status column from projects table
ALTER TABLE octupost.projects DROP COLUMN IF EXISTS project_status;
