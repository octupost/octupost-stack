"""
Billing Routes

Handles Stripe checkout sessions, webhooks, and credit operations.
"""

from typing import Optional, Literal
from fastapi import APIRouter, Request, Header, HTTPException
from pydantic import BaseModel

from app.services.stripe_service import (
    stripe_service,
    PLANS,
    CREDIT_PACKAGES,
    PlanType,
    IntervalType,
    PackageType,
)
from app.services.credit_service import credit_service
from app.services.supabase_client import supabase_service

router = APIRouter()


# =============================================================================
# Request/Response Models
# =============================================================================

class SubscriptionCheckoutRequest(BaseModel):
    """Request body for subscription checkout."""
    plan: PlanType
    interval: IntervalType
    success_url: str
    cancel_url: str


class CreditsCheckoutRequest(BaseModel):
    """Request body for credits checkout."""
    package: PackageType
    success_url: str
    cancel_url: str


class SetupCheckoutRequest(BaseModel):
    """Request body for card setup checkout (free plan)."""
    success_url: str
    cancel_url: str


class PortalRequest(BaseModel):
    """Request body for customer portal."""
    return_url: str


class CheckoutResponse(BaseModel):
    """Response with checkout URL."""
    url: str


class BalanceResponse(BaseModel):
    """Response with credit balance (backwards compatible)."""
    balance: int


class BalanceDetailResponse(BaseModel):
    """Response with detailed credit balance breakdown."""
    total_balance: int
    monthly_balance: int  # Subscription credits (reset each billing cycle)
    extra_balance: int    # Purchased credits (never expire)
    monthly_reset_at: Optional[str]


class SubscriptionResponse(BaseModel):
    """Response with subscription info."""
    plan: str
    status: str
    stripe_customer_id: Optional[str]
    current_period_end: Optional[str]


class PlansResponse(BaseModel):
    """Response with available plans."""
    plans: dict


class PackagesResponse(BaseModel):
    """Response with available credit packages."""
    packages: dict


# =============================================================================
# Checkout Endpoints
# =============================================================================

@router.post("/checkout/subscription", response_model=CheckoutResponse)
async def create_subscription_checkout(
    request: SubscriptionCheckoutRequest,
    x_user_id: str = Header(..., alias="X-User-Id"),
    x_user_email: str = Header(..., alias="X-User-Email"),
):
    """
    Create a Stripe Checkout session for subscription.
    
    Headers:
        X-User-Id: Supabase user ID
        X-User-Email: User email
    """
    # Get or create Stripe customer
    subscription = await _get_user_subscription(x_user_id)
    customer_id = subscription.get("stripe_customer_id") if subscription else None
    
    customer_id = await stripe_service.get_or_create_customer(
        user_id=x_user_id,
        email=x_user_email,
        existing_customer_id=customer_id,
    )
    
    # Ensure subscription record exists
    await _ensure_subscription_record(x_user_id, customer_id)
    
    # Create checkout session
    url = await stripe_service.create_subscription_checkout(
        customer_id=customer_id,
        plan=request.plan,
        interval=request.interval,
        success_url=request.success_url,
        cancel_url=request.cancel_url,
    )
    
    return CheckoutResponse(url=url)


@router.post("/checkout/credits", response_model=CheckoutResponse)
async def create_credits_checkout(
    request: CreditsCheckoutRequest,
    x_user_id: str = Header(..., alias="X-User-Id"),
    x_user_email: str = Header(..., alias="X-User-Email"),
):
    """
    Create a Stripe Checkout session for one-time credit purchase.
    
    Headers:
        X-User-Id: Supabase user ID
        X-User-Email: User email
    """
    # Get or create Stripe customer
    subscription = await _get_user_subscription(x_user_id)
    customer_id = subscription.get("stripe_customer_id") if subscription else None
    
    customer_id = await stripe_service.get_or_create_customer(
        user_id=x_user_id,
        email=x_user_email,
        existing_customer_id=customer_id,
    )
    
    # Ensure subscription record exists
    await _ensure_subscription_record(x_user_id, customer_id)
    
    # Create checkout session
    url = await stripe_service.create_credits_checkout(
        customer_id=customer_id,
        package=request.package,
        success_url=request.success_url,
        cancel_url=request.cancel_url,
    )
    
    return CheckoutResponse(url=url)


