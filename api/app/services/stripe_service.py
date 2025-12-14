"""
Stripe Service

Handles Stripe integration for subscriptions and one-time credit purchases.
Uses Stripe SDK for checkout sessions, customer management, and webhooks.
"""

import stripe
from typing import Optional, Literal
from dataclasses import dataclass

from app.config import get_settings

settings = get_settings()
stripe.api_key = settings.stripe_secret_key


# =============================================================================
# Plan & Package Configuration
# =============================================================================

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
        price_id_monthly=None,  # Free plan has no Stripe price
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

PlanType = Literal["free", "pro", "elite"]
IntervalType = Literal["month", "year"]
PackageType = Literal["small", "medium", "large"]


# =============================================================================
# Stripe Service Class
# =============================================================================

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
        """
        Create a Stripe customer for a user.
        
        Args:
            user_id: Supabase user ID (stored in metadata)
            email: Customer email
            name: Optional customer name
            
        Returns:
            Stripe customer ID
        """
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
        """
        Get existing or create new Stripe customer.
        
        Args:
            user_id: Supabase user ID
            email: Customer email
            existing_customer_id: Existing Stripe customer ID if known
            
        Returns:
            Stripe customer ID
        """
        if existing_customer_id:
            try:
                customer = stripe.Customer.retrieve(existing_customer_id)
                # Check if customer is deleted (SDK v14+ compatibility)
                if not getattr(customer, 'deleted', False):
                    return existing_customer_id
            except stripe.InvalidRequestError:
                pass  # Customer not found, create new one
        
        return await self.create_customer(user_id, email)

    async def create_subscription_checkout(
        self,
        customer_id: str,
        plan: PlanType,
        interval: IntervalType,
        success_url: str,
        cancel_url: str,
    ) -> str:
        """
        Create a Stripe Checkout session for subscription.
        
        Args:
            customer_id: Stripe customer ID
            plan: Plan type (pro or elite)
            interval: Billing interval (month or year)
            success_url: URL to redirect on success
            cancel_url: URL to redirect on cancel
            
        Returns:
            Checkout session URL
        """
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
        """
        Create a Stripe Checkout session for one-time credit purchase.
        
        Args:
            customer_id: Stripe customer ID
            package: Credit package (small, medium, large)
            success_url: URL to redirect on success
            cancel_url: URL to redirect on cancel
            
        Returns:
            Checkout session URL
        """
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
        """
        Create a Stripe Checkout session for card setup (free plan).
        
        This is used for free tier users who need to add a card.
        
        Args:
            customer_id: Stripe customer ID
            success_url: URL to redirect on success
            cancel_url: URL to redirect on cancel
            
        Returns:
            Checkout session URL
        """
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
        """
        Create a Stripe Customer Portal session.
        
        Allows customers to manage their subscription and payment methods.
        
        Args:
            customer_id: Stripe customer ID
            return_url: URL to redirect when leaving portal
            
        Returns:
            Portal session URL
        """
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
        """
        Construct and verify a webhook event.
        
        Args:
            payload: Raw request body
            signature: Stripe-Signature header value
            
        Returns:
            Verified Stripe event
            
        Raises:
            stripe.error.SignatureVerificationError: If signature is invalid
        """
        return stripe.Webhook.construct_event(
            payload,
            signature,
            settings.stripe_webhook_secret,
        )

    async def cancel_subscription(
        self,
        subscription_id: str,
        at_period_end: bool = True,
    ) -> None:
        """
        Cancel a subscription.
        
        Args:
            subscription_id: Stripe subscription ID
            at_period_end: If True, cancel at end of current period
        """
        if at_period_end:
            stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True,
            )
        else:
            stripe.Subscription.cancel(subscription_id)

    async def get_subscription(
        self,
        subscription_id: str,
    ) -> stripe.Subscription:
        """
        Get subscription details.
        
        Args:
            subscription_id: Stripe subscription ID
            
        Returns:
            Stripe Subscription object
        """
        return stripe.Subscription.retrieve(subscription_id)


# Singleton instance
stripe_service = StripeService()

