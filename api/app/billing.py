"""
Octupost Billing

Unified billing service for:
- Credit balance operations (get, deduct, refund)
- Cost calculation (pricing formulas)
- Stripe integration (subscriptions, checkouts)

This file consolidates:
- services/credit_service.py
- services/cost_calculator.py
- services/stripe_service.py
"""

import math
import stripe
from typing import Any, Optional, Literal
from dataclasses import dataclass
from datetime import datetime

from app.config import get_settings
from app.registry import USD_TO_CREDITS

settings = get_settings()
stripe.api_key = settings.stripe_secret_key


# ===========================================================================
# PLAN & PACKAGE CONFIGURATION
# ===========================================================================

PlanType = Literal["free", "pro", "elite"]
IntervalType = Literal["month", "year"]
PackageType = Literal["small", "medium", "large"]
TransactionType = Literal["subscription_grant", "purchase", "usage", "refund"]


@dataclass
class PlanConfig:
    """Subscription plan configuration."""
    monthly_credits: int
    price_id_monthly: Optional[str] = None
    price_id_yearly: Optional[str] = None


@dataclass
class CreditPackageConfig:
    """Credit package configuration."""
    credits: int
    price_id: str
    price_usd: int  # Price in cents


# Plan definitions
PLANS: dict[str, PlanConfig] = {
    "free": PlanConfig(
        monthly_credits=100,
        price_id_monthly=None,
        price_id_yearly=None,
    ),
    "pro": PlanConfig(
        monthly_credits=2000,
        price_id_monthly="price_1SdxrGBLueo7lEa2l69LAFvt",
        price_id_yearly="price_1SdxrGBLueo7lEa2W03xXEug",
    ),
    "elite": PlanConfig(
        monthly_credits=10000,
        price_id_monthly="price_1SdxrHBLueo7lEa2AaRBX1qY",
        price_id_yearly="price_1SdxrHBLueo7lEa2iHv3Y4aM",
    ),
}

# Credit package definitions
CREDIT_PACKAGES: dict[str, CreditPackageConfig] = {
    "small": CreditPackageConfig(
        credits=1000,
        price_id="price_1SdxrHBLueo7lEa2d2EILBUE",
        price_usd=1000,  # $10.00
    ),
    "medium": CreditPackageConfig(
        credits=5500,  # +10% bonus
        price_id="price_1SdxrIBLueo7lEa2QLGrSzZU",
        price_usd=5000,  # $50.00
    ),
    "large": CreditPackageConfig(
        credits=12000,  # +20% bonus
        price_id="price_1SdxrIBLueo7lEa2GZDRtb4X",
        price_usd=10000,  # $100.00
    ),
}


# ===========================================================================
# COST CALCULATOR TYPES
# ===========================================================================

@dataclass
class CostBreakdown:
    """Detailed cost calculation result."""
    base_cost: float
    effective_base_unit_price: float
    parameter_multiplier: float
    applied_multipliers: list[dict[str, Any]]
    markup_multiplier: float
    total_cost_usd: float
    total_credits: int


class PricingConfigRequiredError(Exception):
    """Raised when pricing_config is required but missing or invalid."""
    pass


# ===========================================================================
# CREDIT BALANCE TYPES
# ===========================================================================

@dataclass
class CreditBalanceDetail:
    """Detailed credit balance with monthly and extra breakdown."""
    total_balance: int
    monthly_balance: int
    extra_balance: int
    monthly_reset_at: Optional[datetime]


# ===========================================================================
# COST CALCULATION FUNCTIONS
# ===========================================================================

def round_to_bucket(units: float, bucket_size: int) -> float:
    """Round units up to the nearest bucket size."""
    if bucket_size <= 1:
        return units
    return math.ceil(units / bucket_size) * bucket_size