@router.post("/checkout/setup", response_model=CheckoutResponse)
async def create_setup_checkout(
    request: SetupCheckoutRequest,
    x_user_id: str = Header(..., alias="X-User-Id"),
    x_user_email: str = Header(..., alias="X-User-Email"),
):
    """
    Create a Stripe Checkout session for card setup (free plan).
    
    This is used for users who want to use the free tier but
    need to add a card on file first.
    
    Headers:
        X-User-Id: Supabase user ID
        X-User-Email: User email
    """
    # Get or create Stripe customer
    subscription = await _get_user_subscription(x_user_id)
    customer_id = subscription.get("stripe_customer_id") if subscription else None
    
    customer_id = await stripe_service.get_or_create_customer(
        user_id=x_user_id,
        email=x_user_email,
        existing_customer_id=customer_id,
    )
    
    # Ensure subscription record exists
    await _ensure_subscription_record(x_user_id, customer_id)
    
    # Create setup session
    url = await stripe_service.create_setup_checkout(
        customer_id=customer_id,
        success_url=request.success_url,
        cancel_url=request.cancel_url,
    )
    
    return CheckoutResponse(url=url)


@router.post("/portal", response_model=CheckoutResponse)
async def create_portal_session(
    request: PortalRequest,
    x_user_id: str = Header(..., alias="X-User-Id"),
):
    """
    Create a Stripe Customer Portal session.
    
    Allows users to manage their subscription and payment methods.
    
    Headers:
        X-User-Id: Supabase user ID
    """
    subscription = await _get_user_subscription(x_user_id)
    if not subscription or not subscription.get("stripe_customer_id"):
        raise HTTPException(status_code=404, detail="No subscription found")
    
    url = await stripe_service.create_portal_session(
        customer_id=subscription["stripe_customer_id"],
        return_url=request.return_url,
    )
    
    return CheckoutResponse(url=url)


# =============================================================================
# Balance & Subscription Endpoints
# =============================================================================

@router.get("/balance", response_model=BalanceResponse)
async def get_credit_balance(
    x_user_id: str = Header(..., alias="X-User-Id"),
):
    """
    Get current total credit balance for the user.
    
    For detailed breakdown (monthly vs extra), use /balance/detail
    
    Headers:
        X-User-Id: Supabase user ID
    """
    balance = await credit_service.get_balance(x_user_id)
    return BalanceResponse(balance=balance)


@router.get("/balance/detail", response_model=BalanceDetailResponse)
async def get_credit_balance_detail(
    x_user_id: str = Header(..., alias="X-User-Id"),
):
    """
    Get detailed credit balance breakdown for the user.
    
    Returns:
        - total_balance: Sum of monthly + extra credits
        - monthly_balance: Subscription credits (reset each billing cycle)
        - extra_balance: Purchased credits (never expire, use after monthly depleted)
        - monthly_reset_at: When the monthly balance was last reset
    
    Credits are deducted from monthly_balance first, then extra_balance.
    
    Headers:
        X-User-Id: Supabase user ID
    """
    detail = await credit_service.get_balance_detail(x_user_id)
    # Handle both string (from Supabase RPC) and datetime objects
    monthly_reset_at_str = None
    if detail.monthly_reset_at:
        monthly_reset_at_str = detail.monthly_reset_at if isinstance(detail.monthly_reset_at, str) else detail.monthly_reset_at.isoformat()
    return BalanceDetailResponse(
        total_balance=detail.total_balance,
        monthly_balance=detail.monthly_balance,
        extra_balance=detail.extra_balance,
        monthly_reset_at=monthly_reset_at_str,
    )


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    x_user_id: str = Header(..., alias="X-User-Id"),
):
    """
    Get current subscription info for the user.
    
    Headers:
        X-User-Id: Supabase user ID
    """
    subscription = await _get_user_subscription(x_user_id)
    
    if not subscription:
        return SubscriptionResponse(
            plan="free",
            status="active",
            stripe_customer_id=None,
            current_period_end=None,
        )
    
    return SubscriptionResponse(
        plan=subscription.get("plan", "free"),
        status=subscription.get("status", "active"),
        stripe_customer_id=subscription.get("stripe_customer_id"),
        current_period_end=subscription.get("current_period_end"),
    )


