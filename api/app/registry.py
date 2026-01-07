"""
Octupost Model Registry

Single source of truth for:
- Model aliases (friendly names → endpoints)
- Model capabilities (inputs, modes, pricing)
- Constants (aspect ratios, resolutions, voices, languages)

This file consolidates:
- registry/models.py
- registry/aliases.py
"""

import math
from dataclasses import dataclass, field, fields
from typing import Any, Optional


# ===========================================================================
# REQUIRED SENTINEL
# ===========================================================================

class _Required:
    """Sentinel value indicating a required field with no default.

    Usage:
    - default=REQUIRED → Field is required (user must provide)
    - default=None → Field is optional AND nullable (user can pass null)
    - default=<value> → Field is optional with that default (not nullable)
    """
    def __repr__(self) -> str:
        return "REQUIRED"

    def __bool__(self) -> bool:
        return False  # Falsy so `if default:` works correctly

REQUIRED = _Required()


# ===========================================================================
# MODEL ALIASES
# ===========================================================================
# Maps user-friendly model names to actual provider endpoints.
# Users can use short names like "veo3.1" instead of "fal-ai/veo3.1".

MODEL_ALIASES: dict[str, str] = {
    # =========================================================================
    # Video Models
    # =========================================================================

    # Google Veo
    "veo3.1": "fal-ai/veo3.1",
    "veo3.1-fast": "fal-ai/veo3.1/fast",

    # Kling (Kuaishou)
    "kling-2.6-pro": "fal-ai/kling-video/v2.6/pro",

    # OpenAI Sora
    "sora-2": "fal-ai/sora-2",

    # MiniMax Hailuo
    "hailuo-2.3-standard": "fal-ai/minimax/hailuo-2.3/standard",

    # LTX Video
    "ltx-2-fast": "fal-ai/ltx-2/fast",

    # Longcat (extended duration)
    "longcat-distilled": "fal-ai/longcat-video/distilled",

    # =========================================================================
    # Image Models
    # =========================================================================

    # OpenAI GPT Image
    "gpt-image-1-mini": "fal-ai/gpt-image-1-mini",
    "gpt-image-1.5": "fal-ai/gpt-image-1.5",

    # Flux
    "flux-2": "fal-ai/flux-2",

    # ByteDance Seedream
    "seedream-4.5": "fal-ai/bytedance/seedream/v4.5",

    # Z-Image
    "z-image-turbo": "fal-ai/z-image/turbo",

    # Nano Banana
    "nano-banana-pro": "fal-ai/nano-banana/pro",

    # =========================================================================
    # Audio / Speech Models
    # =========================================================================

    # ElevenLabs TTS
    "elevenlabs-v2": "elevenlabs/eleven_multilingual_v2",
    "elevenlabs-v3": "elevenlabs/eleven_v3",
    "elevenlabs-turbo": "elevenlabs/eleven_turbo_v2_5",

    # =========================================================================
    # Avatar Models
    # =========================================================================

    # Kling Avatar
    "kling-avatar-pro": "fal-ai/kling-video/ai-avatar/v2/pro",

    # Veed Fabric
    "veed-fabric": "veed/fabric-1.0",

    # Whisper
    "whisper": "fal-ai/whisper",
}

# Model type inference based on endpoint patterns
MODEL_TYPE_PATTERNS: dict[str, list[str]] = {
    "video": ["veo", "kling-video", "sora", "hailuo", "ltx", "longcat", "wan"],
    "image": ["gpt-image", "flux", "seedream", "z-image"],
    "audio": ["elevenlabs", "mmaudio"],
    "avatar": ["avatar", "veed"],
}


# ===========================================================================
# INBOUND SCHEMAS (FAL Response -> Normalized Format)
# ===========================================================================
# These define how to transform raw FAL responses into our normalized format.
# Symmetrical to outbound_schema (which transforms our params to FAL params).
#
# NOTE: Models automatically use the default schema based on output_media_type:
#   - output_media_type="video" → INBOUND_VIDEO
#   - output_media_type="image" → INBOUND_IMAGE
#   - output_media_type="audio" → INBOUND_AUDIO
# Only specify inbound_schema on a model if you need to OVERRIDE the default.

INBOUND_VIDEO: dict[str, Any] = {
    "source_key": "video",  # FAL returns {"video": {...}}
    "media_type": "video",
    "defaults": {
        "content_type": "video/mp4",
    },
    "preserve": ["seed", "timestamps"],
}

INBOUND_IMAGE: dict[str, Any] = {
    "source_key": "images",  # FAL returns {"images": [...]} or {"image": {...}}
    "media_type": "image",
    "defaults": {
        "content_type": "image/png",
        "duration": None,
    },
    "preserve": ["seed"],
}

INBOUND_AUDIO: dict[str, Any] = {
    "source_key": "audio",  # FAL returns {"audio": {...}} or {"audio_url": "..."}
    "media_type": "audio",
    "defaults": {
        "content_type": "audio/wav",
        "width": None,
        "height": None,
    },
    "preserve": ["seed"],
}

# JSON/Transcript inbound schema - preserves the entire response
INBOUND_JSON: dict[str, Any] = {
    "source_key": None,  # Special: return entire response
    "media_type": "json",
    "passthrough": True,  # Signal to return response as-is
}

def resolve_model_alias(friendly_name: str) -> str:
    """
    Resolve a friendly model name to the actual endpoint.

    Args:
        friendly_name: User-friendly name (e.g., "veo3.1", "kling")

    Returns:
        Actual model endpoint (e.g., "fal-ai/veo3.1")
        Returns input unchanged if not found in aliases.
    """
    normalized = friendly_name.lower().strip()
    return MODEL_ALIASES.get(normalized, friendly_name)


# Reverse mapping: endpoint -> friendly name
_ENDPOINT_TO_ALIAS: dict[str, str] = {v: k for k, v in MODEL_ALIASES.items()}


def get_friendly_name(model_id: str) -> str:
    """
    Get a URL-friendly name for a model ID.

    Priority:
    1. Look up in reverse alias mapping
    2. Clean up the model_id for URL use

    Examples:
        "fal-ai/z-image/turbo" -> "z-image-turbo"
        "google/veo-3.1" -> "veo-3-1" (if not in aliases)
        "elevenlabs/eleven_v3" -> "elevenlabs-v3"
    """
    # Check reverse mapping first
    if model_id in _ENDPOINT_TO_ALIAS:
        return _ENDPOINT_TO_ALIAS[model_id]

    # Fallback: clean up the model_id
    # Remove common prefixes
    clean = model_id
    for prefix in ["fal-ai/", "openai/", "google/", "elevenlabs/"]:
        if clean.startswith(prefix):
            clean = clean[len(prefix):]
            break

    # Convert to URL-safe format
    clean = clean.replace("/", "-").replace("_", "-").replace(".", "-")
    return clean

def get_model_type(model_id: str) -> Optional[str]:
    """
    Infer the model type from the model ID.

    Args:
        model_id: Model identifier (friendly name or endpoint)

    Returns:
        Model type: "video", "image", "audio", "avatar", or None
    """
    # Resolve alias first
    endpoint = resolve_model_alias(model_id)
    normalized = endpoint.lower()

    for model_type, patterns in MODEL_TYPE_PATTERNS.items():
        for pattern in patterns:
            if pattern in normalized:
                return model_type

    return None

def is_valid_model(model_id: str) -> bool:
    """Check if a model ID or alias is valid."""
    normalized = model_id.lower().strip()
    if normalized in MODEL_ALIASES:
        return True
    if "/" in model_id:
        return True
    return False

def list_models_by_type(model_type: str) -> list[str]:
    """List all model aliases of a given type."""
    results = []
    for alias in MODEL_ALIASES.keys():
        if get_model_type(alias) == model_type:
            results.append(alias)
    return sorted(set(results))
# ===========================================================================
# SHARED CONSTANTS
# ===========================================================================

# Conversion rate for external use
USD_TO_CREDITS = 100

# ElevenLabs model language support
# Language codes are ISO 639-1. "auto" means don't send language_code (let model detect).
# Voices are now stored in database (octupost.elevenlabs_voices), not hardcoded here.
ELEVENLABS_MODEL_LANGUAGES: dict[str, list[str]] = {
    # Multilingual v2: 29 languages
    "eleven_multilingual_v2": [
        "_skip_", "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl",
        "cs", "ar", "zh", "ja", "ko", "hi", "id", "fil", "ms", "sv",
        "ro", "uk", "el", "da", "fi", "bg", "hr", "sk", "ta",
    ],
    # Turbo v2.5 / Flash v2.5: 32 languages (adds vi, hu, no)
    "eleven_turbo_v2_5": [
        "_skip_", "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl",
        "cs", "ar", "zh", "ja", "ko", "hi", "id", "fil", "ms", "sv",
        "ro", "uk", "el", "da", "fi", "bg", "hr", "sk", "ta",
        "vi", "hu", "no",
    ],
    # V3: 74+ languages (comprehensive list - same as turbo for now, expand as needed)
    "eleven_v3": [
        "_skip_", "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl",
        "cs", "ar", "zh", "ja", "ko", "hi", "id", "fil", "ms", "sv",
        "ro", "uk", "el", "da", "fi", "bg", "hr", "sk", "ta",
        "vi", "hu", "no",
    ],
}

