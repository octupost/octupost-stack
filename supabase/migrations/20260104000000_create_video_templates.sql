-- Create video_templates table for storing full video composition templates
-- These are complete template overlays that can be applied to projects

begin;

-- =============================================================================
-- Table: video_templates
-- =============================================================================
-- Stores full video composition templates with all overlays.
-- Can be system-wide (user_id = null, is_system = true) or user-created.

create table if not exists octupost.video_templates (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references auth.users(id) on delete cascade,

    -- Template identification
    name text not null,
    description text,
    category text not null default 'Custom',
    tags text[] not null default '{}',

    -- Preview
    thumbnail text,  -- URL to thumbnail image

    -- Video composition details
    duration integer not null,  -- Total duration in frames
    aspect_ratio text not null default '16:9',

    -- The full overlay composition (array of overlay objects)
    overlays jsonb not null default '[]'::jsonb,
    -- Each overlay contains: id, type, content, src, from, row, left, top,
    -- width, height, rotation, durationInFrames, styles, etc.

    -- Metadata
    is_system boolean not null default false,  -- System templates can't be deleted by users
    is_public boolean not null default false,  -- Public templates visible to all users
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),

    -- Constraints
    constraint valid_aspect_ratio check (aspect_ratio in ('16:9', '9:16', '1:1', '4:5'))
);

-- Indexes for common queries
create index idx_video_templates_user_id on octupost.video_templates(user_id);
create index idx_video_templates_category on octupost.video_templates(category);
create index idx_video_templates_aspect_ratio on octupost.video_templates(aspect_ratio);
create index idx_video_templates_is_system on octupost.video_templates(is_system) where is_system = true;
create index idx_video_templates_is_public on octupost.video_templates(is_public) where is_public = true;
create index idx_video_templates_tags on octupost.video_templates using gin(tags);

-- Enable RLS
alter table octupost.video_templates enable row level security;

-- =============================================================================
-- RLS Policies
-- =============================================================================

-- Everyone can view system templates
create policy "Anyone can view system templates"
    on octupost.video_templates for select
    using (is_system = true);

-- Authenticated users can view public templates
create policy "Authenticated users can view public templates"
    on octupost.video_templates for select
    to authenticated
    using (is_public = true);

-- Users can view their own templates
create policy "Users can view their own templates"
    on octupost.video_templates for select
    to authenticated
    using (user_id = auth.uid());

-- Users can create their own templates
create policy "Users can create their own templates"
    on octupost.video_templates for insert
    to authenticated
    with check (
        user_id = auth.uid()
        and is_system = false  -- Users cannot create system templates
    );

-- Users can update their own non-system templates
create policy "Users can update their own templates"
    on octupost.video_templates for update
    to authenticated
    using (user_id = auth.uid() and is_system = false)
    with check (user_id = auth.uid() and is_system = false);

-- Users can delete their own non-system templates
create policy "Users can delete their own templates"
    on octupost.video_templates for delete
    to authenticated
    using (user_id = auth.uid() and is_system = false);

-- =============================================================================
-- Trigger: Update updated_at on modification
-- =============================================================================

create or replace function octupost.update_video_template_timestamp()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

create trigger trigger_update_video_template_timestamp
    before update on octupost.video_templates
    for each row
    execute function octupost.update_video_template_timestamp();

-- =============================================================================
-- Seed: System templates from existing JSON files
-- =============================================================================

