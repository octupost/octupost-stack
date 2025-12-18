# Adding New Models Guide

This guide explains how to add new AI models to Octupost using the **labelKey system**.

## Overview

The labelKey system provides a clean way to configure how model parameters are displayed in the UI. Each parameter has:

- **labelKey**: Determines the component type, icon, and i18n label
- **displayMode**: Where the parameter appears (source, primary, inline, menu, hidden)
- **mapping**: The API field name sent to the provider

## Quick Start

### 1. Add Model in Admin Panel

1. Go to Admin → Model Configs
2. Click "Add Model" and enter the FAL endpoint
3. The schema will be fetched automatically

### 2. Configure Parameters

For each parameter, set:

| Field | Purpose | Example |
|-------|---------|---------|
| **Label Key** | UI component and label | `prompt_textarea`, `duration_slider` |
| **Display Mode** | Where to show | `source`, `primary`, `inline`, `menu`, `hidden` |
| **API Mapping** | Field name for API | `prompt`, `num_frames` |

### 3. Save and Test

Save the config and test in the playground.

---

## LabelKey Reference

### Naming Convention

```
{semantic_name}_{component_type}
```

The suffix determines the component:
- `_textarea` → Large text input
- `_input` → Small text/number input
- `_toggle` → Boolean switch
- `_dropdown` → Select with options
- `_slider` → Range slider
- `_json` → Object input (width/height)
- `_image` → Image upload
- `_video` → Video upload
- `_audio` → Audio upload

### Available LabelKeys

#### Text Inputs (textarea)
| LabelKey | Use For |
|----------|---------|
| `prompt_textarea` | Main generation prompt |
| `negative_prompt_textarea` | Things to avoid |
| `text_textarea` | TTS text input |

#### Small Inputs (input)
| LabelKey | Use For |
|----------|---------|
| `seed_input` | Random seed for reproducibility |
| `previous_text_input` | Context before text (TTS) |
| `next_text_input` | Context after text (TTS) |

#### Toggles
| LabelKey | Use For |
|----------|---------|
| `enhance_prompt_toggle` | AI prompt enhancement |
| `enable_audio_toggle` | Audio generation with video |
| `safety_checker_toggle` | Content safety filtering |
| `asmr_mode_toggle` | ASMR audio mode |
| `transparent_bg_toggle` | Transparent background |

#### Dropdowns
| LabelKey | Use For |
|----------|---------|
| `aspect_ratio_dropdown` | 16:9, 9:16, 1:1, etc. |
| `resolution_dropdown` | 720p, 1080p, 4K, etc. |
| `fps_dropdown` | Frame rate selection |
| `quality_dropdown` | Quality level |
| `background_dropdown` | Background options |
| `duration_dropdown` | Fixed duration options |
| `elevenlabs_voice_dropdown` | ElevenLabs voices |
| `kling_voice_dropdown` | Kling voices |
| `minimax_voice_dropdown` | Minimax voices |
| `minimax_voice_emotion_dropdown` | Voice emotions |
| `iso_language_dropdown` | Language selection |
| `ltx_retake_mode_dropdown` | LTX retake modes |

#### Sliders
| LabelKey | Use For |
|----------|---------|
| `duration_slider` | Variable duration (seconds) |
| `speed_slider` | Speech speed (0.5x-2x) |
| `speech_stability_slider` | Voice consistency |
| `speech_similarity_boost_slider` | Voice matching |
| `speech_style_slider` | Style exaggeration |

#### Media Inputs
| LabelKey | Use For |
|----------|---------|
| `source_image_image` | Image-to-video source |
| `first_frame_image` | Starting frame |
| `last_frame_image` | Ending frame |
| `reference_images_image` | Style references |
| `avatar_image_image` | Avatar image |
| `source_video_video` | Video input |
| `source_audio_audio` | Audio input |

#### Special
| LabelKey | Use For |
|----------|---------|
| `resolution_json` | Custom width/height |

---

## Display Modes

| Mode | Description | Example Parameters |
|------|-------------|-------------------|
| `source` | Input media at top (uploads) | source_image, source_video, source_audio |
| `primary` | Text prompt area below source | prompt, text |
| `inline` | Compact controls in generation bar | aspect_ratio, duration |
| `menu` | Advanced settings dropdown | seed, quality |
| `hidden` | Not shown, uses default value | internal params |

### Visual Layout

```
┌─────────────────────────────────────────────────┐
│  SOURCE ZONE (displayMode: "source")            │
│  [Image/Video/Audio Upload]                     │
├─────────────────────────────────────────────────┤
│  PRIMARY ZONE (displayMode: "primary")          │
│  [Prompt Textarea]                              │
├─────────────────────────────────────────────────┤
│  INLINE (displayMode: "inline")                 │
│  [Aspect ▼] [Duration ━●━] [Generate]           │
├─────────────────────────────────────────────────┤
│  ⚙️ MENU (displayMode: "menu")                 │
│  [Seed] [Quality] [CFG Scale]                   │
└─────────────────────────────────────────────────┘
```