# Default voice ID (Sarah - used when no voice specified)
ELEVENLABS_DEFAULT_VOICE_ID = "EXAVITQu4vr4xnSDxMaL"

ASPECT_RATIO_DIMENSIONS: dict[str, tuple[int, int]] = {
    "9:16": (1080, 1920),
    "4:5": (1080, 1350),
    "1:1": (1080, 1080),
    "5:4": (1350, 1080),
    "16:9": (1920, 1080),
}

# Resolution to height in pixels (for computing image_size)
RESOLUTION_HEIGHTS: dict[str, int] = {
    "480p": 480,
    "720p": 720,
    "768p": 768,
    "1080p": 1080,
    "2048p": 2048,
    "2160p": 2160,
    "2560p": 2560,
    "3840p": 3840,
    "4096p": 4096,
}

# Aspect ratio as (width_ratio, height_ratio) tuples (for computing image_size)
ASPECT_RATIO_TUPLES: dict[str, tuple[int, int]] = {
    "9:16": (9, 16),
    "4:5": (4, 5),
    "1:1": (1, 1),
    "5:4": (5, 4),
    "16:9": (16, 9),
}

# GPT Image aspect ratio to image_size mapping
GPT_IMAGE_SIZE_MAP: dict[str, str] = {
    "1:1": "1024x1024",
    "5:4": "1536x1024",
    "4:5": "1024x1536",
}

# GPT Image background toggle mapping
GPT_BACKGROUND_MAP: dict[bool, str] = {
    True: "transparent",
    False: "opaque",
}

# Nano Banana resolution mapping
NANO_BANANA_RESOLUTION_MAP: dict[str, str] = {
    "1080p": "1K",
    "2048p": "2K",
    "4096p": "4K",
}


# ===========================================================================
# PRICING DATACLASSES
# ===========================================================================

@dataclass
class BasePriceSelector:
    """
    Selects base_unit_price dynamically based on a SINGLE parameter value.

    Example: Different base prices for different resolutions
    - param_key: "resolution"
    - price_map: {"720p": 0.05, "1080p": 0.08, "4k": 0.15}
    """
    param_key: str
    price_map: dict[str, float]


@dataclass
class MatrixPriceSelector:
    """
    Selects base_unit_price based on MULTIPLE parameter values (composite key).

    Example: GPT Image pricing depends on quality + size combination
    """
    param_keys: list[str]
    price_matrix: dict[str, float]
    separator: str = "|"


@dataclass
class ToggleMultiplier:
    """
    Multiplier applied when a boolean toggle is enabled.

    Example: Enable audio adds 100% cost
    - param_key: "generate_audio"
    - multiplier: 2.0
    """
    param_key: str
    multiplier: float
    apply_when: bool = True


@dataclass
class OptionMultiplier:
    """
    Multiplier applied based on selected option value.

    Example: Resolution affects price
    - param_key: "resolution"
    - value_multipliers: {"720p": 0.8, "1080p": 1.0, "4k": 2.0}
    """
    param_key: str
    value_multipliers: dict[str, float]


@dataclass
class Pricing:
    """
    Complete pricing configuration for a model.

    Formula:
    Final Cost = effective_base_unit_price
               x units (duration/megapixels/characters/1)
               x product(toggle_multipliers when enabled)
               x product(option_multipliers for selected values)
               x markup_multiplier
    """

    # Core pricing
    base_unit_price: float
    base_unit: str  # "generation", "second", "character", "megapixel"
    markup_multiplier: float = 1.0

    # Unit configuration
    unit_source_param: Optional[str] = None
    unit_bucket_size: int = 1

    # Dynamic base price selectors
    base_price_selector: Optional[BasePriceSelector] = None
    matrix_price_selector: Optional[MatrixPriceSelector] = None

    # Multipliers
    toggle_multipliers: list[ToggleMultiplier] = field(default_factory=list)
    option_multipliers: list[OptionMultiplier] = field(default_factory=list)
    parameter_multipliers: dict[str, dict[str, float]] = field(default_factory=dict)

    def to_pricing_config(self) -> dict[str, Any]:
        """Convert to PricingConfig dict for cost_calculator.py"""
        config: dict[str, Any] = {
            "base_unit_price": self.base_unit_price,
            "base_unit": self.base_unit,
            "markup_multiplier": self.markup_multiplier,
            "unit_bucket_size": self.unit_bucket_size,
        }

        if self.unit_source_param:
            config["unit_source_param"] = self.unit_source_param

        if self.matrix_price_selector:
            config["matrix_price_selector"] = {
                "paramKeys": self.matrix_price_selector.param_keys,
                "priceMatrix": self.matrix_price_selector.price_matrix,
                "separator": self.matrix_price_selector.separator,
            }
        elif self.base_price_selector:
            config["base_price_selector"] = {
                "paramKey": self.base_price_selector.param_key,
                "priceMap": self.base_price_selector.price_map,
            }

        # Build multipliers array format for frontend cost calculator
        # Frontend expects: multipliers: [{paramKey, type, booleanMultipliers/valueMultipliers}]
        multipliers_array: list[dict[str, Any]] = []

        # Add toggle multipliers (boolean type)
        for toggle in self.toggle_multipliers:
            multipliers_array.append({
                "paramKey": toggle.param_key,
                "type": "boolean",
                "booleanMultipliers": {
                    "true": toggle.multiplier if toggle.apply_when else 1.0,
                    "false": 1.0 if toggle.apply_when else toggle.multiplier,
                },
            })

        # Add option multipliers (discrete type)
        for option in self.option_multipliers:
            multipliers_array.append({
                "paramKey": option.param_key,
                "type": "discrete",
                "valueMultipliers": option.value_multipliers,
            })

        # Add legacy parameter_multipliers (discrete type)
        for param_key, value_map in self.parameter_multipliers.items():
            # Check if this param was already added as toggle or option
            if not any(m["paramKey"] == param_key for m in multipliers_array):
                multipliers_array.append({
                    "paramKey": param_key,
                    "type": "discrete",
                    "valueMultipliers": value_map,
                })

        if multipliers_array:
            config["multipliers"] = multipliers_array

        return config

    def _round_to_bucket(self, units: float) -> float:
        """Round units up to nearest bucket size."""
        if self.unit_bucket_size <= 1:
            return units
        return math.ceil(units / self.unit_bucket_size) * self.unit_bucket_size

    def _get_effective_base_price(self, params: dict[str, Any]) -> float:
        """Get effective base price considering selectors."""
        if self.matrix_price_selector:
            separator = self.matrix_price_selector.separator
            key_parts = []
            for param_key in self.matrix_price_selector.param_keys:
                value = params.get(param_key)
                if value is None:
                    break
                key_parts.append(str(value))

            if len(key_parts) == len(self.matrix_price_selector.param_keys):
                composite_key = separator.join(key_parts)
                price = self.matrix_price_selector.price_matrix.get(composite_key)
                if price is not None:
                    return price

        if self.base_price_selector:
            value = params.get(self.base_price_selector.param_key)
            if value is not None:
                price = self.base_price_selector.price_map.get(str(value))
                if price is not None:
                    return price

        return self.base_unit_price

    def _calculate_units(self, params: dict[str, Any], override_units: Optional[float] = None) -> float:
        """Calculate the number of units based on base_unit type.

        Valid base_unit values: generation, second, character, megapixel
        """
        if override_units is not None:
            return override_units

        base_unit = self.base_unit.lower()

        if base_unit == "generation":
            return 1.0

        if not self.unit_source_param:
            return 1.0

        value = params.get(self.unit_source_param)
        if value is None:
            return 1.0

        if base_unit == "second":
            return float(value)

        if base_unit == "character":
            if isinstance(value, str):
                return float(len(value))
            return float(value)

        if base_unit == "megapixel":
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, dict) and "width" in value and "height" in value:
                return (value["width"] * value["height"]) / 1_000_000
            return 1.0

        raise ValueError(
            f"Invalid base_unit: '{base_unit}'. Must be one of: generation, second, character, megapixel."
        )

    def _calculate_multipliers(self, params: dict[str, Any]) -> float:
        """Calculate total multiplier from all toggle and option multipliers."""
        total = 1.0

        for toggle in self.toggle_multipliers:
            value = params.get(toggle.param_key)
            if value is not None and bool(value) == toggle.apply_when:
                total *= toggle.multiplier

        for option in self.option_multipliers:
            value = params.get(option.param_key)
            if value is not None:
                multiplier = option.value_multipliers.get(str(value))
                if multiplier is not None:
                    total *= multiplier

        for param_key, multipliers in self.parameter_multipliers.items():
            value = params.get(param_key)
            if value is not None:
                value_str = str(value).lower() if isinstance(value, bool) else str(value)
                multiplier = multipliers.get(value_str)
                if multiplier is not None:
                    total *= multiplier

        return total

    def calculate_cost(self, params: dict[str, Any], override_units: Optional[float] = None) -> float:
        """Calculate cost in USD."""
        base_price = self._get_effective_base_price(params)
        raw_units = self._calculate_units(params, override_units)
        bucketed_units = self._round_to_bucket(raw_units)
        multiplier = self._calculate_multipliers(params)
        return base_price * bucketed_units * multiplier * self.markup_multiplier

    def calculate_credits(self, params: dict[str, Any], override_units: Optional[float] = None) -> int:
        """Calculate cost in credits."""
        cost_usd = self.calculate_cost(params, override_units)
        return max(int(cost_usd * USD_TO_CREDITS + 0.5), 1)