-- Template: Relax Tiktok (9:16 vertical)
insert into octupost.video_templates (name, description, category, tags, duration, aspect_ratio, overlays, is_system, is_public)
values (
    'Relax Tiktok',
    'A relaxing vertical video template perfect for TikTok',
    'Lifestyle',
    array['tiktok', 'vertical', 'relaxing', 'lifestyle'],
    330,
    '9:16',
    '[
        {
            "left": 0,
            "top": 0,
            "width": 1086,
            "height": 1950,
            "durationInFrames": 83,
            "from": 0,
            "id": 0,
            "rotation": 0,
            "row": 4,
            "isDragging": false,
            "type": "video",
            "content": "https://images.pexels.com/videos/31515004/pexels-photo-31515004.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=1200&w=630",
            "src": "https://videos.pexels.com/video-files/31515004/13434969_360_640_60fps.mp4",
            "videoStartTime": 0,
            "styles": {
                "opacity": 1,
                "zIndex": 100,
                "transform": "none",
                "objectFit": "cover",
                "padding": "65px",
                "paddingBackgroundColor": "#47a8d9"
            }
        },
        {
            "left": 0,
            "top": 0,
            "width": 1076,
            "height": 1906,
            "durationInFrames": 84,
            "from": 69,
            "id": 1,
            "rotation": 0,
            "row": 1,
            "isDragging": false,
            "type": "video",
            "content": "https://images.pexels.com/videos/31525167/cheonggyecheon-cheonggyecheon-stream-jongno-gu-jongro-gu-31525167.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=1200&w=630",
            "src": "https://videos.pexels.com/video-files/31525167/13437855_360_640_30fps.mp4",
            "videoStartTime": 0,
            "styles": {
                "opacity": 1,
                "zIndex": 100,
                "transform": "none",
                "objectFit": "cover",
                "padding": "65px",
                "paddingBackgroundColor": "#d67d76"
            }
        },
        {
            "left": 0,
            "top": 0,
            "width": 1070,
            "height": 1929,
            "durationInFrames": 84,
            "from": 137,
            "id": 2,
            "rotation": 0,
            "row": 2,
            "isDragging": false,
            "type": "video",
            "content": "https://images.pexels.com/videos/31508697/langkawi-sea-beach-31508697.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=1200&w=630",
            "src": "https://videos.pexels.com/video-files/31508697/13432546_360_640_60fps.mp4",
            "videoStartTime": 0,
            "styles": {
                "opacity": 1,
                "zIndex": 100,
                "transform": "none",
                "objectFit": "cover",
                "padding": "65px",
                "paddingBackgroundColor": "#e6844d"
            }
        },
        {
            "left": 0,
            "top": 0,
            "width": 1078,
            "height": 1925,
            "durationInFrames": 118,
            "from": 212,
            "id": 3,
            "rotation": 0,
            "row": 3,
            "isDragging": false,
            "type": "video",
            "content": "https://images.pexels.com/videos/31497019/architecture-bleu-celebre-ciel-31497019.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=1200&w=630",
            "src": "https://videos.pexels.com/video-files/31497019/13429172_360_640_30fps.mp4",
            "videoStartTime": 0,
            "styles": {
                "opacity": 1,
                "zIndex": 100,
                "transform": "none",
                "objectFit": "cover",
                "padding": "65px",
                "paddingBackgroundColor": "#b07344"
            }
        },
        {
            "left": 117,
            "top": 843,
            "width": 871,
            "height": 291,
            "durationInFrames": 326,
            "from": 0,
            "id": 4,
            "row": 0,
            "rotation": 0,
            "isDragging": false,
            "type": "text",
            "content": "Time to RELAX",
            "styles": {
                "fontSize": "3rem",
                "fontWeight": "900",
                "color": "#FFFFFF",
                "backgroundColor": "",
                "fontFamily": "font-league-spartan",
                "fontStyle": "normal",
                "textDecoration": "none",
                "lineHeight": "1",
                "textAlign": "center",
                "letterSpacing": "0.02em",
                "textTransform": "uppercase",
                "textShadow": "2px 2px 0px rgba(0, 0, 0, 0.2)",
                "opacity": 1,
                "zIndex": 1,
                "transform": "none"
            }
        }
    ]'::jsonb,
    true,
    true
);

