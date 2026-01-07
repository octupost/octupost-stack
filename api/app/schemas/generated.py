"""
Auto-generated Pydantic models from the capabilities registry.

This module generates model-specific request schemas that provide:
- Proper OpenAPI documentation with required/optional fields
- Type validation with min/max constraints
- Enum validation for option fields
- Discriminated union support for Scalar UI

The models are generated at import time from the registry.
"""

from typing import Any, Literal, Optional
from pydantic import BaseModel, Field, create_model

from app.registry import (
    get_all_capabilities,
    InputField,
    ModelCapabilities,
    _Required,
)


def _sanitize_model_name(model_id: str) -> str:
    """Convert model_id to valid Python class name."""
    name = model_id.replace("/", "_").replace("-", "_").replace(".", "_")
    parts = name.split("_")
    return "".join(part.capitalize() for part in parts if part)


def _get_field_description(field_key: str, field_type: str, field: InputField) -> str:
    """Generate a user-friendly description for a field."""
    # Known field descriptions
    descriptions = {
        "prompt": "Text description of what you want to generate. Be specific about subjects, actions, style, and mood.",
        "negative_prompt": "Things to avoid in the generation. Specify unwanted elements, styles, or qualities.",
        "duration": f"Length of the generated content in seconds",
        "aspect_ratio": "Output aspect ratio",
        "resolution": "Output resolution quality",
        "seed": "Random seed for reproducibility. Use the same seed to get similar results.",
        "image_url": "URL of the source image",
        "video_url": "URL of the source video",
        "audio_url": "URL of the source audio file",
        "first_frame_url": "URL of the image to use as the first frame",
        "last_frame_url": "URL of the image to use as the last frame",
        "reference_url": "URL of a reference image or video for style guidance",
        "generate_audio": "Whether to generate audio with the video",
        "text": "The text content to process",
        "voice_id": "ID of the voice to use for speech synthesis",
        "language": "Language code for the output",
    }
    
    base_desc = descriptions.get(field_key, field_key.replace("_", " ").title())
    
    # Add range info for numbers
    if field.min_value is not None and field.max_value is not None:
        base_desc += f" (range: {field.min_value}-{field.max_value})"
    elif field.min_value is not None:
        base_desc += f" (min: {field.min_value})"
    elif field.max_value is not None:
        base_desc += f" (max: {field.max_value})"
    
    # Add enum options
    if field.enum:
        options_str = ", ".join(f"'{v}'" for v in field.enum)
        base_desc += f". Options: {options_str}"
    
    return base_desc


def _create_field_type(field: InputField) -> tuple[type, Any]:
    """
    Create Pydantic field type and Field() from InputField.

    Three states based on field.default:
    - REQUIRED sentinel → required, not nullable
    - None → optional AND nullable (like seed)
    - any value → optional with default, NOT nullable

    Returns: (type_annotation, Field instance)
    """
    # Base type
    if field.type == "string":
        base_type = str
    elif field.type == "url":
        base_type = str
    elif field.type == "public_url":
        base_type = str
    elif field.type == "array<public_url>":
        base_type = list[str]
    elif field.type == "number":
        base_type = float
    elif field.type == "boolean":
        base_type = bool
    elif field.type == "array":
        if field.item_type == "url":
            base_type = list[str]
        else:
            base_type = list[str]
    else:
        base_type = Any

    # Create Field constraints
    field_kwargs: dict[str, Any] = {}

    # Generate user-friendly description
    field_key = field.key.split("_")[-1] if "_" in field.key else field.key  # Extract key from composer_xxx_yyy format
    # Actually use the raw key for lookup
    raw_key = field.key
    # Try to extract meaningful key from patterns like "composer_video_prompt_textarea"
    for known_key in ["prompt", "negative_prompt", "duration", "aspect_ratio", "resolution", "seed",
                      "image_url", "video_url", "audio_url", "first_frame_url", "last_frame_url",
                      "reference_url", "generate_audio", "text", "voice_id", "language"]:
        if known_key in raw_key.lower():
            raw_key = known_key
            break

    field_kwargs["description"] = _get_field_description(raw_key, field.type, field)

    # Add examples for common fields - use field's default/enum when available
    static_examples: dict[str, Any] = {
        "prompt": "A serene mountain landscape at sunset with golden light",
        "negative_prompt": "blurry, low quality, distorted",
        "seed": 42,
    }

    # For fields with enum, use the default or first enum value as example
    if raw_key in static_examples:
        field_kwargs["examples"] = [static_examples[raw_key]]
    elif field.enum and len(field.enum) > 0:
        # Use field's default if available and in enum, otherwise first enum value
        if field.default is not None and field.default in field.enum:
            field_kwargs["examples"] = [field.default]
        else:
            field_kwargs["examples"] = [field.enum[0]]
    elif field.default is not None and not isinstance(field.default, _Required):
        # Use field's default as example
        field_kwargs["examples"] = [field.default]

    # Min/max for numbers
    if field.min_value is not None:
        field_kwargs["ge"] = field.min_value
    if field.max_value is not None:
        field_kwargs["le"] = field.max_value

    # Min/max items for arrays
    if field.min_items is not None:
        field_kwargs["min_length"] = field.min_items
    if field.max_items is not None:
        field_kwargs["max_length"] = field.max_items

    # Enum options - add to schema
    if field.enum:
        field_kwargs["json_schema_extra"] = {"enum": field.enum}

    # Three-state logic based on default value
    if field.is_required:
        # REQUIRED: user must provide, not nullable
        return (base_type, Field(..., **field_kwargs))
    elif field.is_nullable:
        # NULLABLE: optional, can be null (like seed where null = random)
        field_kwargs["default"] = None
        return (Optional[base_type], Field(**field_kwargs))
    else:
        # HAS DEFAULT: optional with default value, NOT nullable
        field_kwargs["default"] = field.default
        return (base_type, Field(**field_kwargs))


