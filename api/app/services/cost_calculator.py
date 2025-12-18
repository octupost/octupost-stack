"""
Cost Calculator Service

Calculates generation costs based on pricing configuration stored in model_configs.

Formula:
Final Cost = base_unit_price
           × units (duration/1)
           × Π(parameter_multipliers)
           × markup_multiplier
"""

import math
from typing import Any, Optional, TypedDict
from dataclasses import dataclass


# =============================================================================
# Types
# =============================================================================

class ParameterMultipliers(TypedDict, total=False):
    """Maps parameter names to their option value multipliers."""
    pass  # Dynamic keys


class BasePriceSelector(TypedDict):
    """Base price selector configuration."""
    paramKey: str
    priceMap: dict[str, float]


class PricingConfig(TypedDict, total=False):
    """Pricing configuration structure from database."""
    base_unit_price: float
    base_unit: str
    markup_multiplier: float
    unit_bucket_size: int  # Minimum billable unit size (rounds up to nearest multiple)
    parameter_multipliers: dict[str, dict[str, float]]
    base_price_selector: BasePriceSelector  # Optional base price selector


@dataclass
class BasePriceSource:
    """Source of the base price if from a selector."""
    param: str
    value: str


@dataclass
class CostBreakdown:
    """Detailed cost calculation result."""
    base_cost: float
    effective_base_unit_price: float
    base_price_source: Optional[BasePriceSource]  # Set if base price came from selector
    parameter_multiplier: float
    applied_multipliers: list[dict[str, Any]]
    markup_multiplier: float
    total_cost_usd: float
    total_credits: int
    is_estimable: bool  # False for compute_second pricing without override


# =============================================================================
# Constants
# =============================================================================

# Conversion rate: 1 USD = 100 credits
USD_TO_CREDITS = 100


class PricingConfigRequiredError(Exception):
    """Raised when pricing_config is required but missing or invalid."""
    pass


# =============================================================================
# Core Calculation Functions
# =============================================================================

def round_to_bucket(units: float, bucket_size: int) -> float:
    """
    Round units up to the nearest bucket size.
    
    Args:
        units: The actual number of units
        bucket_size: The minimum billable unit size
        
    Returns:
        Units rounded up to nearest bucket multiple
        
    Examples:
        round_to_bucket(500, 1000) → 1000
        round_to_bucket(1001, 1000) → 2000
        round_to_bucket(3, 5) → 5
        round_to_bucket(7, 5) → 10
    """
    if bucket_size <= 1:
        return units
    return math.ceil(units / bucket_size) * bucket_size


def get_parameter_multiplier(
    pricing_config: PricingConfig,
    param_key: str,
    value: Any
) -> float:
    """
    Get the multiplier for a specific parameter value.
    
    Returns 1.0 if the parameter doesn't have a multiplier configured
    (meaning it has no effect on price).
    
    Args:
        pricing_config: The pricing configuration (REQUIRED)
        param_key: The parameter name
        value: The selected value
        
    Returns:
        The multiplier (1.0 if parameter has no multiplier configured)
    """
    if value is None:
        return 1.0
    
    param_multipliers = pricing_config.get("parameter_multipliers", {})
    if not param_multipliers or param_key not in param_multipliers:
        return 1.0
    
    # Convert value to string for lookup
    value_str = str(value).lower() if isinstance(value, bool) else str(value)
    return param_multipliers[param_key].get(value_str, 1.0)


def calculate_parameter_multipliers(
    pricing_config: PricingConfig,
    params: dict[str, Any]
) -> tuple[float, list[dict[str, Any]]]:
    """
    Calculate the total multiplier from all parameter values.
    
    Args:
        pricing_config: The pricing configuration (REQUIRED)
        params: Generation parameters
        
    Returns:
        Tuple of (total_multiplier, breakdown_list)
    """
    param_multipliers = pricing_config.get("parameter_multipliers", {})
    if not param_multipliers:
        return 1.0, []
    
    total = 1.0
    breakdown = []
    
    for param_key, multipliers in param_multipliers.items():
        value = params.get(param_key)
        if value is None:
            continue
        
        value_str = str(value).lower() if isinstance(value, bool) else str(value)
        multiplier = multipliers.get(value_str)
        
        if multiplier is not None and multiplier != 1.0:
            total *= multiplier
            breakdown.append({
                "param": param_key,
                "value": value_str,
                "multiplier": multiplier
            })
    
    return total, breakdown