# ===========================================================================
# INPUT FIELD DATACLASSES
# ===========================================================================

@dataclass
class InputField:
    """Input field definition for model parameters.

    The `key` field is the semantic identifier used everywhere:
    - Backend API parameters
    - Frontend component rendering (via param-components.ts)
    - i18n translations (params.{key}.label)
    - FAL transformation (via outbound_schema.field_map)

    The `default` field determines required/optional/nullable status:
    - default=REQUIRED → Field is required (user must provide)
    - default=None → Field is optional AND nullable (user can pass null)
    - default=<value> → Field is optional with that default (not nullable)
    """
    type: str  # "string", "url", "array", "number", "boolean", "public_url"
    key: str = ""  # Semantic key (e.g., "first_frame", "video_prompt", "duration")
    default: Any = field(default_factory=lambda: REQUIRED)  # REQUIRED | None | value
    enum: Optional[list[str]] = None
    item_type: Optional[str] = None
    min_items: Optional[int] = None
    max_items: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: Optional[float] = None
    max_length: Optional[int] = None
    description: Optional[str] = None  # Help text for API docs
    api_only: bool = False  # If True, exclude from frontend config (API users can still use)

    @property
    def is_required(self) -> bool:
        """Check if this field is required."""
        return isinstance(self.default, _Required)

    @property
    def is_nullable(self) -> bool:
        """Check if this field accepts null values."""
        return self.default is None

    @property
    def has_default(self) -> bool:
        """Check if this field has a real default value."""
        return not self.is_required and not self.is_nullable


@dataclass
class ModeCapabilities:
    """Capabilities for a specific mode."""
    model_id: Optional[str] = None
    inputs: Optional[dict[str, InputField]] = None
    outbound_schema: Optional[dict[str, Any]] = None
    inbound_schema: Optional[dict[str, Any]] = None  # FAL response -> normalized
    aspect_ratios: Optional[list[str]] = None
    resolutions: Optional[list[str]] = None
    duration: Optional[float] = None
    pricing: Optional[Pricing] = None

    # Frontend UI fields
    display_name: Optional[str] = None  # Friendly tab name (e.g., "Text", "Image", "First + Last")
    summary_params: Optional[list[str]] = None  # Params to show in collapsed dropdown (e.g., ["resolution", "duration"])


@dataclass
class ModelCapabilities:
    """Capabilities and constraints for a model."""
    model_id: str
    inputs: Optional[dict[str, InputField]] = None
    outbound_schema: Optional[dict[str, Any]] = None
    inbound_schema: Optional[dict[str, Any]] = None  # FAL response -> normalized
    modes: dict[str, ModeCapabilities] = field(default_factory=dict)
    pricing: Optional[Pricing] = None

    # Frontend metadata fields
    provider_name: str = ""  # Display name (e.g., "Veo 3.1")
    output_media_type: str = "video"  # "image" | "video" | "audio"
    output_asset_type: str = "video"  # "image" | "video" | "avatar_video" | "speech" | "music" | "sound_effect"
    composer_display_section: str = "video"  # Which composer tab to show in
    tier: str = "Standard"  # "Basic" | "Standard" | "Pro" | "Elite"
    is_active: bool = True  # Whether model is available
    fps: Optional[int] = None  # Frames per second (video models)
    link: Optional[str] = None  # FAL model page URL
    description: str = ""  # Short description for model popup (e.g., "Google's AI video generation model")

    def get_mode_capabilities(self, mode: str) -> dict[str, Any]:
        """Get merged capabilities for a specific mode."""
        result: dict[str, Any] = {}
        if mode in self.modes:
            mode_caps = self.modes[mode]
            for field_obj in fields(mode_caps):
                value = getattr(mode_caps, field_obj.name)
                if value is not None:
                    result[field_obj.name] = value
        return result

    def to_dict(self, mode: Optional[str] = None) -> dict[str, Any]:
        """Convert to dictionary for API response."""
        base = {
            "model_id": self.model_id,
            "inputs": self.inputs,
        }
        if mode:
            base["mode"] = mode
            base.update(self.get_mode_capabilities(mode))
        else:
            base["modes"] = {
                mode_name: self.get_mode_capabilities(mode_name)
                for mode_name in self.modes.keys()
            }
        return base

    def _map_input_type(self, input_type: str) -> str:
        """Map registry input types to frontend parameter types."""
        type_map = {
            "string": "string",
            "number": "number",
            "integer": "integer",
            "boolean": "boolean",
            "url": "string",
            "public_url": "string",
            "array": "string",
            "array<public_url>": "string",
        }
        return type_map.get(input_type, "string")

    def _infer_model_type(self) -> str:
        """Infer model_type from first available mode."""
        if self.modes:
            return list(self.modes.keys())[0]
        return "text-to-video"

    def to_model_config(self, mode: Optional[str] = None) -> dict[str, Any]:
        """
        Convert to frontend ModelConfig-compatible format.

        If mode is specified, returns config for that specific mode.
        Otherwise returns base config with first mode as model_type.
        """
        # Determine which inputs to use (mode-specific or base)
        mode_inputs = {}
        mode_endpoint = self.model_id
        mode_type = self._infer_model_type()
        mode_pricing = self.pricing

        # Mode-specific UI metadata
        mode_display_name: Optional[str] = None
        mode_summary_params: Optional[list[str]] = None

        if mode and mode in self.modes:
            mode_caps = self.modes[mode]
            mode_type = mode
            # Use outbound_schema endpoint as the unique mode identifier
            # This ensures each mode (text-to-video, image-to-video, etc.) has a unique endpoint
            if mode_caps.outbound_schema and "endpoint" in mode_caps.outbound_schema:
                mode_endpoint = mode_caps.outbound_schema["endpoint"]
            elif mode_caps.model_id:
                mode_endpoint = mode_caps.model_id
            if mode_caps.pricing:
                mode_pricing = mode_caps.pricing
            if mode_caps.display_name:
                mode_display_name = mode_caps.display_name
            if mode_caps.summary_params:
                mode_summary_params = mode_caps.summary_params
            # Merge base inputs with mode-specific inputs
            if self.inputs:
                mode_inputs = dict(self.inputs)
            if mode_caps.inputs:
                mode_inputs.update(mode_caps.inputs)
        elif self.inputs:
            mode_inputs = self.inputs

        # Convert inputs dict to parameters array format
        # The key is the semantic identifier used for:
        # - API parameters
        # - Frontend component lookup (via param-components.ts)
        # - i18n translations (params.{key}.label)
        parameters = []
        for _, input_field in mode_inputs.items():
            # Skip api_only parameters - not sent to frontend
            if input_field.api_only:
                continue

            # Use input_field.key as the canonical semantic key
            param: dict[str, Any] = {
                "key": input_field.key,
                "type": self._map_input_type(input_field.type),
                "required": input_field.is_required,
            }
            # Only include default for fields that have a real default value (not REQUIRED, not None)
            if input_field.has_default:
                param["default"] = input_field.default
            if input_field.enum:
                param["enum"] = input_field.enum
                param["options"] = input_field.enum
            if input_field.min_value is not None:
                param["min"] = input_field.min_value
                param["minimum"] = input_field.min_value
            if input_field.max_value is not None:
                param["max"] = input_field.max_value
                param["maximum"] = input_field.max_value
            if input_field.step is not None:
                param["step"] = input_field.step
            if input_field.max_length:
                param["maxLength"] = input_field.max_length
            if input_field.min_items is not None:
                param["minCount"] = input_field.min_items
            if input_field.max_items is not None:
                param["maxCount"] = input_field.max_items
            if input_field.description:
                param["description"] = input_field.description
            parameters.append(param)

        return {
            "id": mode_endpoint,
            "endpoint": mode_endpoint,
            "model_id": self.model_id,  # Semantic model ID (e.g., "openai/gpt-image-1-mini")
            "provider_name": self.provider_name or self.model_id,
            "model_type": mode_type,
            "output_media_type": self.output_media_type,
            "output_asset_type": self.output_asset_type,
            "composer_display_section": self.composer_display_section,
            "tier": self.tier,
            "is_active": self.is_active,
            "fps": self.fps,
            "link": self.link,
            "description": self.description,
            "parameters": parameters,
            "raw_parameters": [],  # Not used in registry approach
            "pricing_config": mode_pricing.to_pricing_config() if mode_pricing else None,
            "schema_synced_at": None,
            "created_at": None,
            "updated_at": None,
            # Mode-specific UI metadata
            "display_name": mode_display_name,
            "summary_params": mode_summary_params,
        }


# ===========================================================================
# INPUT FIELD FACTORIES
# ===========================================================================

def TEXT_INPUT(
    key: str,
    max_length: int = 0,
    default: Any = REQUIRED,
    description: Optional[str] = None,
) -> InputField:
    """Text input for string parameters.

    Args:
        key: Semantic key (e.g., "video_prompt", "speech_text")
        default: REQUIRED (must provide), None (nullable), or string value (optional with default)
    """
    return InputField(
        key=key,
        type="string",
        max_length=max_length,
        default=default,
        description=description,
    )


