"""
Registry reader for loading and querying model/provider configurations.

This module reads the JSON registry files from the shared package and provides
query functions similar to the TypeScript implementation.
"""

import json
import os
from pathlib import Path
from typing import Any, Optional

from .types import (
    GenerationType,
    VideoGenerationMode,
    Model,
    Provider,
    GenerationModeDefinition,
    ValidationResult,
)


# =============================================================================
# Registry Loading
# =============================================================================

def _get_registry_path() -> Path:
    """Get the path to the shared registry directory."""
    # Navigate from octupost-api/app/registry to packages/shared/src/registry
    current_dir = Path(__file__).parent
    registry_path = current_dir.parent.parent.parent / "packages" / "shared" / "src" / "registry"
    return registry_path


def _load_json(filename: str) -> dict[str, Any]:
    """Load a JSON file from the registry directory."""
    registry_path = _get_registry_path()
    file_path = registry_path / filename
    
    if not file_path.exists():
        raise FileNotFoundError(f"Registry file not found: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# Lazy-loaded registry data
_models_cache: Optional[dict[str, Any]] = None
_providers_cache: Optional[dict[str, Any]] = None


def _get_models_data() -> dict[str, Any]:
    """Get the models registry data (cached)."""
    global _models_cache
    if _models_cache is None:
        _models_cache = _load_json("models.json")
    return _models_cache


def _get_providers_data() -> dict[str, Any]:
    """Get the providers registry data (cached)."""
    global _providers_cache
    if _providers_cache is None:
        _providers_cache = _load_json("providers.json")
    return _providers_cache


def reload_registry() -> None:
    """Force reload of registry data from disk."""
    global _models_cache, _providers_cache
    _models_cache = None
    _providers_cache = None


# =============================================================================
# Model Queries
# =============================================================================

def get_model(model_id: str) -> Optional[Model]:
    """Get a model by its ID."""
    models = _get_models_data().get("models", {})
    return models.get(model_id)


def get_all_models() -> dict[str, Model]:
    """Get all models (including disabled ones)."""
    return _get_models_data().get("models", {})


def get_enabled_models() -> dict[str, Model]:
    """Get only enabled models."""
    models = get_all_models()
    return {
        model_id: model
        for model_id, model in models.items()
        if model.get("enabled", False)
    }


def get_models_by_type(gen_type: GenerationType) -> dict[str, Model]:
    """Get enabled models filtered by generation type."""
    models = get_all_models()
    return {
        model_id: model
        for model_id, model in models.items()
        if model.get("type") == gen_type and model.get("enabled", False)
    }


def get_models_by_provider(provider_id: str) -> dict[str, Model]:
    """Get enabled models filtered by provider."""
    models = get_all_models()
    return {
        model_id: model
        for model_id, model in models.items()
        if model.get("provider") == provider_id and model.get("enabled", False)
    }


def get_model_ids(gen_type: GenerationType) -> list[str]:
    """Get model IDs for a specific generation type."""
    return list(get_models_by_type(gen_type).keys())


# =============================================================================
# Provider Queries
# =============================================================================

def get_provider(provider_id: str) -> Optional[Provider]:
    """Get a provider by its ID."""
    providers = _get_providers_data().get("providers", {})
    return providers.get(provider_id)


def get_all_providers() -> dict[str, Provider]:
    """Get all providers."""
    return _get_providers_data().get("providers", {})


def get_provider_for_model(model_id: str) -> Optional[Provider]:
    """Get the provider for a specific model."""
    model = get_model(model_id)
    if not model:
        return None
    return get_provider(model.get("provider", ""))


# =============================================================================
# Generation Mode Queries
# =============================================================================

def get_generation_modes() -> list[GenerationModeDefinition]:
    """Get all video generation modes."""
    modes = _get_models_data().get("generationModes", {})
    return list(modes.values())


def get_generation_mode(mode_id: VideoGenerationMode) -> Optional[GenerationModeDefinition]:
    """Get a specific generation mode by ID."""
    modes = _get_models_data().get("generationModes", {})
    return modes.get(mode_id)


# =============================================================================
# Validation
# =============================================================================

def is_valid_model(model_id: str) -> bool:
    """Check if a model ID is valid and enabled."""
    model = get_model(model_id)
    return model is not None and model.get("enabled", False)


def validate_params(
    model_id: str,
    params: dict[str, Any],
) -> ValidationResult:
    """
    Validate parameters against a model's schema.
    
    Args:
        model_id: The model identifier
        params: Parameters to validate
        
    Returns:
        ValidationResult with valid flag and any errors
    """
    model = get_model(model_id)
    if not model:
        return {"valid": False, "errors": [f"Unknown model: {model_id}"]}
    
    errors: list[str] = []
    parameters = model.get("parameters", {})
    required = parameters.get("required", [])
    optional = parameters.get("optional", {})
    
    # Check required parameters
    for req_param in required:
        if req_param not in params or params[req_param] is None:
            errors.append(f"Missing required parameter: {req_param}")
    
    # Validate optional parameters
    for key, value in params.items():
        if key in required:
            continue
            
        param_def = optional.get(key)
        if not param_def:
            continue  # Unknown parameter, allow it to pass through
        
        param_type = param_def.get("type")
        
        # Type checking
        if param_type in ("integer", "number"):
            if not isinstance(value, (int, float)):
                errors.append(f"{key} must be a number")
                continue
            
            min_val = param_def.get("min")
            max_val = param_def.get("max")
            
            if min_val is not None and value < min_val:
                errors.append(f"{key} must be >= {min_val}")
            if max_val is not None and value > max_val:
                errors.append(f"{key} must be <= {max_val}")
        
        elif param_type == "string":
            if not isinstance(value, str):
                errors.append(f"{key} must be a string")
                continue
            
            max_length = param_def.get("maxLength")
            enum_values = param_def.get("enum")
            
            if max_length is not None and len(value) > max_length:
                errors.append(f"{key} must be <= {max_length} characters")
            if enum_values is not None and value not in enum_values:
                errors.append(f"{key} must be one of: {', '.join(enum_values)}")
        
        elif param_type == "boolean":
            if not isinstance(value, bool):
                errors.append(f"{key} must be a boolean")
    
    return {"valid": len(errors) == 0, "errors": errors}


# =============================================================================
# Cost Calculation
# =============================================================================

def calculate_cost(model_id: str, quantity: float = 1.0) -> float:
    """
    Calculate estimated cost for a generation request.
    
    Args:
        model_id: The model identifier
        quantity: Number of units (images, seconds, characters, etc.)
        
    Returns:
        Estimated cost in USD
    """
    model = get_model(model_id)
    if not model:
        return 0.0
    
    pricing = model.get("pricing", {})
    price_per_unit = pricing.get("pricePerUnit", 0.0)
    
    return price_per_unit * quantity


# =============================================================================
# Parameter Helpers
# =============================================================================

def get_default_params(model_id: str) -> dict[str, Any]:
    """
    Get default parameter values for a model.
    
    Args:
        model_id: The model identifier
        
    Returns:
        Dictionary of parameter names to default values
    """
    model = get_model(model_id)
    if not model:
        return {}
    
    defaults: dict[str, Any] = {}
    optional = model.get("parameters", {}).get("optional", {})
    
    for key, param_def in optional.items():
        if "default" in param_def:
            defaults[key] = param_def["default"]
    
    # Also include provider config defaults
    provider_defaults = model.get("providerConfig", {}).get("defaultParams", {})
    defaults.update(provider_defaults)
    
    return defaults


def apply_parameter_transforms(
    model_id: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    """
    Apply parameter transforms defined in the model's provider config.
    
    Args:
        model_id: The model identifier
        params: Input parameters
        
    Returns:
        Transformed parameters
    """
    model = get_model(model_id)
    if not model:
        return params
    
    result = params.copy()
    transforms = model.get("providerConfig", {}).get("parameterTransforms", {})
    
    for key, transform in transforms.items():
        if key not in result:
            continue
        
        value = result[key]
        
        if not isinstance(value, (int, float)):
            continue
        
        # Apply transforms
        if "min" in transform:
            value = max(value, transform["min"])
        if "max" in transform:
            value = min(value, transform["max"])
        if "multiply" in transform:
            value = value * transform["multiply"]
        
        result[key] = value
    
    return result


def map_parameters_to_provider(
    model_id: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    """
    Map standard parameter names to provider-specific names.
    
    Args:
        model_id: The model identifier
        params: Input parameters with standard names
        
    Returns:
        Parameters with provider-specific names
    """
    model = get_model(model_id)
    if not model:
        return params
    
    mapping = model.get("providerConfig", {}).get("parameterMapping", {})
    if not mapping:
        return params
    
    result: dict[str, Any] = {}
    
    for key, value in params.items():
        mapped_key = mapping.get(key, key)
        
        # Handle nested keys like "image_size.width"
        if "." in mapped_key:
            parts = mapped_key.split(".")
            if parts[0] not in result:
                result[parts[0]] = {}
            result[parts[0]][parts[1]] = value
        else:
            result[mapped_key] = value
    
    return result