def get_parameter_multiplier(
    pricing_config: dict,
    param_key: str,
    value: Any
) -> float:
    """Get the multiplier for a specific parameter value."""
    if value is None:
        return 1.0

    param_multipliers = pricing_config.get("parameter_multipliers", {})
    if not param_multipliers or param_key not in param_multipliers:
        return 1.0

    value_str = str(value).lower() if isinstance(value, bool) else str(value)
    return param_multipliers[param_key].get(value_str, 1.0)


def calculate_parameter_multipliers(
    pricing_config: dict,
    params: dict[str, Any]
) -> tuple[float, list[dict[str, Any]]]:
    """Calculate the total multiplier from all parameter values."""
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


def get_effective_base_unit_price(
    pricing_config: dict,
    params: dict[str, Any]
) -> float:
    """Get the effective base unit price, checking selectors.

    NO FALLBACKS when selectors are configured - raises PricingConfigRequiredError if lookup fails.
    """
    default_price = pricing_config.get("base_unit_price", 0.0)

    # Check matrix selector first (takes precedence)
    matrix_selector = pricing_config.get("matrix_price_selector")
    if matrix_selector:
        param_keys = matrix_selector.get("paramKeys", [])
        price_matrix = matrix_selector.get("priceMatrix", {})
        separator = matrix_selector.get("separator", "|")

        if not param_keys:
            raise PricingConfigRequiredError(
                "matrix_price_selector is configured but paramKeys is empty."
            )
        if not price_matrix:
            raise PricingConfigRequiredError(
                "matrix_price_selector is configured but priceMatrix is empty."
            )

        key_parts = []
        for param_key in param_keys:
            param_value = params.get(param_key)
            if param_value is None:
                # NO FALLBACK: Required matrix param not provided
                raise PricingConfigRequiredError(
                    f"Matrix price selector requires parameter '{param_key}' but it was not provided. "
                    f"Required params: {param_keys}"
                )
            # Convert boolean to lowercase string for consistent lookup
            value_str = str(param_value).lower() if isinstance(param_value, bool) else str(param_value)
            key_parts.append(value_str)

        composite_key = separator.join(key_parts)
        matrix_price = price_matrix.get(composite_key)

        if matrix_price is None:
            # NO FALLBACK: No price configured for this combination
            raise PricingConfigRequiredError(
                f"No price configured for combination '{composite_key}'. "
                f"Available combinations: {list(price_matrix.keys())}"
            )

        return matrix_price

    # Check single-param selector
    selector = pricing_config.get("base_price_selector")
    if selector:
        param_key = selector.get("paramKey")
        price_map = selector.get("priceMap", {})

        if not param_key:
            raise PricingConfigRequiredError(
                "base_price_selector is configured but paramKey is missing."
            )
        if not price_map:
            raise PricingConfigRequiredError(
                "base_price_selector is configured but priceMap is empty."
            )

        param_value = params.get(param_key)
        if param_value is None:
            # NO FALLBACK: Required selector param not provided
            raise PricingConfigRequiredError(
                f"Base price selector requires parameter '{param_key}' but it was not provided."
            )

        value_str = str(param_value).lower() if isinstance(param_value, bool) else str(param_value)
        selector_price = price_map.get(value_str)

        if selector_price is None:
            # NO FALLBACK: Value not found in selector
            raise PricingConfigRequiredError(
                f"No price configured for '{param_key}={value_str}'. "
                f"Available values: {list(price_map.keys())}"
            )

        return selector_price

    # No selectors configured - use base_unit_price (this is the only acceptable fallback)
    return default_price