@router.get("/transactions")
async def get_transactions(
    x_user_id: str = Header(..., alias="X-User-Id"),
    limit: int = 50,
    offset: int = 0,
):
    """
    Get credit transaction history.
    
    Headers:
        X-User-Id: Supabase user ID
    """
    transactions = await credit_service.get_transactions(
        user_id=x_user_id,
        limit=limit,
        offset=offset,
    )
    return {"transactions": transactions}


# =============================================================================
# Plans & Packages Info
# =============================================================================

@router.get("/plans", response_model=PlansResponse)
async def get_plans():
    """Get available subscription plans."""
    plans_info = {}
    for plan_id, config in PLANS.items():
        plans_info[plan_id] = {
            "monthly_credits": config.monthly_credits,
            "has_monthly_price": config.price_id_monthly is not None,
            "has_yearly_price": config.price_id_yearly is not None,
        }
    return PlansResponse(plans=plans_info)


@router.get("/packages", response_model=PackagesResponse)
async def get_packages():
    """Get available credit packages."""
    packages_info = {}
    for pkg_id, config in CREDIT_PACKAGES.items():
        packages_info[pkg_id] = {
            "credits": config.credits,
            "price_usd": config.price_usd / 100,  # Convert cents to dollars
        }
    return PackagesResponse(packages=packages_info)


# =============================================================================
# Webhook Handler
# =============================================================================

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events.
    
    Processes:
    - checkout.session.completed: Grant credits or activate subscription
    - invoice.paid: Grant monthly subscription credits
    - customer.subscription.updated: Update subscription status
    - customer.subscription.deleted: Cancel subscription
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing signature")

    try:
        event = stripe_service.construct_webhook_event(payload, sig_header)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid signature: {str(e)}")

    event_type = event.type
    data = event.data.object

    # Handle different event types
    if event_type == "checkout.session.completed":
        await _handle_checkout_completed(data)
    
    elif event_type == "invoice.paid":
        await _handle_invoice_paid(data)
    
    elif event_type == "customer.subscription.updated":
        await _handle_subscription_updated(data)
    
    elif event_type == "customer.subscription.deleted":
        await _handle_subscription_deleted(data)
    
    elif event_type == "setup_intent.succeeded":
        await _handle_setup_succeeded(data)

    return {"received": True}


# =============================================================================
# Webhook Handlers
# =============================================================================

async def _handle_checkout_completed(session: dict):
    """Handle checkout.session.completed event."""
    customer_id = session.get("customer")
    metadata = session.get("metadata", {})
    mode = session.get("mode")
    
    # Get user from subscription record
    user_id = await _get_user_by_customer_id(customer_id)
    if not user_id:
        return
    
    if mode == "subscription":
        # Subscription checkout completed
        plan = metadata.get("plan", "pro")
        subscription_id = session.get("subscription")
        
        # Update subscription record
        await _update_subscription(
            user_id=user_id,
            plan=plan,
            status="active",
            stripe_subscription_id=subscription_id,
        )
        
        # Grant initial credits
        await credit_service.grant_subscription_credits(
            user_id=user_id,
            plan=plan,
            stripe_subscription_id=subscription_id,
        )
    
    elif mode == "payment" and metadata.get("type") == "credits":
        # One-time credit purchase
        credits = int(metadata.get("credits", 0))
        package = metadata.get("package")
        payment_intent = session.get("payment_intent")
        
        if credits > 0:
            await credit_service.add_credits(
                user_id=user_id,
                amount=credits,
                type="purchase",
                description=f"Credit pack: {package}",
                stripe_payment_id=payment_intent,
            )
    
    elif mode == "setup":
        # Card setup for free plan
        plan = metadata.get("plan", "free")
        
        if plan == "free":
            # Update to active free plan and grant initial credits
            await _update_subscription(
                user_id=user_id,
                plan="free",
                status="active",
            )
            await credit_service.grant_subscription_credits(
                user_id=user_id,
                plan="free",
            )