def is_estimable_pricing_unit(pricing_config: PricingConfig) -> bool:
    """
    Check if the pricing unit type is estimable before generation.
    
    Some units like "compute_second" (GPU time) are only known after
    generation completes, so we cannot estimate cost upfront.
    
    Args:
        pricing_config: The pricing configuration (REQUIRED)
        
    Returns:
        True if cost can be estimated before generation
    """
    base_unit = pricing_config.get("base_unit", "generation").lower()
    
    # Compute seconds = GPU processing time, NOT estimable
    if base_unit in ("compute_second", "compute_seconds"):
        return False
    
    return True


def get_effective_base_unit_price(
    pricing_config: PricingConfig,
    params: dict[str, Any]
) -> tuple[float, Optional[BasePriceSource]]:
    """
    Get the effective base unit price, checking base_price_selector first.
    
    If a base_price_selector is configured and the parameter value is found,
    returns that price. Otherwise, returns the default base_unit_price.
    
    Args:
        pricing_config: The pricing configuration
        params: Generation parameters
        
    Returns:
        Tuple of (effective_price, source) where source is set if selector was used
    """
    selector = pricing_config.get("base_price_selector")
    default_price = pricing_config.get("base_unit_price", 0.0)
    
    # If no selector configured, use default base_unit_price
    if not selector:
        return default_price, None
    
    param_key = selector.get("paramKey")
    price_map = selector.get("priceMap", {})
    
    if not param_key:
        return default_price, None
    
    # Look up the parameter value
    param_value = params.get(param_key)
    if param_value is None:
        # Parameter not set - use default
        return default_price, None
    
    # Look up the price for this value
    value_str = str(param_value)
    selector_price = price_map.get(value_str)
    
    if selector_price is not None:
        # Found price in selector
        return selector_price, BasePriceSource(param=param_key, value=value_str)
    
    # Value not found in selector - use default
    return default_price, None


def calculate_units(
    pricing_config: PricingConfig,
    params: dict[str, Any],
    override_duration: Optional[float] = None
) -> Optional[float]:
    """
    Calculate the number of units based on pricing unit type.
    
    NO FALLBACKS - requires explicit unit_source_param for duration/character pricing.
    
    Args:
        pricing_config: The pricing configuration (REQUIRED)
        params: Generation parameters
        override_duration: Optional duration override
        
    Returns:
        Number of units to multiply base price by, or None if not estimable
        
    Raises:
        PricingConfigRequiredError: If unit_source_param is missing for unit-based pricing
    """
    base_unit = pricing_config.get("base_unit", "generation").lower()
    unit_source_param = pricing_config.get("unit_source_param")
    
    # Compute seconds (GPU time) - NOT estimable before generation
    # This is different from video duration!
    if base_unit in ("compute_second", "compute_seconds"):
        # If we have an override (e.g., from completed generation), use it
        if override_duration is not None:
            return override_duration
        # Otherwise, we cannot estimate
        return None
    
    # Duration-based units (VIDEO seconds, not GPU time)
    if base_unit in ("second", "seconds"):
        if override_duration is not None:
            return override_duration
        
        # NO FALLBACK: Require explicit unit_source_param
        if not unit_source_param:
            raise PricingConfigRequiredError(
                f"unit_source_param is required for base_unit='{base_unit}'. "
                "Please set unit_source_param in pricing_config (e.g., 'duration', 'num_seconds')."
            )
        
        duration = params.get(unit_source_param)
        if duration is None:
            # Parameter not provided - use default of 1
            return 1.0
        return float(duration)
    
    # Per-generation pricing (fixed cost)
    if base_unit in ("generation", "generations", "request"):
        return 1.0
    
    # Character-based pricing (for TTS)
    if base_unit in ("character", "characters"):
        # NO FALLBACK: Require explicit unit_source_param
        if not unit_source_param:
            raise PricingConfigRequiredError(
                f"unit_source_param is required for base_unit='{base_unit}'. "
                "Please set unit_source_param in pricing_config (e.g., 'text', 'script')."
            )
        
        text = params.get(unit_source_param, "")
        return float(len(text)) if text else 1.0
    
    # Unknown base_unit - raise error instead of defaulting
    raise PricingConfigRequiredError(
        f"Unknown base_unit: '{base_unit}'. "
        "Valid values: generation, second, compute_second, character."
    )