def calculate_units(
    pricing_config: dict,
    params: dict[str, Any],
    override_duration: Optional[float] = None
) -> float:
    """Calculate the number of units based on pricing unit type.

    NO FALLBACKS - raises PricingConfigRequiredError if required params are missing.

    Valid base_unit values: generation, second, character, megapixel
    """
    base_unit = pricing_config.get("base_unit", "generation").lower()
    unit_source_param = pricing_config.get("unit_source_param")

    if base_unit == "generation":
        return 1.0

    if base_unit == "second":
        if override_duration is not None:
            return override_duration
        if not unit_source_param:
            raise PricingConfigRequiredError(
                "unit_source_param is required for base_unit='second'."
            )
        duration = params.get(unit_source_param)
        if duration is None:
            # NO FALLBACK: Duration parameter is required
            raise PricingConfigRequiredError(
                f"Duration parameter '{unit_source_param}' is required but was not provided."
            )
        try:
            return float(duration)
        except (TypeError, ValueError) as e:
            raise PricingConfigRequiredError(
                f"Invalid duration value for '{unit_source_param}': {duration}. Error: {e}"
            )

    if base_unit == "character":
        if not unit_source_param:
            raise PricingConfigRequiredError(
                "unit_source_param is required for base_unit='character'."
            )
        text = params.get(unit_source_param)
        if text is None:
            # NO FALLBACK: Text parameter is required
            raise PricingConfigRequiredError(
                f"Text parameter '{unit_source_param}' is required but was not provided."
            )
        if not isinstance(text, str):
            raise PricingConfigRequiredError(
                f"Text parameter '{unit_source_param}' must be a string, got {type(text).__name__}."
            )
        if len(text) == 0:
            raise PricingConfigRequiredError(
                f"Text parameter '{unit_source_param}' cannot be empty."
            )
        return float(len(text))

    if base_unit == "megapixel":
        if not unit_source_param:
            raise PricingConfigRequiredError(
                "unit_source_param is required for base_unit='megapixel'."
            )
        value = params.get(unit_source_param)
        if value is None:
            # NO FALLBACK: Megapixel parameter is required
            raise PricingConfigRequiredError(
                f"Megapixel parameter '{unit_source_param}' is required but was not provided."
            )
        if isinstance(value, (int, float)):
            if value == 0:
                raise PricingConfigRequiredError(
                    f"Megapixel value for '{unit_source_param}' cannot be 0."
                )
            return float(value)
        if isinstance(value, dict) and "width" in value and "height" in value:
            return (value["width"] * value["height"]) / 1_000_000
        # NO FALLBACK: Unsupported value type
        raise PricingConfigRequiredError(
            f"Unsupported value type for megapixel parameter '{unit_source_param}': {type(value).__name__}. "
            "Expected number or dict with width/height."
        )

    raise PricingConfigRequiredError(
        f"Invalid base_unit: '{base_unit}'. Must be one of: generation, second, character, megapixel."
    )


def calculate_cost_breakdown(
    pricing_config: dict,
    params: dict[str, Any],
    override_duration: Optional[float] = None
) -> CostBreakdown:
    """Calculate the full cost with detailed breakdown."""
    if pricing_config.get("base_unit_price") is None:
        raise PricingConfigRequiredError("base_unit_price is required in pricing_config")
    if not pricing_config.get("base_unit"):
        raise PricingConfigRequiredError("base_unit is required in pricing_config")

    raw_units = calculate_units(pricing_config, params, override_duration)

    bucket_size = pricing_config.get("unit_bucket_size", 1)
    effective_units = round_to_bucket(raw_units, bucket_size)

    effective_base_unit_price = get_effective_base_unit_price(pricing_config, params)
    base_cost = effective_base_unit_price * effective_units

    parameter_multiplier, breakdown = calculate_parameter_multipliers(pricing_config, params)

    markup_multiplier = pricing_config.get("markup_multiplier", 1.0)

    total_cost_usd = base_cost * parameter_multiplier * markup_multiplier
    total_credits = max(int(total_cost_usd * USD_TO_CREDITS + 0.5), 1)

    return CostBreakdown(
        base_cost=base_cost,
        effective_base_unit_price=effective_base_unit_price,
        parameter_multiplier=parameter_multiplier,
        applied_multipliers=breakdown,
        markup_multiplier=markup_multiplier,
        total_cost_usd=total_cost_usd,
        total_credits=total_credits,
    )


