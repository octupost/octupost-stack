-- Caption Styles Migration
-- Simplifies categories to just 'text' and 'caption'
-- Adds viral caption styles with highlight/animation support

begin;

-- =============================================================================
-- Step 1: Normalize existing categories to text/caption only
-- =============================================================================
update octupost.overlay_style_templates
set category = 'text'
where category in ('title', 'subtitle');

-- =============================================================================
-- Step 2: Add caption styles with highlight support
-- =============================================================================
-- Note: highlight and animation properties go inside style_data JSONB

insert into octupost.overlay_style_templates (name, description, category, style_data, default_position, is_system)
values
    -- =========================================================================
    -- VIRAL CREATOR STYLES
    -- =========================================================================

    -- Hormozi Yellow - The classic Alex Hormozi look
    (
        'Hormozi Yellow',
        'Bold yellow highlight on active word, Hormozi-style',
        'caption',
        '{
            "fontFamily": "Montserrat",
            "fontSize": 48,
            "fontWeight": "900",
            "color": "#FFFFFF",
            "backgroundColor": null,
            "textAlign": "center",
            "textShadow": "3px 3px 6px rgba(0,0,0,0.8)",
            "letterSpacing": 0,
            "lineHeight": 1.2,
            "textTransform": "uppercase",
            "padding": {"top": 0, "right": 0, "bottom": 0, "left": 0},
            "borderRadius": 0,
            "opacity": 1,
            "highlight": {
                "backgroundColor": "#F7C204",
                "color": "#000000",
                "padding": "4px 8px",
                "borderRadius": "4px",
                "fontWeight": "900"
            },
            "animation": {
                "type": "pop",
                "intensity": "normal"
            },
            "displayMode": "phrase"
        }'::jsonb,
        '{"left": 50, "top": 85, "width": 90}'::jsonb,
        true
    ),

    -- Hormozi Green - Variation with green highlights
    (
        'Hormozi Green',
        'Green highlight variation, high energy',
        'caption',
        '{
            "fontFamily": "Montserrat",
            "fontSize": 48,
            "fontWeight": "900",
            "color": "#FFFFFF",
            "backgroundColor": null,
            "textAlign": "center",
            "textShadow": "3px 3px 6px rgba(0,0,0,0.8)",
            "letterSpacing": 0,
            "lineHeight": 1.2,
            "textTransform": "uppercase",
            "padding": {"top": 0, "right": 0, "bottom": 0, "left": 0},
            "borderRadius": 0,
            "opacity": 1,
            "highlight": {
                "backgroundColor": "#02FB23",
                "color": "#000000",
                "padding": "4px 8px",
                "borderRadius": "4px",
                "fontWeight": "900"
            },
            "animation": {
                "type": "pop",
                "intensity": "strong"
            },
            "displayMode": "phrase"
        }'::jsonb,
        '{"left": 50, "top": 85, "width": 90}'::jsonb,
        true
    ),

    -- MrBeast Style - Comic font with bounce
    (
        'MrBeast Pop',
        'Comic-style with bounce animation and stroke',
        'caption',
        '{
            "fontFamily": "Komika",
            "fontSize": 52,
            "fontWeight": "bold",
            "color": "#FFFFFF",
            "backgroundColor": null,
            "textAlign": "center",
            "textShadow": null,
            "letterSpacing": 1,
            "lineHeight": 1.1,
            "textTransform": "uppercase",
            "padding": {"top": 0, "right": 0, "bottom": 0, "left": 0},
            "borderRadius": 0,
            "opacity": 1,
            "stroke": {
                "color": "#000000",
                "width": 3
            },
            "highlight": {
                "color": "#FFD700",
                "scale": 1.15
            },
            "animation": {
                "type": "bounce",
                "intensity": "strong"
            },
            "displayMode": "phrase"
        }'::jsonb,
        '{"left": 50, "top": 80, "width": 95}'::jsonb,
        true
    ),

    -- =========================================================================
    -- MINIMAL / AESTHETIC STYLES
    -- =========================================================================

    -- Minimal White - Clean TikTok aesthetic
    (
        'Minimal White',
        'Clean, subtle captions for aesthetic content',
        'caption',
        '{
            "fontFamily": "Inter",
            "fontSize": 32,
            "fontWeight": "500",
            "color": "#FFFFFF",
            "backgroundColor": null,
            "textAlign": "center",
            "textShadow": "1px 1px 3px rgba(0,0,0,0.5)",
            "letterSpacing": 0,
            "lineHeight": 1.4,
            "padding": {"top": 0, "right": 0, "bottom": 0, "left": 0},
            "borderRadius": 0,
            "opacity": 0.95,
            "highlight": {
                "opacity": 1,
                "fontWeight": "600"
            },
            "animation": {
                "type": "fade",
                "intensity": "subtle"
            },
            "displayMode": "sentence"
        }'::jsonb,
        '{"left": 50, "top": 88, "width": 85}'::jsonb,
        true
    ),

    -- Minimal Dark - Light background variation
    (
        'Minimal Dark',
        'Dark text on light background, Instagram-style',
        'caption',
        '{
            "fontFamily": "Inter",
            "fontSize": 28,
            "fontWeight": "500",
            "color": "#1A1A1A",
            "backgroundColor": "rgba(255,255,255,0.9)",
            "textAlign": "center",
            "textShadow": null,
            "letterSpacing": 0,
            "lineHeight": 1.4,
            "padding": {"top": 8, "right": 16, "bottom": 8, "left": 16},
            "borderRadius": 8,
            "opacity": 1,
            "highlight": {
                "color": "#000000",
                "fontWeight": "700"
            },
            "animation": {
                "type": "fade",
                "intensity": "subtle"
            },
            "displayMode": "sentence"
        }'::jsonb,
        '{"left": 50, "top": 88, "width": 80}'::jsonb,
        true
    ),

    -- =========================================================================
    -- PODCAST / PROFESSIONAL STYLES
    -- =========================================================================

    -- Podcast Bar - Classic podcast caption
    (
        'Podcast Bar',
        'Dark bar at bottom, perfect for talking head videos',
        'caption',
        '{
            "fontFamily": "Inter",
            "fontSize": 28,
            "fontWeight": "600",
            "color": "#FFFFFF",
            "backgroundColor": "rgba(0,0,0,0.85)",
            "textAlign": "center",
            "textShadow": null,
            "letterSpacing": 0,
            "lineHeight": 1.4,
            "padding": {"top": 14, "right": 24, "bottom": 14, "left": 24},
            "borderRadius": 8,
            "opacity": 1,
            "highlight": {
                "color": "#3B82F6",
                "fontWeight": "700"
            },
            "animation": {
                "type": "none"
            },
            "displayMode": "sentence"
        }'::jsonb,
        '{"left": 50, "top": 92, "width": 95}'::jsonb,
        true
    ),

    -- =========================================================================
    -- KARAOKE / MUSIC STYLES
    -- =========================================================================

    -- Karaoke Classic - Yellow highlight sweep
    (
        'Karaoke Classic',
        'Classic karaoke-style with yellow word highlight',
        'caption',
        '{
            "fontFamily": "Inter",
            "fontSize": 36,
            "fontWeight": "700",
            "color": "#FFFFFF",
            "backgroundColor": null,
            "textAlign": "center",
            "textShadow": "2px 2px 4px rgba(0,0,0,0.7)",
            "letterSpacing": 0,
            "lineHeight": 1.3,
            "padding": {"top": 0, "right": 0, "bottom": 0, "left": 0},
            "borderRadius": 0,
            "opacity": 1,
            "highlight": {
                "color": "#FFEB3B",
                "fontWeight": "800"
            },
            "animation": {
                "type": "karaoke",
                "intensity": "normal"
            },
            "displayMode": "sentence"
        }'::jsonb,
        '{"left": 50, "top": 85, "width": 90}'::jsonb,
        true
    ),

    -- Neon Glow - EDM/nightlife style
    (
        'Neon Glow',
        'Glowing neon effect for music and nightlife content',
        'caption',
        '{
            "fontFamily": "Inter",
            "fontSize": 40,
            "fontWeight": "800",
            "color": "#FFFFFF",
            "backgroundColor": null,
            "textAlign": "center",
            "textShadow": "0 0 10px #FF00FF, 0 0 20px #FF00FF, 0 0 30px #FF00FF",
            "letterSpacing": 2,
            "lineHeight": 1.2,
            "textTransform": "uppercase",
            "padding": {"top": 0, "right": 0, "bottom": 0, "left": 0},
            "borderRadius": 0,
            "opacity": 1,
            "highlight": {
                "color": "#00FFFF",
                "textShadow": "0 0 10px #00FFFF, 0 0 20px #00FFFF, 0 0 40px #00FFFF"
            },
            "animation": {
                "type": "glow",
                "intensity": "strong"
            },
            "displayMode": "phrase"
        }'::jsonb,
        '{"left": 50, "top": 85, "width": 90}'::jsonb,
        true
    ),

    -- =========================================================================
    -- BOLD / IMPACT STYLES
    -- =========================================================================

    -- Bold Impact - Maximum attention
    (
        'Bold Impact',
        'Maximum impact, news headline style',
        'caption',
        '{
            "fontFamily": "Inter",
            "fontSize": 44,
            "fontWeight": "900",
            "color": "#FFFFFF",
            "backgroundColor": "#000000",
            "textAlign": "center",
            "textShadow": null,
            "letterSpacing": 1,
            "lineHeight": 1.1,
            "textTransform": "uppercase",
            "padding": {"top": 12, "right": 20, "bottom": 12, "left": 20},
            "borderRadius": 0,
            "opacity": 1,
            "highlight": {
                "backgroundColor": "#EF4444",
                "color": "#FFFFFF",
                "padding": "4px 8px"
            },
            "animation": {
                "type": "pop",
                "intensity": "normal"
            },
            "displayMode": "phrase"
        }'::jsonb,
        '{"left": 50, "top": 85, "width": 90}'::jsonb,
        true
    ),

    -- Gradient Modern - Trendy gradient background
    (
        'Gradient Modern',
        'Modern gradient background with smooth animations',
        'caption',
        '{
            "fontFamily": "Inter",
            "fontSize": 32,
            "fontWeight": "700",
            "color": "#FFFFFF",
            "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "textAlign": "center",
            "textShadow": "0 2px 4px rgba(0,0,0,0.3)",
            "letterSpacing": 0,
            "lineHeight": 1.3,
            "padding": {"top": 12, "right": 24, "bottom": 12, "left": 24},
            "borderRadius": 12,
            "opacity": 1,
            "highlight": {
                "scale": 1.1,
                "fontWeight": "800"
            },
            "animation": {
                "type": "pop",
                "intensity": "subtle"
            },
            "displayMode": "phrase"
        }'::jsonb,
        '{"left": 50, "top": 85, "width": 85}'::jsonb,
        true
    ),

    -- =========================================================================
    -- SPECIAL EFFECTS
    -- =========================================================================

    -- Typewriter - Character by character reveal
    (
        'Typewriter',
        'Dramatic character-by-character reveal',
        'caption',
        '{
            "fontFamily": "JetBrains Mono",
            "fontSize": 28,
            "fontWeight": "500",
            "color": "#00FF00",
            "backgroundColor": "rgba(0,0,0,0.9)",
            "textAlign": "left",
            "textShadow": "0 0 5px #00FF00",
            "letterSpacing": 1,
            "lineHeight": 1.4,
            "padding": {"top": 12, "right": 20, "bottom": 12, "left": 20},
            "borderRadius": 4,
            "opacity": 1,
            "animation": {
                "type": "typewriter",
                "intensity": "normal"
            },
            "displayMode": "sentence"
        }'::jsonb,
        '{"left": 50, "top": 88, "width": 90}'::jsonb,
        true
    ),

    -- Single Word Focus - Only shows current word
    (
        'Single Word',
        'Maximum focus - only shows the current word',
        'caption',
        '{
            "fontFamily": "Inter",
            "fontSize": 56,
            "fontWeight": "900",
            "color": "#FFFFFF",
            "backgroundColor": null,
            "textAlign": "center",
            "textShadow": "4px 4px 8px rgba(0,0,0,0.8)",
            "letterSpacing": 0,
            "lineHeight": 1.1,
            "textTransform": "uppercase",
            "padding": {"top": 0, "right": 0, "bottom": 0, "left": 0},
            "borderRadius": 0,
            "opacity": 1,
            "animation": {
                "type": "pop",
                "intensity": "strong"
            },
            "displayMode": "word"
        }'::jsonb,
        '{"left": 50, "top": 50, "width": 90}'::jsonb,
        true
    ),

    -- Emoji Pop - Gen-Z style with emoji support
    (
        'Emoji Pop',
        'Colorful captions with auto-emoji support',
        'caption',
        '{
            "fontFamily": "Inter",
            "fontSize": 34,
            "fontWeight": "700",
            "color": "#FFFFFF",
            "backgroundColor": null,
            "textAlign": "center",
            "textShadow": "2px 2px 4px rgba(0,0,0,0.6)",
            "letterSpacing": 0,
            "lineHeight": 1.3,
            "padding": {"top": 0, "right": 0, "bottom": 0, "left": 0},
            "borderRadius": 0,
            "opacity": 1,
            "highlight": {
                "backgroundColor": "#FF6B6B",
                "color": "#FFFFFF",
                "padding": "2px 8px",
                "borderRadius": "6px"
            },
            "animation": {
                "type": "bounce",
                "intensity": "normal"
            },
            "displayMode": "phrase",
            "autoEmoji": true
        }'::jsonb,
        '{"left": 50, "top": 85, "width": 90}'::jsonb,
        true
    );

-- =============================================================================
-- Step 3: Update the existing "Bottom Caption" to have highlight support
-- =============================================================================
update octupost.overlay_style_templates
set style_data = style_data || '{
    "highlight": {
        "color": "#3B82F6",
        "fontWeight": "700"
    },
    "animation": {
        "type": "none"
    },
    "displayMode": "sentence"
}'::jsonb
where name = 'Bottom Caption' and is_system = true;

commit;
