"""
Parameter Transformer

Transforms parameters based on model's parameter definitions from model_configs.
Handles type conversion, key mapping, and special transformations like:
- Integer to string conversion (e.g., duration: 4 -> "4s")
- Duration to num_frames multiplication (e.g., duration * fps)
- Key renaming via mapping (including nested paths like "audio_url.url")
- Array vs indexed mapping for multiple images

Supports both old format (param_mappings, notes) and new labelKey format.
"""

from typing import Any, Optional


def _get_param_definitions(model_config: dict) -> dict[str, dict]:
    """
    Extract parameter definitions from model config, indexed by key.
    
    Args:
        model_config: Model configuration from model_configs table
        
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
        model_config: Model configuration from model_configs table
        
    Returns:
        Dictionary of default values to merge into request
    """
    defaults = {}
    for param in model_config.get("parameters", []):
        if isinstance(param, dict) and "default_values" in param:
            defaults.update(param["default_values"])
    return defaults


def _get_admin_defaults(model_config: dict) -> dict[str, Any]:
    """
    Extract admin-defined param_defaults from model_configs table.
    
    These are defaults set in the admin panel that apply to all parameters
    (especially hidden ones). They take precedence over schema defaults
    but are overridden by user input.
    
    Args:
        model_config: Model configuration from database
        
    Returns:
        Dictionary of admin-defined default values
    """
    return model_config.get("param_defaults", {})


def _set_nested_value(obj: dict, path: str, value: Any) -> None:
    """
    Set a value in a nested dictionary using dot notation path.
    
    Example: _set_nested_value({}, "audio_url.url", "http://...") 
             -> {"audio_url": {"url": "http://..."}}
    
    Args:
        obj: Dictionary to modify
        path: Dot-separated path (e.g., "audio_url.url")
        value: Value to set
    """
    keys = path.split(".")
    current = obj
    
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value


def _get_mapping_info(param_def: dict, model_config: dict) -> tuple[str, str, str]:
    """
    Get mapping information from a parameter definition.
    
    Supports both new labelKey format and old param_mappings format.
    
    Args:
        param_def: Parameter definition
        model_config: Model configuration
        
    Returns:
        Tuple of (mapping, mapping_type, notes)
    """
    key = param_def.get("key", "")
    
    # New format: mapping is directly in param_def
    if "mapping" in param_def:
        mapping = param_def["mapping"]
    else:
        # Old format: check param_mappings
        param_mappings = model_config.get("param_mappings", {})
        mapping_info = param_mappings.get(key, {})
        mapping = mapping_info.get("mapping", key)
    
    # Get mapping type (for type conversion)
    mapping_type = param_def.get("mapping_type", param_def.get("type", "string"))
    
    # Get notes for legacy transformation hints
    notes = param_def.get("notes", "")
    
    return mapping, mapping_type, notes


def _apply_transformations(
    value: Any, 
    param_def: dict,
    mapping: str, 
    mapping_type: str, 
    notes: str,
    model_config: dict
) -> Any:
    """
    Apply transformations to a parameter value.
    
    Supports both new multiplyByFps field and legacy notes-based transformations.
    
    Args:
        value: The input value
        param_def: The parameter definition
        mapping: The target parameter name
        mapping_type: The target type
        notes: Transformation hints (legacy)
        model_config: Model configuration
        
    Returns:
        Transformed value
    """
    # Handle duration to num_frames multiplication
    # New format: multiplyByFps field
    multiply_by_fps = param_def.get("multiplyByFps")
    if multiply_by_fps is not None and isinstance(value, (int, float)):
        return int(value * multiply_by_fps)
    
    # Legacy format: notes contain multiplication hint
    if "Multiply second by 30" in notes:
        if isinstance(value, (int, float)):
            return int(value * 30)
    
    # Check for FPS-based multiplication from model config
    if "Multiply second by" in notes:
        fps = model_config.get("fps", 30)
        if isinstance(value, (int, float)):
            return int(value * fps)
    
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