-- Template: Sport (16:9 horizontal)
insert into octupost.video_templates (name, description, category, tags, duration, aspect_ratio, overlays, is_system, is_public)
values (
    'Sport',
    'Dynamic sports template with energetic transitions',
    'Sports',
    array['sports', 'horizontal', 'dynamic', 'energetic'],
    353,
    '16:9',
    '[
        {
            "id": 752284,
            "type": "sound",
            "content": "Upbeat Corporate",
            "src": "https://rwxrdxvxndclnqvznxfj.supabase.co/storage/v1/object/public/sounds/sound-1.mp3",
            "from": 0,
            "row": 4,
            "left": 0,
            "top": 0,
            "width": 1920,
            "height": 100,
            "rotation": 0,
            "isDragging": false,
            "durationInFrames": 353,
            "styles": {
                "opacity": 1
            }
        },
        {
            "left": 0,
            "top": 0,
            "width": 1280,
            "height": 720,
            "durationInFrames": 88,
            "from": 0,
            "id": 643873,
            "rotation": 0,
            "row": 3,
            "isDragging": false,
            "type": "video",
            "content": "https://images.pexels.com/videos/7660624/pexels-photo-7660624.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=630&w=1200",
            "src": "https://videos.pexels.com/video-files/7660624/7660624-uhd_2560_1440_25fps.mp4",
            "videoStartTime": 0,
            "styles": {
                "opacity": 1,
                "zIndex": 100,
                "transform": "none",
                "objectFit": "cover"
            }
        },
        {
            "left": 0,
            "top": 0,
            "width": 1280,
            "height": 720,
            "durationInFrames": 263,
            "from": 84,
            "id": 215002,
            "rotation": 0,
            "row": 2,
            "isDragging": false,
            "type": "video",
            "content": "https://images.pexels.com/videos/5803095/cycling-dirt-bike-drone-engine-5803095.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=630&w=1200",
            "src": "https://videos.pexels.com/video-files/5803095/5803095-uhd_2560_1440_25fps.mp4",
            "videoStartTime": 0,
            "styles": {
                "opacity": 1,
                "zIndex": 100,
                "transform": "none",
                "objectFit": "cover"
            }
        },
        {
            "left": 91,
            "top": 142,
            "width": 1176,
            "height": 399,
            "durationInFrames": 341,
            "from": 7,
            "id": 653205,
            "row": 1,
            "rotation": 0,
            "isDragging": false,
            "type": "text",
            "content": "BUILD.",
            "styles": {
                "fontSize": "3rem",
                "fontWeight": "900",
                "color": "#FFFFFF",
                "backgroundColor": "transparent",
                "fontFamily": "font-sans",
                "fontStyle": "normal",
                "textDecoration": "none",
                "lineHeight": "1",
                "textAlign": "center",
                "letterSpacing": "0.02em",
                "textShadow": "2px 2px 0px rgba(0, 0, 0, 0.2)",
                "opacity": 1,
                "zIndex": 1,
                "transform": "none",
                "animation": {
                    "enter": "fade",
                    "exit": "fade"
                }
            }
        }
    ]'::jsonb,
    true,
    true
);

-- Template: Intro Example (9:16 vertical)
insert into octupost.video_templates (name, description, category, tags, duration, aspect_ratio, overlays, is_system, is_public)
values (
    'Intro Example',
    'Are you ready intro template with animated text',
    'Intro',
    array['tiktok', 'intro', 'animated', 'ad'],
    86,
    '9:16',
    '[
        {
            "left": 0,
            "top": 0,
            "width": 1101,
            "height": 1924,
            "durationInFrames": 86,
            "from": 0,
            "id": 0,
            "rotation": 0,
            "row": 4,
            "isDragging": false,
            "type": "video",
            "content": "https://images.pexels.com/videos/1943483/free-video-1943483.jpg?auto=compress&cs=tinysrgb&fit=crop&h=630&w=1200",
            "src": "https://videos.pexels.com/video-files/1943483/1943483-uhd_2560_1440_25fps.mp4",
            "videoStartTime": 0,
            "styles": {
                "opacity": 1,
                "zIndex": 100,
                "transform": "none",
                "objectFit": "cover",
                "animation": {"exit": "fade"}
            }
        },
        {
            "left": 126,
            "top": 569,
            "width": 847,
            "height": 402,
            "durationInFrames": 70,
            "from": 8,
            "id": 1,
            "row": 0,
            "rotation": 0,
            "isDragging": false,
            "type": "text",
            "content": "ARE",
            "styles": {
                "fontSize": "3rem",
                "fontWeight": "900",
                "color": "#FFFFFF",
                "backgroundColor": "",
                "fontFamily": "font-sans",
                "fontStyle": "normal",
                "textDecoration": "none",
                "lineHeight": "1",
                "textAlign": "center",
                "letterSpacing": "0.02em",
                "textTransform": "uppercase",
                "textShadow": "2px 2px 0px rgba(0, 0, 0, 0.2)",
                "opacity": 1,
                "zIndex": 1,
                "transform": "none",
                "animation": {"enter": "snapRotate"}
            }
        },
        {
            "left": 126,
            "top": 927,
            "width": 847,
            "height": 402,
            "durationInFrames": 67,
            "from": 11,
            "id": 2,
            "row": 1,
            "rotation": 0,
            "isDragging": false,
            "type": "text",
            "content": "YOU",
            "styles": {
                "fontSize": "3rem",
                "fontWeight": "900",
                "color": "#FFFFFF",
                "backgroundColor": "",
                "fontFamily": "font-sans",
                "fontStyle": "normal",
                "textDecoration": "none",
                "lineHeight": "1",
                "textAlign": "center",
                "letterSpacing": "0.02em",
                "textTransform": "uppercase",
                "textShadow": "2px 2px 0px rgba(0, 0, 0, 0.2)",
                "opacity": 1,
                "zIndex": 1,
                "transform": "none",
                "animation": {"enter": "snapRotate"}
            }
        },
        {
            "left": -25,
            "top": 1294,
            "width": 1164,
            "height": 251,
            "durationInFrames": 63,
            "from": 15,
            "id": 3,
            "row": 2,
            "rotation": 0,
            "isDragging": false,
            "type": "text",
            "content": "READY?",
            "styles": {
                "fontSize": "3rem",
                "fontWeight": "900",
                "color": "#FFFFFF",
                "backgroundColor": "",
                "fontFamily": "font-sans",
                "fontStyle": "normal",
                "textDecoration": "none",
                "lineHeight": "1",
                "textAlign": "center",
                "letterSpacing": "0.02em",
                "textTransform": "uppercase",
                "textShadow": "2px 2px 0px rgba(0, 0, 0, 0.2)",
                "opacity": 1,
                "zIndex": 1,
                "transform": "none",
                "animation": {"enter": "snapRotate"}
            }
        }
    ]'::jsonb,
    true,
    true
);

