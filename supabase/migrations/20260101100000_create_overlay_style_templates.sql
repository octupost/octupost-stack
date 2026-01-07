-- Phase 5: Overlay Style Templates
-- Predefined text/caption styles for consistent branding

begin;

-- =============================================================================
-- Table: overlay_style_templates
-- =============================================================================
-- Stores reusable style presets for text overlays.
-- Can be system-wide (brand_kit_id = null) or brand-specific.

create table if not exists octupost.overlay_style_templates (
    id uuid primary key default gen_random_uuid(),
    brand_kit_id uuid references octupost.brand_kits(id) on delete cascade,

    -- Template identification
    name text not null,
    description text,
    category text not null default 'text',  -- 'text', 'caption', 'title', 'subtitle'

    -- Visual styling (matches overlay data structure)
    style_data jsonb not null default '{}'::jsonb,
    -- Expected keys:
    --   fontFamily: string
    --   fontSize: number
    --   fontWeight: string (normal, bold, etc.)
    --   color: string (hex)
    --   backgroundColor: string | null
    --   textAlign: string (left, center, right)
    --   textShadow: string | null
    --   letterSpacing: number
    --   lineHeight: number
    --   padding: object {top, right, bottom, left}
    --   borderRadius: number
    --   opacity: number

    -- Layout defaults
    default_position jsonb default '{"left": 50, "top": 80, "width": 80}'::jsonb,

    -- Metadata
    is_system boolean not null default false,  -- System templates can't be deleted
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- Indexes
create index idx_style_templates_brand_kit on octupost.overlay_style_templates(brand_kit_id);
create index idx_style_templates_category on octupost.overlay_style_templates(category);

-- Enable RLS
alter table octupost.overlay_style_templates enable row level security;

-- RLS Policies
-- Users can view system templates and their own brand's templates
create policy "Users can view system templates"
    on octupost.overlay_style_templates for select
    using (is_system = true);

create policy "Users can view brand templates they own"
    on octupost.overlay_style_templates for select
    using (
        brand_kit_id in (
            select id from octupost.brand_kits
            where user_id = auth.uid()
        )
    );

create policy "Users can manage their brand templates"
    on octupost.overlay_style_templates for all
    using (
        brand_kit_id in (
            select id from octupost.brand_kits
            where user_id = auth.uid()
        )
        and is_system = false
    );

-- =============================================================================
-- Seed: System-wide default templates
-- =============================================================================

insert into octupost.overlay_style_templates (name, description, category, style_data, default_position, is_system)
values
    -- Bold headline for key moments
    (
        'Bold Headline',
        'Large, impactful text for key statements',
        'title',
        '{
            "fontFamily": "Inter",
            "fontSize": 72,
            "fontWeight": "bold",
            "color": "#FFFFFF",
            "backgroundColor": null,
            "textAlign": "center",
            "textShadow": "2px 2px 8px rgba(0,0,0,0.5)",
            "letterSpacing": -1,
            "lineHeight": 1.1,
            "padding": {"top": 0, "right": 0, "bottom": 0, "left": 0},
            "borderRadius": 0,
            "opacity": 1
        }'::jsonb,
        '{"left": 50, "top": 50, "width": 90}'::jsonb,
        true
    ),

    -- Subtitle for supporting text
    (
        'Subtitle',
        'Medium-weight text below headlines',
        'subtitle',
        '{
            "fontFamily": "Inter",
            "fontSize": 36,
            "fontWeight": "500",
            "color": "#FFFFFF",
            "backgroundColor": null,
            "textAlign": "center",
            "textShadow": "1px 1px 4px rgba(0,0,0,0.4)",
            "letterSpacing": 0,
            "lineHeight": 1.3,
            "padding": {"top": 0, "right": 0, "bottom": 0, "left": 0},
            "borderRadius": 0,
            "opacity": 0.9
        }'::jsonb,
        '{"left": 50, "top": 65, "width": 80}'::jsonb,
        true
    ),

    -- Podcast-style caption at bottom
    (
        'Bottom Caption',
        'Clean caption bar at the bottom',
        'caption',
        '{
            "fontFamily": "Inter",
            "fontSize": 28,
            "fontWeight": "600",
            "color": "#FFFFFF",
            "backgroundColor": "rgba(0,0,0,0.7)",
            "textAlign": "center",
            "textShadow": null,
            "letterSpacing": 0,
            "lineHeight": 1.4,
            "padding": {"top": 16, "right": 24, "bottom": 16, "left": 24},
            "borderRadius": 8,
            "opacity": 1
        }'::jsonb,
        '{"left": 50, "top": 90, "width": 90}'::jsonb,
        true
    ),

    -- Modern highlight box
    (
        'Highlight Box',
        'Text with colored background highlight',
        'text',
        '{
            "fontFamily": "Inter",
            "fontSize": 32,
            "fontWeight": "bold",
            "color": "#FFFFFF",
            "backgroundColor": "#3B82F6",
            "textAlign": "center",
            "textShadow": null,
            "letterSpacing": 0.5,
            "lineHeight": 1.2,
            "padding": {"top": 12, "right": 20, "bottom": 12, "left": 20},
            "borderRadius": 6,
            "opacity": 1
        }'::jsonb,
        '{"left": 50, "top": 50, "width": 70}'::jsonb,
        true
    ),

    -- Minimal/subtle text
    (
        'Minimal',
        'Clean, understated text',
        'text',
        '{
            "fontFamily": "Inter",
            "fontSize": 24,
            "fontWeight": "400",
            "color": "#FFFFFF",
            "backgroundColor": null,
            "textAlign": "left",
            "textShadow": "1px 1px 2px rgba(0,0,0,0.3)",
            "letterSpacing": 0,
            "lineHeight": 1.5,
            "padding": {"top": 0, "right": 0, "bottom": 0, "left": 0},
            "borderRadius": 0,
            "opacity": 0.85
        }'::jsonb,
        '{"left": 10, "top": 85, "width": 60}'::jsonb,
        true
    ),

    -- Call to action
    (
        'Call to Action',
        'Eye-catching CTA button style',
        'text',
        '{
            "fontFamily": "Inter",
            "fontSize": 28,
            "fontWeight": "bold",
            "color": "#FFFFFF",
            "backgroundColor": "#EF4444",
            "textAlign": "center",
            "textShadow": null,
            "letterSpacing": 1,
            "lineHeight": 1.2,
            "padding": {"top": 16, "right": 32, "bottom": 16, "left": 32},
            "borderRadius": 50,
            "opacity": 1
        }'::jsonb,
        '{"left": 50, "top": 80, "width": 40}'::jsonb,
        true
    ),

    -- Lower third (TV-style)
    (
        'Lower Third',
        'Professional lower-third name plate',
        'text',
        '{
            "fontFamily": "Inter",
            "fontSize": 24,
            "fontWeight": "600",
            "color": "#FFFFFF",
            "backgroundColor": "rgba(0,0,0,0.85)",
            "textAlign": "left",
            "textShadow": null,
            "letterSpacing": 0.5,
            "lineHeight": 1.3,
            "padding": {"top": 12, "right": 24, "bottom": 12, "left": 24},
            "borderRadius": 0,
            "opacity": 1
        }'::jsonb,
        '{"left": 5, "top": 85, "width": 50}'::jsonb,
        true
    );

-- =============================================================================
-- Trigger: Update updated_at on modification
-- =============================================================================

create or replace function octupost.update_style_template_timestamp()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

create trigger trigger_update_style_template_timestamp
    before update on octupost.overlay_style_templates
    for each row
    execute function octupost.update_style_template_timestamp();

-- Grant permissions
grant select on octupost.overlay_style_templates to authenticated;
grant insert, update, delete on octupost.overlay_style_templates to authenticated;

commit;