def _handle_array_mapping(
    result: dict,
    param_def: dict,
    values: list[Any],
    mapping: str
) -> None:
    """
    Handle mapping of array values (e.g., multiple images).
    
    Args:
        result: Result dictionary to modify
        param_def: Parameter definition
        values: List of values to map
        mapping: Base mapping key
    """
    mapping_type = param_def.get("mappingType", "array")
    
    if mapping_type == "indexed":
        # Map as separate indexed keys: image_1, image_2, etc.
        for i, val in enumerate(values, 1):
            result[f"{mapping}_{i}"] = val
    else:
        # Default: map as array
        if "." in mapping:
            _set_nested_value(result, mapping, values)
        else:
            result[mapping] = values


def transform_params(params: dict[str, Any], model_config: dict) -> dict[str, Any]:
    """
    Transform parameters based on model's parameter definitions.
    
    This handles:
    1. Type conversion based on mapping_type
    2. Key renaming based on mapping (including nested paths like "audio_url.url")
    3. Duration to num_frames multiplication (multiplyByFps or legacy notes)
    4. Array vs indexed mapping for multiple images (mappingType)
    5. Merging default_values (from parameters array)
    6. Merging param_defaults (from model_configs table - admin-defined)
    
    Priority order (later overrides earlier):
    1. Schema default_values (hidden config)
    2. Admin param_defaults (set in admin panel)
    3. User-provided params
    
    Supports both old format (param_mappings, notes) and new labelKey format.
    
    Args:
        params: Input parameters from frontend
        model_config: Model configuration from model_configs table
        
    Returns:
        Transformed parameters ready for the API
    """
    result = {}
    param_defs = _get_param_definitions(model_config)
    default_values = _get_default_values(model_config)
    admin_defaults = _get_admin_defaults(model_config)
    
    # Start with schema default_values (lowest priority)
    result.update(default_values)
    
    # Apply admin-defined defaults (these override schema defaults)
    # Admin defaults are for the raw parameter keys, not mapped names
    for key, value in admin_defaults.items():
        param_def = param_defs.get(key)
        if param_def and value is not None:
            mapping, mapping_type, notes = _get_mapping_info(param_def, model_config)
            transformed_value = _apply_transformations(
                value, param_def, mapping, mapping_type, notes, model_config
            )
            if "." in mapping:
                _set_nested_value(result, mapping, transformed_value)
            else:
                result[mapping] = transformed_value
        elif value is not None:
            # Unknown parameter key, apply as-is
            result[key] = value
    
    # Process each input parameter
    for key, value in params.items():
        if value is None:
            continue
            
        param_def = param_defs.get(key)
        
        if not param_def:
            # Unknown parameter, pass through as-is
            result[key] = value
            continue
        
        # Get mapping info (supports both old and new formats)
        mapping, mapping_type, notes = _get_mapping_info(param_def, model_config)
        
        # Handle array values (multiple images)
        if isinstance(value, list):
            _handle_array_mapping(result, param_def, value, mapping)
            continue
        
        # Apply transformations
        transformed_value = _apply_transformations(
            value, param_def, mapping, mapping_type, notes, model_config
        )
        
        # Handle nested mapping (e.g., "audio_url.url" -> {audio_url: {url: value}})
        if "." in mapping:
            _set_nested_value(result, mapping, transformed_value)
        else:
            result[mapping] = transformed_value
    
    # Apply defaults for missing parameters (from parameter definitions)
    for key, param_def in param_defs.items():
        mapping, mapping_type, notes = _get_mapping_info(param_def, model_config)
        
        # For nested mappings, check the root key
        root_key = mapping.split(".")[0] if "." in mapping else mapping
        
        if root_key not in result and "default" in param_def:
            default = param_def["default"]
            if default != "":  # Skip empty string defaults
                transformed_default = _apply_transformations(
                    default, param_def, mapping, mapping_type, notes, model_config
                )
                if "." in mapping:
                    _set_nested_value(result, mapping, transformed_default)
                else:
                    result[mapping] = transformed_default
    
    return result