def URL_INPUT(
    key: str,
    description: Optional[str] = None,
) -> InputField:
    """URL input for URL parameters. Always required.

    Args:
        key: Semantic key (e.g., "first_frame", "source_video")
    """
    return InputField(
        key=key,
        type="public_url",
        default=REQUIRED,
        description=description,
    )


def ARRAY_URL_INPUT(
    key: str,
    min_items: int = 1,
    max_items: int = 10,
    description: Optional[str] = None,
) -> InputField:
    """Array of URL inputs for multiple images/files. Always required.

    Args:
        key: Semantic key (e.g., "reference_images")
    """
    return InputField(
        key=key,
        type="array<public_url>",
        default=REQUIRED,
        min_items=min_items,
        max_items=max_items,
        description=description,
    )


def TOGGLE_INPUT(
    key: str,
    default: bool = False,
    description: Optional[str] = None,
) -> InputField:
    """Toggle input for boolean parameters. Always has a default.

    Args:
        key: Semantic key (e.g., "enhance_prompt", "generate_audio")
    """
    return InputField(
        key=key,
        type="boolean",
        default=default,
        description=description,
    )


def SLIDER_INPUT(
    key: str,
    min_value: float = 0.0,
    max_value: float = 1.0,
    step: float = 0.1,
    default: Any = REQUIRED,
    description: Optional[str] = None,
    api_only: bool = False,
) -> InputField:
    """Slider input for numeric parameters.

    Args:
        key: Semantic key (e.g., "duration", "speed", "seed")
        default: REQUIRED (must provide), None (nullable, e.g. seed), or number (optional with default)
        api_only: If True, exclude from frontend config (API users can still use)
    """
    return InputField(
        key=key,
        type="number",
        min_value=min_value,
        max_value=max_value,
        step=step,
        default=default,
        description=description,
        api_only=api_only,
    )


def DROPDOWN_INPUT(
    key: str,
    enum: Optional[list[str]] = None,
    default: Any = REQUIRED,
    description: Optional[str] = None,
) -> InputField:
    """Dropdown input for selecting from predefined options.

    Args:
        key: Semantic key (e.g., "aspect_ratio", "resolution", "voice")
        default: REQUIRED (must provide), None (nullable), or string value (optional with default)
    """
    return InputField(
        key=key,
        type="string",
        enum=enum or [],
        default=default,
        description=description,
    )


# ===========================================================================
# TRANSFORM HELPERS
# ===========================================================================

def add_s_to_integer(value: int) -> str:
    return f"{value}s"

def integer_to_string(value: int) -> str:
    return str(value)

def string_to_integer(value: str) -> int:
    return int(value)

def seconds_to_frames(fps: int = 24, max_frames: int | None = None):
    """Factory that returns a transform function to convert seconds to frame count.

    Args:
        fps: Frames per second (default 24)
        max_frames: Maximum frame count cap (e.g., 961 for longcat-video)
    """
    def transform(seconds: int | str) -> int:
        frames = int(float(seconds)) * fps  # Convert to int first, then multiply
        if max_frames is not None:
            return min(frames, max_frames)
        return frames
    return transform

def empty_to_dot(value: str | None) -> str:
    """Convert empty/null values to a single dot for APIs that require non-empty strings."""
    if not value or value.strip() == "":
        return "."
    return value