-- Template: Make Great Videos (16:9 horizontal)
insert into octupost.video_templates (name, description, category, tags, duration, aspect_ratio, overlays, is_system, is_public)
values (
    'Make Great Videos',
    'Make great videos with this professional template',
    'Promo',
    array['promo', 'horizontal', 'professional', 'vintage'],
    124,
    '16:9',
    '[
        {
            "left": 0,
            "top": 0,
            "width": 1280,
            "height": 720,
            "durationInFrames": 61,
            "from": 0,
            "id": 791325,
            "rotation": 0,
            "row": 3,
            "isDragging": false,
            "type": "video",
            "content": "https://images.pexels.com/videos/2821900/free-video-2821900.jpg?auto=compress&cs=tinysrgb&fit=crop&h=630&w=1200",
            "src": "https://videos.pexels.com/video-files/2821900/2821900-hd_1280_720_25fps.mp4",
            "videoStartTime": 0,
            "styles": {
                "opacity": 1,
                "zIndex": 100,
                "transform": "none",
                "objectFit": "cover",
                "padding": "50px",
                "paddingBackgroundColor": "#ffffff",
                "filter": "contrast(130%) sepia(45%) brightness(85%) saturate(160%) hue-rotate(5deg)"
            }
        },
        {
            "left": 24,
            "top": 127,
            "width": 1195,
            "height": 444,
            "durationInFrames": 47,
            "from": 9,
            "id": 407242,
            "row": 1,
            "rotation": 0,
            "isDragging": false,
            "type": "text",
            "content": "MAKE",
            "styles": {
                "fontSize": "3rem",
                "fontWeight": "700",
                "color": "rgba(255, 169, 2, 1)",
                "backgroundColor": "",
                "fontFamily": "font-league-spartan",
                "fontStyle": "normal",
                "textDecoration": "none",
                "lineHeight": "1.1",
                "textAlign": "center",
                "letterSpacing": "-0.03em",
                "opacity": 1,
                "zIndex": 1,
                "transform": "none"
            }
        },
        {
            "left": 38,
            "top": 141,
            "width": 1195,
            "height": 444,
            "durationInFrames": 48,
            "from": 9,
            "id": 162812,
            "row": 2,
            "rotation": 0,
            "isDragging": false,
            "type": "text",
            "content": "MAKE",
            "styles": {
                "fontSize": "3rem",
                "fontWeight": "700",
                "color": "rgb(24, 23, 22)",
                "backgroundColor": "",
                "fontFamily": "font-league-spartan",
                "fontStyle": "normal",
                "textDecoration": "none",
                "lineHeight": "1.1",
                "textAlign": "center",
                "letterSpacing": "-0.03em",
                "opacity": 1,
                "zIndex": 1,
                "transform": "none"
            }
        },
        {
            "left": 0,
            "top": 0,
            "width": 1280,
            "height": 720,
            "durationInFrames": 52,
            "from": 57,
            "id": 634772,
            "rotation": 0,
            "row": 2,
            "isDragging": false,
            "type": "video",
            "content": "https://images.pexels.com/videos/7778850/pexels-photo-7778850.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=630&w=1200",
            "src": "https://videos.pexels.com/video-files/7778850/7778850-uhd_2732_1440_25fps.mp4",
            "videoStartTime": 0,
            "styles": {
                "opacity": 1,
                "zIndex": 100,
                "transform": "none",
                "objectFit": "cover",
                "filter": "contrast(130%) sepia(45%) brightness(85%) saturate(160%) hue-rotate(5deg)",
                "padding": "50px",
                "paddingBackgroundColor": "#ffffff"
            }
        },
        {
            "left": 24,
            "top": 127,
            "width": 1195,
            "height": 444,
            "durationInFrames": 40,
            "from": 62,
            "id": 957241,
            "row": 0,
            "rotation": 0,
            "isDragging": false,
            "type": "text",
            "content": "GREAT",
            "styles": {
                "fontSize": "3rem",
                "fontWeight": "700",
                "color": "rgba(255, 169, 2, 1)",
                "backgroundColor": "",
                "fontFamily": "font-league-spartan",
                "fontStyle": "normal",
                "textDecoration": "none",
                "lineHeight": "1.1",
                "textAlign": "center",
                "letterSpacing": "-0.03em",
                "opacity": 1,
                "zIndex": 1,
                "transform": "none"
            }
        },
        {
            "left": 38,
            "top": 141,
            "width": 1195,
            "height": 444,
            "durationInFrames": 41,
            "from": 62,
            "id": 671754,
            "row": 1,
            "rotation": 0,
            "isDragging": false,
            "type": "text",
            "content": "GREAT",
            "styles": {
                "fontSize": "3rem",
                "fontWeight": "700",
                "color": "rgb(24, 23, 22)",
                "backgroundColor": "",
                "fontFamily": "font-league-spartan",
                "fontStyle": "normal",
                "textDecoration": "none",
                "lineHeight": "1.1",
                "textAlign": "center",
                "letterSpacing": "-0.03em",
                "opacity": 1,
                "zIndex": 1,
                "transform": "none"
            }
        },
        {
            "left": 0,
            "top": 0,
            "width": 1280,
            "height": 720,
            "durationInFrames": 54,
            "from": 101,
            "id": 949039,
            "rotation": 0,
            "row": 3,
            "isDragging": false,
            "type": "video",
            "content": "https://images.pexels.com/videos/3044090/free-video-3044090.jpg?auto=compress&cs=tinysrgb&fit=crop&h=630&w=1200",
            "src": "https://videos.pexels.com/video-files/3044090/3044090-uhd_2560_1440_24fps.mp4",
            "videoStartTime": 0,
            "styles": {
                "opacity": 1,
                "padding": "50px",
                "paddingBackgroundColor": "#ffffff",
                "zIndex": 100,
                "transform": "none",
                "objectFit": "cover",
                "filter": "contrast(130%) sepia(45%) brightness(85%) saturate(160%) hue-rotate(5deg)"
            }
        },
        {
            "left": 24,
            "top": 127,
            "width": 1195,
            "height": 444,
            "durationInFrames": 47,
            "from": 108,
            "id": 947381,
            "row": 0,
            "rotation": 0,
            "isDragging": false,
            "type": "text",
            "content": "VIDEOS",
            "styles": {
                "fontSize": "3rem",
                "fontWeight": "700",
                "color": "rgba(255, 169, 2, 1)",
                "backgroundColor": "",
                "fontFamily": "font-league-spartan",
                "fontStyle": "normal",
                "textDecoration": "none",
                "lineHeight": "1.1",
                "textAlign": "center",
                "letterSpacing": "-0.03em",
                "opacity": 1,
                "zIndex": 1,
                "transform": "none"
            }
        },
        {
            "left": 38,
            "top": 141,
            "width": 1195,
            "height": 444,
            "durationInFrames": 47,
            "from": 108,
            "id": 286216,
            "row": 1,
            "rotation": 0,
            "isDragging": false,
            "type": "text",
            "content": "VIDEOS",
            "styles": {
                "fontSize": "3rem",
                "fontWeight": "700",
                "color": "rgb(24, 23, 22)",
                "backgroundColor": "",
                "fontFamily": "font-league-spartan",
                "fontStyle": "normal",
                "textDecoration": "none",
                "lineHeight": "1.1",
                "textAlign": "center",
                "letterSpacing": "-0.03em",
                "opacity": 1,
                "zIndex": 1,
                "transform": "none"
            }
        },
        {
            "id": 957242,
            "type": "sound",
            "content": "Another Lowfi",
            "src": "https://rwxrdxvxndclnqvznxfj.supabase.co/storage/v1/object/public/sounds/sound-3.mp3",
            "from": 0,
            "row": 4,
            "left": 0,
            "top": 0,
            "width": 1920,
            "height": 100,
            "rotation": 0,
            "isDragging": false,
            "durationInFrames": 156,
            "styles": {"opacity": 1}
        }
    ]'::jsonb,
    true,
    true
);