def merge_defaults(params: dict[str, Any], model_config: dict) -> dict[str, Any]:
    """
    Merge default parameter values with provided parameters.
    
    Args:
        params: User-provided parameters
        model_config: Model configuration from model_configs table
        
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
        
        # Skip hidden params for required check (they use defaults)
        display_mode = param_def.get("displayMode", "")
        if display_mode == "hidden":
            continue
        
        if required and key not in params and not has_default:
            errors.append(f"Missing required parameter: {key}")
    
    # Validate values against accepted_values/enum/min/max
    for key, value in params.items():
        param_def = param_defs.get(key)
        if not param_def:
            continue
        
        # Check enum values
        enum_values = param_def.get("enum") or param_def.get("options")
        if enum_values is not None and value not in enum_values:
            errors.append(f"{key} must be one of: {enum_values}")
            continue
        
        # Check min/max (new format)
        min_val = param_def.get("min") or param_def.get("minimum")
        max_val = param_def.get("max") or param_def.get("maximum")
        
        if min_val is not None and isinstance(value, (int, float)) and value < min_val:
            errors.append(f"{key} must be >= {min_val}")
        if max_val is not None and isinstance(value, (int, float)) and value > max_val:
            errors.append(f"{key} must be <= {max_val}")
        
        # Legacy: Check accepted_values
        accepted = param_def.get("accepted_values")
        if accepted is not None:
            if isinstance(accepted, list):
                if value not in accepted:
                    errors.append(f"{key} must be one of: {accepted}")
            elif isinstance(accepted, dict):
                min_val = accepted.get("min_duration") or accepted.get("min_speed") or accepted.get("min")
                max_val = accepted.get("max_duration") or accepted.get("max_speed") or accepted.get("max")
                
                if min_val is not None and isinstance(value, (int, float)) and value < min_val:
                    errors.append(f"{key} must be >= {min_val}")
                if max_val is not None and isinstance(value, (int, float)) and value > max_val:
                    errors.append(f"{key} must be <= {max_val}")
    
    if errors:
        return {}, errors
    
    # Transform parameters
    transformed = transform_params(params, model_config)
    return transformed, []


def get_visible_params(model_config: dict) -> list[dict]:
    """
    Get parameters that should be visible in the UI.
    
    Supports both new displayMode format and legacy hidden_params array.
    
    Args:
        model_config: Model configuration
        
    Returns:
        List of visible parameter definitions
    """
    params = model_config.get("parameters", [])
    hidden_params = set(model_config.get("hidden_params", []))
    
    visible = []
    for param in params:
        if not isinstance(param, dict) or "key" not in param:
            continue
        
        # New format: check displayMode
        display_mode = param.get("displayMode", "")
        if display_mode == "hidden":
            continue
        
        # Legacy format: check hidden_params array
        if param["key"] in hidden_params:
            continue
        
        visible.append(param)
    
    return visible


def get_params_by_display_mode(model_config: dict) -> dict[str, list[dict]]:
    """
    Group parameters by their display mode.
    
    Args:
        model_config: Model configuration
        
    Returns:
        Dictionary with keys: source, primary, inline, menu, hidden
    """
    params = model_config.get("parameters", [])
    inline_params = set(model_config.get("inline_params", []))
    hidden_params = set(model_config.get("hidden_params", []))
    
    result = {
        "source": [],
        "primary": [],
        "inline": [],
        "menu": [],
        "hidden": [],
    }
    
    for param in params:
        if not isinstance(param, dict) or "key" not in param:
            continue
        
        key = param["key"]
        
        # New format: use displayMode directly
        if "displayMode" in param:
            mode = param["displayMode"]
            if mode in result:
                result[mode].append(param)
            else:
                result["menu"].append(param)
            continue
        
        # Legacy format: infer from inline_params/hidden_params
        if key in hidden_params:
            result["hidden"].append(param)
        elif key in inline_params:
            result["inline"].append(param)
        elif key in ("prompt", "negative_prompt", "text", "script"):
            result["primary"].append(param)
        else:
            result["menu"].append(param)
    
    return result
