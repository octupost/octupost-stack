"""
AI Model Registry

Centralized configuration for all AI models. This module reads from the
shared JSON registry that is also used by the frontend.

Example:
    from app.registry import get_model, get_models_by_type, validate_params

    # Get a specific model
    model = get_model("fal-ai/flux/schnell")

    # Get all image models
    image_models = get_models_by_type("text-to-image")

    # Validate parameters
    result = validate_params("fal-ai/flux/schnell", {"prompt": "A cat"})
"""

from .reader import (
    get_model,
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
)

from .types import (
    GenerationType,
    VideoGenerationMode,
    ProviderType,
    AuthMethod,
    PricingUnit,
    Provider,
    ModelPricing,
    DurationRange,
    ModelCapabilities,
    ParameterDefinition,
    ModelParameters,
    ParameterTransform,
    ProviderConfig,
    Model,
    GenerationModeDefinition,
    ValidationResult,
)

__all__ = [
    # Reader functions
    "get_model",
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
    # Types
    "GenerationType",
    "VideoGenerationMode",
    "ProviderType",
    "AuthMethod",
    "PricingUnit",
    "Provider",
    "ModelPricing",
    "DurationRange",
    "ModelCapabilities",
    "ParameterDefinition",
    "ModelParameters",
    "ParameterTransform",
    "ProviderConfig",
    "Model",
    "GenerationModeDefinition",
    "ValidationResult",
]

