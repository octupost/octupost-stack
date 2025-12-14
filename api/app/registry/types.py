"""
Type definitions for the AI Model Registry.

These types match the schema in packages/shared/src/registry/provider.json
"""

from typing import Any, Literal, TypedDict, Optional, Union


# =============================================================================
# Generation Types
# =============================================================================

GenerationType = Literal[
    "text-to-image",
    "text-to-video",
    "image-to-video",
    "text-to-speech",
    "text-to-audio",
    "text-to-music",
    "video-to-audio",
    "avatar",
    "reference-to-video",
    "first-last-frame-to-video",
    "retake",
    "text-generation",
]

VideoGenerationMode = Literal[
    "text-to-video",
    "first-frame",
    "first-last-frame",
    "components",
]

TierType = Literal["Basic", "Standard", "Plus", "Pro", "Elite"]

BillingStrategy = Literal["direct", "reservation"]


# =============================================================================
# Provider Types
# =============================================================================

ProviderType = Literal["sdk", "rest", "websocket"]
AuthMethod = Literal["api-key", "oauth", "bearer"]


class Provider(TypedDict, total=False):
    """Provider configuration (synthesized from model configs)."""
    name: str
    type: ProviderType
    sdkPackage: Optional[str]
    authMethod: AuthMethod
    authEnvVar: str
    baseUrl: Optional[str]
    capabilities: list[str]
    responseMapping: dict[str, str]


# =============================================================================
# Pricing Types
# =============================================================================

PricingUnit = Literal[
    "per_second", 
    "per_request", 
    "per_char",
    "image", 
    "second", 
    "character", 
    "request", 
    "generation"
]


class ModelPricing(TypedDict, total=False):
    """Pricing information for a model from provider.json."""
    unit: PricingUnit
    price_per_unit: float
    billing_unit_size: int
    tier: dict[str, float]  # Tiered pricing by resolution/duration
    tier_field_key: str  # Field to use for tier lookup
    multiplier_field_key: Union[str, list[str]]  # Field(s) that trigger multiplier
    multiplier_value: float


# =============================================================================
# Parameter Types (matching provider.json schema)
# =============================================================================

ParameterType = Literal["string", "integer", "float", "boolean", "image", "image_array"]


class AcceptedValuesRange(TypedDict, total=False):
    """Range-based accepted values for numeric parameters."""
    steps: Union[int, float]
    min_duration: int
    max_duration: int
    min_speed: float
    max_speed: float


# AcceptedValues can be a list of strings or a range object
AcceptedValues = Union[list[str], list[int], AcceptedValuesRange]


class ParameterDefinition(TypedDict, total=False):
    """
    Definition for a model parameter from provider.json.
    
    Example:
    {
        "key": "duration",
        "type": "integer",
        "notes": "Add s at the end of the duration",
        "default": 4,
        "mapping": "duration",
        "required": true,
        "mapping_type": "string",
        "accepted_values": {"steps": 2, "max_duration": 8, "min_duration": 4}
    }
    """
    key: str
    type: ParameterType
    notes: str  # Contains transformation hints like "Add s at the end"
    default: Any
    mapping: str  # Provider-specific parameter name
    required: bool
    mapping_type: str  # Target type: "string", "integer", "float", "boolean"
    accepted_values: AcceptedValues


class DefaultValuesDefinition(TypedDict, total=False):
    """
    Default values that should be merged into the request.
    
    Example:
    {
        "default_values": {
            "fps": 30,
            "seed": 42,
            "sync_mode": false
        }
    }
    """
    default_values: dict[str, Any]


# A parameter entry can be either a ParameterDefinition or DefaultValuesDefinition
ParameterEntry = Union[ParameterDefinition, DefaultValuesDefinition]


# =============================================================================
# Model Types (matching provider.json schema)
# =============================================================================

class Model(TypedDict, total=False):
    """
    Model configuration from provider.json.
    
    Example:
    {
        "fps": 24,
        "link": "https://fal.ai/models/fal-ai/veo3.1",
        "tier": "Elite",
        "type": "text-to-video",
        "price": {"unit": "per_second", "price_per_unit": 0.2},
        "endpoint": "fal-ai/veo3.1",
        "provider": "Veo3.1",
        "is_active": true,
        "parameters": [...],
        "parent_type": "text-to-video",
        "billing_strategy": "direct"
    }
    """
    fps: Optional[int]
    link: str
    tier: TierType
    type: GenerationType
    price: ModelPricing
    endpoint: str
    provider: str
    is_active: bool
    parameters: list[ParameterEntry]
    parent_type: str
    billing_strategy: BillingStrategy  # Defaults to "direct" if not specified


class GenerationModeDefinition(TypedDict):
    """Video generation mode definition."""
    id: str
    label: str
    description: str


# =============================================================================
# Result Types
# =============================================================================

class ValidationResult(TypedDict):
    """Result of parameter validation."""
    valid: bool
    errors: list[str]


# =============================================================================
# Legacy Types (for backward compatibility)
# =============================================================================

class DurationRange(TypedDict, total=False):
    """Duration range in seconds (legacy)."""
    min: int
    max: int
    step: int


class ModelCapabilities(TypedDict, total=False):
    """Model capabilities and constraints (legacy)."""
    resolutions: list[str]
    aspectRatios: list[str]
    duration: DurationRange
    maxImages: int
    voices: list[str]
    voiceLabels: dict[str, str]
    languages: list[str]
    supportedModes: list[VideoGenerationMode]
    genres: list[str]
    maxTokens: int


class ParameterTransform(TypedDict, total=False):
    """Transformation to apply to a parameter (legacy)."""
    max: float
    min: float
    multiply: float


class ProviderConfig(TypedDict, total=False):
    """Provider-specific configuration for a model (legacy)."""
    endpoint: str
    method: Literal["POST", "GET"]
    parameterMapping: dict[str, str]
    parameterTransforms: dict[str, ParameterTransform]
    defaultParams: dict[str, Any]
    model: str


class ModelParameters(TypedDict, total=False):
    """Parameter definitions for a model (legacy)."""
    required: list[str]
    optional: dict[str, Any]
