# Video Generation System Documentation

This document explains how the backend API handles video generation requests, focusing on parameter transformation, validation, and the data flow from frontend to Fal AI.

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Key Files](#key-files)
4. [Provider.json Schema](#providerjson-schema)
5. [Parameter Transformation](#parameter-transformation)
6. [Validation System](#validation-system)
7. [Request Flow](#request-flow)
8. [Model-Specific Behavior](#model-specific-behavior)
9. [Debugging Guide](#debugging-guide)
10. [Common Issues](#common-issues)

---

## System Overview

The video generation system routes requests through several layers:

1. **Frontend** sends parameters with standard types (e.g., `duration: 4` as integer)
2. **Routes** receive requests and validate them dynamically
3. **Registry** provides model configuration from `provider.json`
4. **Transformer** converts parameters based on model requirements
5. **FalProvider** sends transformed parameters to Fal AI

The core challenge this system solves: **Different AI models expect different parameter types and formats**, even for the same logical parameter like "duration".

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                 FRONTEND                                     │
│                                                                              │
│   user input ──► VideoGenerator.tsx ──► apiClient.generateVideo()           │
│                                              │                               │
│                                              ▼                               │
│                                    POST /api/generate/video                  │
│                                    {                                         │
│                                      model: "fal-ai/veo3.1",                 │
│                                      prompt: "A cat walking",                │
│                                      duration: 4,  ◄── INTEGER               │
│                                      aspect_ratio: "16:9"                    │
│                                    }                                         │
└──────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                              BACKEND API                                     │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  routes/generate.py                                                    │  │
│  │  ─────────────────                                                     │  │
│  │  1. Receives FlexibleVideoRequest                                      │  │
│  │  2. Calls validate_params(model_id, params)                            │  │
│  │  3. Creates Inngest event with raw params                              │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                           │                                  │
│                                           ▼                                  │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  registry/reader.py                                                    │  │
│  │  ──────────────────                                                    │  │
│  │  • Loads provider.json (46 models)                                     │  │
│  │  • get_model(model_id) → returns model config                          │  │
│  │  • validate_params() → checks against accepted_values                  │  │
│  │                                                                        │  │
│  │  provider.json structure:                                              │  │
│  │  [{endpoint, type, parameters: [{key, mapping, mapping_type}]}]        │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                           │                                  │
│                                           ▼                                  │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  Inngest Worker (generate.py)                                          │  │
│  │  ────────────────────────────                                          │  │
│  │  • Receives event with job_id, model, params                           │  │
│  │  • Calls generation_service.generate(model_id, params)                 │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                           │                                  │
│                                           ▼                                  │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  services/generation_service.py                                        │  │
│  │  ──────────────────────────────                                        │  │
│  │  • Gets model config from registry                                     │  │
│  │  • Routes to FalProvider.generate()                                    │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                           │                                  │
│                                           ▼                                  │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  services/providers/fal_provider.py                                    │  │
│  │  ──────────────────────────────────                                    │  │
│  │  1. Calls transform_params(params, model_config)                       │  │
│  │  2. Sends to fal_client.subscribe_async(endpoint, arguments)           │  │
│  │  3. Normalizes response                                                │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                           │                                  │
│                                           ▼                                  │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  services/providers/transformer.py                                     │  │
│  │  ─────────────────────────────────                                     │  │
│  │  THE CRITICAL FILE FOR PARAMETER HANDLING                              │  │
│  │                                                                        │  │
│  │  transform_params(params, model_config):                               │  │
│  │    • Reads parameter definitions from model_config                     │  │
│  │    • Applies type conversion based on mapping_type                     │  │
│  │    • Handles special transformations from "notes"                      │  │
│  │    • Renames keys based on "mapping"                                   │  │
│  │    • Merges default_values                                             │  │
│  │                                                                        │  │
│  │  Example transformations:                                              │  │
│  │    duration: 4 (int) ──► duration: "4s" (string)  [Veo3.1]             │  │
│  │    duration: 4 (int) ──► num_frames: 120 (int)    [Long Cat]           │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                           │                                  │
│                                           ▼                                  │
│                                      FAL AI API                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Files

| File | Purpose |
|------|---------|
| `packages/shared/src/registry/provider.json` | **Source of truth** for all model configurations |
| `api/app/registry/reader.py` | Loads and queries provider.json, validation |
| `api/app/registry/types.py` | TypedDict definitions matching provider.json schema |
| `api/app/services/providers/transformer.py` | **Parameter transformation logic** |
| `api/app/services/providers/fal_provider.py` | Fal AI integration, calls transformer |
| `api/app/routes/generate.py` | API endpoints, request validation |
| `api/app/services/generation_service.py` | Orchestrates generation flow |
| `api/app/inngest/functions/generate.py` | Background job processing |

---

## Provider.json Schema

Each model in `provider.json` has this structure:

```json
{
  "fps": 24,
  "link": "https://fal.ai/models/fal-ai/veo3.1",
  "tier": "Elite",
  "type": "text-to-video",
  "price": {
    "unit": "per_second",
    "price_per_unit": 0.2,
    "multiplier_field_key": "enable_audio",
    "multiplier_value": 2
  },
  "endpoint": "fal-ai/veo3.1",
  "provider": "Veo3.1",
  "is_active": true,
  "parameters": [
    {
      "key": "prompt",
      "type": "string",
      "notes": "",
      "default": "",
      "mapping": "prompt",
      "required": true,
      "mapping_type": "string"
    },
    {
      "key": "duration",
      "type": "integer",
      "notes": "Add s at the end of the duration",
      "default": 4,
      "mapping": "duration",
      "required": true,
      "mapping_type": "string",
      "accepted_values": {
        "steps": 2,
        "max_duration": 8,
        "min_duration": 4
      }
    },
    {
      "default_values": {
        "auto_fix": true
      }
    }
  ],
  "parent_type": "text-to-video"
}
```

### Parameter Definition Fields

| Field | Description |
|-------|-------------|
| `key` | Frontend parameter name (e.g., "duration") |
| `type` | Frontend type: "string", "integer", "float", "boolean" |
| `mapping` | Backend/API parameter name (e.g., "num_frames") |
| `mapping_type` | Target type for the API |
| `notes` | **Transformation hints** - parsed by transformer |
| `required` | Whether parameter is required |
| `default` | Default value if not provided |
| `accepted_values` | Validation constraints (array or range object) |

### Important `notes` Values

The `notes` field contains hints that the transformer parses:

| Note | Transformation Applied |
|------|----------------------|
| `"Add s at the end of the duration"` | Converts `4` → `"4s"` |
| `"Multiply second by 30 to get the number of frames"` | Converts `4` → `120` |
| `"Value type is string"` | Converts to string (no suffix) |

---

## Parameter Transformation

The transformer (`services/providers/transformer.py`) applies these transformations:

### 1. Type Conversion Based on `mapping_type`

```python
# If mapping_type is "string" and value is not string:
if mapping_type == "string" and not isinstance(value, str):
    if "Add s at the end" in notes:
        return f"{value}s"  # 4 → "4s"
    else:
        return str(value)   # 4 → "4"
```

### 2. Duration Multiplication

```python
# If notes contain multiplication instruction:
if "Multiply second by 30" in notes:
    return int(value * 30)  # 4 → 120
```

### 3. Key Renaming

```python
# Rename from frontend key to API key:
# key="duration", mapping="num_frames"
# Result: {num_frames: 120} instead of {duration: 4}
```

### 4. Default Value Merging

```python
# Merge default_values from provider.json:
# {"fps": 30, "seed": 42, "sync_mode": false}
```

---

## Validation System

Validation happens in `registry/reader.py`:

```python
def validate_params(model_id: str, params: dict) -> ValidationResult:
    # 1. Check model exists
    # 2. For each required parameter:
    #    - Skip if has default or is boolean
    #    - Error if truly required and missing
    # 3. For each provided value:
    #    - Check type matches
    #    - Check against accepted_values (enum or range)
```

### Accepted Values Types

**Array (enum):**
```json
"accepted_values": ["720p", "1080p", "1440p"]
```

**Range object:**
```json
"accepted_values": {
  "steps": 2,
  "min_duration": 4,
  "max_duration": 8
}
```

---

## Request Flow

### Step-by-Step Flow

1. **Frontend sends:**
   ```json
   POST /api/generate/video
   {
     "model": "fal-ai/veo3.1",
     "prompt": "A cat walking",
     "duration": 4,
     "aspect_ratio": "16:9"
   }
   ```

2. **Route validates:**
   - Checks model is valid and active
   - Validates duration is within 4-8 (from accepted_values)

3. **Inngest job created:**
   - Event `ai/video.generate` with raw params

4. **Worker processes:**
   - Gets model config from registry
   - Calls `FalProvider.generate()`

5. **FalProvider transforms:**
   ```python
   input:  {"prompt": "...", "duration": 4, "aspect_ratio": "16:9"}
   output: {"prompt": "...", "duration": "4s", "aspect_ratio": "16:9", "auto_fix": true}
   ```

6. **Fal AI receives:**
   ```python
   fal_client.subscribe_async("fal-ai/veo3.1", arguments={
     "prompt": "A cat walking",
     "duration": "4s",
     "aspect_ratio": "16:9",
     "auto_fix": true
   })
   ```

---

## Model-Specific Behavior

### Veo3.1 Models
- Duration: integer → string with "s" suffix
- `duration: 4` becomes `duration: "4s"`
- Endpoints: `fal-ai/veo3.1`, `fal-ai/veo3.1/fast`, `fal-ai/veo3.1/image-to-video`

### Hailuo Models
- Duration: integer → string (no suffix)
- `duration: 6` becomes `duration: "6"`
- Notes say "Value type is string"
- Endpoints: `fal-ai/minimax/hailuo-2.3/*`

### Long Cat Models
- Duration: integer → num_frames (× 30)
- `duration: 4` becomes `num_frames: 120`
- Uses `mapping: "num_frames"` in parameter definition
- Endpoints: `fal-ai/longcat-video/*`

### Sora 2 Models
- Duration: stays as integer
- `duration: 8` stays `duration: 8`
- `mapping_type: "integer"`
- Endpoints: `fal-ai/sora-2/*`

### LTX 2 Models
- Duration: stays as integer
- Endpoints: `fal-ai/ltx-2/*`

### Kling Models
- Duration: stays as integer
- Some have `generate_audio` mapped from `enable_audio`
- Endpoints: `fal-ai/kling-video/*`

---

## Debugging Guide

### 1. Check Model Configuration

```python
from app.registry import get_model

model = get_model("fal-ai/veo3.1")
print(model)  # See full config

# Check specific parameter
for param in model.get("parameters", []):
    if isinstance(param, dict) and param.get("key") == "duration":
        print(f"mapping: {param.get('mapping')}")
        print(f"mapping_type: {param.get('mapping_type')}")
        print(f"notes: {param.get('notes')}")
```

### 2. Test Transformation

```python
from app.registry import get_model
from app.services.providers.transformer import transform_params

model_config = get_model("fal-ai/veo3.1")
input_params = {"prompt": "test", "duration": 4, "aspect_ratio": "16:9"}
output = transform_params(input_params, model_config)
print(output)
# Expected: {..., "duration": "4s", ...}
```

### 3. Test Validation

```python
from app.registry import validate_params

result = validate_params("fal-ai/veo3.1", {
    "prompt": "test",
    "duration": 100  # Invalid - max is 8
})
print(result)
# Expected: {"valid": False, "errors": ["duration must be <= 8"]}
```

### 4. Reload Registry

If you modify `provider.json`, reload the cache:

```python
from app.registry import reload_registry
reload_registry()
```

---

## Common Issues

### Issue: "Duration must be <= X" error

**Cause:** Duration value exceeds model's max_duration in accepted_values.

**Solution:** Check the model's accepted_values in provider.json:
```json
"accepted_values": {
  "max_duration": 8,  // This is the limit
  "min_duration": 4
}
```

### Issue: Fal AI returns "invalid parameter type"

**Cause:** Parameter not being transformed correctly.

**Debug:**
1. Find the model in provider.json
2. Check the parameter's `mapping_type`
3. Check if `notes` contains transformation hints
4. Verify transformer is handling this case

**Example fix in transformer.py:**
```python
if "Add s at the end" in notes:
    return f"{value}s"
```

### Issue: Parameter not being renamed

**Cause:** The `mapping` field is different from `key` but not being applied.

**Debug:**
```python
# In provider.json:
{
  "key": "duration",       # Frontend name
  "mapping": "num_frames"  # API name (should be renamed)
}
```

Check that `transform_params()` is renaming correctly:
```python
if mapping != key:
    del result[key]
result[mapping] = transformed_value
```

### Issue: Missing default_values

**Cause:** Some models require specific defaults (like `sync_mode: false`).

**Solution:** Check for `default_values` object in parameters array:
```json
{
  "default_values": {
    "fps": 30,
    "seed": 42,
    "sync_mode": false
  }
}
```

### Issue: Model not found

**Cause:** Using wrong model ID format.

**Solution:** Model IDs are the `endpoint` values in provider.json:
```
✓ Correct: "fal-ai/veo3.1"
✗ Wrong:   "veo3.1" or "Veo3.1"
```

---

## Adding a New Model

1. **Add to provider.json:**
   ```json
   {
     "endpoint": "fal-ai/new-model",
     "type": "text-to-video",
     "provider": "New Provider",
     "is_active": true,
     "parameters": [...]
   }
   ```

2. **Define parameters correctly:**
   - Set `mapping` if API expects different key name
   - Set `mapping_type` if type conversion needed
   - Add `notes` for special transformations
   - Set `accepted_values` for validation

3. **Test transformation:**
   ```python
   from app.registry import get_model
   from app.services.providers.transformer import transform_params
   
   config = get_model("fal-ai/new-model")
   result = transform_params({"duration": 4}, config)
   print(result)  # Verify output
   ```

4. **Reload registry if needed:**
   ```python
   from app.registry import reload_registry
   reload_registry()
   ```

---

## Quick Reference: Transformation Rules

| notes Content | Transformation |
|---------------|----------------|
| `"Add s at the end"` | `4` → `"4s"` |
| `"Multiply second by 30"` | `4` → `120` |
| `"Value type is string"` | `4` → `"4"` |
| (none, mapping_type=integer) | No change |
| (none, mapping_type=string) | `4` → `"4"` |

| mapping vs key | Result |
|----------------|--------|
| Same | No renaming |
| Different | Key renamed to mapping value |

---

## Contact

For questions about this system, refer to:
- This documentation
- `provider.json` for model configurations
- `transformer.py` for transformation logic
- `reader.py` for validation logic