def calculate_cost(
    pricing_config: dict,
    params: dict[str, Any],
    override_duration: Optional[float] = None
) -> float:
    """Calculate cost in USD."""
    return calculate_cost_breakdown(pricing_config, params, override_duration).total_cost_usd


def calculate_credits(
    pricing_config: dict,
    params: dict[str, Any],
    override_duration: Optional[float] = None
) -> int:
    """Calculate cost in credits."""
    return calculate_cost_breakdown(pricing_config, params, override_duration).total_credits


def get_pricing_config_for_model(endpoint: str) -> Optional[dict]:
    """Fetch pricing configuration for a model from registry.py (single source of truth).

    Checks both base-level pricing and mode-level pricing. If the endpoint matches
    a mode's outbound_schema.endpoint, uses that mode's pricing.
    """
    from app.registry import get_capabilities

    caps = get_capabilities(endpoint)
    if not caps:
        return None

    # First, check if endpoint matches a mode's endpoint and use that mode's pricing
    for mode_caps in caps.modes.values():
        if mode_caps.outbound_schema:
            mode_endpoint = mode_caps.outbound_schema.get("endpoint")
            if mode_endpoint == endpoint and mode_caps.pricing:
                return mode_caps.pricing.to_pricing_config()

    # Fall back to base-level pricing
    if not caps.pricing:
        return None

    return caps.pricing.to_pricing_config()


def calculate_credits_for_generation(
    endpoint: str,
    params: dict[str, Any],
    override_duration: Optional[float] = None
) -> int:
    """Calculate credits for a generation request using registry pricing config."""
    pricing_config = get_pricing_config_for_model(endpoint)

    if not pricing_config:
        raise PricingConfigRequiredError(
            f"No pricing_config found for model '{endpoint}'."
        )

    return calculate_credits(pricing_config, params, override_duration)


# ===========================================================================
# CREDIT SERVICE
# ===========================================================================

class DatabaseClientError(Exception):
    """Raised when database client is not available."""
    pass