-- Template: Color Grading (9:16 vertical)
insert into octupost.video_templates (name, description, category, tags, duration, aspect_ratio, overlays, is_system, is_public)
values (
    'Color Grading',
    'Experimenting with color grading effects',
    'Creative',
    array['creative', 'vertical', 'color-grading', 'artistic'],
    124,
    '9:16',
    '[
        {
            "left": 0,
            "top": 0,
            "width": 1087,
            "height": 1924,
            "durationInFrames": 160,
            "from": 0,
            "id": 343983,
            "rotation": 0,
            "row": 2,
            "isDragging": false,
            "type": "video",
            "content": "https://images.pexels.com/videos/4235591/pexels-photo-4235591.jpeg",
            "src": "https://videos.pexels.com/video-files/4235591/4235591-hd_1920_1080_25fps.mp4",
            "videoStartTime": 0,
            "styles": {
                "opacity": 1,
                "zIndex": 100,
                "transform": "none",
                "objectFit": "cover",
                "filter": "brightness(100%) sepia(20%) hue-rotate(180deg) saturate(90%)"
            }
        },
        {
            "left": 152,
            "top": 729,
            "width": 799,
            "height": 155,
            "durationInFrames": 521,
            "from": 0,
            "id": 157316,
            "row": 0,
            "rotation": 0,
            "isDragging": false,
            "type": "text",
            "content": "color grading",
            "styles": {
                "fontSize": "3rem",
                "fontWeight": "700",
                "color": "rgba(17, 16, 16, 0.69)",
                "backgroundColor": "",
                "fontFamily": "font-league-spartan",
                "fontStyle": "normal",
                "textDecoration": "none",
                "lineHeight": "1.1",
                "textAlign": "center",
                "letterSpacing": "-0.03em",
                "opacity": 1,
                "zIndex": 1,
                "transform": "none"
            }
        },
        {
            "id": 971436,
            "type": "sound",
            "content": "Inspiring Cinematic",
            "src": "https://rwxrdxvxndclnqvznxfj.supabase.co/storage/v1/object/public/sounds/sound-2.mp3",
            "from": 0,
            "row": 3,
            "left": 0,
            "top": 0,
            "width": 1920,
            "height": 100,
            "rotation": 0,
            "isDragging": false,
            "durationInFrames": 522,
            "styles": {"opacity": 1}
        }
    ]'::jsonb,
    true,
    true
);

