"""
Octupost Gateway

Unified gateway for all AI generation requests:
1. Resolve model alias → endpoint
2. Infer generation mode from inputs
3. Transform parameters for FAL API
4. Execute generation
5. Normalize response

This file consolidates:
- resolvers/orchestrator.py
- resolvers/fal.py
- services/generation_service.py
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Tuple

import fal_client

from app.registry import (
    MODEL_ALIASES,
    get_model_type,
    get_capabilities,
    RESOLUTION_HEIGHTS,
    ASPECT_RATIO_TUPLES,
    ASPECT_RATIO_DIMENSIONS,
)


# ===========================================================================
# CONSTANTS
# ===========================================================================

# Friendly aspect ratio names (for user input normalization)
ASPECT_RATIO_VALUES: dict[str, str] = {
    "landscape": "16:9",
    "portrait": "9:16",
    "square": "1:1",
    "wide": "21:9",
    "standard": "4:3",
    "cinematic": "21:9",
}


# ===========================================================================
# RESOLVED REQUEST DATACLASS
# ===========================================================================

@dataclass
class ResolvedRequest:
    """
    Result of request resolution.

    Contains the resolved model endpoint, inferred mode,
    and transformed parameters ready for the provider.
    """

    # Model information
    endpoint: str
    friendly_name: str
    model_type: str
    provider: str

    # Inferred mode
    mode: str

    # Transformed parameters for the provider API
    params: dict[str, Any] = field(default_factory=dict)

    # Original request for reference
    original: dict[str, Any] = field(default_factory=dict)

    # Validation errors (if any)
    errors: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """Check if resolution was successful."""
        return len(self.errors) == 0


# ===========================================================================
# MODEL RESOLUTION
# ===========================================================================

def resolve_model(model_input: str) -> Tuple[str, str, Optional[str]]:
    """
    Resolve a model name to endpoint and extract mode suffix.

    Some models have mode suffixes like "veo3.1/image-to-video".
    This function separates the base model from the mode.

    Args:
        model_input: User-provided model name

    Returns:
        Tuple of (endpoint, friendly_name, explicit_mode)
    """
    normalized = model_input.lower().strip()
    explicit_mode = None
    friendly_name = normalized

    # Check for explicit mode suffix
    mode_suffixes = [
        "text-to-video",
        "image-to-video",
        "first-last-frame-to-video",
        "reference-to-video",
        "text-to-image",
        "image-to-image",
        "text-to-speech",
        "video-to-audio",
    ]

    for suffix in mode_suffixes:
        if normalized.endswith(f"/{suffix}"):
            explicit_mode = suffix
            friendly_name = normalized.rsplit(f"/{suffix}", 1)[0]
            break

    # Resolve the base model alias
    endpoint = MODEL_ALIASES.get(friendly_name, model_input)

    # If mode was explicit, append it to endpoint if not already there
    if explicit_mode and not endpoint.endswith(f"/{explicit_mode}"):
        endpoint = f"{endpoint}/{explicit_mode}"

    return endpoint, friendly_name, explicit_mode


def get_model_provider(model_id: str) -> str:
    """Extract the provider from a model ID."""
    endpoint, _, _ = resolve_model(model_id)

    if "/" in endpoint:
        return endpoint.split("/")[0]

    if "elevenlabs" in model_id.lower():
        return "elevenlabs"
    if "veed" in model_id.lower():
        return "veed"

    return "fal-ai"


def get_required_inputs(model_id: str, mode: str) -> list[str]:
    """
    Get required input fields dynamically from registry.

    This uses the registry as the single source of truth - no hardcoded mappings needed.
    When you add a new model to registry.py, validation automatically works.
    """
    from app.registry import get_required_inputs_for_mode
    return get_required_inputs_for_mode(model_id, mode)


def validate_mode_inputs(model_id: str, request: dict[str, Any], mode: str) -> list[str]:
    """Validate that required inputs for a mode are present."""
    required = get_required_inputs(model_id, mode)
    missing = []

    for field_name in required:
        if not request.get(field_name):
            missing.append(field_name)

    return missing


# ===========================================================================
# ASPECT RATIO RESOLUTION
# ===========================================================================

def resolve_aspect_ratio(value: str) -> str:
    """Resolve friendly aspect ratio to standard format."""
    normalized = value.lower().strip()

    # Check if it's a friendly name
    if normalized in ASPECT_RATIO_VALUES:
        return ASPECT_RATIO_VALUES[normalized]

    # Check if it's already a ratio
    if ":" in value:
        return value

    return value


# ===========================================================================
# REGISTRY-DRIVEN PARAMETER TRANSFORMATION
# ===========================================================================

def _calculate_image_size(aspect_ratio: str, resolution: str) -> dict[str, int]:
    """Calculate exact pixel dimensions from aspect_ratio and resolution."""
    height = RESOLUTION_HEIGHTS.get(resolution, 1080)
    w_ratio, h_ratio = ASPECT_RATIO_TUPLES.get(aspect_ratio, (16, 9))
    width = int(height * w_ratio / h_ratio)
    return {"width": width, "height": height}


def transform_for_provider(
    model_id: str,
    mode: str,
    params: dict[str, Any],
) -> Tuple[str, dict[str, Any]]:
    """
    Transform parameters using registry's outbound_schema.

    This is the single source of truth for parameter transformation.
    Reads from registry.py's ModelCapabilities to apply:
    - field_map: Rename our keys to provider's keys
    - transforms: Apply value transformation functions
    - value_map: Map values to provider-specific values
    - compute: Calculate derived fields (e.g., image_size from aspect_ratio + resolution)
    - static: Add default values if not set
    - fixed: Always override with these values
    - optional: Skip if None

    Args:
        model_id: Model identifier
        mode: Generation mode (text-to-video, image-to-video, etc.)
        params: User-provided parameters

    Returns:
        Tuple of (endpoint, transformed_params)

    Raises:
        ValueError: If a parameter value is not in the allowed enum
    """
    # Get capabilities from registry
    caps = get_capabilities(model_id)
    if not caps:
        # Fallback: return params unchanged with model_id as endpoint
        return model_id, params.copy()

    # Validate input values against registry enums
    # Merge base inputs with mode-specific inputs
    all_inputs = dict(caps.inputs) if caps.inputs else {}
    if mode and mode in caps.modes:
        mode_caps = caps.modes[mode]
        if mode_caps.inputs:
            all_inputs.update(mode_caps.inputs)

    # Check each param against its enum (if defined)
    for param_key, param_value in params.items():
        if param_value is None:
            continue
        if param_key in all_inputs:
            input_field = all_inputs[param_key]
            if input_field.enum and param_value not in input_field.enum:
                raise ValueError(
                    f"Invalid value '{param_value}' for parameter '{param_key}'. "
                    f"Allowed values: {input_field.enum}"
                )

    # Get base outbound_schema
    base_schema = caps.outbound_schema or {}

    # Get mode-specific outbound_schema and merge
    mode_schema = {}
    if mode and mode in caps.modes:
        mode_caps = caps.modes[mode]
        if mode_caps.outbound_schema:
            mode_schema = mode_caps.outbound_schema

    # Merge schemas (mode overrides base)
    merged_schema = {**base_schema}
    for key, value in mode_schema.items():
        if key == "field_map" and "field_map" in merged_schema:
            merged_schema["field_map"] = {**merged_schema["field_map"], **value}
        elif key == "transforms" and "transforms" in merged_schema:
            merged_schema["transforms"] = {**merged_schema["transforms"], **value}
        elif key == "value_map" and "value_map" in merged_schema:
            merged_schema["value_map"] = {**merged_schema["value_map"], **value}
        elif key == "compute" and "compute" in merged_schema:
            merged_schema["compute"] = {**merged_schema["compute"], **value}
        elif key == "static" and "static" in merged_schema:
            merged_schema["static"] = {**merged_schema["static"], **value}
        elif key == "fixed" and "fixed" in merged_schema:
            merged_schema["fixed"] = {**merged_schema["fixed"], **value}
        elif key == "optional" and "optional" in merged_schema:
            merged_schema["optional"] = list(set(merged_schema["optional"] + value))
        else:
            merged_schema[key] = value

    # Get endpoint from merged schema
    endpoint = merged_schema.get("endpoint", model_id)

    # Build result dictionary
    result: dict[str, Any] = {}

    # Get field_map for renaming
    # field_map format: {"our_key": "fal_key"} - our key maps to FAL's key
    field_map = merged_schema.get("field_map", {})

    # Copy all params, applying field_map
    for our_key, value in params.items():
        if value is None:
            continue
        fal_key = field_map.get(our_key, our_key)
        result[fal_key] = value

    # Apply transforms (value functions)
    transforms = merged_schema.get("transforms", {})
    for fal_key, transform_fn in transforms.items():
        if fal_key in result and callable(transform_fn):
            try:
                result[fal_key] = transform_fn(result[fal_key])
            except (TypeError, ValueError):
                pass

    # Apply value_map (value lookups)
    value_map = merged_schema.get("value_map", {})
    for fal_key, mapping in value_map.items():
        if fal_key in result:
            source_value = result[fal_key]
            # Handle both dict and callable mappings
            if isinstance(mapping, dict) and source_value in mapping:
                result[fal_key] = mapping[source_value]

    # Apply compute (calculated fields)
    compute = merged_schema.get("compute", {})
    for target_key, config in compute.items():
        compute_type = config.get("type")

        if compute_type == "image_dimensions":
            aspect_ratio = params.get("aspect_ratio", "16:9")
            resolution = params.get("resolution", "1080p")
            result[target_key] = _calculate_image_size(aspect_ratio, resolution)
            # Remove the input fields that were used for computation
            result.pop("aspect_ratio", None)
            result.pop("resolution", None)

    # Apply static defaults (only if not already set)
    static = merged_schema.get("static", {})
    for key, value in static.items():
        if key not in result:
            result[key] = value

    # Apply fixed overrides (always override)
    fixed = merged_schema.get("fixed", {})
    for key, value in fixed.items():
        result[key] = value

    # Handle optional fields with None values or special "_skip_" keyword
    # "_skip_" means don't include this field in the payload (e.g., language auto-detection)
    optional = set(merged_schema.get("optional", []))
    result = {
        k: v for k, v in result.items()
        if (v is not None and v != "_skip_") or k not in optional
    }

    return endpoint, result


# ===========================================================================
# RESPONSE NORMALIZATION (INBOUND)
# ===========================================================================

def transform_from_provider(
    model_id: str,
    mode: str,
    response: dict[str, Any],
    original_params: dict[str, Any],
) -> dict[str, Any]:
    """
    Transform FAL response to normalized format using registry's inbound_schema.

    Symmetrical to transform_for_provider().

    Args:
        model_id: Model identifier
        mode: Generation mode (text-to-video, etc.)
        response: Raw FAL response
        original_params: Original user parameters (for dimension defaults)

    Returns:
        Normalized response:
        {
            "outputs": [{"url", "content_type", "file_name", "file_size", "width", "height", "duration"}],
            "media_type": "image" | "video" | "audio",
            # ... extra fields preserved (seed, timestamps, etc.)
        }
    """
    from app.registry import (
        get_capabilities,
        INBOUND_VIDEO,
        INBOUND_IMAGE,
        INBOUND_AUDIO,
        ASPECT_RATIO_DIMENSIONS,
    )

    caps = get_capabilities(model_id)

    # Get merged inbound_schema (base + mode)
    schema = _get_merged_inbound_schema(caps, mode)

    # Fallback to default schema based on output_media_type
    if not schema:
        media_type = caps.output_media_type if caps else None
        schema = _get_default_inbound_schema(media_type)

    return _apply_inbound_schema(response, schema, original_params)


def _get_merged_inbound_schema(
    caps: Optional[Any],
    mode: str,
) -> Optional[dict[str, Any]]:
    """Merge base and mode-specific inbound schemas."""
    if not caps:
        return None

    base_schema = caps.inbound_schema or {}
    mode_schema = {}

    if mode and mode in caps.modes:
        mode_caps = caps.modes[mode]
        if mode_caps.inbound_schema:
            mode_schema = mode_caps.inbound_schema

    if not base_schema and not mode_schema:
        return None

    if not base_schema:
        return mode_schema.copy()
    if not mode_schema:
        return base_schema.copy()

    # Merge: mode overrides base
    merged = base_schema.copy()
    for key, value in mode_schema.items():
        if key in ("field_map", "transforms", "defaults") and key in merged:
            merged[key] = {**merged.get(key, {}), **value}
        elif key == "preserve" and key in merged:
            merged[key] = list(set(merged.get(key, []) + value))
        else:
            merged[key] = value

    return merged


def _get_default_inbound_schema(media_type: Optional[str]) -> dict[str, Any]:
    """Get default inbound schema based on media type."""
    from app.registry import INBOUND_VIDEO, INBOUND_IMAGE, INBOUND_AUDIO, INBOUND_JSON

    defaults = {
        "video": INBOUND_VIDEO,
        "image": INBOUND_IMAGE,
        "audio": INBOUND_AUDIO,
        "json": INBOUND_JSON,
    }
    return defaults.get(media_type, INBOUND_VIDEO)


def _apply_inbound_schema(
    response: dict[str, Any],
    schema: dict[str, Any],
    original_params: dict[str, Any],
) -> dict[str, Any]:
    """Apply inbound schema to transform FAL response to normalized format."""
    from app.registry import ASPECT_RATIO_DIMENSIONS

    # Handle passthrough mode (for JSON/transcript responses)
    if schema.get("passthrough"):
        return {
            "outputs": [response],  # Entire response as single output
            "media_type": schema.get("media_type", "json"),
        }

    outputs = []
    source_key = schema.get("source_key", "url")
    media_type = schema.get("media_type", "unknown")
    field_map = schema.get("field_map", {})
    defaults = schema.get("defaults", {})
    preserve = schema.get("preserve", [])
    transforms = schema.get("transforms", {})

    # Extract source data from response
    raw_data = _extract_source_data(response, source_key)

    # Normalize to list
    if not isinstance(raw_data, list):
        raw_data = [raw_data] if raw_data else []

    # Get default dimensions from original_params
    aspect_ratio = original_params.get("aspect_ratio", "16:9")
    default_width, default_height = ASPECT_RATIO_DIMENSIONS.get(
        aspect_ratio, (1920, 1080)
    )

    # Transform each item
    for item in raw_data:
        output = _transform_output_item(
            item, field_map, defaults, transforms, original_params,
            default_width, default_height, media_type
        )
        if output.get("url"):  # Only include valid outputs with URL
            outputs.append(output)

    # Build normalized response
    normalized: dict[str, Any] = {
        "outputs": outputs,
        "media_type": media_type,
    }

    # Preserve extra fields from response (exclude media-specific keys)
    excluded = {source_key, "images", "image", "video", "audio", "audio_url", "url"}
    for key, value in response.items():
        if key not in excluded:
            normalized[key] = value

    # Also preserve explicitly listed fields
    for key in preserve:
        if key in response and key not in normalized:
            normalized[key] = response[key]

    return normalized


def _extract_source_data(
    response: dict[str, Any],
    source_key: str,
) -> Any:
    """Extract source data from response, handling common variants."""
    # Direct field access
    if source_key in response:
        return response[source_key]

    # Handle common variants
    if source_key == "images":
        # Try "image" (singular) as fallback
        if "image" in response:
            return [response["image"]]
    elif source_key == "audio":
        # Try "audio_url" as fallback
        if "audio_url" in response:
            return {"url": response["audio_url"], "duration": response.get("duration")}
    elif source_key == "video":
        # Try top-level "url" for video
        if "url" in response:
            return {"url": response["url"]}

    # Final fallback: top-level url
    if "url" in response:
        return {"url": response["url"]}

    return None


def _transform_output_item(
    item: Any,
    field_map: dict[str, str],
    defaults: dict[str, Any],
    transforms: dict[str, Any],
    original_params: dict[str, Any],
    default_width: int,
    default_height: int,
    media_type: str,
) -> dict[str, Any]:
    """Transform a single output item to normalized format."""
    output: dict[str, Any] = {}

    # Handle string URL (simple response format)
    if isinstance(item, str):
        output["url"] = item
        output["content_type"] = defaults.get("content_type")
        output["file_name"] = None
        output["file_size"] = None
        output["width"] = default_width if media_type != "audio" else None
        output["height"] = default_height if media_type != "audio" else None
        output["duration"] = defaults.get("duration") or original_params.get("duration")
        return output

    # Handle dict response
    if isinstance(item, dict):
        # Standard fields - use from response or defaults
        output["url"] = item.get("url")
        output["content_type"] = item.get("content_type", defaults.get("content_type"))
        output["file_name"] = item.get("file_name")
        output["file_size"] = item.get("file_size")

        # Dimensions - audio has no dimensions
        if media_type == "audio":
            output["width"] = None
            output["height"] = None
        else:
            output["width"] = item.get("width") or default_width
            output["height"] = item.get("height") or default_height

        # Duration - use from response, then original_params, then defaults
        output["duration"] = (
            item.get("duration")
            or original_params.get("duration")
            or defaults.get("duration")
        )

        # Frame URLs for video continuity (FAL extracts first/last frames)
        if item.get("start_frame_url"):
            output["start_frame_url"] = item.get("start_frame_url")
        if item.get("end_frame_url"):
            output["end_frame_url"] = item.get("end_frame_url")

        # Apply field_map if defined
        for fal_key, our_key in field_map.items():
            if fal_key in item:
                value = item[fal_key]
                # Apply transform if exists
                if our_key in transforms and callable(transforms[our_key]):
                    value = transforms[our_key](value)
                output[our_key] = value

    return output


# ===========================================================================
# REQUEST RESOLUTION
# ===========================================================================

def resolve_request(request: dict[str, Any]) -> ResolvedRequest:
    """
    Resolve a user-friendly request to provider-ready format.

    This orchestrates the full resolution pipeline:
    1. Extract model and mode from request (both required)
    2. Validate required inputs for mode
    3. Transform parameters using registry's outbound_schema (single source of truth)
    """
    errors = []

    model_input = request.get("model", "")
    mode = request.get("mode", "")

    if not model_input:
        errors.append("Model is required")
    if not mode:
        errors.append("Mode is required")

    if errors:
        return ResolvedRequest(
            endpoint="",
            friendly_name="",
            model_type="unknown",
            provider="unknown",
            mode="unknown",
            original=request,
            errors=errors,
        )

    # Get model type from registry
    model_type = get_model_type(model_input) or "unknown"

    # Validate required inputs for mode (uses registry as single source of truth)
    missing = validate_mode_inputs(model_input, request, mode)
    for field_name in missing:
        errors.append(f"Missing required field for {mode}: {field_name}")

    # Use registry-driven transformation (single source of truth)
    # The endpoint is looked up from the mode's outbound_schema
    endpoint, params = transform_for_provider(model_input, mode, request)
    provider = endpoint.split("/")[0] if "/" in endpoint else "unknown"

    return ResolvedRequest(
        endpoint=endpoint,
        friendly_name=model_input,
        model_type=model_type,
        provider=provider,
        mode=mode,
        params=params,
        original=request,
        errors=errors,
    )