class CreditService:
    """Service for credit balance operations."""

    def _get_client(self):
        """Get the Supabase client, raising error if unavailable."""
        from app.services.supabase_client import supabase_service

        client = supabase_service.client
        if not client:
            raise DatabaseClientError("Database client is not available. Please try again later.")
        return client

    async def get_balance(self, user_id: str) -> int:
        """Get current total credit balance for a user."""
        client = self._get_client()

        result = client.schema("stripe").rpc(
            "get_credit_balance",
            {"p_user_id": user_id}
        ).execute()

        return result.data or 0

    async def get_balance_detail(self, user_id: str) -> CreditBalanceDetail:
        """Get detailed credit balance breakdown for a user."""
        client = self._get_client()

        result = client.schema("stripe").rpc(
            "get_credit_balances_detail",
            {"p_user_id": user_id}
        ).execute()

        if result.data and len(result.data) > 0:
            data = result.data[0]
            return CreditBalanceDetail(
                total_balance=data.get("total_balance", 0),
                monthly_balance=data.get("monthly_balance", 0),
                extra_balance=data.get("extra_balance", 0),
                monthly_reset_at=data.get("monthly_reset_at")
            )

        return CreditBalanceDetail(
            total_balance=0,
            monthly_balance=0,
            extra_balance=0,
            monthly_reset_at=None
        )

    async def has_sufficient_credits(self, user_id: str, amount: int) -> bool:
        """Check if user has sufficient credits."""
        balance = await self.get_balance(user_id)
        return balance >= amount

    async def deduct_credits(
        self,
        user_id: str,
        amount: int,
        model_id: Optional[str] = None,
        job_id: Optional[str] = None,
        description: Optional[str] = None,
    ) -> bool:
        """Atomically deduct credits from a user's balance."""
        client = self._get_client()

        result = client.schema("stripe").rpc(
            "deduct_credits",
            {
                "p_user_id": user_id,
                "p_amount": amount,
                "p_model_id": model_id,
                "p_job_id": job_id,
                "p_description": description,
            }
        ).execute()

        return result.data is True

    async def add_credits(
        self,
        user_id: str,
        amount: int,
        type: TransactionType,
        description: Optional[str] = None,
        stripe_payment_id: Optional[str] = None,
    ) -> int:
        """Add credits to a user's balance."""
        client = self._get_client()

        result = client.schema("stripe").rpc(
            "add_credits",
            {
                "p_user_id": user_id,
                "p_amount": amount,
                "p_type": type,
                "p_description": description,
                "p_stripe_payment_id": stripe_payment_id,
            }
        ).execute()

        return result.data or 0

    async def refund_credits(
        self,
        user_id: str,
        amount: int,
        job_id: str,
        description: str = "Generation failed - credits refunded",
    ) -> int:
        """Refund credits for a failed generation."""
        client = self._get_client()

        result = client.schema("stripe").rpc(
            "refund_credits",
            {
                "p_user_id": user_id,
                "p_amount": amount,
                "p_job_id": job_id,
                "p_description": description,
            }
        ).execute()

        return result.data or 0

    async def grant_subscription_credits(
        self,
        user_id: str,
        plan: PlanType,
        stripe_subscription_id: Optional[str] = None,
    ) -> int:
        """Grant monthly credits for a subscription."""
        plan_config = PLANS.get(plan)
        if not plan_config:
            raise ValueError(f"Invalid plan: {plan}")

        credits = plan_config.monthly_credits
        description = f"{plan.title()} plan monthly credits"

        client = self._get_client()

        result = client.schema("stripe").rpc(
            "grant_subscription_credits",
            {
                "p_user_id": user_id,
                "p_amount": credits,
                "p_description": description,
                "p_stripe_subscription_id": stripe_subscription_id,
            }
        ).execute()

        return result.data or 0

    async def initialize_user_balance(self, user_id: str) -> None:
        """Initialize credit balance for a new user."""
        client = self._get_client()

        client.schema("stripe").table("credit_balances").upsert(
            {"user_id": user_id, "balance": 0},
            on_conflict="user_id",
        ).execute()

    async def get_transactions(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """Get credit transaction history for a user."""
        client = self._get_client()

        result = client.schema("stripe").table("credit_transactions") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()

        return result.data or []

    # =========================================================================
    # CREDIT RESERVATION METHODS
    # =========================================================================

    async def reserve_credits(
        self,
        user_id: str,
        estimated_amount: int,
        job_id: str,
        model_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Reserve credits for a generation job.

        Holds credits from the user's balance until the job completes.
        Returns reservation_id if successful, None if insufficient credits.

        Args:
            user_id: User's UUID
            estimated_amount: Estimated credits needed
            job_id: Associated job ID
            model_id: Optional model identifier

        Returns:
            Reservation UUID if successful, None if insufficient credits
        """
        client = self._get_client()

        result = client.schema("stripe").rpc(
            "reserve_credits",
            {
                "p_user_id": user_id,
                "p_estimated_amount": estimated_amount,
                "p_job_id": job_id,
                "p_model_id": model_id,
            }
        ).execute()

        # Returns UUID string or null
        return result.data if result.data else None

    async def settle_reservation(
        self,
        reservation_id: str,
        actual_amount: int,
    ) -> dict:
        """
        Settle a credit reservation with the actual cost.

        If actual_amount < reserved_amount: refund the excess
        If actual_amount > reserved_amount: charge the difference (if balance allows)
        If actual_amount == reserved_amount: no adjustment

        Args:
            reservation_id: The reservation UUID
            actual_amount: Actual credits used

        Returns:
            Dict with {refunded, charged_extra, final_cost, reserved_amount} or {error}
        """
        client = self._get_client()

        result = client.schema("stripe").rpc(
            "settle_reservation",
            {
                "p_reservation_id": reservation_id,
                "p_actual_amount": actual_amount,
            }
        ).execute()

        return result.data or {"error": "Settlement failed"}

    async def release_reservation(
        self,
        reservation_id: str,
        reason: str = "generation_failed",
    ) -> bool:
        """
        Release a credit reservation (full refund).

        Called when a generation fails and reserved credits should be returned.

        Args:
            reservation_id: The reservation UUID
            reason: Reason for release (for logging)

        Returns:
            True if released successfully, False otherwise
        """
        client = self._get_client()

        result = client.schema("stripe").rpc(
            "release_reservation",
            {
                "p_reservation_id": reservation_id,
                "p_reason": reason,
            }
        ).execute()

        return result.data is True


# ===========================================================================
# STRIPE SERVICE
# ===========================================================================

class StripeService:
    """Service for Stripe operations."""

    def get_plan_config(self, plan: PlanType) -> PlanConfig:
        """Get configuration for a plan."""
        return PLANS[plan]

    def get_package_config(self, package: PackageType) -> CreditPackageConfig:
        """Get configuration for a credit package."""
        return CREDIT_PACKAGES[package]

    async def create_customer(
        self,
        user_id: str,
        email: str,
        name: Optional[str] = None,
    ) -> str:
        """Create a Stripe customer for a user."""
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={"user_id": user_id},
        )
        return customer.id

    async def get_or_create_customer(
        self,
        user_id: str,
        email: str,
        existing_customer_id: Optional[str] = None,
    ) -> str:
        """Get existing or create new Stripe customer."""
        if existing_customer_id:
            try:
                customer = stripe.Customer.retrieve(existing_customer_id)
                if not getattr(customer, 'deleted', False):
                    return existing_customer_id
            except stripe.InvalidRequestError:
                pass

        return await self.create_customer(user_id, email)

    async def create_subscription_checkout(
        self,
        customer_id: str,
        plan: PlanType,
        interval: IntervalType,
        success_url: str,
        cancel_url: str,
    ) -> str:
        """Create a Stripe Checkout session for subscription."""
        plan_config = PLANS.get(plan)
        if not plan_config:
            raise ValueError(f"Invalid plan: {plan}")

        price_id = (
            plan_config.price_id_monthly if interval == "month"
            else plan_config.price_id_yearly
        )

        if not price_id:
            raise ValueError(f"Plan {plan} does not have a {interval}ly price")

        session = stripe.checkout.Session.create(
            customer=customer_id,
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"plan": plan, "interval": interval},
        )

        return session.url

    async def create_credits_checkout(
        self,
        customer_id: str,
        package: PackageType,
        success_url: str,
        cancel_url: str,
    ) -> str:
        """Create a Stripe Checkout session for one-time credit purchase."""
        package_config = CREDIT_PACKAGES.get(package)
        if not package_config:
            raise ValueError(f"Invalid package: {package}")

        session = stripe.checkout.Session.create(
            customer=customer_id,
            mode="payment",
            line_items=[{"price": package_config.price_id, "quantity": 1}],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "type": "credits",
                "package": package,
                "credits": str(package_config.credits),
            },
        )

        return session.url

    async def create_setup_checkout(
        self,
        customer_id: str,
        success_url: str,
        cancel_url: str,
    ) -> str:
        """Create a Stripe Checkout session for card setup."""
        session = stripe.checkout.Session.create(
            customer=customer_id,
            mode="setup",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"type": "setup", "plan": "free"},
        )

        return session.url

    async def create_portal_session(
        self,
        customer_id: str,
        return_url: str,
    ) -> str:
        """Create a Stripe Customer Portal session."""
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )

        return session.url

    def construct_webhook_event(
        self,
        payload: bytes,
        signature: str,
    ) -> stripe.Event:
        """Construct and verify a webhook event."""
        return stripe.Webhook.construct_event(
            payload,
            signature,
            settings.stripe_webhook_secret,
        )


# ===========================================================================
# SINGLETON INSTANCES
# ===========================================================================

credit_service = CreditService()
stripe_service = StripeService()