# ===========================================================================
# CAPABILITIES REGISTRY
# ===========================================================================
class CapabilitiesRegistry:
    """Registry of model capabilities."""

    def __init__(self):
        self._capabilities: dict[str, ModelCapabilities] = {}
        self._load_defaults()

    def _load_defaults(self):
        """Load capabilities for known models."""

        # =====================================================================
        # VIDEO MODELS
        # =====================================================================

        # Veo 3.1
        self._register(ModelCapabilities(
            model_id="google/veo-3.1",
            provider_name="Veo 3.1",
            description="Google's flagship AI video model with cinematic quality",
            output_media_type="video",
            output_asset_type="video",
            composer_display_section="video",
            tier="Elite",
            fps=24,
            link="https://fal.ai/models/fal-ai/veo3.1",
            inputs={
                "video_prompt": TEXT_INPUT(key="video_prompt", max_length=20000),
                "duration": DROPDOWN_INPUT(key="duration", enum=["4", "6", "8"], default="4"),
                "resolution": DROPDOWN_INPUT(key="resolution", enum=["auto", "720p", "1080p"], default="auto"),
                "aspect_ratio": DROPDOWN_INPUT(key="aspect_ratio", enum=["9:16", "16:9"], default="16:9"),
                "generate_audio": TOGGLE_INPUT(key="generate_audio"),
                "seed": SLIDER_INPUT(key="seed", default=None, min_value=0, max_value=46000, step=1, api_only=True),
            },
            outbound_schema={
                "field_map": {
                    "video_prompt": "prompt",  # Our key → FAL's key
                },
                "transforms": {
                    "duration": add_s_to_integer,
                },
                "static": {
                    "auto_fix": True,
                    "negative_prompt": "",
                },
                "optional": ["seed"],
            },
            modes={
                "text-to-video": ModeCapabilities(
                    display_name="From Text",
                    summary_params=["resolution", "duration", "aspect_ratio"],
                    inputs={
                        "resolution": DROPDOWN_INPUT(key="resolution", enum=["720p", "1080p"], default="1080p"),
                    },
                    outbound_schema={
                        "endpoint": "fal-ai/veo3.1",
                    }
                ),
                "image-to-video": ModeCapabilities(
                    display_name="From Image",
                    summary_params=["resolution", "duration", "aspect_ratio"],
                    inputs={
                        "first_frame": URL_INPUT(key="first_frame"),
                    },
                    outbound_schema={
                        "endpoint": "fal-ai/veo3.1/image-to-video",
                        "field_map": {
                            "first_frame": "image_url"  # Our key → FAL's key
                        }
                    },
                ),
                "first-last-frame-to-video": ModeCapabilities(
                    display_name="Start + End",
                    summary_params=["duration","resolution", "aspect_ratio"],
                    inputs={
                        "first_frame": URL_INPUT(key="first_frame"),
                        "last_frame": URL_INPUT(key="last_frame"),
                        "duration": DROPDOWN_INPUT(key="duration", enum=["8"], default="8"),
                        "aspect_ratio": DROPDOWN_INPUT(key="aspect_ratio", enum=["9:16", "16:9"], default="16:9"),
                    },
                    outbound_schema={
                        "endpoint": "fal-ai/veo3.1/first-last-frame-to-video",
                        "field_map": {
                            "first_frame": "first_frame_url",
                            "last_frame": "last_frame_url",
                        }
                    },
                ),
                "extend-video": ModeCapabilities(
                    display_name="Extend",
                    summary_params=["duration", "resolution", "aspect_ratio"],
                    inputs={
                        "source_video": URL_INPUT(key="source_video"),
                        "duration": DROPDOWN_INPUT(key="duration", enum=["7"], default="7"),
                        "resolution": DROPDOWN_INPUT(key="resolution", enum=["720p", "1080p"], default="1080p"),
                    },
                    outbound_schema={
                        "endpoint": "fal-ai/veo3.1/extend-video",
                        "field_map": {
                            "source_video": "video_url",
                        }
                    },
                ),
                "reference-to-video": ModeCapabilities(
                    display_name="Reference",
                    summary_params=["duration", "resolution", "aspect_ratio"],
                    inputs={
                        "reference_images": ARRAY_URL_INPUT(key="reference_images", min_items=1, max_items=3),
                        "duration": DROPDOWN_INPUT(key="duration", enum=["8"], default="8"),
                        "aspect_ratio": DROPDOWN_INPUT(key="aspect_ratio", enum=["9:16", "16:9"], default="16:9"),
                    },
                    outbound_schema={
                        "endpoint": "fal-ai/veo3.1/reference-to-video",
                        "field_map": {
                            "reference_images": "image_urls",
                        }
                    },
                ),
            },
            pricing=Pricing(
                base_unit_price=0.20,
                base_unit="second",
                unit_source_param="duration",
                markup_multiplier=1,
                toggle_multipliers=[
                    ToggleMultiplier(param_key="generate_audio", multiplier=2),
                ],
            )
        ))

        # Veo 3.1 Fast
        self._register(ModelCapabilities(
            model_id="google/veo-3.1/fast",
            provider_name="Veo 3.1 Fast",
            description="Fast version of Google's video model for quicker generations",
            output_media_type="video",
            output_asset_type="video",
            composer_display_section="video",
            tier="Pro",
            fps=24,
            link="https://fal.ai/models/fal-ai/veo3.1/fast",
            inputs={
                "video_prompt": TEXT_INPUT(key="video_prompt", max_length=20000),
                "duration": DROPDOWN_INPUT(key="duration", enum=["4", "6", "8"], default="4"),
                "resolution": DROPDOWN_INPUT(key="resolution", enum=["auto", "720p", "1080p"], default="auto"),
                "aspect_ratio": DROPDOWN_INPUT(key="aspect_ratio", enum=["9:16", "16:9"], default="16:9"),
                "generate_audio": TOGGLE_INPUT(key="generate_audio", default=False),
                "seed": SLIDER_INPUT(key="seed", default=None, min_value=0, max_value=46000, step=1, api_only=True),
            },
            outbound_schema={
                "field_map": {
                    "video_prompt": "prompt",
                },
                "static": {
                    "auto_fix": True,
                    "negative_prompt": "",
                },
                "transforms": {
                    "duration": add_s_to_integer,
                },
                "optional": ["seed"],
            },
            modes={
                "text-to-video": ModeCapabilities(
                    display_name="From Text",
                    summary_params=["resolution", "duration", "aspect_ratio"],
                    inputs={
                        "resolution": DROPDOWN_INPUT(key="resolution", enum=["720p", "1080p"], default="1080p"),
                    },
                    outbound_schema={
                        "endpoint": "fal-ai/veo3.1/fast",
                    },
                ),
                "image-to-video": ModeCapabilities(
                    display_name="From Image",
                    summary_params=["resolution", "duration", "aspect_ratio"],
                    inputs={
                        "first_frame": URL_INPUT(key="first_frame"),
                    },
                    outbound_schema={
                        "endpoint": "fal-ai/veo3.1/fast/image-to-video",
                        "field_map": {
                            "first_frame": "image_url",
                        },
                    },
                ),
                "first-last-frame-to-video": ModeCapabilities(
                    display_name="Start + End",
                    summary_params=["duration", "aspect_ratio", "resolution"],
                    inputs={
                        "first_frame": URL_INPUT(key="first_frame"),
                        "last_frame": URL_INPUT(key="last_frame"),
                        "duration": DROPDOWN_INPUT(key="duration", enum=["8"], default="8"),
                        "aspect_ratio": DROPDOWN_INPUT(key="aspect_ratio", enum=["9:16", "16:9"], default="16:9"),
                    },
                    outbound_schema={
                        "endpoint": "fal-ai/veo3.1/fast/first-last-frame-to-video",
                        "field_map": {
                            "first_frame": "first_frame_url",
                            "last_frame": "last_frame_url",
                        },
                    },
                ),
                "extend-video": ModeCapabilities(
                    display_name="Extend",
                    summary_params=["duration", "resolution", "aspect_ratio"],
                    inputs={
                        "source_video": URL_INPUT(key="source_video"),
                        "duration": DROPDOWN_INPUT(key="duration", enum=["7"], default="7"),
                        "resolution": DROPDOWN_INPUT(key="resolution", enum=["720p", "1080p"], default="1080p"),
                    },
                    outbound_schema={
                        "endpoint": "fal-ai/veo3.1/fast/extend-video",
                        "field_map": {
                            "source_video": "video_url",
                        },
                    },
                ),
            },
            pricing=Pricing(
                base_unit_price=0.10,
                base_unit="second",
                unit_source_param="duration",
                markup_multiplier=1,
                toggle_multipliers=[
                    ToggleMultiplier(param_key="generate_audio", multiplier=1.5),
                ],
            )
        ))

        # Kling Pro
        self._register(ModelCapabilities(
            model_id="kling/video/v2.6/pro",
            provider_name="Kling 2.6 Pro",
            description="High-quality video synthesis with realistic motion",
            output_media_type="video",
            output_asset_type="video",
            composer_display_section="video",
            tier="Pro",
            fps=30,
            link="https://fal.ai/models/fal-ai/kling-video/v2.6/pro",
            inputs={
                "video_prompt": TEXT_INPUT(key="video_prompt", max_length=2500),
                "duration": DROPDOWN_INPUT(key="duration", enum=["5", "10"], default="5"),
                "resolution": DROPDOWN_INPUT(key="resolution", enum=["1080p"], default="1080p"),
                "aspect_ratio": DROPDOWN_INPUT(key="aspect_ratio", enum=["9:16", "1:1", "16:9"], default="16:9"),
                "generate_audio": TOGGLE_INPUT(key="generate_audio", default=False),
            },
            outbound_schema={
                "field_map": {
                    "video_prompt": "prompt",
                },
                "transforms": {
                    "duration": integer_to_string,
                },
                "static": {
                    "cfg_scale": 0.5,
                    "negative_prompt": "",
                }
            },
            modes={
                "text-to-video": ModeCapabilities(
                    display_name="From Text",
                    summary_params=["resolution", "duration", "aspect_ratio"],
                    outbound_schema={
                        "endpoint": "fal-ai/kling-video/v2.6/pro/text-to-video",
                    },
                ),
                "image-to-video": ModeCapabilities(
                    display_name="From Image",
                    summary_params=["resolution", "duration", "aspect_ratio"],
                    inputs={
                        "first_frame": URL_INPUT(key="first_frame"),
                    },
                    outbound_schema={
                        "endpoint": "fal-ai/kling-video/v2.6/pro/image-to-video",
                        "field_map": {
                            "first_frame": "image_url",
                        },
                        "optional": ["voice_ids"],
                    },
                ),
            },
            pricing=Pricing(
                base_unit_price=0.07,
                base_unit="second",
                unit_source_param="duration",
                markup_multiplier=1,
                toggle_multipliers=[
                    ToggleMultiplier(param_key="generate_audio", multiplier=2),
                ],
            )
        ))

        # OpenAI Sora 2
        self._register(ModelCapabilities(
            model_id="openai/sora-2",
            provider_name="Sora 2",
            description="OpenAI's cinematic video generation model",
            output_media_type="video",
            output_asset_type="video",
            composer_display_section="video",
            tier="Pro",
            fps=24,
            link="https://fal.ai/models/fal-ai/sora-2",
            inputs={
                "video_prompt": TEXT_INPUT(key="video_prompt", max_length=5000),
                "duration": DROPDOWN_INPUT(key="duration", enum=["4", "8", "12"], default="4"),
                "resolution": DROPDOWN_INPUT(key="resolution", enum=["720p"], default="720p"),
                "aspect_ratio": DROPDOWN_INPUT(key="aspect_ratio", enum=["9:16", "16:9"], default="16:9"),
            },
            outbound_schema={
                "field_map": {
                    "video_prompt": "prompt",
                },
                "static": {
                    "delete_video": True,
                },
            },
            modes={
                "text-to-video": ModeCapabilities(
                    display_name="From Text",
                    summary_params=["resolution", "duration", "aspect_ratio"],
                    outbound_schema={
                        "endpoint": "fal-ai/sora-2/text-to-video",
                    },
                ),
                "image-to-video": ModeCapabilities(
                    display_name="From Image",
                    summary_params=["resolution", "duration", "aspect_ratio"],
                    inputs={
                        "first_frame": URL_INPUT(key="first_frame"),
                    },
                    outbound_schema={
                        "endpoint": "fal-ai/sora-2/image-to-video",
                        "field_map": {
                            "first_frame": "image_url",
                        },
                    },
                ),
            },
            pricing=Pricing(
                base_unit_price=0.1,
                base_unit="second",
                unit_source_param="duration",
                markup_multiplier=1
            )
        ))

        # Hailuo Standard
        self._register(ModelCapabilities(
            model_id="minimax/hailuo-2.3/standard",
            provider_name="Hailuo 2.3 Standard",
            description="MiniMax's video model with natural motion",
            output_media_type="video",
            output_asset_type="video",
            composer_display_section="video",
            tier="Standard",
            fps=24,
            link="https://fal.ai/models/fal-ai/minimax/hailuo-2.3/standard",
            inputs={
                "video_prompt": TEXT_INPUT(key="video_prompt", max_length=2000),
                "duration": DROPDOWN_INPUT(key="duration", enum=["6", "10"], default="6"),
                "resolution": DROPDOWN_INPUT(key="resolution", enum=["768p"], default="768p"),
                "aspect_ratio": DROPDOWN_INPUT(key="aspect_ratio", enum=["16:9"], default="16:9"),
                "enhance_prompt": TOGGLE_INPUT(key="enhance_prompt", default=False),
            },
            outbound_schema={
                "field_map": {
                    "video_prompt": "prompt",
                    "enhance_prompt": "prompt_optimizer",
                },
                "transforms": {
                    "duration": integer_to_string,
                },
            },
            modes={
                "text-to-video": ModeCapabilities(
                    display_name="From Text",
                    summary_params=["resolution", "duration", "aspect_ratio"],
                    outbound_schema={
                        "endpoint": "fal-ai/minimax/hailuo-2.3/standard/text-to-video",
                    },
                ),
                "image-to-video": ModeCapabilities(
                    display_name="From Image",
                    summary_params=["resolution", "duration", "aspect_ratio"],
                    inputs={
                        "first_frame": URL_INPUT(key="first_frame"),
                    },
                    outbound_schema={
                        "endpoint": "fal-ai/minimax/hailuo-2.3/standard/image-to-video",
                        "field_map": {
                            "first_frame": "image_url",
                        },
                    },
                ),
            },
            pricing=Pricing(
                base_unit_price=0.28,
                base_unit="generation",
                markup_multiplier=1,
                base_price_selector=BasePriceSelector(
                    param_key="duration",
                    price_map={"6": 0.28, "10": 0.56}
                ),
            )
        ))

        # LTX 2 Distilled
        self._register(ModelCapabilities(
            model_id="ltx/2/fast",
            provider_name="LTX 2 Fast",
            description="Ultra-fast video generation for quick iterations",
            output_media_type="video",
            output_asset_type="video",
            composer_display_section="video",
            tier="Standard",
            fps=25,
            link="https://fal.ai/models/fal-ai/ltx-2/fast",
            inputs={
                "video_prompt": TEXT_INPUT(key="video_prompt", max_length=5000),
                "duration": DROPDOWN_INPUT(key="duration", enum=["6", "8", "10", "12", "14", "16", "18", "20"], default="6"),
                "resolution": DROPDOWN_INPUT(key="resolution", enum=["1080p", "1440p", "2160p"], default="1080p"),
                "aspect_ratio": DROPDOWN_INPUT(key="aspect_ratio", enum=["16:9"], default="16:9"),
                "generate_audio": TOGGLE_INPUT(key="generate_audio", default=False),
            },
            outbound_schema={
                "field_map": {
                    "video_prompt": "prompt",
                },
                "transforms": {
                    "duration": string_to_integer,
                },
                "static": {
                    "fps": 25,
                },
            },
            modes={
                "text-to-video": ModeCapabilities(
                    display_name="From Text",
                    summary_params=["resolution", "duration", "aspect_ratio"],
                    outbound_schema={
                        "endpoint": "fal-ai/ltx-2/text-to-video/fast",
                    },
                ),
                "image-to-video": ModeCapabilities(
                    display_name="From Image",
                    summary_params=["resolution", "duration", "aspect_ratio"],
                    inputs={
                        "first_frame": URL_INPUT(key="first_frame"),
                    },
                    outbound_schema={
                        "endpoint": "fal-ai/ltx-2/image-to-video/fast",
                        "field_map": {
                            "first_frame": "image_url",
                        },
                    },
                ),
            },
            pricing=Pricing(
                base_unit_price=0.04,
                base_unit="second",
                unit_source_param="duration",
                markup_multiplier=1,
                base_price_selector=BasePriceSelector(
                    param_key="resolution",
                    price_map={"1080p": 0.04, "1440p": 0.08, "2160p": 0.16}
                ),
            ),
        ))

        # Longcat Distilled
        self._register(ModelCapabilities(
            model_id="longcat/video/distilled",
            provider_name="Longcat Distilled",
            description="Efficient video model optimized for speed",
            output_media_type="video",
            output_asset_type="video",
            composer_display_section="video",
            tier="Basic",
            fps=30,  # FAL longcat outputs at 30 fps
            link="https://fal.ai/models/fal-ai/longcat-video/distilled",
            inputs={
                "video_prompt": TEXT_INPUT(key="video_prompt", max_length=5000),
                "duration": DROPDOWN_INPUT(key="duration", enum=[str(i) for i in range(2, 31)], default="4"),
                "resolution": DROPDOWN_INPUT(key="resolution", enum=["720p"], default="720p"),
                "aspect_ratio": DROPDOWN_INPUT(key="aspect_ratio", enum=["16:9", "9:16", "1:1"], default="16:9"),
                "enhance_prompt": TOGGLE_INPUT(key="enhance_prompt", default=True),
                "seed": SLIDER_INPUT(key="seed", default=None, min_value=0, max_value=46000, step=1, api_only=True),
            },
            outbound_schema={
                "field_map": {
                    "video_prompt": "prompt",
                    "enhance_prompt": "enable_prompt_expansion",
                    "duration": "num_frames",  # our duration -> FAL's num_frames
                },
                "static": {
                    "enable_safety_checker": True,
                },
                "transforms": {
                    "num_frames": seconds_to_frames(fps=30, max_frames=961),  # Converts seconds → frames at 30 fps (capped at 961)
                },
                "optional": ["seed"],
            },
            modes={
                "text-to-video": ModeCapabilities(
                    display_name="From Text",
                    summary_params=["duration", "aspect_ratio", "resolution"],
                    outbound_schema={
                        "endpoint": "fal-ai/longcat-video/distilled/text-to-video/720p",
                    },
                ),
                "image-to-video": ModeCapabilities(
                    display_name="From Image",
                    summary_params=["duration", "aspect_ratio", "resolution"],
                    inputs={
                        "first_frame": URL_INPUT(key="first_frame"),
                    },
                    outbound_schema={
                        "endpoint": "fal-ai/longcat-video/distilled/image-to-video/720p",
                        "field_map": {
                            "first_frame": "image_url",
                        },
                    },
                ),
            },
            pricing=Pricing(
                base_unit_price=0.01, 
                base_unit="second",
                unit_source_param="duration",
                markup_multiplier=1,
            ),
        ))

        # =====================================================================
        # IMAGE MODELS
        # =====================================================================

        # GPT Image 1 Mini
        self._register(ModelCapabilities(
            model_id="openai/gpt-image-1-mini",
            provider_name="GPT Image 1 Mini",
            description="OpenAI's compact image generation model",
            output_media_type="image",
            output_asset_type="image",
            composer_display_section="image",
            tier="Standard",
            link="https://fal.ai/models/fal-ai/gpt-image-1-mini",
            inputs={
                "image_prompt": TEXT_INPUT(key="image_prompt", max_length=10000),
                "aspect_ratio": DROPDOWN_INPUT(key="aspect_ratio", enum=["1:1", "5:4", "4:5"], default="1:1"),
                "remove_background": TOGGLE_INPUT(key="remove_background", default=False),
                "quality": DROPDOWN_INPUT(key="quality", enum=["low", "medium", "high"], default="medium"),
            },
            outbound_schema={
                "field_map": {
                    "image_prompt": "prompt",
                    "aspect_ratio": "image_size",
                    "remove_background": "background",
                },
                "value_map": {
                    "image_size": GPT_IMAGE_SIZE_MAP,
                    "background": GPT_BACKGROUND_MAP,
                },
            },
            modes={
                "text-to-image": ModeCapabilities(
                    display_name="From Text",
                    summary_params=["aspect_ratio", "quality"],
                    outbound_schema={
                        "endpoint": "fal-ai/gpt-image-1-mini",
                    },
                ),
                "image-to-image": ModeCapabilities(
                    display_name="Edit",
                    summary_params=["aspect_ratio", "quality"],
                    inputs={
                        "reference_images": ARRAY_URL_INPUT(key="reference_images", min_items=1, max_items=5),
                    },
                    outbound_schema={
                        "endpoint": "fal-ai/gpt-image-1-mini/edit",
                        "field_map": {
                            "reference_images": "image_urls",
                        },
                    },
                ),
            },
            pricing=Pricing(
                base_unit_price=0.02,
                base_unit="generation",
                markup_multiplier=1,
            ),
        ))


        # Nano Banana Pro
        self._register(ModelCapabilities(
            model_id="google/nano-banana-pro",
            provider_name="Nano Banana Pro",
            description="Google's fast and efficient image model",
            output_media_type="image",
            output_asset_type="image",
            composer_display_section="image",
            tier="Elite",
            link="https://fal.ai/models/fal-ai/nano-banana-pro",
            inputs={
                "image_prompt": TEXT_INPUT(key="image_prompt", max_length=50000),
                "aspect_ratio": DROPDOWN_INPUT(key="aspect_ratio", enum=["9:16", "4:5", "1:1", "5:4", "16:9"], default="1:1"),
                "resolution": DROPDOWN_INPUT(key="resolution", enum=["1080p", "2048p", "4096p"], default="1080p"),
                "websearch": TOGGLE_INPUT(key="websearch", default=False),
            },
            outbound_schema={
                "field_map": {
                    "image_prompt": "prompt",
                    "websearch": "enable_web_search",
                },
                "value_map": {
                    "resolution": NANO_BANANA_RESOLUTION_MAP,
                },
            },
            modes={
                "text-to-image": ModeCapabilities(
                    display_name="From Text",
                    summary_params=["resolution", "aspect_ratio"],
                    outbound_schema={
                        "endpoint": "fal-ai/nano-banana-pro",
                    },
                ),
                "image-to-image": ModeCapabilities(
                    display_name="Edit",
                    summary_params=["resolution", "aspect_ratio"],
                    inputs={
                        "reference_images": ARRAY_URL_INPUT(key="reference_images", min_items=1, max_items=4),
                    },
                    outbound_schema={
                        "endpoint": "fal-ai/nano-banana-pro/edit",
                        "field_map": {
                            "reference_images": "image_urls",
                        },
                    },
                ),
            },
            pricing=Pricing(
                base_unit_price=0.15,
                base_unit="generation",
                markup_multiplier=1,
                # Use form field key "websearch" (not transformed key "enable_web_search")
                # so frontend cost calculation works correctly
                matrix_price_selector=MatrixPriceSelector(
                    param_keys=["websearch", "resolution"],
                    price_matrix={
                        "false|1080p": 0.15,
                        "false|2048p": 0.15,
                        "false|4096p": 0.30,
                        "true|1080p": 0.2,
                        "true|2048p": 0.2,
                        "true|4096p": 0.35,
                    }
                ),
            ),
        ))

        # Z-Image Turbo
        self._register(ModelCapabilities(
            model_id="fal-ai/z-image/turbo",
            provider_name="Z-Image Turbo",
            description="High-speed image generation for rapid prototyping",
            output_media_type="image",
            output_asset_type="image",
            composer_display_section="image",
            tier="Basic",
            link="https://fal.ai/models/fal-ai/z-image/turbo",
            inputs={
                "image_prompt": TEXT_INPUT(key="image_prompt", max_length=10000),
                "aspect_ratio": DROPDOWN_INPUT(key="aspect_ratio", enum=["9:16", "4:5", "1:1", "5:4", "16:9"], default="1:1"),
                "resolution": DROPDOWN_INPUT(key="resolution", enum=["1080p", "2048p", "4096p"], default="1080p"),
                "enhance_prompt": TOGGLE_INPUT(key="enhance_prompt", default=False),
                "seed": SLIDER_INPUT(key="seed", default=None, min_value=0, max_value=46000, step=1, api_only=True),
            },
            outbound_schema={
                "field_map": {
                    "image_prompt": "prompt",
                    "enhance_prompt": "enable_prompt_expansion",
                },
                "compute": {
                    "image_size": {
                        "type": "image_dimensions",
                        "inputs": ["aspect_ratio", "resolution"],
                    },
                },
                "static": {
                    "acceleration": "regular",
                },
                "optional": ["seed"],
            },
            modes={
                "text-to-image": ModeCapabilities(
                    display_name="From Text",
                    summary_params=["resolution", "aspect_ratio"],
                    outbound_schema={
                        "endpoint": "fal-ai/z-image/turbo",
                    },
                ),
                "image-to-image": ModeCapabilities(
                    display_name="Edit",
                    summary_params=["resolution", "aspect_ratio"],
                    inputs={
                        "source_image": URL_INPUT(key="source_image"),
                    },
                    outbound_schema={
                        "endpoint": "fal-ai/z-image/turbo/image-to-image",
                        "field_map": {
                            "source_image": "image_url",
                        },
                    },
                ),
            },
            pricing=Pricing(
                base_unit_price=0.006,
                base_unit="generation",
                markup_multiplier=1,
                matrix_price_selector=MatrixPriceSelector(
                    param_keys=["aspect_ratio", "resolution"],
                    price_matrix={
                        "9:16|1080p": 0.010,
                        "4:5|1080p": 0.007,
                        "1:1|1080p": 0.006,
                        "5:4|1080p": 0.007,
                        "16:9|1080p": 0.010,
                        "9:16|2048p": 0.037,
                        "4:5|2048p": 0.026,
                        "1:1|2048p": 0.021,
                        "5:4|2048p": 0.026,
                        "16:9|2048p": 0.037,
                        "9:16|4096p": 0.149,
                        "4:5|4096p": 0.105,
                        "1:1|4096p": 0.084,
                        "5:4|4096p": 0.105,
                        "16:9|4096p": 0.149,
                    },
                ),
            ),
        ))

        # =====================================================================
        # AUDIO MODELS
        # =====================================================================

        # Beatoven Music Generation
        self._register(ModelCapabilities(
            model_id="beatoven/music-generation",
            provider_name="Beatoven Music",
            description="Professional background music and soundtracks",
            output_media_type="audio",
            output_asset_type="music",
            composer_display_section="music",
            tier="Pro",
            link="https://fal.ai/models/beatoven/music-generation",
            inputs={
                "music_prompt": TEXT_INPUT(key="music_prompt", max_length=5000),
                "duration": SLIDER_INPUT(key="duration", default=90, min_value=5, max_value=150, step=1),
                "seed": SLIDER_INPUT(key="seed", default=None, min_value=0, max_value=46000, step=1, api_only=True),
            },
            outbound_schema={
                "field_map": {
                    "music_prompt": "prompt",
                },
                "static": {
                    "negative_prompt": ""
                },
                "optional": ["seed"],
            },
            modes={
                "text-to-music": ModeCapabilities(
                    display_name="From Text",
                    summary_params=["duration"],
                    outbound_schema={
                        "endpoint": "beatoven/music-generation",
                    },
                ),
            },
            pricing=Pricing(
                base_unit_price=0.1,
                base_unit="generation",
                markup_multiplier=1,
            ),
        ))

        # ElevenLabs Sound Effect Generation V2
        self._register(ModelCapabilities(
            model_id="elevenlabs/sound-effect-generation-v2",
            provider_name="ElevenLabs SFX V2",
            description="Premium sound effect generation",
            output_media_type="audio",
            output_asset_type="sound_effect",
            composer_display_section="sound_effect",
            tier="Pro",
            link="https://fal.ai/models/fal-ai/elevenlabs/sound-effects/v2",
            inputs={
                "sfx_prompt": TEXT_INPUT(key="sfx_prompt", max_length=5000),
                "duration": SLIDER_INPUT(key="duration", default=5, min_value=0.5, max_value=22, step=0.5),
                "loop": TOGGLE_INPUT(key="loop", default=False),
            },
            outbound_schema={
                "field_map": {
                    "sfx_prompt": "text",
                    "duration": "duration_seconds",
                },
                "optional": ["duration_seconds"],
            },
            modes={
                "text-to-sound-effect": ModeCapabilities(
                    display_name="From Text",
                    summary_params=["duration"],
                    outbound_schema={
                        "endpoint": "fal-ai/elevenlabs/sound-effects/v2",
                    },
                ),
            },
            pricing=Pricing(
                base_unit_price=0.002,
                base_unit="second",
                unit_source_param="duration",
                markup_multiplier=1,
            ),
        ))

        # ElevenLabs V2
        self._register(ModelCapabilities(
            model_id="elevenlabs/eleven_multilingual_v2",
            provider_name="ElevenLabs V2",
            description="Natural-sounding text-to-speech synthesis",
            output_media_type="audio",
            output_asset_type="speech",
            composer_display_section="speech",
            tier="Elite",
            link="https://fal.ai/models/fal-ai/elevenlabs/tts/multilingual-v2",
            inputs={
                "speech_text": TEXT_INPUT(key="speech_text", max_length=10000),
                "previous_text": TEXT_INPUT(key="previous_text", max_length=2000, default=None),
                "next_text": TEXT_INPUT(key="next_text", max_length=2000, default=None),
                "voice": DROPDOWN_INPUT(key="voice", default=ELEVENLABS_DEFAULT_VOICE_ID),
                "language": DROPDOWN_INPUT(key="language", enum=list(ELEVENLABS_MODEL_LANGUAGES["eleven_multilingual_v2"]), default="_skip_"),
                "speed": SLIDER_INPUT(key="speed", default=1, min_value=0.7, max_value=1.2, step=0.1),
            },
            outbound_schema={
                "field_map": {
                    "speech_text": "text",
                    "language": "language_code",
                },
                "static": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0,
                },
                "optional": ["previous_text", "next_text", "language_code"],
            },
            modes={
                "text-to-speech": ModeCapabilities(
                    display_name="From Text",
                    summary_params=["voice", "speed"],
                    outbound_schema={
                        "endpoint": "fal-ai/elevenlabs/tts/multilingual-v2",
                    },
                ),
            },
            pricing=Pricing(
                base_unit_price=0.0001,
                base_unit="character",
                unit_source_param="speech_text",
                unit_bucket_size=1000,
                markup_multiplier=1,
            ),
        ))

        # ElevenLabs Turbo
        self._register(ModelCapabilities(
            model_id="elevenlabs/eleven_turbo_v2_5",
            provider_name="ElevenLabs Turbo",
            description="Ultra-fast speech synthesis for real-time apps",
            output_media_type="audio",
            output_asset_type="speech",
            composer_display_section="speech",
            tier="Pro",
            link="https://fal.ai/models/fal-ai/elevenlabs/tts/turbo-v2.5",
            inputs={
                "speech_text": TEXT_INPUT(key="speech_text", max_length=10000),
                "previous_text": TEXT_INPUT(key="previous_text", max_length=2000, default=None),
                "next_text": TEXT_INPUT(key="next_text", max_length=2000, default=None),
                "voice": DROPDOWN_INPUT(key="voice", default=ELEVENLABS_DEFAULT_VOICE_ID),
                "language": DROPDOWN_INPUT(key="language", enum=list(ELEVENLABS_MODEL_LANGUAGES["eleven_turbo_v2_5"]), default="_skip_"),
                "speed": SLIDER_INPUT(key="speed", default=1, min_value=0.7, max_value=1.2, step=0.1),
            },
            outbound_schema={
                "field_map": {
                    "speech_text": "text",
                    "language": "language_code",
                },
                "static": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0,
                },
                "optional": ["previous_text", "next_text", "language_code"],
            },
            modes={
                "text-to-speech": ModeCapabilities(
                    display_name="From Text",
                    summary_params=["voice", "speed"],
                    outbound_schema={
                        "endpoint": "fal-ai/elevenlabs/tts/turbo-v2.5",
                    },
                ),
            },
            pricing=Pricing(
                base_unit_price=0.00005,
                base_unit="character",
                unit_source_param="speech_text",
                unit_bucket_size=1000,
                markup_multiplier=1,
            ),
        ))

        # =====================================================================
        # AVATAR MODELS
        # =====================================================================

        # Kling Avatar Standard
        self._register(ModelCapabilities(
            model_id="kling-video/ai-avatar/v2/standard",
            provider_name="Kling Avatar Standard",
            description="Standard AI avatar for presentations",
            output_media_type="video",
            output_asset_type="avatar_video",
            composer_display_section="avatar",
            tier="Pro",
            fps=30,
            link="https://fal.ai/models/fal-ai/kling-video/ai-avatar/v2/standard",
            inputs={
                "avatar_prompt": TEXT_INPUT(key="avatar_prompt", max_length=2000, default=None),
                "source_speech": URL_INPUT(key="source_speech"),
                "source_image": URL_INPUT(key="source_image"),
            },
            outbound_schema={
                "field_map": {
                    "avatar_prompt": "prompt",
                    "source_speech": "audio_url",
                    "source_image": "image_url",
                },
                "transforms": {
                    "avatar_prompt": empty_to_dot,
                },
            },
            modes={
                "speech-to-avatar": ModeCapabilities(
                    display_name="From Speech",
                    summary_params=[],
                    outbound_schema={
                        "endpoint": "fal-ai/kling-video/ai-avatar/v2/standard",
                    },
                ),
            },
            pricing=Pricing(
                base_unit_price=0.0562,
                base_unit="second",
                unit_source_param="@source_speech",
                markup_multiplier=1,
            ),
        ))

        # Veed Fabric
        self._register(ModelCapabilities(
            model_id="veed/fabric-1.0",
            provider_name="Veed Fabric",
            description="AI avatar platform for personalized content",
            output_media_type="video",
            output_asset_type="avatar_video",
            composer_display_section="avatar",
            tier="Pro",
            fps=25,
            link="https://fal.ai/models/veed/fabric-1.0",
            inputs={
                "source_image": URL_INPUT(key="source_image"),
                "resolution": DROPDOWN_INPUT(key="resolution", enum=["480p", "720p"], default="480p"),
            },
            outbound_schema={
                "field_map": {
                    "source_image": "image_url",
                },
            },
            modes={
                "speech-to-avatar": ModeCapabilities(
                    display_name="From Speech",
                    summary_params=["resolution"],
                    inputs={
                        "source_speech": URL_INPUT(key="source_speech"),
                    },
                    outbound_schema={
                        "endpoint": "veed/fabric-1.0",
                        "field_map": {
                            "source_speech": "audio_url",
                        },
                    },
                    pricing=Pricing(
                        base_unit_price=0.08,
                        base_unit="second",
                        unit_source_param="@source_speech",
                        markup_multiplier=1,
                        base_price_selector=BasePriceSelector(
                            param_key="resolution",
                            price_map={"480p": 0.08, "720p": 0.15}
                        ),
                    ),
                ),
                "text-to-avatar": ModeCapabilities(
                    display_name="From Text",
                    summary_params=["resolution"],
                    inputs={
                        "speech_text": TEXT_INPUT(key="speech_text", max_length=5000),
                        "voice_description": TEXT_INPUT(key="voice_description", max_length=1000, default=None),
                    },
                    outbound_schema={
                        "endpoint": "veed/fabric-1.0/text",
                        "field_map": {
                            "speech_text": "text",
                        },
                        "optional": ["voice_description"],
                    },
                    pricing=Pricing(
                        base_unit_price=0.0008,
                        base_unit="character",
                        unit_source_param="speech_text",
                        unit_bucket_size=100,
                        markup_multiplier=1,
                        base_price_selector=BasePriceSelector(
                            param_key="resolution",
                            price_map={"480p": 0.0008, "720p": 0.0015}
                        ),
                    ),
                ),
            },
        ))
        # =====================================================================
        # Whisper Models
        self._register(ModelCapabilities(
            model_id="openai/whisper-1",
            provider_name="OpenAI Whisper",
            description="Robust speech-to-text transcription with word-level timestamps",
            output_media_type="json",
            output_asset_type="transcript",
            composer_display_section="speech",
            tier="Basic",
            link="https://fal.ai/models/fal-ai/whisper",
            inputs={
                "audio_file": URL_INPUT(key="audio_file"),
            },
            outbound_schema={
                "field_map": {
                    "audio_file": "audio_url",
                },
                "static": {
                    "task": "transcribe",
                    "chunk_level": "word",
                    "version": "3",
                    "batch_size": 64,
                    "num_speakers": None
                }
            },
            modes={
                "transcribe": ModeCapabilities(
                    display_name="Transcribe Audio",
                    outbound_schema={
                        "endpoint": "fal-ai/whisper",
                    },
                ),
            },
            pricing=Pricing(
                base_unit_price=0.01,
                base_unit="generation",
                markup_multiplier=1,
            )
        ))

    def _register(self, capabilities: ModelCapabilities):
        """Register capabilities for a model.
        
        Indexes by:
        1. model_id (semantic identifier like "google/veo-3.1")
        2. Each mode's outbound_schema.endpoint (FAL endpoint like "fal-ai/veo3.1")
        
        Note: Base outbound_schema should NOT have endpoint - only modes have endpoints.
        """
        # Register by model_id
        self._capabilities[capabilities.model_id] = capabilities
        
        # Register by each mode's endpoint
        for mode_caps in capabilities.modes.values():
            if mode_caps.outbound_schema:
                mode_endpoint = mode_caps.outbound_schema.get("endpoint")
                if mode_endpoint and mode_endpoint not in self._capabilities:
                    self._capabilities[mode_endpoint] = capabilities

    def get(self, model_id: str) -> Optional[ModelCapabilities]:
        """Get capabilities for a model.

        Looks up by:
        1. Direct model_id match
        2. Resolved alias (friendly name -> endpoint)
        """
        if model_id in self._capabilities:
            return self._capabilities[model_id]

        endpoint = resolve_model_alias(model_id)
        if endpoint in self._capabilities:
            return self._capabilities[endpoint]

        return None

    def get_all(self) -> list[ModelCapabilities]:
        """Get capabilities for all registered models."""
        seen = set()
        result = []
        for caps in self._capabilities.values():
            if caps.model_id not in seen:
                seen.add(caps.model_id)
                result.append(caps)
        return result