---

## Examples

### Video Generation Model

```
Parameter: prompt
  → labelKey: prompt_textarea
  → displayMode: primary
  → mapping: prompt

Parameter: aspect_ratio
  → labelKey: aspect_ratio_dropdown
  → displayMode: inline
  → mapping: aspect_ratio

Parameter: duration
  → labelKey: duration_slider
  → displayMode: inline
  → mapping: duration
  → multiplyByFps: 30  (if API expects frames)

Parameter: enhance_prompt
  → labelKey: enhance_prompt_toggle
  → displayMode: inline
  → mapping: expand_prompt
```

### TTS Model

```
Parameter: text
  → labelKey: text_textarea
  → displayMode: primary
  → mapping: text

Parameter: voice_id
  → labelKey: elevenlabs_voice_dropdown
  → displayMode: inline
  → mapping: voice_id

Parameter: stability
  → labelKey: speech_stability_slider
  → displayMode: menu
  → mapping: voice_settings.stability
  → min: 0, max: 1, step: 0.1
```

### Image-to-Video Model

```
Parameter: image_url
  → labelKey: source_image_image
  → displayMode: source       ← Input media at top
  → mapping: image_url

Parameter: prompt
  → labelKey: prompt_textarea
  → displayMode: primary      ← Text below the image
  → mapping: prompt

Parameter: duration
  → labelKey: duration_dropdown
  → displayMode: inline
  → mapping: duration
```

---

## Adding a New LabelKey

If you need a labelKey that doesn't exist:

### 1. Add to Label Registry

Edit `frontend/lib/constants/label-registry.ts`:

```typescript
// Add to LabelKey type
export type LabelKey =
  // ... existing keys
  | "my_new_param_dropdown"

// Add to LABEL_REGISTRY
export const LABEL_REGISTRY: Record<LabelKey, LabelRegistryEntry> = {
  // ... existing entries
  
  my_new_param_dropdown: {
    component: "dropdown",
    icon: MyIcon,
  },
}
```

### 2. Add i18n Labels

Edit `frontend/messages/en.json`:

```json
{
  "params": {
    "my_new_param_dropdown": {
      "label": "My Parameter",
      "description": "Description of what this does."
    }
  }
}
```

Edit `frontend/messages/tr.json` for Turkish translation.

### 3. Use in Model Config

Now you can use `my_new_param_dropdown` as a labelKey in the admin panel.

---

## API Mapping

### Simple Mapping

```
mapping: "prompt"
→ API receives: { "prompt": "value" }
```

### Nested Mapping (dot notation)

```
mapping: "voice_settings.stability"
→ API receives: { "voice_settings": { "stability": 0.5 } }
```

### Duration to Frames

For models that expect frame count instead of seconds:

```
mapping: "num_frames"
multiplyByFps: 30
→ duration=5 becomes num_frames=150
```

### Multiple Images

For parameters accepting multiple images:

```
count: 4
mappingType: "array"
→ API receives: { "images": ["url1", "url2", ...] }

mappingType: "indexed"
→ API receives: { "image_1": "url1", "image_2": "url2", ... }
```

---

## Migration from Old System

If you have models using the old `param_mappings` system:

### Run Migration Script

```bash
# Preview changes
npx tsx frontend/scripts/migrate-to-label-keys.ts --dry-run

# Migrate specific model
npx tsx frontend/scripts/migrate-to-label-keys.ts --endpoint fal-ai/kling-video

# Migrate all
npx tsx frontend/scripts/migrate-to-label-keys.ts
```

### Manual Migration

Old format:
```json
{
  "parameters": [{ "key": "aspect_ratio", "type": "string", "enum": [...] }],
  "param_mappings": { "aspect_ratio": { "mapping": "aspect_ratio" } },
  "inline_params": ["aspect_ratio"],
  "hidden_params": []
}
```

New format:
```json
{
  "parameters": [{
    "key": "aspect_ratio",
    "type": "string",
    "enum": [...],
    "labelKey": "aspect_ratio_dropdown",
    "displayMode": "inline",
    "mapping": "aspect_ratio"
  }]
}
```

---

## Troubleshooting

### Parameter Not Showing

1. Check if `labelKey` is set
2. Check if `displayMode` is not "hidden"
3. Verify the labelKey exists in `LABEL_REGISTRY`

### Wrong Component Type

The component is determined by the labelKey suffix. Use:
- `_dropdown` for select inputs
- `_slider` for range inputs
- `_toggle` for booleans

### i18n Label Not Showing

1. Check `messages/en.json` has the labelKey
2. Verify the structure: `params.{labelKey}.label`

### API Field Wrong Name

Check the `mapping` field. Use dot notation for nested fields.

