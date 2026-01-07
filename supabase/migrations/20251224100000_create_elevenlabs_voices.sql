-- ElevenLabs Voices Schema
-- Stores voice metadata for TTS, including default voices and user-cloned voices

begin;

-- =============================================================================
-- Table: elevenlabs_voices
-- =============================================================================
create table if not exists octupost.elevenlabs_voices (
  id uuid primary key default gen_random_uuid(),
  elevenlabs_voice_id text not null,
  name text not null,
  category text not null check (category in ('premade', 'professional', 'cloned')),
  description text,
  preview_url text,
  labels jsonb not null default '{}',
  user_id uuid references auth.users(id) on delete cascade,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  -- Unique constraint: one voice per elevenlabs_voice_id per user (null for defaults)
  constraint elevenlabs_voices_unique unique nulls not distinct (elevenlabs_voice_id, user_id)
);

-- Indexes
create index if not exists idx_elevenlabs_voices_user_id on octupost.elevenlabs_voices(user_id);
create index if not exists idx_elevenlabs_voices_category on octupost.elevenlabs_voices(category);
create index if not exists idx_elevenlabs_voices_is_active on octupost.elevenlabs_voices(is_active);

-- =============================================================================
-- Table: elevenlabs_voice_languages
-- =============================================================================
create table if not exists octupost.elevenlabs_voice_languages (
  id uuid primary key default gen_random_uuid(),
  voice_id uuid not null references octupost.elevenlabs_voices(id) on delete cascade,
  language_code text not null,
  locale text,
  accent text,
  preview_url text not null,

  constraint elevenlabs_voice_languages_unique unique (voice_id, language_code)
);

-- Indexes
create index if not exists idx_elevenlabs_voice_languages_voice_id on octupost.elevenlabs_voice_languages(voice_id);
create index if not exists idx_elevenlabs_voice_languages_language_code on octupost.elevenlabs_voice_languages(language_code);

-- =============================================================================
-- RLS Policies
-- =============================================================================

-- Enable RLS
alter table octupost.elevenlabs_voices enable row level security;
alter table octupost.elevenlabs_voice_languages enable row level security;

-- Voices: users can read default voices (user_id IS NULL) and their own voices
create policy "Users can read default and own voices"
  on octupost.elevenlabs_voices for select
  using (user_id is null or auth.uid() = user_id);

-- Voices: users can insert their own voices
create policy "Users can insert own voices"
  on octupost.elevenlabs_voices for insert
  with check (auth.uid() = user_id);

-- Voices: users can update their own voices
create policy "Users can update own voices"
  on octupost.elevenlabs_voices for update
  using (auth.uid() = user_id);

-- Voices: users can delete their own voices
create policy "Users can delete own voices"
  on octupost.elevenlabs_voices for delete
  using (auth.uid() = user_id);

-- Voice languages: users can read languages for voices they can see
create policy "Users can read voice languages"
  on octupost.elevenlabs_voice_languages for select
  using (
    exists (
      select 1 from octupost.elevenlabs_voices v
      where v.id = voice_id
      and (v.user_id is null or v.user_id = auth.uid())
    )
  );

-- Voice languages: users can manage languages for their own voices
create policy "Users can insert own voice languages"
  on octupost.elevenlabs_voice_languages for insert
  with check (
    exists (
      select 1 from octupost.elevenlabs_voices v
      where v.id = voice_id and v.user_id = auth.uid()
    )
  );

create policy "Users can update own voice languages"
  on octupost.elevenlabs_voice_languages for update
  using (
    exists (
      select 1 from octupost.elevenlabs_voices v
      where v.id = voice_id and v.user_id = auth.uid()
    )
  );

create policy "Users can delete own voice languages"
  on octupost.elevenlabs_voice_languages for delete
  using (
    exists (
      select 1 from octupost.elevenlabs_voices v
      where v.id = voice_id and v.user_id = auth.uid()
    )
  );

-- Service role full access
create policy "Service role full access elevenlabs_voices"
  on octupost.elevenlabs_voices for all
  using (auth.role() = 'service_role');

create policy "Service role full access elevenlabs_voice_languages"
  on octupost.elevenlabs_voice_languages for all
  using (auth.role() = 'service_role');

-- =============================================================================
-- Seed Default Voices (user_id = NULL)
-- =============================================================================

