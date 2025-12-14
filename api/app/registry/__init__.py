"""
AI Model Registry

Centralized configuration for all AI models. This module reads from
provider.json in the shared package.

Example:
    from app.registry import get_model, get_models_by_type, validate_params

    # Get a specific model
    model = get_model("fal-ai/veo3.1")

    # Get all video models
    video_models = get_models_by_type("text-to-video")

    # Validate parameters dynamically
    result = validate_params("fal-ai/veo3.1", {"prompt": "A cat", "duration": 4})
"""

from .reader import (
    get_model,
    get_model_config,
    get_all_models,
    get_enabled_models,
    get_models_by_type,
    get_models_by_provider,
    get_model_ids,
    get_provider,
    get_all_providers,
    get_provider_for_model,
    get_generation_modes,
    get_generation_mode,
    is_valid_model,
    validate_params,
    calculate_cost,
    get_default_params,
    reload_registry,
)

from .types import (
    GenerationType,
    VideoGenerationMode,
    TierType,
    ProviderType,
    AuthMethod,
    PricingUnit,
    Provider,
    ModelPricing,
    AcceptedValuesRange,
    AcceptedValues,
    ParameterDefinition,
    DefaultValuesDefinition,
    ParameterEntry,
    Model,
    GenerationModeDefinition,
    ValidationResult,
    # Legacy types for backward compatibility
    DurationRange,
    ModelCapabilities,
    ParameterTransform,
    ProviderConfig,
    ModelParameters,
)

__all__ = [
    # Reader functions
    "get_model",
    "get_model_config",
    "get_all_models",
    "get_enabled_models",
    "get_models_by_type",
    "get_models_by_provider",
    "get_model_ids",
    "get_provider",
    "get_all_providers",
    "get_provider_for_model",
    "get_generation_modes",
    "get_generation_mode",
    "is_valid_model",
    "validate_params",
    "calculate_cost",
    "get_default_params",
    "reload_registry",
    # Types
    "GenerationType",
    "VideoGenerationMode",
    "TierType",
    "ProviderType",
    "AuthMethod",
    "PricingUnit",
    "Provider",
    "ModelPricing",
    "AcceptedValuesRange",
    "AcceptedValues",
    "ParameterDefinition",
    "DefaultValuesDefinition",
    "ParameterEntry",
    "Model",
    "GenerationModeDefinition",
    "ValidationResult",
    # Legacy types
    "DurationRange",
    "ModelCapabilities",
    "ParameterTransform",
    "ProviderConfig",
    "ModelParameters",
]
