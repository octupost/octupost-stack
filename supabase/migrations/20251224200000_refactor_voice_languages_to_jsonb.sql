-- Refactor: Move language previews from separate table to JSONB column
-- Language support is model-dependent, not voice-dependent
-- Preview URLs per language are stored as JSONB for flexibility

begin;

-- =============================================================================
-- Step 1: Add preview_urls JSONB column
-- =============================================================================
alter table octupost.elevenlabs_voices
add column if not exists preview_urls jsonb not null default '{}';

-- =============================================================================
-- Step 2: Migrate data from voice_languages table to JSONB
-- =============================================================================
update octupost.elevenlabs_voices v
set preview_urls = (
  select jsonb_object_agg(l.language_code, l.preview_url)
  from octupost.elevenlabs_voice_languages l
  where l.voice_id = v.id
)
where exists (
  select 1 from octupost.elevenlabs_voice_languages l where l.voice_id = v.id
);

-- =============================================================================
-- Step 3: Drop the voice_languages table (no longer needed)
-- =============================================================================

-- Drop policies first
drop policy if exists "Users can read voice languages" on octupost.elevenlabs_voice_languages;
drop policy if exists "Users can insert own voice languages" on octupost.elevenlabs_voice_languages;
drop policy if exists "Users can update own voice languages" on octupost.elevenlabs_voice_languages;
drop policy if exists "Users can delete own voice languages" on octupost.elevenlabs_voice_languages;
drop policy if exists "Service role full access elevenlabs_voice_languages" on octupost.elevenlabs_voice_languages;

-- Drop the table
drop table if exists octupost.elevenlabs_voice_languages;

commit;