-- Template: Hand Template (16:9 horizontal - default when aspect ratio not specified)
insert into octupost.video_templates (name, description, category, tags, duration, aspect_ratio, overlays, is_system, is_public)
values (
    'Hand Template',
    'Experiment with text animation letter by letter',
    'Creative',
    array['creative', 'horizontal', 'animation', 'text'],
    203,
    '16:9',
    '[
        {
            "left": 0,
            "top": 0,
            "width": 1280,
            "height": 720,
            "durationInFrames": 86,
            "from": 0,
            "id": 337525,
            "rotation": 0,
            "row": 5,
            "isDragging": false,
            "type": "image",
            "src": "https://images.pexels.com/photos/255527/pexels-photo-255527.jpeg",
            "styles": {
                "objectFit": "cover",
                "animation": {"enter": "fadeIn", "exit": "fadeOut"},
                "padding": "55px",
                "paddingBackgroundColor": "#d00120"
            }
        },
        {
            "left": -5,
            "top": 57,
            "width": 585,
            "height": 296,
            "durationInFrames": 59,
            "from": 19,
            "id": 863266,
            "row": 0,
            "rotation": 0,
            "isDragging": false,
            "type": "text",
            "content": "h",
            "styles": {
                "fontSize": "3rem",
                "fontWeight": "700",
                "color": "rgb(10, 9, 9)",
                "backgroundColor": "",
                "fontFamily": "font-bungee-inline",
                "fontStyle": "normal",
                "textDecoration": "none",
                "lineHeight": "1.1",
                "textAlign": "center",
                "letterSpacing": "-0.03em",
                "opacity": 1,
                "zIndex": 1,
                "transform": "none",
                "animation": {"enter": "none", "exit": "scale"}
            }
        },
        {
            "left": 178,
            "top": 58,
            "width": 585,
            "height": 296,
            "durationInFrames": 54,
            "from": 24,
            "id": 985874,
            "row": 1,
            "rotation": 0,
            "isDragging": false,
            "type": "text",
            "content": "a",
            "styles": {
                "fontSize": "3rem",
                "fontWeight": "700",
                "color": "rgb(10, 9, 9)",
                "backgroundColor": "",
                "fontFamily": "font-bungee-inline",
                "fontStyle": "normal",
                "textDecoration": "none",
                "lineHeight": "1.1",
                "textAlign": "center",
                "letterSpacing": "-0.03em",
                "opacity": 1,
                "zIndex": 1,
                "transform": "none",
                "animation": {"enter": "none", "exit": "scale"}
            }
        },
        {
            "left": 344,
            "top": 58,
            "width": 585,
            "height": 296,
            "durationInFrames": 48,
            "from": 30,
            "id": 108804,
            "row": 2,
            "rotation": 0,
            "isDragging": false,
            "type": "text",
            "content": "n",
            "styles": {
                "fontSize": "3rem",
                "fontWeight": "700",
                "color": "rgb(10, 9, 9)",
                "backgroundColor": "",
                "fontFamily": "font-bungee-inline",
                "fontStyle": "normal",
                "textDecoration": "none",
                "lineHeight": "1.1",
                "textAlign": "center",
                "letterSpacing": "-0.03em",
                "opacity": 1,
                "zIndex": 1,
                "transform": "none",
                "animation": {"enter": "none", "exit": "scale"}
            }
        },
        {
            "left": 511,
            "top": 57,
            "width": 585,
            "height": 296,
            "durationInFrames": 40,
            "from": 38,
            "id": 51349,
            "row": 3,
            "rotation": 0,
            "isDragging": false,
            "type": "text",
            "content": "d",
            "styles": {
                "fontSize": "3rem",
                "fontWeight": "700",
                "color": "rgb(10, 9, 9)",
                "backgroundColor": "",
                "fontFamily": "font-bungee-inline",
                "fontStyle": "normal",
                "textDecoration": "none",
                "lineHeight": "1.1",
                "textAlign": "center",
                "letterSpacing": "-0.03em",
                "opacity": 1,
                "zIndex": 1,
                "transform": "none",
                "animation": {"enter": "none", "exit": "scale"}
            }
        },
        {
            "left": 652,
            "top": 57,
            "width": 585,
            "height": 296,
            "durationInFrames": 32,
            "from": 46,
            "id": 21742,
            "row": 4,
            "rotation": 0,
            "isDragging": false,
            "type": "text",
            "content": ".",
            "styles": {
                "fontSize": "3rem",
                "fontWeight": "700",
                "color": "rgb(10, 9, 9)",
                "backgroundColor": "",
                "fontFamily": "font-bungee-inline",
                "fontStyle": "normal",
                "textDecoration": "none",
                "lineHeight": "1.1",
                "textAlign": "center",
                "letterSpacing": "-0.03em",
                "opacity": 1,
                "zIndex": 1,
                "transform": "none",
                "animation": {"enter": "none", "exit": "scale"}
            }
        }
    ]'::jsonb,
    true,
    true
);

-- Grant permissions
grant select on octupost.video_templates to authenticated;
grant insert, update, delete on octupost.video_templates to authenticated;

commit;