# ===========================================================================
# GLOBAL REGISTRY INSTANCE
# ===========================================================================
_registry = CapabilitiesRegistry()


def get_capabilities(model_id: str) -> Optional[ModelCapabilities]:
    """Get capabilities for a model."""
    return _registry.get(model_id)


def get_all_capabilities() -> list[ModelCapabilities]:
    """Get capabilities for all registered models."""
    return _registry.get_all()


def get_required_inputs_for_mode(model_id: str, mode: str) -> list[str]:
    """
    Dynamically get required input field names for a model+mode combination.

    Merges base inputs with mode-specific inputs, then filters for required fields.
    This is the single source of truth for input validation - no hardcoded mappings needed.

    Args:
        model_id: Model identifier (e.g., "google/veo-3.1", "openai/gpt-image-1.5")
        mode: Generation mode (e.g., "text-to-video", "image-to-image")

    Returns:
        List of required input field keys (e.g., ["video_prompt", "first_frame"])
    """
    caps = get_capabilities(model_id)
    if not caps:
        return []

    # Merge base inputs with mode-specific inputs
    all_inputs = dict(caps.inputs) if caps.inputs else {}
    if mode and mode in caps.modes:
        mode_caps = caps.modes[mode]
        if mode_caps.inputs:
            all_inputs.update(mode_caps.inputs)

    # Filter for required inputs (those with default=REQUIRED)
    return [
        field_key
        for field_key, input_field in all_inputs.items()
        if input_field.is_required
    ]


