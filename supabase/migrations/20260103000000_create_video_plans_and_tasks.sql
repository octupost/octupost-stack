-- Migration: Create project_video_plans and project_tasks tables
-- Required for agent planning and task tracking workflow

-- =============================================================================
-- project_video_plans: Stores video creation plans awaiting user approval
-- =============================================================================

CREATE TABLE IF NOT EXISTS octupost.project_video_plans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES octupost.projects(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT,
  total_duration_seconds FLOAT,
  estimated_credits FLOAT,
  estimated_duration_minutes FLOAT,
  scenes_breakdown JSONB,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'executing', 'completed', 'completed_with_errors', 'cancelled')),
  approved_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Auto-update updated_at
CREATE TRIGGER update_project_video_plans_updated_at
  BEFORE UPDATE ON octupost.project_video_plans
  FOR EACH ROW
  EXECUTE FUNCTION octupost.update_updated_at_column();

-- Index for project lookups
CREATE INDEX idx_video_plans_project ON octupost.project_video_plans(project_id);
CREATE INDEX idx_video_plans_status ON octupost.project_video_plans(status);

-- =============================================================================
-- project_tasks: Tracks individual tasks within a video creation plan
-- =============================================================================

CREATE TABLE IF NOT EXISTS octupost.project_tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES octupost.projects(id) ON DELETE CASCADE,
  plan_id UUID REFERENCES octupost.project_video_plans(id) ON DELETE CASCADE,
  scene_id UUID REFERENCES octupost.project_scenes(id) ON DELETE SET NULL,
  title TEXT NOT NULL,
  description TEXT,
  task_type TEXT NOT NULL CHECK (task_type IN (
    'create_scene',
    'generate_video',
    'generate_speech',
    'generate_music',
    'generate_sound_effect',
    'add_text',
    'add_image',
    'custom'
  )),
  order_index INTEGER NOT NULL,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'failed', 'skipped')),
  error_message TEXT,
  metadata JSONB DEFAULT '{}',
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Auto-update updated_at
CREATE TRIGGER update_project_tasks_updated_at
  BEFORE UPDATE ON octupost.project_tasks
  FOR EACH ROW
  EXECUTE FUNCTION octupost.update_updated_at_column();

-- Indexes for efficient queries
CREATE INDEX idx_tasks_project ON octupost.project_tasks(project_id);
CREATE INDEX idx_tasks_plan ON octupost.project_tasks(plan_id);
CREATE INDEX idx_tasks_scene ON octupost.project_tasks(scene_id);
CREATE INDEX idx_tasks_status ON octupost.project_tasks(status);
CREATE INDEX idx_tasks_order ON octupost.project_tasks(plan_id, order_index);

-- =============================================================================
-- Row Level Security
-- =============================================================================

ALTER TABLE octupost.project_video_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE octupost.project_tasks ENABLE ROW LEVEL SECURITY;

-- Video Plans: Users can manage plans for their own projects
CREATE POLICY "Users can view their project plans"
  ON octupost.project_video_plans
  FOR SELECT
  USING (
    project_id IN (SELECT id FROM octupost.projects WHERE owner_id = auth.uid())
  );

CREATE POLICY "Users can create plans for their projects"
  ON octupost.project_video_plans
  FOR INSERT
  WITH CHECK (
    project_id IN (SELECT id FROM octupost.projects WHERE owner_id = auth.uid())
  );

CREATE POLICY "Users can update their project plans"
  ON octupost.project_video_plans
  FOR UPDATE
  USING (
    project_id IN (SELECT id FROM octupost.projects WHERE owner_id = auth.uid())
  );

CREATE POLICY "Users can delete their project plans"
  ON octupost.project_video_plans
  FOR DELETE
  USING (
    project_id IN (SELECT id FROM octupost.projects WHERE owner_id = auth.uid())
  );

-- Tasks: Users can manage tasks for their own projects
CREATE POLICY "Users can view their project tasks"
  ON octupost.project_tasks
  FOR SELECT
  USING (
    project_id IN (SELECT id FROM octupost.projects WHERE owner_id = auth.uid())
  );

CREATE POLICY "Users can create tasks for their projects"
  ON octupost.project_tasks
  FOR INSERT
  WITH CHECK (
    project_id IN (SELECT id FROM octupost.projects WHERE owner_id = auth.uid())
  );

CREATE POLICY "Users can update their project tasks"
  ON octupost.project_tasks
  FOR UPDATE
  USING (
    project_id IN (SELECT id FROM octupost.projects WHERE owner_id = auth.uid())
  );

CREATE POLICY "Users can delete their project tasks"
  ON octupost.project_tasks
  FOR DELETE
  USING (
    project_id IN (SELECT id FROM octupost.projects WHERE owner_id = auth.uid())
  );

-- Service role bypass for backend operations
CREATE POLICY "Service role full access to plans"
  ON octupost.project_video_plans
  FOR ALL
  USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to tasks"
  ON octupost.project_tasks
  FOR ALL
  USING (auth.role() = 'service_role');

-- =============================================================================
-- Enable Realtime for task progress updates
-- =============================================================================

ALTER PUBLICATION supabase_realtime ADD TABLE octupost.project_video_plans;
ALTER PUBLICATION supabase_realtime ADD TABLE octupost.project_tasks;

COMMENT ON TABLE octupost.project_video_plans IS 'Video creation plans awaiting user approval before execution';
COMMENT ON TABLE octupost.project_tasks IS 'Individual tasks within a video creation plan for progress tracking';