async def _handle_invoice_paid(invoice: dict):
    """Handle invoice.paid event (subscription renewal)."""
    subscription_id = invoice.get("subscription")
    customer_id = invoice.get("customer")
    
    if not subscription_id:
        return  # Not a subscription invoice
    
    # Get user and subscription info
    user_id = await _get_user_by_customer_id(customer_id)
    if not user_id:
        return
    
    subscription = await _get_user_subscription(user_id)
    if not subscription:
        return
    
    plan = subscription.get("plan", "free")
    
    # Grant monthly credits (only for paid plans on renewal)
    # Skip if this is the first invoice (already granted in checkout)
    billing_reason = invoice.get("billing_reason")
    if billing_reason == "subscription_cycle":
        await credit_service.grant_subscription_credits(
            user_id=user_id,
            plan=plan,
            stripe_subscription_id=subscription_id,
        )


async def _handle_subscription_updated(subscription: dict):
    """Handle customer.subscription.updated event."""
    customer_id = subscription.get("customer")
    subscription_id = subscription.get("id")
    status = subscription.get("status")
    current_period_end = subscription.get("current_period_end")
    
    user_id = await _get_user_by_customer_id(customer_id)
    if not user_id:
        return
    
    # Map Stripe status to our status
    status_map = {
        "active": "active",
        "past_due": "past_due",
        "canceled": "canceled",
        "unpaid": "past_due",
        "incomplete": "incomplete",
        "incomplete_expired": "canceled",
        "trialing": "active",
    }
    
    await _update_subscription(
        user_id=user_id,
        status=status_map.get(status, "active"),
        stripe_subscription_id=subscription_id,
        current_period_end=current_period_end,
    )


async def _handle_subscription_deleted(subscription: dict):
    """Handle customer.subscription.deleted event."""
    customer_id = subscription.get("customer")
    
    user_id = await _get_user_by_customer_id(customer_id)
    if not user_id:
        return
    
    # Downgrade to free plan
    await _update_subscription(
        user_id=user_id,
        plan="free",
        status="active",
        stripe_subscription_id=None,
    )


async def _handle_setup_succeeded(setup_intent: dict):
    """Handle setup_intent.succeeded event."""
    # This is handled in checkout.session.completed for setup mode
    pass


# =============================================================================
# Helper Functions
# =============================================================================

async def _get_user_subscription(user_id: str) -> Optional[dict]:
    """Get subscription record for a user."""
    client = supabase_service.client
    if not client:
        return None
    
    try:
        result = client.schema("stripe").table("subscriptions") \
            .select("*") \
            .eq("user_id", user_id) \
            .single() \
            .execute()
        return result.data
    except Exception:
        return None


async def _get_user_by_customer_id(customer_id: str) -> Optional[str]:
    """Get user ID from Stripe customer ID."""
    client = supabase_service.client
    if not client:
        return None
    
    try:
        result = client.schema("stripe").table("subscriptions") \
            .select("user_id") \
            .eq("stripe_customer_id", customer_id) \
            .single() \
            .execute()
        return result.data.get("user_id") if result.data else None
    except Exception:
        return None


async def _ensure_subscription_record(user_id: str, customer_id: str) -> None:
    """Ensure a subscription record exists for the user."""
    client = supabase_service.client
    if not client:
        return
    
    # Upsert subscription record
    client.schema("stripe").table("subscriptions").upsert(
        {
            "user_id": user_id,
            "stripe_customer_id": customer_id,
            "plan": "free",
            "status": "active",
        },
        on_conflict="user_id",
    ).execute()
    
    # Also ensure credit balance exists
    await credit_service.initialize_user_balance(user_id)


async def _update_subscription(
    user_id: str,
    plan: Optional[str] = None,
    status: Optional[str] = None,
    stripe_subscription_id: Optional[str] = None,
    current_period_end: Optional[int] = None,
) -> None:
    """Update subscription record."""
    client = supabase_service.client
    if not client:
        return
    
    updates = {"updated_at": "now()"}
    if plan is not None:
        updates["plan"] = plan
    if status is not None:
        updates["status"] = status
    if stripe_subscription_id is not None:
        updates["stripe_subscription_id"] = stripe_subscription_id
    if current_period_end is not None:
        from datetime import datetime
        updates["current_period_end"] = datetime.fromtimestamp(current_period_end).isoformat()
    
    client.schema("stripe").table("subscriptions") \
        .update(updates) \
        .eq("user_id", user_id) \
        .execute()