insert into octupost.elevenlabs_voices (elevenlabs_voice_id, name, category, description, preview_url, labels, user_id)
values
  ('CwhRBWXzGAHq8TQ4Fs17', 'Roger - Laid-Back, Casual, Resonant', 'premade', 'Easy going and perfect for casual conversations.', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/CwhRBWXzGAHq8TQ4Fs17/58ee3ff5-f6f2-4628-93b8-e38eb31806b0.mp3', '{"accent": "american", "descriptive": "classy", "age": "middle_aged", "gender": "male", "language": "en", "use_case": "conversational"}', null),
  ('EXAVITQu4vr4xnSDxMaL', 'Sarah - Mature, Reassuring, Confident', 'premade', 'Young adult woman with a confident and warm, mature quality and a reassuring, professional tone.', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/EXAVITQu4vr4xnSDxMaL/01a3e33c-6e99-4ee7-8543-ff2216a32186.mp3', '{"accent": "american", "descriptive": "professional", "age": "young", "gender": "female", "language": "en", "use_case": "entertainment_tv"}', null),
  ('FGY2WhTYpPnrIDTdsKH5', 'Laura - Enthusiast, Quirky Attitude', 'premade', 'This young adult female voice delivers sunny enthusiasm with a quirky attitude.', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/FGY2WhTYpPnrIDTdsKH5/67341759-ad08-41a5-be6e-de12fe448618.mp3', '{"accent": "american", "descriptive": "sassy", "age": "young", "gender": "female", "language": "en", "use_case": "social_media"}', null),
  ('IKne3meq5aSn9XLyUdCD', 'Charlie - Deep, Confident, Energetic', 'premade', 'A young Australian male with a confident and energetic voice.', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/IKne3meq5aSn9XLyUdCD/102de6f2-22ed-43e0-a1f1-111fa75c5481.mp3', '{"accent": "australian", "descriptive": "hyped", "age": "young", "gender": "male", "language": "en", "use_case": "conversational"}', null),
  ('JBFqnCBsd6RMkjVDRZzb', 'George - Warm, Captivating Storyteller', 'premade', 'Warm resonance that instantly captivates listeners.', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/JBFqnCBsd6RMkjVDRZzb/e6206d1a-0721-4787-aafb-06a6e705cac5.mp3', '{"accent": "british", "descriptive": "mature", "age": "middle_aged", "gender": "male", "language": "en", "use_case": "narrative_story"}', null),
  ('N2lVS1w4EtoT3dr4eOWO', 'Callum - Husky Trickster', 'premade', 'Deceptively gravelly, yet unsettling edge.', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/N2lVS1w4EtoT3dr4eOWO/ac833bd8-ffda-4938-9ebc-b0f99ca25481.mp3', '{"accent": "american", "age": "middle_aged", "language": "en", "gender": "male", "use_case": "characters_animation"}', null),
  ('SAz9YHcvj6GT2YYXdXww', 'River - Relaxed, Neutral, Informative', 'premade', 'A relaxed, neutral voice ready for narrations or conversational projects.', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/SAz9YHcvj6GT2YYXdXww/e6c95f0b-2227-491a-b3d7-2249240decb7.mp3', '{"accent": "american", "descriptive": "calm", "age": "middle_aged", "gender": "neutral", "language": "en", "use_case": "conversational"}', null),
  ('SOYHLrjzK2X1ezoPC6cr', 'Harry - Fierce Warrior', 'premade', 'An animated warrior ready to charge forward.', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/SOYHLrjzK2X1ezoPC6cr/86d178f6-f4b6-4e0e-85be-3de19f490794.mp3', '{"accent": "american", "descriptive": "rough", "age": "young", "gender": "male", "language": "en", "use_case": "characters_animation"}', null),
  ('TX3LPaxmHKxFdv7VOQHJ', 'Liam - Energetic, Social Media Creator', 'premade', 'A young adult with energy and warmth - suitable for reels and shorts.', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/TX3LPaxmHKxFdv7VOQHJ/63148076-6363-42db-aea8-31424308b92c.mp3', '{"accent": "american", "descriptive": "confident", "age": "young", "gender": "male", "language": "en", "use_case": "social_media"}', null),
  ('Xb7hH8MSUJpSbSDYk0k2', 'Alice - Clear, Engaging Educator', 'premade', 'Clear and engaging, friendly woman with a British accent suitable for e-learning.', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/Xb7hH8MSUJpSbSDYk0k2/d10f7534-11f6-41fe-a012-2de1e482d336.mp3', '{"accent": "british", "descriptive": "professional", "age": "middle_aged", "gender": "female", "language": "en", "use_case": "informative_educational"}', null),
  ('XrExE9yKIg1WjnnlVkGX', 'Matilda - Knowledgable, Professional', 'premade', 'A professional woman with a pleasing alto pitch. Suitable for many use cases.', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/XrExE9yKIg1WjnnlVkGX/b930e18d-6b4d-466e-bab2-0ae97c6d8535.mp3', '{"accent": "american", "descriptive": "upbeat", "age": "middle_aged", "gender": "female", "language": "en", "use_case": "informative_educational"}', null),
  ('bIHbv24MWmeRgasZH58o', 'Will - Relaxed Optimist', 'premade', 'Conversational and laid back.', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/bIHbv24MWmeRgasZH58o/8caf8f3d-ad29-4980-af41-53f20c72d7a4.mp3', '{"accent": "american", "descriptive": "chill", "age": "young", "gender": "male", "language": "en", "use_case": "conversational"}', null),
  ('cgSgspJ2msm6clMCkdW9', 'Jessica - Playful, Bright, Warm', 'premade', 'Young and popular, this playful American female voice is perfect for trendy content.', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/cgSgspJ2msm6clMCkdW9/56a97bf8-b69b-448f-846c-c3a11683d45a.mp3', '{"accent": "american", "descriptive": "cute", "age": "young", "gender": "female", "language": "en", "use_case": "conversational"}', null),
  ('cjVigY5qzO86Huf0OWal', 'Eric - Smooth, Trustworthy', 'premade', 'A smooth tenor pitch from a man in his 40s - perfect for agentic use cases.', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/cjVigY5qzO86Huf0OWal/d098fda0-6456-4030-b3d8-63aa048c9070.mp3', '{"accent": "american", "descriptive": "classy", "age": "middle_aged", "gender": "male", "language": "en", "use_case": "conversational"}', null),
  ('iP95p4xoKVk53GoZ742B', 'Chris - Charming, Down-to-Earth', 'premade', 'Natural and real, this down-to-earth voice is great across many use-cases.', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/iP95p4xoKVk53GoZ742B/3f4bde72-cc48-40dd-829f-57fbf906f4d7.mp3', '{"accent": "american", "descriptive": "casual", "age": "middle_aged", "gender": "male", "language": "en", "use_case": "conversational"}', null),
  ('nPczCjzI2devNBz1zQrb', 'Brian - Deep, Resonant and Comforting', 'premade', 'Middle-aged man with a resonant and comforting tone. Great for narrations and advertisements.', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/nPczCjzI2devNBz1zQrb/2dd3e72c-4fd3-42f1-93ea-abc5d4e5aa1d.mp3', '{"accent": "american", "descriptive": "classy", "age": "middle_aged", "gender": "male", "language": "en", "use_case": "social_media"}', null),
  ('onwK4e9ZLuTAKqWW03F9', 'Daniel - Steady Broadcaster', 'premade', 'A strong voice perfect for delivering a professional broadcast or news story.', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/onwK4e9ZLuTAKqWW03F9/7eee0236-1a72-4b86-b303-5dcadc007ba9.mp3', '{"accent": "british", "descriptive": "formal", "age": "middle_aged", "gender": "male", "language": "en", "use_case": "informative_educational"}', null),
  ('pFZP5JQG7iQjIQuC4Bku', 'Lily - Velvety Actress', 'premade', 'Velvety British female voice delivers news and narrations with warmth and clarity.', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/pFZP5JQG7iQjIQuC4Bku/89b68b35-b3dd-4348-a84a-a3c13a3c2b30.mp3', '{"accent": "british", "descriptive": "confident", "age": "middle_aged", "gender": "female", "language": "en", "use_case": "informative_educational"}', null),
  ('pNInz6obpgDQGcFmaJgB', 'Adam - Dominant, Firm', 'premade', 'A bright tenor pitch that immediately cuts through. The delivery is brash and openly confident, speaking with unwavering certainty and a slightly aggressive self-assurance.', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/pNInz6obpgDQGcFmaJgB/d6905d7a-dd26-4187-bfff-1bd3a5ea7cac.mp3', '{"accent": "american", "age": "middle_aged", "language": "en", "gender": "male", "use_case": "social_media"}', null),
  ('pqHfZKP75CvOlQylNhV4', 'Bill - Wise, Mature, Balanced', 'premade', 'Friendly and comforting voice ready to narrate your stories.', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/pqHfZKP75CvOlQylNhV4/d782b3ff-84ba-4029-848c-acf01285524d.mp3', '{"accent": "american", "descriptive": "crisp", "age": "old", "gender": "male", "language": "en", "use_case": "advertisement"}', null),
  ('EkK5I93UQWFDigLMpZcX', 'James - Husky & Engaging', 'professional', 'A slightly husky and bassy voice with a standard American accent. Modulated, controlled, and direct and perfect for audiobooks, captivating narrations, or storytelling, or other professional voiceover work.', 'https://storage.googleapis.com/eleven-public-prod/database/workspace/48ab3aae468d4e9baded4b1693820088/voices/EkK5I93UQWFDigLMpZcX/xvjT3EK4vD3zlwfawHeV.mp3', '{"accent": "american", "descriptive": "deep", "age": "middle_aged", "gender": "male", "language": "en", "use_case": "narrative_story"}', null);

-- =============================================================================
-- Seed Language Previews
-- =============================================================================

insert into octupost.elevenlabs_voice_languages (voice_id, language_code, locale, accent, preview_url)
select v.id, lang.language_code, lang.locale, lang.accent, lang.preview_url
from (values
  -- Roger
  ('CwhRBWXzGAHq8TQ4Fs17', 'en', 'en-US', 'american', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/CwhRBWXzGAHq8TQ4Fs17/58ee3ff5-f6f2-4628-93b8-e38eb31806b0.mp3'),
  ('CwhRBWXzGAHq8TQ4Fs17', 'fr', 'fr-FR', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/CwhRBWXzGAHq8TQ4Fs17/042d9b70-5927-4630-985e-e95107b74ec2.mp3'),
  ('CwhRBWXzGAHq8TQ4Fs17', 'de', 'de-DE', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/CwhRBWXzGAHq8TQ4Fs17/fa6a7658-18a9-4634-a96f-95dc3c47629d.mp3'),
  ('CwhRBWXzGAHq8TQ4Fs17', 'nl', 'nl-NL', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/CwhRBWXzGAHq8TQ4Fs17/12a2ba8b-4fb3-44b6-9bc7-da0afd076fc9.mp3'),
  ('CwhRBWXzGAHq8TQ4Fs17', 'es', 'es-ES', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/CwhRBWXzGAHq8TQ4Fs17/f172f037-5e23-44ea-a08e-56ddb6447d5b.mp3'),
  -- Sarah
  ('EXAVITQu4vr4xnSDxMaL', 'en', 'en-US', 'american', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/EXAVITQu4vr4xnSDxMaL/01a3e33c-6e99-4ee7-8543-ff2216a32186.mp3'),
  ('EXAVITQu4vr4xnSDxMaL', 'fr', 'fr-FR', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/EXAVITQu4vr4xnSDxMaL/093154f2-dd9f-4a4c-b5c3-81836c7ac3f6.mp3'),
  ('EXAVITQu4vr4xnSDxMaL', 'ar', null, 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/EXAVITQu4vr4xnSDxMaL/ecb43dfe-b9f3-4691-8ee8-90c5ad3f4dbb.mp3'),
  ('EXAVITQu4vr4xnSDxMaL', 'zh', 'cmn-CN', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/EXAVITQu4vr4xnSDxMaL/d9b9f54d-c08b-426e-80f3-b4f2089c3a59.mp3'),
  ('EXAVITQu4vr4xnSDxMaL', 'es', 'es-ES', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/EXAVITQu4vr4xnSDxMaL/57ab5344-ed96-46fc-b319-82dc1c89bf66.mp3'),
  ('EXAVITQu4vr4xnSDxMaL', 'hi', 'hi-IN', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/EXAVITQu4vr4xnSDxMaL/2f2caaae-ad5e-4ff2-a084-7a6067913a69.mp3'),
  -- Laura
  ('FGY2WhTYpPnrIDTdsKH5', 'en', 'en-US', 'american', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/FGY2WhTYpPnrIDTdsKH5/67341759-ad08-41a5-be6e-de12fe448618.mp3'),
  ('FGY2WhTYpPnrIDTdsKH5', 'fr', 'fr-FR', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/FGY2WhTYpPnrIDTdsKH5/21082ee9-c176-4454-ac50-54bdf230ef49.mp3'),
  ('FGY2WhTYpPnrIDTdsKH5', 'ar', null, 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/FGY2WhTYpPnrIDTdsKH5/ec8fcd73-ed00-4478-ad2f-0dca5c5a5583.mp3'),
  ('FGY2WhTYpPnrIDTdsKH5', 'zh', 'cmn-CN', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/FGY2WhTYpPnrIDTdsKH5/56e58899-8324-4908-a617-3e7710251c39.mp3'),
  ('FGY2WhTYpPnrIDTdsKH5', 'de', 'de-DE', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/FGY2WhTYpPnrIDTdsKH5/210e72ad-ba9e-475e-9e18-000bc7cd771c.mp3'),
  -- Charlie
  ('IKne3meq5aSn9XLyUdCD', 'en', 'en-AU', 'australian', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/IKne3meq5aSn9XLyUdCD/102de6f2-22ed-43e0-a1f1-111fa75c5481.mp3'),
  ('IKne3meq5aSn9XLyUdCD', 'zh', 'cmn-CN', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/IKne3meq5aSn9XLyUdCD/51392837-4691-4e9c-a11d-658848033ace.mp3'),
  ('IKne3meq5aSn9XLyUdCD', 'pt', 'pt-BR', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/IKne3meq5aSn9XLyUdCD/f1d38c1a-b69a-44f5-9d91-76d17dcce479.mp3'),
  ('IKne3meq5aSn9XLyUdCD', 'fil', 'fil-PH', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/IKne3meq5aSn9XLyUdCD/7eae8500-ea92-47c1-95fc-394cf3bc45d2.mp3'),
  ('IKne3meq5aSn9XLyUdCD', 'es', 'es-ES', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/IKne3meq5aSn9XLyUdCD/52f3846a-eee1-43e4-bcd1-0280f20fe202.mp3'),
  -- George
  ('JBFqnCBsd6RMkjVDRZzb', 'en', 'en-GB', 'british', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/JBFqnCBsd6RMkjVDRZzb/e6206d1a-0721-4787-aafb-06a6e705cac5.mp3'),
  ('JBFqnCBsd6RMkjVDRZzb', 'fr', 'fr-FR', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/JBFqnCBsd6RMkjVDRZzb/6096acce-e18f-4e95-a8e3-bb1c0a27624e.mp3'),
  ('JBFqnCBsd6RMkjVDRZzb', 'ar', null, 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/JBFqnCBsd6RMkjVDRZzb/0ece09f9-7d3e-4031-af75-936aa0cda577.mp3'),
  ('JBFqnCBsd6RMkjVDRZzb', 'ja', 'ja-JP', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/JBFqnCBsd6RMkjVDRZzb/709a894a-d0d1-46d7-9c10-3b140e3a69f2.mp3'),
  ('JBFqnCBsd6RMkjVDRZzb', 'cs', 'cs-CZ', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/JBFqnCBsd6RMkjVDRZzb/4347a4c3-142a-4490-9777-00671ef3855c.mp3'),
  ('JBFqnCBsd6RMkjVDRZzb', 'fil', 'fil-PH', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/JBFqnCBsd6RMkjVDRZzb/924cfaf5-c7db-49fe-b835-7d37ca424314.mp3'),
  ('JBFqnCBsd6RMkjVDRZzb', 'es', 'es-ES', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/JBFqnCBsd6RMkjVDRZzb/eae50a0d-5a39-4795-9b1e-1d58f7f87e63.mp3'),
  ('JBFqnCBsd6RMkjVDRZzb', 'hi', 'hi-IN', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/JBFqnCBsd6RMkjVDRZzb/15c58de3-5d6c-461a-8111-c473fd185573.mp3'),
  -- Callum
  ('N2lVS1w4EtoT3dr4eOWO', 'en', 'en-US', 'american', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/N2lVS1w4EtoT3dr4eOWO/ac833bd8-ffda-4938-9ebc-b0f99ca25481.mp3'),
  ('N2lVS1w4EtoT3dr4eOWO', 'fr', 'fr-FR', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/N2lVS1w4EtoT3dr4eOWO/cae55f06-da58-4810-ad48-5e6eb0fe72a9.mp3'),
  ('N2lVS1w4EtoT3dr4eOWO', 'hi', 'hi-IN', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/N2lVS1w4EtoT3dr4eOWO/b4465e6f-051d-4e0b-b588-617ff34de35b.mp3'),
  -- River
  ('SAz9YHcvj6GT2YYXdXww', 'en', 'en-US', 'american', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/SAz9YHcvj6GT2YYXdXww/e6c95f0b-2227-491a-b3d7-2249240decb7.mp3'),
  ('SAz9YHcvj6GT2YYXdXww', 'it', 'it-IT', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/SAz9YHcvj6GT2YYXdXww/62da5f17-c5cb-48bb-ad7c-e0b7623d16cc.mp3'),
  ('SAz9YHcvj6GT2YYXdXww', 'fr', 'fr-FR', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/SAz9YHcvj6GT2YYXdXww/cd628aed-b6a3-463a-b96f-1e7eebd34f04.mp3'),
  ('SAz9YHcvj6GT2YYXdXww', 'pt', 'pt-BR', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/SAz9YHcvj6GT2YYXdXww/81a2500f-c016-4ca1-a9b9-09ab065a084f.mp3'),
  ('SAz9YHcvj6GT2YYXdXww', 'zh', 'cmn-CN', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/SAz9YHcvj6GT2YYXdXww/cf733b36-9256-4224-9890-20c67ada259c.mp3'),
  -- Harry
  ('SOYHLrjzK2X1ezoPC6cr', 'en', 'en-US', 'american', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/SOYHLrjzK2X1ezoPC6cr/86d178f6-f4b6-4e0e-85be-3de19f490794.mp3'),
  -- Liam
  ('TX3LPaxmHKxFdv7VOQHJ', 'en', 'en-US', 'american', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/TX3LPaxmHKxFdv7VOQHJ/63148076-6363-42db-aea8-31424308b92c.mp3'),
  ('TX3LPaxmHKxFdv7VOQHJ', 'de', 'de-DE', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/TX3LPaxmHKxFdv7VOQHJ/9d63d255-b011-4231-a945-fd5a64d94bfc.mp3'),
  ('TX3LPaxmHKxFdv7VOQHJ', 'pt', 'pt-BR', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/TX3LPaxmHKxFdv7VOQHJ/56d7e6ac-b450-48e0-ba68-ff47921b7241.mp3'),
  ('TX3LPaxmHKxFdv7VOQHJ', 'cs', 'cs-CZ', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/TX3LPaxmHKxFdv7VOQHJ/e87b9bfb-9aee-4106-ad72-81b6982dea22.mp3'),
  ('TX3LPaxmHKxFdv7VOQHJ', 'pl', 'pl-PL', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/TX3LPaxmHKxFdv7VOQHJ/0100273d-0f0e-4560-9803-84af8f7e8809.mp3'),
  ('TX3LPaxmHKxFdv7VOQHJ', 'tr', 'tr-TR', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/TX3LPaxmHKxFdv7VOQHJ/172d9bf5-8094-4438-b06f-b382ead09a2f.mp3'),
  ('TX3LPaxmHKxFdv7VOQHJ', 'hi', 'hi-IN', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/TX3LPaxmHKxFdv7VOQHJ/437fbcd7-782a-42c0-b813-307a2e5089d6.mp3'),
  -- Alice
  ('Xb7hH8MSUJpSbSDYk0k2', 'en', 'en-GB', 'british', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/Xb7hH8MSUJpSbSDYk0k2/d10f7534-11f6-41fe-a012-2de1e482d336.mp3'),
  ('Xb7hH8MSUJpSbSDYk0k2', 'it', 'it-IT', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/Xb7hH8MSUJpSbSDYk0k2/5cb52c82-8152-47f0-a959-58df75b33fac.mp3'),
  ('Xb7hH8MSUJpSbSDYk0k2', 'fr', 'fr-FR', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/Xb7hH8MSUJpSbSDYk0k2/8078faa3-8ac4-4e55-b9ae-2d43a17fba42.mp3'),
  ('Xb7hH8MSUJpSbSDYk0k2', 'ar', null, 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/Xb7hH8MSUJpSbSDYk0k2/0d220e32-be6e-42b5-b478-38dd287887c8.mp3'),
  ('Xb7hH8MSUJpSbSDYk0k2', 'ja', 'ja-JP', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/Xb7hH8MSUJpSbSDYk0k2/290e5e0e-485a-4206-9f86-b687eed71132.mp3'),
  ('Xb7hH8MSUJpSbSDYk0k2', 'pl', 'pl-PL', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/Xb7hH8MSUJpSbSDYk0k2/bed01e1d-3dec-4c78-bb58-c3e7299cec23.mp3'),
  ('Xb7hH8MSUJpSbSDYk0k2', 'hi', 'hi-IN', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/Xb7hH8MSUJpSbSDYk0k2/063f6922-9fc5-44d7-b9ca-d5b0ed6eeb98.mp3'),
  -- Matilda
  ('XrExE9yKIg1WjnnlVkGX', 'en', 'en-US', 'american', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/XrExE9yKIg1WjnnlVkGX/b930e18d-6b4d-466e-bab2-0ae97c6d8535.mp3'),
  ('XrExE9yKIg1WjnnlVkGX', 'it', 'it-IT', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/XrExE9yKIg1WjnnlVkGX/68da6da6-38b0-4de9-b941-1345c4503948.mp3'),
  ('XrExE9yKIg1WjnnlVkGX', 'fr', 'fr-FR', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/XrExE9yKIg1WjnnlVkGX/40f2148b-d09e-4f24-97b6-66aafef1b0bb.mp3'),
  ('XrExE9yKIg1WjnnlVkGX', 'de', 'de-DE', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/XrExE9yKIg1WjnnlVkGX/9d8aab27-268f-4fea-9815-7da3938539d1.mp3'),
  ('XrExE9yKIg1WjnnlVkGX', 'ar', null, 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/XrExE9yKIg1WjnnlVkGX/3c5bb9c4-a406-4d10-b61d-275c18e84f26.mp3'),
  ('XrExE9yKIg1WjnnlVkGX', 'es', 'es-ES', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/XrExE9yKIg1WjnnlVkGX/20291a6d-1e7f-45e4-9d85-a764997a2fdb.mp3'),
  -- Will
  ('bIHbv24MWmeRgasZH58o', 'en', 'en-US', 'american', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/bIHbv24MWmeRgasZH58o/8caf8f3d-ad29-4980-af41-53f20c72d7a4.mp3'),
  ('bIHbv24MWmeRgasZH58o', 'fr', 'fr-FR', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/bIHbv24MWmeRgasZH58o/a46e8450-1b81-4370-adbc-f6b504a409ad.mp3'),
  ('bIHbv24MWmeRgasZH58o', 'de', 'de-DE', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/bIHbv24MWmeRgasZH58o/20efefbb-9e19-4808-97f1-9c7ae0eebf7b.mp3'),
  ('bIHbv24MWmeRgasZH58o', 'pt', 'pt-BR', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/bIHbv24MWmeRgasZH58o/8e6ace43-9e5a-413d-a491-2ec365e0a2ae.mp3'),
  ('bIHbv24MWmeRgasZH58o', 'zh', 'cmn-CN', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/bIHbv24MWmeRgasZH58o/2c7ea680-0d76-4ac5-a77a-765e59417560.mp3'),
  ('bIHbv24MWmeRgasZH58o', 'cs', 'cs-CZ', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/bIHbv24MWmeRgasZH58o/b6b630a8-eda6-4972-a527-bfcde1df0b7c.mp3'),
  ('bIHbv24MWmeRgasZH58o', 'fil', 'fil-PH', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/bIHbv24MWmeRgasZH58o/7890ca34-065a-4d2f-a2db-2102909c96a4.mp3'),
  ('bIHbv24MWmeRgasZH58o', 'sk', 'sk-SK', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/bIHbv24MWmeRgasZH58o/3dc86617-878a-4964-a464-3b9d39113d2a.mp3'),
  ('bIHbv24MWmeRgasZH58o', 'es', 'es-ES', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/bIHbv24MWmeRgasZH58o/9b17b1ba-98f6-4c6d-9da7-dc03a76bc50c.mp3'),
  ('bIHbv24MWmeRgasZH58o', 'sv', 'sv-SE', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/bIHbv24MWmeRgasZH58o/090d5fe3-c80a-4990-b536-e83f33d23fe1.mp3'),
  -- Jessica
  ('cgSgspJ2msm6clMCkdW9', 'en', 'en-US', 'american', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/cgSgspJ2msm6clMCkdW9/56a97bf8-b69b-448f-846c-c3a11683d45a.mp3'),
  ('cgSgspJ2msm6clMCkdW9', 'fr', 'fr-FR', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/cgSgspJ2msm6clMCkdW9/83ed5b34-be48-4473-93f8-58633129bc87.mp3'),
  ('cgSgspJ2msm6clMCkdW9', 'ar', null, 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/cgSgspJ2msm6clMCkdW9/114425d8-26e7-4b3d-aa31-52ab8bbdcbed.mp3'),
  ('cgSgspJ2msm6clMCkdW9', 'ja', 'ja-JP', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/cgSgspJ2msm6clMCkdW9/a4011375-88c2-4469-a61b-96b0fb239caf.mp3'),
  ('cgSgspJ2msm6clMCkdW9', 'zh', 'cmn-CN', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/cgSgspJ2msm6clMCkdW9/6f4a6924-34c9-465a-9017-707f7e823e24.mp3'),
  ('cgSgspJ2msm6clMCkdW9', 'de', 'de-DE', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/cgSgspJ2msm6clMCkdW9/eb773c99-fcf2-4f0c-ace5-84dc43880c34.mp3'),
  ('cgSgspJ2msm6clMCkdW9', 'cs', 'cs-CZ', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/cgSgspJ2msm6clMCkdW9/9fdd6daa-383a-47b8-97be-fbec0cfbe4e2.mp3'),
  ('cgSgspJ2msm6clMCkdW9', 'hi', 'hi-IN', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/cgSgspJ2msm6clMCkdW9/3a9a4248-9eb3-4e12-8823-f3766c3fd48f.mp3'),
  -- Eric
  ('cjVigY5qzO86Huf0OWal', 'en', 'en-US', 'american', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/cjVigY5qzO86Huf0OWal/d098fda0-6456-4030-b3d8-63aa048c9070.mp3'),
  ('cjVigY5qzO86Huf0OWal', 'fr', 'fr-FR', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/cjVigY5qzO86Huf0OWal/4c076868-22c6-42a6-9edd-b836f6a33f9f.mp3'),
  ('cjVigY5qzO86Huf0OWal', 'pt', 'pt-BR', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/cjVigY5qzO86Huf0OWal/c893545f-603a-4023-ae26-0b779ab9e8c2.mp3'),
  ('cjVigY5qzO86Huf0OWal', 'de', 'de-DE', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/cjVigY5qzO86Huf0OWal/e8e9e810-3ef3-4992-a61f-4a43279b6909.mp3'),
  ('cjVigY5qzO86Huf0OWal', 'sk', 'sk-SK', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/cjVigY5qzO86Huf0OWal/99655517-0f65-49b4-8d88-bd2a40821e65.mp3'),
  ('cjVigY5qzO86Huf0OWal', 'es', 'es-ES', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/cjVigY5qzO86Huf0OWal/4d56a844-3fc5-4048-b8d9-daff582c2746.mp3'),
  -- Chris
  ('iP95p4xoKVk53GoZ742B', 'en', 'en-US', 'american', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/iP95p4xoKVk53GoZ742B/3f4bde72-cc48-40dd-829f-57fbf906f4d7.mp3'),
  ('iP95p4xoKVk53GoZ742B', 'fr', 'fr-FR', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/iP95p4xoKVk53GoZ742B/34ab53c0-7f77-4624-a26b-65b58394ea69.mp3'),
  ('iP95p4xoKVk53GoZ742B', 'ar', null, 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/iP95p4xoKVk53GoZ742B/ffdde76f-4afa-4933-94fc-6c015b4b497e.mp3'),
  ('iP95p4xoKVk53GoZ742B', 'pt', 'pt-BR', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/iP95p4xoKVk53GoZ742B/00131b8d-38d7-4f63-91ed-91ddbe227a7d.mp3'),
  ('iP95p4xoKVk53GoZ742B', 'sv', 'sv-SE', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/iP95p4xoKVk53GoZ742B/8710d1a0-bea3-41c9-a051-e5a4593f6a32.mp3'),
  ('iP95p4xoKVk53GoZ742B', 'hi', 'hi-IN', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/iP95p4xoKVk53GoZ742B/a0a92736-9321-4bbc-9677-c84b84d3f30b.mp3'),
  -- Brian
  ('nPczCjzI2devNBz1zQrb', 'en', 'en-US', 'american', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/nPczCjzI2devNBz1zQrb/2dd3e72c-4fd3-42f1-93ea-abc5d4e5aa1d.mp3'),
  ('nPczCjzI2devNBz1zQrb', 'ar', null, 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/nPczCjzI2devNBz1zQrb/e56be0c3-fc89-4529-8248-9726d42175fb.mp3'),
  ('nPczCjzI2devNBz1zQrb', 'zh', 'cmn-CN', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/nPczCjzI2devNBz1zQrb/0bfb8e30-e0e8-44d9-9276-22af13da50b3.mp3'),
  ('nPczCjzI2devNBz1zQrb', 'pt', 'pt-BR', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/nPczCjzI2devNBz1zQrb/7c88e63a-f321-40d6-ac25-899559a3ff26.mp3'),
  ('nPczCjzI2devNBz1zQrb', 'de', 'de-DE', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/nPczCjzI2devNBz1zQrb/0b33b286-75f0-404f-bcec-68a56e6b37e8.mp3'),
  ('nPczCjzI2devNBz1zQrb', 'nl', 'nl-NL', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/nPczCjzI2devNBz1zQrb/d3e8efb2-0c52-4288-85d7-4fde1ea4b9cf.mp3'),
  ('nPczCjzI2devNBz1zQrb', 'sk', 'sk-SK', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/nPczCjzI2devNBz1zQrb/f743b7c8-71b8-447a-9744-d66d11dcabac.mp3'),
  ('nPczCjzI2devNBz1zQrb', 'ro', 'ro-RO', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/nPczCjzI2devNBz1zQrb/75b05b25-29ce-44b8-bbc4-f42600da8c5c.mp3'),
  ('nPczCjzI2devNBz1zQrb', 'hi', 'hi-IN', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/nPczCjzI2devNBz1zQrb/945c1b51-4743-43ae-b0e7-7cab7e08a85e.mp3'),
  -- Daniel
  ('onwK4e9ZLuTAKqWW03F9', 'en', 'en-GB', 'british', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/onwK4e9ZLuTAKqWW03F9/7eee0236-1a72-4b86-b303-5dcadc007ba9.mp3'),
  ('onwK4e9ZLuTAKqWW03F9', 'de', 'de-DE', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/onwK4e9ZLuTAKqWW03F9/7c30c661-8448-4a1e-b7b7-b5b629ec641b.mp3'),
  ('onwK4e9ZLuTAKqWW03F9', 'tr', 'tr-TR', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/onwK4e9ZLuTAKqWW03F9/f56723eb-7529-4617-bc87-5cf65658e538.mp3'),
  -- Lily
  ('pFZP5JQG7iQjIQuC4Bku', 'en', 'en-GB', 'british', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/pFZP5JQG7iQjIQuC4Bku/89b68b35-b3dd-4348-a84a-a3c13a3c2b30.mp3'),
  ('pFZP5JQG7iQjIQuC4Bku', 'it', 'it-IT', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/pFZP5JQG7iQjIQuC4Bku/b2edb800-06a3-4d47-9bb7-461c2e5af7b2.mp3'),
  ('pFZP5JQG7iQjIQuC4Bku', 'de', 'de-DE', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/pFZP5JQG7iQjIQuC4Bku/0c5c2b73-34b6-4d17-ae2f-f4e4cb7b0636.mp3'),
  ('pFZP5JQG7iQjIQuC4Bku', 'zh', 'cmn-CN', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/pFZP5JQG7iQjIQuC4Bku/288da6a0-85aa-4705-b033-73d5304cdbaa.mp3'),
  ('pFZP5JQG7iQjIQuC4Bku', 'cs', 'cs-CZ', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/pFZP5JQG7iQjIQuC4Bku/f13ad751-dcab-45d0-9b3d-cb8b3b9e3f1d.mp3'),
  ('pFZP5JQG7iQjIQuC4Bku', 'nl', 'nl-NL', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/pFZP5JQG7iQjIQuC4Bku/86353d12-c42f-4e3e-afc2-a574c7030884.mp3'),
  ('pFZP5JQG7iQjIQuC4Bku', 'pl', 'pl-PL', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/pFZP5JQG7iQjIQuC4Bku/646f864e-fe42-42b2-a757-3da7b80275c2.mp3'),
  -- Adam
  ('pNInz6obpgDQGcFmaJgB', 'en', 'en-US', 'american', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/pNInz6obpgDQGcFmaJgB/d6905d7a-dd26-4187-bfff-1bd3a5ea7cac.mp3'),
  -- Bill
  ('pqHfZKP75CvOlQylNhV4', 'en', 'en-US', 'american', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/pqHfZKP75CvOlQylNhV4/d782b3ff-84ba-4029-848c-acf01285524d.mp3'),
  ('pqHfZKP75CvOlQylNhV4', 'fr', 'fr-FR', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/pqHfZKP75CvOlQylNhV4/ef978e66-26c2-446e-94fc-81b4362d71b1.mp3'),
  ('pqHfZKP75CvOlQylNhV4', 'ar', null, 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/pqHfZKP75CvOlQylNhV4/617b7973-2e00-462e-bcd9-dc324db17ecc.mp3'),
  ('pqHfZKP75CvOlQylNhV4', 'zh', 'cmn-CN', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/pqHfZKP75CvOlQylNhV4/3e232368-c1ea-4548-a41d-048c8406a645.mp3'),
  ('pqHfZKP75CvOlQylNhV4', 'de', 'de-DE', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/pqHfZKP75CvOlQylNhV4/a1eee806-7c72-46c4-9270-dc9256ddffe6.mp3'),
  ('pqHfZKP75CvOlQylNhV4', 'cs', 'cs-CZ', 'standard', 'https://storage.googleapis.com/eleven-public-prod/premade/voices/pqHfZKP75CvOlQylNhV4/bf99c000-ca7f-4445-847c-b01e00ec063b.mp3'),
  -- James (professional)
  ('EkK5I93UQWFDigLMpZcX', 'en', 'en-US', 'american', 'https://storage.googleapis.com/eleven-public-prod/database/workspace/48ab3aae468d4e9baded4b1693820088/voices/EkK5I93UQWFDigLMpZcX/xvjT3EK4vD3zlwfawHeV.mp3'),
  ('EkK5I93UQWFDigLMpZcX', 'hu', 'hu-HU', 'standard', 'https://storage.googleapis.com/eleven-public-prod/database/workspace/48ab3aae468d4e9baded4b1693820088/voices/EkK5I93UQWFDigLMpZcX/e4d34109-8c70-46ca-8657-1515a4259454.mp3'),
  ('EkK5I93UQWFDigLMpZcX', 'tr', 'tr-TR', 'standard', 'https://storage.googleapis.com/eleven-public-prod/database/workspace/48ab3aae468d4e9baded4b1693820088/voices/EkK5I93UQWFDigLMpZcX/82dd8f8c-bc89-407d-bed5-81c53a44d0ad.mp3'),
  ('EkK5I93UQWFDigLMpZcX', 'ms', 'ms-MY', 'standard', 'https://storage.googleapis.com/eleven-public-prod/database/workspace/48ab3aae468d4e9baded4b1693820088/voices/EkK5I93UQWFDigLMpZcX/d6e6bdbb-5f0b-42cd-9fa2-1b0b2ea42a58.mp3'),
  ('EkK5I93UQWFDigLMpZcX', 'ru', 'ru-RU', 'standard', 'https://storage.googleapis.com/eleven-public-prod/database/workspace/48ab3aae468d4e9baded4b1693820088/voices/EkK5I93UQWFDigLMpZcX/b99ef7b0-71e9-4d2b-98ab-b8a6411e3b2f.mp3'),
  ('EkK5I93UQWFDigLMpZcX', 'el', 'el-GR', 'standard', 'https://storage.googleapis.com/eleven-public-prod/database/workspace/48ab3aae468d4e9baded4b1693820088/voices/EkK5I93UQWFDigLMpZcX/a0912c5b-ba55-4b5e-bdb6-cf4acee1b549.mp3'),
  ('EkK5I93UQWFDigLMpZcX', 'hr', 'hr-HR', 'standard', 'https://storage.googleapis.com/eleven-public-prod/database/workspace/48ab3aae468d4e9baded4b1693820088/voices/EkK5I93UQWFDigLMpZcX/02cda600-f67f-40b8-9d9a-f20aba9c6e01.mp3'),
  ('EkK5I93UQWFDigLMpZcX', 'ta', 'ta-IN', 'standard', 'https://storage.googleapis.com/eleven-public-prod/database/workspace/48ab3aae468d4e9baded4b1693820088/voices/EkK5I93UQWFDigLMpZcX/6b7ed5d2-f66a-4dfc-a1b4-60f5dafdbc96.mp3')
) as lang(elevenlabs_voice_id, language_code, locale, accent, preview_url)
join octupost.elevenlabs_voices v on v.elevenlabs_voice_id = lang.elevenlabs_voice_id and v.user_id is null;

commit;
