"""
Registry reader for loading and querying model/provider configurations.

This module reads provider.json from the shared package and provides
query functions for model lookups, validation, and parameter handling.
"""

import json
import math
from pathlib import Path
from typing import Any, Optional, Union

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
    # Navigate from api/app/registry to packages/shared/src/registry
    current_dir = Path(__file__).parent
    registry_path = current_dir.parent.parent.parent / "packages" / "shared" / "src" / "registry"
    return registry_path


def _load_json(filename: str) -> Any:
    """Load a JSON file from the registry directory."""
    registry_path = _get_registry_path()
    file_path = registry_path / filename
    
    if not file_path.exists():
        raise FileNotFoundError(f"Registry file not found: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# Lazy-loaded registry data
_models_cache: Optional[dict[str, Any]] = None


def _get_models_data() -> dict[str, Any]:
    """
    Load and index models from provider.json by endpoint.
    
    The provider.json file contains an array of model configurations.
    We index them by endpoint for quick lookup.
    """
    global _models_cache
    if _models_cache is None:
        raw_data = _load_json("provider.json")  # Array of model configs
        models = {}
        for model in raw_data:
            endpoint = model.get("endpoint")
            if endpoint:
                models[endpoint] = model
        _models_cache = {"models": models}
    return _models_cache


def reload_registry() -> None:
    """Force reload of registry data from disk."""
    global _models_cache
    _models_cache = None


# =============================================================================
# Model Queries
# =============================================================================

def get_model(model_id: str) -> Optional[Model]:
    """Get a model by its ID (endpoint)."""
    models = _get_models_data().get("models", {})
    return models.get(model_id)


def get_all_models() -> dict[str, Model]:
    """Get all models (including disabled ones)."""
    return _get_models_data().get("models", {})


def get_enabled_models() -> dict[str, Model]:
    """Get only enabled/active models."""
    models = get_all_models()
    return {
        model_id: model
        for model_id, model in models.items()
        if model.get("is_active", False)
    }


def get_models_by_type(gen_type: GenerationType) -> dict[str, Model]:
    """Get enabled models filtered by generation type."""
    models = get_all_models()
    return {
        model_id: model
        for model_id, model in models.items()
        if model.get("type") == gen_type and model.get("is_active", False)
    }


def get_models_by_provider(provider_name: str) -> dict[str, Model]:
    """Get enabled models filtered by provider name."""
    models = get_all_models()
    return {
        model_id: model
        for model_id, model in models.items()
        if model.get("provider") == provider_name and model.get("is_active", False)
    }


def get_model_ids(gen_type: GenerationType) -> list[str]:
    """Get model IDs for a specific generation type."""
    return list(get_models_by_type(gen_type).keys())


# =============================================================================
# Provider Queries
# =============================================================================

def get_provider(provider_id: str) -> Optional[Provider]:
    """
    Get a provider configuration.
    
    Note: In the new schema, providers are embedded in model configs.
    This returns a synthesized provider object for compatibility.
    """
    # Build provider from first matching model
    models = get_all_models()
    for model in models.values():
        if model.get("provider") == provider_id:
            return {
                "name": provider_id,
                "type": "sdk",
                "sdkPackage": "fal-client",
                "authMethod": "api-key",
                "authEnvVar": "FAL_KEY",
                "baseUrl": None,
                "capabilities": [model.get("type", "")],
                "responseMapping": {},
            }
    return None


def get_all_providers() -> dict[str, Provider]:
    """Get all unique providers from models."""
    providers: dict[str, Provider] = {}
    models = get_all_models()
    
    for model in models.values():
        provider_name = model.get("provider", "")
        if provider_name and provider_name not in providers:
            providers[provider_name] = {
                "name": provider_name,
                "type": "sdk",
                "sdkPackage": "fal-client",
                "authMethod": "api-key",
                "authEnvVar": "FAL_KEY",
                "baseUrl": None,
                "capabilities": [],
                "responseMapping": {},
            }
        # Add capability if not already present
        if provider_name:
            model_type = model.get("type", "")
            if model_type and model_type not in providers[provider_name]["capabilities"]:
                providers[provider_name]["capabilities"].append(model_type)
    
    return providers


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
    return [
        {"id": "text-to-video", "label": "Text to Video", "description": "Generate video from text prompt"},
        {"id": "first-frame", "label": "Image to Video", "description": "Generate video from an image"},
        {"id": "first-last-frame", "label": "First & Last Frame", "description": "Generate video between two frames"},
        {"id": "components", "label": "Components", "description": "Build video from components"},
    ]


def get_generation_mode(mode_id: VideoGenerationMode) -> Optional[GenerationModeDefinition]:
    """Get a specific generation mode by ID."""
    modes = {m["id"]: m for m in get_generation_modes()}
    return modes.get(mode_id)


# =============================================================================
# Validation
# =============================================================================

def is_valid_model(model_id: str) -> bool:
    """Check if a model ID is valid and enabled."""
    model = get_model(model_id)
    return model is not None and model.get("is_active", False)


def _get_param_definitions(model: dict) -> dict[str, dict]:
    """Extract parameter definitions from model config, indexed by key."""
    param_defs = {}
    for param in model.get("parameters", []):
        if isinstance(param, dict) and "key" in param:
            param_defs[param["key"]] = param
    return param_defs


def _get_param_definitions_with_fal_fallback(model_id: str, model: dict) -> dict[str, dict]:
    """
    Get parameter definitions from provider.json, falling back to FAL OpenAPI schema.
    
    This ensures validation works even when provider.json doesn't have parameter definitions.
    """
    # First try provider.json
    param_defs = _get_param_definitions(model)
    
    # If provider.json has parameters, use those (they may have custom overrides)
    if param_defs:
        return param_defs
    
    # Otherwise, fetch from FAL OpenAPI schema
    try:
        from app.services.fal_schema_service import fal_schema_service
        return fal_schema_service.get_param_definitions(model_id)
    except Exception as e:
        # Log error but continue - validation will be lenient
        import logging
        logging.warning(f"Failed to fetch FAL schema for {model_id}: {e}")
        return {}


def validate_params(
    model_id: str,
    params: dict[str, Any],
) -> ValidationResult:
    """
    Validate parameters against a model's schema.
    
    First checks provider.json for parameter definitions.
    If not defined there, fetches schema from FAL's OpenAPI endpoint.
    
    Note: This validation is lenient - it only checks values that are provided.
    Required parameters with defaults will be filled in by the transformer.
    
    Args:
        model_id: The model identifier (endpoint)
        params: Parameters to validate
        
    Returns:
        ValidationResult with valid flag and any errors
    """
    model = get_model(model_id)
    if not model:
        return {"valid": False, "errors": [f"Unknown model: {model_id}"]}
    
    errors: list[str] = []
    param_defs = _get_param_definitions_with_fal_fallback(model_id, model)
    
    # #region agent log
    import json
    from datetime import datetime
    def _debug_log_validation(location: str, message: str, data: dict, hypothesis_id: str = ""):
        log_entry = {"location": location, "message": message, "data": data, "timestamp": datetime.now().isoformat(), "sessionId": "debug-session", "hypothesisId": hypothesis_id}
        try:
            with open("/Users/serhatcamici/dev/octupost-stack/.cursor/debug.log", "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
            pass
    _debug_log_validation("reader.py:validate_params", "Validation param_defs", {"model_id": model_id, "param_keys": list(param_defs.keys()), "params_provided": list(params.keys()), "source": "fal_schema" if not _get_param_definitions(model) else "provider.json"}, "H2")
    # #endregion
    
    # Build a mapping target lookup - if another param maps to the same target and is provided, that's OK
    mapping_targets: dict[str, list[str]] = {}
    for k, p in param_defs.items():
        target = p.get("mapping", k)
        # Handle nested mappings - use root key
        root_target = target.split(".")[0] if "." in target else target
        if root_target not in mapping_targets:
            mapping_targets[root_target] = []
        mapping_targets[root_target].append(k)
    
    # Check required parameters that are truly required (no default, not a boolean with implicit false)
    for key, param_def in param_defs.items():
        required = param_def.get("required", False)
        param_type = param_def.get("type", "string")
        
        if required and key not in params:
            # Check if there's a default value
            has_default = "default" in param_def
            is_empty_default = param_def.get("default") == ""
            
            # #region agent log
            _debug_log_validation("reader.py:required_check", f"Checking required param: {key}", {"key": key, "required": required, "has_default": has_default, "is_empty_default": is_empty_default, "param_type": param_type}, "H2")
            # #endregion
            
            # Booleans have implicit false default, skip validation
            if param_type == "boolean":
                continue
            
            # Skip if has a non-empty default
            if has_default and not is_empty_default:
                continue
            
            # Check if another param with the same mapping target is provided
            # e.g., if image_url maps to "avatar" and avatar maps to "avatar", 
            # and avatar is provided, then image_url requirement is satisfied
            mapping_target = param_def.get("mapping", key)
            root_target = mapping_target.split(".")[0] if "." in mapping_target else mapping_target
            sibling_keys = mapping_targets.get(root_target, [])
            sibling_provided = any(k in params and k != key for k in sibling_keys)
            if sibling_provided:
                continue
            
            # Only error on truly required params with no default
            errors.append(f"Missing required parameter: {key}")
            continue
        
        if key not in params:
            continue
        
        value = params[key]
        accepted = param_def.get("accepted_values")
        
        # Type checking
        if param_type == "integer" and not isinstance(value, int):
            # Allow float that is whole number
            if isinstance(value, float) and value.is_integer():
                pass
            else:
                errors.append(f"{key} must be an integer")
                continue
        
        if param_type in ("float", "number") and not isinstance(value, (int, float)):
            errors.append(f"{key} must be a number")
            continue
        
        if param_type == "boolean" and not isinstance(value, bool):
            errors.append(f"{key} must be a boolean")
            continue
        
        if param_type == "string" and not isinstance(value, str):
            # Allow numbers that will be converted to strings
            if not isinstance(value, (int, float)):
                errors.append(f"{key} must be a string")
                continue
        
        # Validate against accepted_values / enum
        if accepted is not None:
            if isinstance(accepted, list):
                # Check if this is a list of objects (like avatar accepted_values)
                if len(accepted) > 0 and isinstance(accepted[0], dict):
                    # For object lists, check if value matches any 'name' field
                    valid_names = [item.get("name") for item in accepted if isinstance(item, dict)]
                    if value not in valid_names:
                        errors.append(f"{key} must be one of the available options")
                # Simple enum validation
                elif value not in accepted:
                    errors.append(f"{key} must be one of: {accepted}")
            elif isinstance(accepted, dict):
                # Range validation
                min_val = accepted.get("min_duration") or accepted.get("min_speed")
                max_val = accepted.get("max_duration") or accepted.get("max_speed")
                
                if min_val is not None and value < min_val:
                    errors.append(f"{key} must be >= {min_val}")
                if max_val is not None and value > max_val:
                    errors.append(f"{key} must be <= {max_val}")
        
        # Validate against minimum/maximum from OpenAPI schema
        minimum = param_def.get("minimum")
        maximum = param_def.get("maximum")
        
        if minimum is not None and isinstance(value, (int, float)) and value < minimum:
            errors.append(f"{key} must be >= {minimum}")
        if maximum is not None and isinstance(value, (int, float)) and value > maximum:
            errors.append(f"{key} must be <= {maximum}")
    
    return {"valid": len(errors) == 0, "errors": errors}


# =============================================================================
# Cost Calculation
# =============================================================================

def calculate_cost(model_id: str, quantity: float = 1.0, params: Optional[dict] = None) -> float:
    """
    Calculate estimated cost for a generation request.
    
    For per_char pricing with billing_unit_size, rounds UP to the nearest billing unit.
    e.g., billing_unit_size=1000, price_per_unit=$0.1:
      - 1-1000 chars = 1 unit = $0.10
      - 1001-2000 chars = 2 units = $0.20
    
    Args:
        model_id: The model identifier
        quantity: Number of units (images, seconds, characters, etc.)
        params: Optional parameters for tiered pricing
        
    Returns:
        Estimated cost in USD
    """
    model = get_model(model_id)
    if not model:
        return 0.0
    
    pricing = model.get("price", {})
    unit = pricing.get("unit", "per_request")
    
    # Handle per_char pricing with billing_unit_size
    if unit == "per_char":
        billing_unit_size = pricing.get("billing_unit_size", 1)
        price_per_unit = pricing.get("price_per_unit", 0)
        
        # Round UP to nearest billing unit (minimum 1 unit if quantity > 0)
        billing_units = math.ceil(quantity / billing_unit_size) if quantity > 0 else 0
        return billing_units * price_per_unit
    
    # Simple per-unit pricing (per_second, per_request)
    if "price_per_unit" in pricing:
        base_cost = pricing["price_per_unit"] * quantity
        
        # Apply multiplier if applicable
        multiplier_key = pricing.get("multiplier_field_key")
        if multiplier_key and params:
            if isinstance(multiplier_key, list):
                # Check any of the keys
                if any(params.get(k) for k in multiplier_key):
                    base_cost *= pricing.get("multiplier_value", 1)
            elif params.get(multiplier_key):
                base_cost *= pricing.get("multiplier_value", 1)
        
        return base_cost
    
    # Tiered pricing
    if "tier" in pricing:
        tier_field = pricing.get("tier_field_key", "")
        tier_value = str(params.get(tier_field, "")) if params else ""
        tier_prices = pricing["tier"]
        
        if tier_value in tier_prices:
            return tier_prices[tier_value] * quantity
        
        # Default to first tier
        if tier_prices:
            first_tier = next(iter(tier_prices.values()))
            return first_tier * quantity
    
    return 0.0


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
    
    for param in model.get("parameters", []):
        if isinstance(param, dict):
            if "key" in param and "default" in param:
                defaults[param["key"]] = param["default"]
            elif "default_values" in param:
                # Merge default_values dict
                defaults.update(param["default_values"])
    
    return defaults


def get_model_config(model_id: str) -> Optional[dict[str, Any]]:
    """
    Get the full model configuration for provider use.
    
    Args:
        model_id: The model identifier
        
    Returns:
        Full model configuration dict or None
    """
    return get_model(model_id)
