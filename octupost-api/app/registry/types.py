"""
Type definitions for the AI Model Registry.

These types mirror the TypeScript definitions in packages/shared/src/registry/types.ts
"""

from typing import Any, Literal, TypedDict, Optional


# =============================================================================
# Generation Types
# =============================================================================

GenerationType = Literal[
    "text-to-image",
    "text-to-video",
    "image-to-video",
    "text-to-speech",
    "text-to-audio",
    "text-generation",
]

VideoGenerationMode = Literal[
    "text-to-video",
    "first-frame",
    "first-last-frame",
    "components",
]


# =============================================================================
# Provider Types
# =============================================================================

ProviderType = Literal["sdk", "rest", "websocket"]
AuthMethod = Literal["api-key", "oauth", "bearer"]


class Provider(TypedDict):
    """Provider configuration."""
    name: str
    type: ProviderType
    sdkPackage: Optional[str]
    authMethod: AuthMethod
    authEnvVar: str
    baseUrl: Optional[str]
    capabilities: list[GenerationType]
    responseMapping: dict[str, str]


# =============================================================================
# Model Types
# =============================================================================

PricingUnit = Literal["image", "second", "character", "request", "generation"]


class ModelPricing(TypedDict):
    """Pricing information for a model."""
    unit: PricingUnit
    pricePerUnit: float


class DurationRange(TypedDict, total=False):
    """Duration range in seconds."""
    min: int
    max: int
    step: int  # Step size for duration values (defaults to 1 if not specified)


class ModelCapabilities(TypedDict, total=False):
    """Model capabilities and constraints."""
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


ParameterType = Literal["string", "number", "integer", "boolean"]


class ParameterDefinition(TypedDict, total=False):
    """Definition for a model parameter."""
    type: ParameterType
    default: Any
    min: float
    max: float
    maxLength: int
    enum: list[str]
    description: str


class ModelParameters(TypedDict):
    """Parameter definitions for a model."""
    required: list[str]
    optional: dict[str, ParameterDefinition]


class ParameterTransform(TypedDict, total=False):
    """Transformation to apply to a parameter."""
    max: float
    min: float
    multiply: float


class ProviderConfig(TypedDict, total=False):
    """Provider-specific configuration for a model."""
    endpoint: str
    method: Literal["POST", "GET"]
    parameterMapping: dict[str, str]
    parameterTransforms: dict[str, ParameterTransform]
    defaultParams: dict[str, Any]
    model: str


class Model(TypedDict):
    """Model configuration."""
    provider: str
    type: GenerationType
    name: str
    description: str
    enabled: bool
    pricing: ModelPricing
    capabilities: ModelCapabilities
    parameters: ModelParameters
    providerConfig: ProviderConfig


class GenerationModeDefinition(TypedDict):
    """Video generation mode definition."""
    id: VideoGenerationMode
    label: str
    description: str


# =============================================================================
# Result Types
# =============================================================================

class ValidationResult(TypedDict):
    """Result of parameter validation."""
    valid: bool
    errors: list[str]

