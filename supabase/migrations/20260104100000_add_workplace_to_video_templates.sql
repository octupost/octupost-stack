-- Add workplace_id to video_templates for workspace-scoped templates
-- Supports three template scopes:
--   1. Community (is_system=true OR is_public=true, workplace_id=null) - visible to everyone
--   2. Workspace (workplace_id set) - visible to workspace members
--   3. Personal (user_id set, workplace_id=null, is_public=false) - visible only to creator

begin;

-- =============================================================================
-- Add workplace_id column
-- =============================================================================

alter table octupost.video_templates
    add column if not exists workplace_id uuid references octupost.workplaces(id) on delete cascade;

-- Index for efficient workspace queries
create index if not exists idx_video_templates_workplace_id
    on octupost.video_templates(workplace_id)
    where workplace_id is not null;

-- =============================================================================
-- Update RLS Policies for workspace support
-- =============================================================================

-- Drop existing policies to recreate them with workspace support
drop policy if exists "Anyone can view system templates" on octupost.video_templates;
drop policy if exists "Authenticated users can view public templates" on octupost.video_templates;
drop policy if exists "Users can view their own templates" on octupost.video_templates;
drop policy if exists "Users can create their own templates" on octupost.video_templates;
drop policy if exists "Users can update their own templates" on octupost.video_templates;
drop policy if exists "Users can delete their own templates" on octupost.video_templates;

-- =============================================================================
-- SELECT Policies
-- =============================================================================

-- 1. Community templates: system templates visible to everyone (including anon)
create policy "Anyone can view system templates"
    on octupost.video_templates for select
    using (is_system = true);

-- 2. Community templates: public templates visible to authenticated users
create policy "Authenticated users can view public templates"
    on octupost.video_templates for select
    to authenticated
    using (is_public = true and is_system = false);

-- 3. Workspace templates: visible to workspace members
create policy "Workspace members can view workspace templates"
    on octupost.video_templates for select
    to authenticated
    using (
        workplace_id is not null
        and exists (
            select 1 from octupost.workplace_members wm
            where wm.workplace_id = video_templates.workplace_id
            and wm.user_id = auth.uid()
        )
    );

-- 4. Personal templates: visible only to the creator
create policy "Users can view their own templates"
    on octupost.video_templates for select
    to authenticated
    using (
        user_id = auth.uid()
        and workplace_id is null
        and is_system = false
    );

-- =============================================================================
-- INSERT Policies
-- =============================================================================

-- Users can create personal templates (no workplace)
create policy "Users can create personal templates"
    on octupost.video_templates for insert
    to authenticated
    with check (
        user_id = auth.uid()
        and is_system = false
        and workplace_id is null
    );

-- Workspace members can create workspace templates
create policy "Workspace members can create workspace templates"
    on octupost.video_templates for insert
    to authenticated
    with check (
        workplace_id is not null
        and is_system = false
        and exists (
            select 1 from octupost.workplace_members wm
            where wm.workplace_id = video_templates.workplace_id
            and wm.user_id = auth.uid()
        )
    );

-- =============================================================================
-- UPDATE Policies
-- =============================================================================

-- Users can update their own personal templates
create policy "Users can update their own templates"
    on octupost.video_templates for update
    to authenticated
    using (
        user_id = auth.uid()
        and is_system = false
        and workplace_id is null
    )
    with check (
        user_id = auth.uid()
        and is_system = false
        and workplace_id is null
    );

-- Workspace owners/admins can update workspace templates
create policy "Workspace admins can update workspace templates"
    on octupost.video_templates for update
    to authenticated
    using (
        workplace_id is not null
        and is_system = false
        and exists (
            select 1 from octupost.workplace_members wm
            where wm.workplace_id = video_templates.workplace_id
            and wm.user_id = auth.uid()
            and wm.role in ('owner', 'admin')
        )
    )
    with check (
        workplace_id is not null
        and is_system = false
        and exists (
            select 1 from octupost.workplace_members wm
            where wm.workplace_id = video_templates.workplace_id
            and wm.user_id = auth.uid()
            and wm.role in ('owner', 'admin')
        )
    );

-- =============================================================================
-- DELETE Policies
-- =============================================================================

-- Users can delete their own personal templates
create policy "Users can delete their own templates"
    on octupost.video_templates for delete
    to authenticated
    using (
        user_id = auth.uid()
        and is_system = false
        and workplace_id is null
    );

-- Workspace owners/admins can delete workspace templates
create policy "Workspace admins can delete workspace templates"
    on octupost.video_templates for delete
    to authenticated
    using (
        workplace_id is not null
        and is_system = false
        and exists (
            select 1 from octupost.workplace_members wm
            where wm.workplace_id = video_templates.workplace_id
            and wm.user_id = auth.uid()
            and wm.role in ('owner', 'admin')
        )
    );

commit;