def _format_model_name(model_id: str) -> str:
    """Convert model_id to a friendly display name."""
    # Map known model IDs to friendly names
    names = {
        "google/veo-3.1": "Google Veo 3.1",
        "google/veo-3.1/fast": "Google Veo 3.1 Fast",
        "kling/video/v2.6/pro": "Kling Pro",
        "openai/sora-2": "OpenAI Sora 2",
        "minimax/hailuo-2.3/standard": "Minimax Hailuo",
        "ltx/2/fast": "LTX 2 Fast",
        "longcat/video/distilled": "Longcat Distilled",
        "openai/gpt-image-1-mini": "OpenAI GPT Image Mini",
        "openai/gpt-image-1.5": "OpenAI GPT Image 1.5",
        "google/nano-banana-pro": "Google Nano Banana Pro",
        "black-forest-labs/flux-2": "Flux 2",
        "bytedance/seedream-v4.5": "Bytedance Seedream",
        "fal-ai/z-image/turbo": "Z-Image Turbo",
        "elevenlabs/eleven_multilingual_v2": "ElevenLabs V2",
        "elevenlabs/eleven_v3": "ElevenLabs V3",
        "elevenlabs/eleven_turbo_v2_5": "ElevenLabs Turbo",
        "minimax/music/v2": "Minimax Music",
        "beatoven/music-generation": "Beatoven Music",
        "elevenlabs/sound-effect-generation-v2": "ElevenLabs Sound Effects",
        "beatoven/sound-effect-generation": "Beatoven Sound Effects",
        "kling-video/ai-avatar/v2/pro": "Kling Avatar Pro",
        "kling-video/ai-avatar/v2/standard": "Kling Avatar Standard",
        "veed/fabric-1.0": "Veed Fabric",
    }
    return names.get(model_id, model_id.replace("/", " ").replace("-", " ").title())


def _format_mode_name(mode: str) -> str:
    """Convert mode to a friendly display name."""
    names = {
        "text-to-video": "Text to Video",
        "image-to-video": "Image to Video",
        "first-last-frame-to-video": "First & Last Frame to Video",
        "extend-video": "Extend Video",
        "reference-to-video": "Reference to Video",
        "text-to-image": "Text to Image",
        "image-to-image": "Image to Image",
        "text-to-speech": "Text to Speech",
        "text-to-music": "Text to Music",
        "text-to-sound-effect": "Text to Sound Effect",
        "speech-to-avatar": "Speech to Avatar",
        "text-to-avatar": "Text to Avatar",
    }
    return names.get(mode, mode.replace("-", " ").title())


def _generate_model_for_caps(caps: ModelCapabilities, mode: Optional[str] = None) -> type[BaseModel]:
    """
    Generate a Pydantic model for a specific model+mode combination.
    """
    all_inputs: dict[str, InputField] = {}
    
    if caps.inputs:
        all_inputs.update(caps.inputs)
    
    if mode and mode in caps.modes:
        mode_caps = caps.modes[mode]
        if mode_caps.inputs:
            all_inputs.update(mode_caps.inputs)
    
    field_definitions: dict[str, Any] = {}
    
    # Model field - optional with default (auto-filled from URL path)
    model_value = caps.model_id
    friendly_model = _format_model_name(model_value)
    field_definitions["model"] = (
        Optional[Literal[model_value]],  # type: ignore
        Field(
            default=model_value,
            description=f"Model ID (auto-filled: {friendly_model})",
            json_schema_extra={"const": model_value, "readOnly": True}
        )
    )

    # Mode field - optional with default (auto-filled from URL path)
    if mode:
        friendly_mode = _format_mode_name(mode)
        field_definitions["mode"] = (
            Optional[Literal[mode]],  # type: ignore
            Field(
                default=mode,
                description=f"Generation mode (auto-filled: {friendly_mode})",
                json_schema_extra={"const": mode, "readOnly": True}
            )
        )
    
    # Add all input fields
    for field_name, field_def in all_inputs.items():
        field_type, field_instance = _create_field_type(field_def)
        field_definitions[field_name] = (field_type, field_instance)
    
    mode_suffix = f"_{mode.replace('-', '_')}" if mode else ""
    class_name = f"{_sanitize_model_name(caps.model_id)}{_sanitize_model_name(mode_suffix)}Request"
    
    friendly_model = _format_model_name(caps.model_id)
    friendly_mode = _format_mode_name(mode) if mode else ""
    doc = f"Generate content using {friendly_model}"
    if friendly_mode:
        doc += f" in {friendly_mode} mode"
    
    model = create_model(
        class_name,
        __doc__=doc,
        **field_definitions,
    )
    
    return model


def generate_all_models() -> dict[str, type[BaseModel]]:
    """Generate Pydantic models for all registered capabilities."""
    all_caps = get_all_capabilities()
    models: dict[str, type[BaseModel]] = {}
    
    for caps in all_caps:
        for mode_name in caps.modes.keys():
            key = f"{caps.model_id}:{mode_name}"
            try:
                models[key] = _generate_model_for_caps(caps, mode_name)
            except Exception as e:
                import logging
                logging.warning(f"Failed to generate model for {key}: {e}")
    
    return models


# Pre-generate all models at import time
_GENERATED_MODELS: dict[str, type[BaseModel]] = {}


def get_generated_models() -> dict[str, type[BaseModel]]:
    """Get all generated model schemas."""
    global _GENERATED_MODELS
    if not _GENERATED_MODELS:
        _GENERATED_MODELS = generate_all_models()
    return _GENERATED_MODELS