def calculate_cost_breakdown(
    pricing_config: PricingConfig,
    params: dict[str, Any],
    override_duration: Optional[float] = None
) -> CostBreakdown:
    """
    Calculate the full cost with detailed breakdown.
    
    NO FALLBACKS - pricing_config is REQUIRED.
    
    Args:
        pricing_config: The pricing configuration (REQUIRED)
        params: Generation parameters
        override_duration: Optional duration override
        
    Returns:
        CostBreakdown with detailed calculation results.
        Check `is_estimable` to see if the cost is reliable.
        
    Raises:
        PricingConfigRequiredError: If pricing_config is invalid
    """
    # Validate required fields
    if pricing_config.get("base_unit_price") is None:
        raise PricingConfigRequiredError("base_unit_price is required in pricing_config")
    if not pricing_config.get("base_unit"):
        raise PricingConfigRequiredError("base_unit is required in pricing_config")
    
    # Calculate units - may be None for compute_second pricing
    raw_units = calculate_units(pricing_config, params, override_duration)
    
    # If units is None, we can't estimate the cost (e.g., compute_second pricing)
    is_estimable = raw_units is not None
    
    # Apply bucket rounding if configured
    bucket_size = pricing_config.get("unit_bucket_size", 1)
    effective_units = round_to_bucket(raw_units, bucket_size) if raw_units is not None else 0.0
    
    # Get effective base price (from selector or default)
    effective_base_unit_price, base_price_source = get_effective_base_unit_price(pricing_config, params)
    base_cost = effective_base_unit_price * effective_units
    
    # Calculate parameter multipliers
    parameter_multiplier, breakdown = calculate_parameter_multipliers(pricing_config, params)
    
    # Get markup (default 1.0 is okay - no markup)
    markup_multiplier = pricing_config.get("markup_multiplier", 1.0)
    
    # Calculate final cost
    total_cost_usd = base_cost * parameter_multiplier * markup_multiplier
    total_credits = max(int(total_cost_usd * USD_TO_CREDITS + 0.5), 1) if is_estimable else 0
    
    return CostBreakdown(
        base_cost=base_cost,
        effective_base_unit_price=effective_base_unit_price,
        base_price_source=base_price_source,
        parameter_multiplier=parameter_multiplier,
        applied_multipliers=breakdown,
        markup_multiplier=markup_multiplier,
        total_cost_usd=total_cost_usd,
        total_credits=total_credits,
        is_estimable=is_estimable
    )


def calculate_cost(
    pricing_config: PricingConfig,
    params: dict[str, Any],
    override_duration: Optional[float] = None
) -> float:
    """
    Calculate cost in USD.
    
    NO FALLBACKS - pricing_config is REQUIRED.
    
    Args:
        pricing_config: The pricing configuration (REQUIRED)
        params: Generation parameters
        override_duration: Optional duration override
        
    Returns:
        Cost in USD
    """
    return calculate_cost_breakdown(pricing_config, params, override_duration).total_cost_usd


def calculate_credits(
    pricing_config: PricingConfig,
    params: dict[str, Any],
    override_duration: Optional[float] = None
) -> int:
    """
    Calculate cost in credits.
    
    NO FALLBACKS - pricing_config is REQUIRED.
    
    Args:
        pricing_config: The pricing configuration (REQUIRED)
        params: Generation parameters
        override_duration: Optional duration override
        
    Returns:
        Cost in credits (minimum 1)
    """
    return calculate_cost_breakdown(pricing_config, params, override_duration).total_credits


# =============================================================================
# Supabase Integration
# =============================================================================

async def get_pricing_config_for_model(endpoint: str) -> Optional[PricingConfig]:
    """
    Fetch pricing configuration for a model from the database.
    
    Args:
        endpoint: The model endpoint (e.g., "fal-ai/ltx-video")
        
    Returns:
        PricingConfig or None if not found
    """
    from .supabase_client import supabase_service
    
    client = supabase_service.client
    if not client:
        return None
    
    result = client.schema("octupost").from_("model_configs").select(
        "pricing_config"
    ).eq("endpoint", endpoint).execute()
    
    if result.data and len(result.data) > 0:
        return result.data[0].get("pricing_config")
    
    return None


async def calculate_credits_for_generation(
    endpoint: str,
    params: dict[str, Any],
    override_duration: Optional[float] = None
) -> int:
    """
    Calculate credits for a generation request using database pricing config.
    
    NO FALLBACKS - pricing_config must exist in database.
    
    Args:
        endpoint: The model endpoint
        params: Generation parameters
        override_duration: Optional duration override
        
    Returns:
        Credits needed (minimum 1)
        
    Raises:
        PricingConfigRequiredError: If pricing_config is missing
    """
    pricing_config = await get_pricing_config_for_model(endpoint)
    
    if not pricing_config:
        raise PricingConfigRequiredError(
            f"No pricing_config found for model '{endpoint}'. "
            "Please configure pricing in the admin panel."
        )
    
    return calculate_credits(pricing_config, params, override_duration)

