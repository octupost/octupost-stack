-- Atomic Session Upsert Function
-- Prevents race condition when creating agent sessions
-- Uses COALESCE to keep existing session_id if one exists

begin;

-- Create atomic upsert function in octupost schema
create or replace function octupost.get_or_create_agent_session(
  p_project_id uuid,
  p_new_session_id text
)
returns text
language plpgsql
security definer
as $$
declare
  v_session_id text;
begin
  -- Atomic update: only set session_id if currently NULL
  update octupost.projects
  set agent_session_id = coalesce(agent_session_id, p_new_session_id)
  where id = p_project_id
  returning agent_session_id into v_session_id;

  return v_session_id;
end;
$$;

comment on function octupost.get_or_create_agent_session(uuid, text) is
'Atomically gets or creates an agent session ID for a project. Prevents race conditions by using COALESCE in a single UPDATE.';

commit;