# ===========================================================================
# FRONTEND MODEL CONFIG HELPERS
# ===========================================================================

def get_all_model_configs() -> list[dict[str, Any]]:
    """
    Get all model capabilities as frontend ModelConfig format.

    Returns a flat list of model configs, with each mode as a separate entry
    when models have mode-specific endpoints.
    """
    all_caps = get_all_capabilities()
    configs = []

    for caps in all_caps:
        if not caps.is_active:
            continue

        # If model has modes, create a config for each mode with unique endpoint
        if caps.modes:
            for mode_name in caps.modes.keys():
                mode_config = caps.to_model_config(mode=mode_name)
                configs.append(mode_config)
        else:
            # No modes - just return base config
            base_config = caps.to_model_config()
            configs.append(base_config)

    return configs


def get_model_configs_by_section(section: str) -> list[dict[str, Any]]:
    """
    Get model configs filtered by composer_display_section.

    Args:
        section: The composer tab section ("image", "video", "avatar", "speech", "music", "sound_effect")

    Returns:
        List of model configs matching the section.
    """
    return [c for c in get_all_model_configs() if c["composer_display_section"] == section]


def get_model_config_by_endpoint(endpoint: str) -> Optional[dict[str, Any]]:
    """
    Get a single model config by endpoint.

    Args:
        endpoint: The model endpoint (e.g., "fal-ai/veo3.1")

    Returns:
        The model config dict or None if not found.
    """
    caps = get_capabilities(endpoint)
    if not caps:
        return None

    # Find which mode this endpoint belongs to
    for mode_name, mode_caps in caps.modes.items():
        if mode_caps.outbound_schema:
            mode_endpoint = mode_caps.outbound_schema.get("endpoint")
            if mode_endpoint == endpoint:
                return caps.to_model_config(mode=mode_name)

    # Fallback to base config
    return caps.to_model_config()
