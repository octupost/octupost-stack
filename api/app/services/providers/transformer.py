"""
Parameter Transformer

Transforms parameters based on model's parameter definitions from provider.json.
Handles type conversion, key mapping, and special transformations like:
- Integer to string conversion (e.g., duration: 4 -> "4s")
- Duration to num_frames multiplication (e.g., duration * 30)
- Key renaming (e.g., "duration" -> "num_frames")
"""

from typing import Any, Optional


def _get_param_definitions(model_config: dict) -> dict[str, dict]:
    """
    Extract parameter definitions from model config, indexed by key.
    
    Args:
        model_config: Model configuration from provider.json
        
    Returns:
        Dictionary mapping parameter keys to their definitions
    """
    param_defs = {}
    for param in model_config.get("parameters", []):
        if isinstance(param, dict) and "key" in param:
            param_defs[param["key"]] = param
    return param_defs


def _get_default_values(model_config: dict) -> dict[str, Any]:
    """
    Extract default_values from the model's parameters list.
    
    Args:
        model_config: Model configuration from provider.json
        
    Returns:
        Dictionary of default values to merge into request
    """
    defaults = {}
    for param in model_config.get("parameters", []):
        if isinstance(param, dict) and "default_values" in param:
            defaults.update(param["default_values"])
    return defaults


def transform_params(params: dict[str, Any], model_config: dict) -> dict[str, Any]:
    """
    Transform parameters based on model's parameter definitions.
    
    This handles:
    1. Type conversion based on mapping_type
    2. Special transformations from notes (e.g., "Add s at the end")
    3. Key renaming based on mapping
    4. Duration to num_frames multiplication
    5. Merging default_values
    
    Args:
        params: Input parameters from frontend
        model_config: Model configuration from provider.json
        
    Returns:
        Transformed parameters ready for the API
    """
    result = {}
    param_defs = _get_param_definitions(model_config)
    default_values = _get_default_values(model_config)
    
    # Start with default values
    result.update(default_values)
    
    # Process each input parameter
    for key, value in params.items():
        if value is None:
            continue
            
        param_def = param_defs.get(key)
        
        if not param_def:
            # Unknown parameter, pass through as-is
            result[key] = value
            continue
        
        # Get mapping info
        mapping = param_def.get("mapping", key)
        mapping_type = param_def.get("mapping_type", param_def.get("type", "string"))
        notes = param_def.get("notes", "")
        
        # Apply transformations based on notes
        transformed_value = _apply_transformations(value, mapping, mapping_type, notes)
        
        # Store with the mapped key
        result[mapping] = transformed_value
    
    # Apply defaults for missing required parameters
    for key, param_def in param_defs.items():
        mapping = param_def.get("mapping", key)
        if mapping not in result and "default" in param_def:
            default = param_def["default"]
            if default != "":  # Skip empty string defaults
                mapping_type = param_def.get("mapping_type", param_def.get("type", "string"))
                notes = param_def.get("notes", "")
                result[mapping] = _apply_transformations(default, mapping, mapping_type, notes)
    
    return result


def _apply_transformations(
    value: Any, 
    mapping: str, 
    mapping_type: str, 
    notes: str
) -> Any:
    """
    Apply transformations to a parameter value.
    
    Args:
        value: The input value
        mapping: The target parameter name
        mapping_type: The target type
        notes: Transformation hints from provider.json
        
    Returns:
        Transformed value
    """
    # Handle duration to num_frames multiplication FIRST (before type conversion)
    # Notes: "Multiply second by 30 to get the number of frames"
    if "Multiply second by 30" in notes:
        if isinstance(value, (int, float)):
            value = int(value * 30)
            # After multiplication, return early since mapping_type is integer
            return value
    
    # Handle type conversion
    if mapping_type == "string":
        if not isinstance(value, str):
            # Check for suffix requirement
            # Notes: "Add s at the end of the duration"
            if "Add s at the end" in notes:
                return f"{value}s"
            else:
                return str(value)
    
    elif mapping_type == "integer":
        if isinstance(value, str):
            # Try to parse string to int
            try:
                return int(value.rstrip('s'))  # Remove 's' suffix if present
            except ValueError:
                return value
        elif isinstance(value, float):
            return int(value)
    
    elif mapping_type == "float":
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return value
        elif isinstance(value, int):
            return float(value)
    
    elif mapping_type == "boolean":
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes")
        elif isinstance(value, int):
            return value != 0
    
    return value


def merge_defaults(params: dict[str, Any], model_config: dict) -> dict[str, Any]:
    """
    Merge default parameter values with provided parameters.
    
    Args:
        params: User-provided parameters
        model_config: Model configuration from provider.json
        
    Returns:
        Merged parameters (user params take precedence)
    """
    param_defs = _get_param_definitions(model_config)
    default_values = _get_default_values(model_config)
    
    result = {}
    
    # Add parameter defaults
    for key, param_def in param_defs.items():
        if "default" in param_def and param_def["default"] != "":
            result[key] = param_def["default"]
    
    # Add default_values
    result.update(default_values)
    
    # User params take precedence
    result.update(params)
    
    return result


def validate_and_transform(
    params: dict[str, Any], 
    model_config: dict
) -> tuple[dict[str, Any], list[str]]:
    """
    Validate parameters and transform them in one pass.
    
    Args:
        params: Input parameters
        model_config: Model configuration
        
    Returns:
        Tuple of (transformed_params, errors)
    """
    errors = []
    param_defs = _get_param_definitions(model_config)
    
    # Check required parameters
    for key, param_def in param_defs.items():
        required = param_def.get("required", False)
        has_default = "default" in param_def and param_def["default"] != ""
        
        if required and key not in params and not has_default:
            errors.append(f"Missing required parameter: {key}")
    
    # Validate values against accepted_values
    for key, value in params.items():
        param_def = param_defs.get(key)
        if not param_def:
            continue
        
        accepted = param_def.get("accepted_values")
        if accepted is None:
            continue
        
        if isinstance(accepted, list):
            if value not in accepted:
                errors.append(f"{key} must be one of: {accepted}")
        elif isinstance(accepted, dict):
            min_val = accepted.get("min_duration") or accepted.get("min_speed")
            max_val = accepted.get("max_duration") or accepted.get("max_speed")
            
            if min_val is not None and isinstance(value, (int, float)) and value < min_val:
                errors.append(f"{key} must be >= {min_val}")
            if max_val is not None and isinstance(value, (int, float)) and value > max_val:
                errors.append(f"{key} must be <= {max_val}")
    
    if errors:
        return {}, errors
    
    # Transform parameters
    transformed = transform_params(params, model_config)
    return transformed, []

