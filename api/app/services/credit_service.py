"""
Credit Service

Handles credit balance operations with atomic updates to prevent race conditions.
Uses Supabase RPC functions for transactional safety.

Dual Balance System:
- monthly_balance: Subscription credits that reset each billing cycle (use first)
- extra_balance: Purchased credits that never expire (use after monthly depleted)

Credit Reservation System:
- For models with unknown output duration (avatar, speech where duration depends on script)
- Flow: reserve_credits -> generation -> settle_reservation OR release_reservation
"""

from typing import Optional, Literal, Any
from dataclasses import dataclass
from datetime import datetime

from app.services.supabase_client import supabase_service
from app.services.stripe_service import PLANS, PlanType


# =============================================================================
# Duration Estimation Constants
# =============================================================================

# Average speaking rates by model type (characters per second)
# Based on ~140-150 words per minute, ~5 characters per word
CHARS_PER_SECOND: dict[str, float] = {
    "avatar": 14.0,           # ~14 chars/sec (140 WPM)
    "text-to-speech": 14.0,   # ~14 chars/sec (140 WPM)
}

# Buffer multiplier for reservations (30% safety buffer)
BUFFER_MULTIPLIER = 1.3


# =============================================================================
# Duration Estimation Functions
# =============================================================================

def estimate_duration_from_text(text: str, model_type: str) -> float:
    """
    Estimate output duration from input text length.
    
    Args:
        text: Input text/script
        model_type: Model type (avatar, text-to-speech)
        
    Returns:
        Estimated duration in seconds
    """
    if not text:
        return 1.0  # Minimum 1 second
    
    char_count = len(text)
    chars_per_sec = CHARS_PER_SECOND.get(model_type, 14.0)
    
    # Calculate estimated duration
    estimated_duration = char_count / chars_per_sec
    
    # Minimum 1 second, no maximum (let the model handle limits)
    return max(estimated_duration, 1.0)


def get_text_from_params(params: dict[str, Any]) -> str:
    """
    Extract text input from generation parameters.
    
    Checks common field names used for text/script input.
    
    Args:
        params: Generation parameters dictionary
        
    Returns:
        Text content or empty string if not found
    """
    # Try common text field names in order of preference
    for key in ("prompt", "text", "script", "input_text", "content"):
        value = params.get(key)
        if value and isinstance(value, str):
            return value
    return ""


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class CreditTransaction:
    """Credit transaction record."""
    id: str
    user_id: str
    amount: int
    balance_after: int
    type: str
    description: Optional[str]
    model_id: Optional[str]
    job_id: Optional[str]
    stripe_payment_id: Optional[str]
    created_at: datetime


@dataclass
class CreditBalanceDetail:
    """Detailed credit balance with monthly and extra breakdown."""
    total_balance: int
    monthly_balance: int
    extra_balance: int
    monthly_reset_at: Optional[datetime]


@dataclass
class CreditReservation:
    """Credit reservation for unknown-duration generations."""
    id: str
    user_id: str
    job_id: str
    reserved_amount: int
    estimated_amount: int
    actual_amount: Optional[int]
    status: str  # 'pending', 'settled', 'released', 'failed'
    model_id: Optional[str]
    created_at: datetime
    settled_at: Optional[datetime]


@dataclass
class SettlementResult:
    """Result of settling a credit reservation."""
    refunded: int
    charged_extra: int
    final_cost: int
    reserved_amount: int


TransactionType = Literal["subscription_grant", "purchase", "usage", "refund"]


class CreditService:
    """Service for credit balance operations."""

    async def get_balance(self, user_id: str) -> int:
        """
        Get current total credit balance for a user.
        
        Args:
            user_id: Supabase user ID
            
        Returns:
            Current total credit balance (monthly + extra, 0 if no record exists)
        """
        client = supabase_service.client
        if not client:
            return 0
        
        result = client.schema("stripe").rpc(
            "get_credit_balance",
            {"p_user_id": user_id}
        ).execute()
        
        return result.data or 0

    async def get_balance_detail(self, user_id: str) -> CreditBalanceDetail:
        """
        Get detailed credit balance breakdown for a user.
        
        Args:
            user_id: Supabase user ID
            
        Returns:
            CreditBalanceDetail with monthly_balance, extra_balance, and total
        """
        client = supabase_service.client
        if not client:
            return CreditBalanceDetail(
                total_balance=0,
                monthly_balance=0,
                extra_balance=0,
                monthly_reset_at=None
            )
        
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
        """
        Check if user has sufficient credits.
        
        Args:
            user_id: Supabase user ID
            amount: Credits needed
            
        Returns:
            True if user has enough credits
        """
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
        """
        Atomically deduct credits from a user's balance.
        
        Uses database-level locking to prevent race conditions.
        
        Args:
            user_id: Supabase user ID
            amount: Credits to deduct
            model_id: AI model used for generation
            job_id: Generation job ID
            description: Optional description
            
        Returns:
            True if deduction successful, False if insufficient credits
        """
        client = supabase_service.client
        if not client:
            return False
        
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
        """
        Add credits to a user's balance.
        
        Args:
            user_id: Supabase user ID
            amount: Credits to add
            type: Transaction type (subscription_grant, purchase, refund)
            description: Optional description
            stripe_payment_id: Stripe payment/session ID
            
        Returns:
            New balance after addition
        """
        client = supabase_service.client
        if not client:
            return 0
        
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
        """
        Refund credits for a failed generation.
        
        Args:
            user_id: Supabase user ID
            amount: Credits to refund
            job_id: Failed job ID
            description: Refund reason
            
        Returns:
            New balance after refund
        """
        client = supabase_service.client
        if not client:
            return 0
        
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
        """
        Grant monthly credits for a subscription.
        
        RESETS the monthly_balance (doesn't add). Extra credits are preserved.
        Called when a subscription is created or renewed.
        
        Args:
            user_id: Supabase user ID
            plan: Subscription plan (free, pro, elite)
            stripe_subscription_id: Stripe subscription ID
            
        Returns:
            New total balance after grant
        """
        plan_config = PLANS.get(plan)
        if not plan_config:
            raise ValueError(f"Invalid plan: {plan}")

        credits = plan_config.monthly_credits
        description = f"{plan.title()} plan monthly credits"

        client = supabase_service.client
        if not client:
            return 0
        
        # Use the new grant_subscription_credits RPC that RESETS monthly balance
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
        """
        Initialize credit balance for a new user.
        
        Creates a balance record with 0 credits.
        Called when user first signs up.
        
        Args:
            user_id: Supabase user ID
        """
        client = supabase_service.client
        if not client:
            return
        
        # Upsert to handle race conditions
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
        """
        Get credit transaction history for a user.
        
        Args:
            user_id: Supabase user ID
            limit: Maximum transactions to return
            offset: Pagination offset
            
        Returns:
            List of transaction records
        """
        client = supabase_service.client
        if not client:
            return []
        
        result = client.schema("stripe").table("credit_transactions") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()
        
        return result.data or []

    # =========================================================================
    # Credit Reservation Methods
    # For models with unknown output duration (avatar, text-to-speech)
    # =========================================================================

    async def reserve_credits(
        self,
        user_id: str,
        estimated_amount: int,
        job_id: str,
        model_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Reserve credits for a generation with unknown final cost.
        
        Reserves estimated_amount * BUFFER_MULTIPLIER (30% buffer) from the
        user's balance. Use settle_reservation() after generation to adjust
        for actual cost, or release_reservation() on failure.
        
        Args:
            user_id: Supabase user ID
            estimated_amount: Estimated credits based on input
            job_id: Generation job ID
            model_id: AI model identifier
            
        Returns:
            Reservation ID if successful, None if insufficient credits
        """
        client = supabase_service.client
        if not client:
            # #region agent log
            self._debug_log("credit_service.py:no_client", "Supabase client is None", {}, "H5")
            # #endregion
            return None
        
        # #region agent log
        self._debug_log("credit_service.py:rpc_call", "Calling stripe.reserve_credits RPC", {
            "user_id": user_id,
            "estimated_amount": estimated_amount,
            "job_id": job_id,
            "model_id": model_id,
            "buffer": BUFFER_MULTIPLIER
        }, "H5")
        # #endregion
        
        try:
            result = client.schema("stripe").rpc(
                "reserve_credits",
                {
                    "p_user_id": user_id,
                    "p_estimated_amount": estimated_amount,
                    "p_job_id": job_id,
                    "p_model_id": model_id,
                    "p_buffer_multiplier": BUFFER_MULTIPLIER,
                }
            ).execute()
            
            # #region agent log
            self._debug_log("credit_service.py:rpc_success", "RPC call successful", {
                "result_data": str(result.data)[:100] if result.data else None
            }, "H5")
            # #endregion
        except Exception as rpc_exc:
            # #region agent log
            self._debug_log("credit_service.py:rpc_error", "RPC call failed", {
                "error": str(rpc_exc),
                "error_type": type(rpc_exc).__name__
            }, "H5")
            # #endregion
            raise
        
        # Returns UUID if successful, null if insufficient credits
        return result.data if result.data else None
    
    # #region agent log
    def _debug_log(self, location: str, message: str, data: dict, hypothesis_id: str = ""):
        """Write debug log entry to file."""
        import json
        from datetime import datetime
        log_entry = {
            "location": location,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "sessionId": "debug-session",
            "hypothesisId": hypothesis_id
        }
        try:
            with open("/Users/serhatcamici/dev/octupost-stack/.cursor/debug.log", "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
            pass
    # #endregion

    async def settle_reservation(
        self,
        reservation_id: str,
        actual_amount: int,
    ) -> Optional[SettlementResult]:
        """
        Settle a reservation with the actual cost.
        
        If actual < reserved: refunds the difference to user
        If actual > reserved: charges the difference from user balance
        
        Args:
            reservation_id: UUID of the reservation
            actual_amount: Actual credits used
            
        Returns:
            SettlementResult with refunded/charged_extra amounts, or None on error
        """
        client = supabase_service.client
        if not client:
            return None
        
        result = client.schema("stripe").rpc(
            "settle_reservation",
            {
                "p_reservation_id": reservation_id,
                "p_actual_amount": actual_amount,
            }
        ).execute()
        
        if result.data and isinstance(result.data, dict):
            if "error" in result.data:
                return None
            return SettlementResult(
                refunded=result.data.get("refunded", 0),
                charged_extra=result.data.get("charged_extra", 0),
                final_cost=result.data.get("final_cost", actual_amount),
                reserved_amount=result.data.get("reserved_amount", 0),
            )
        
        return None

    async def release_reservation(
        self,
        reservation_id: str,
        reason: str = "Generation failed",
    ) -> int:
        """
        Release a reservation on generation failure.
        
        Returns all reserved credits back to the user's balance.
        
        Args:
            reservation_id: UUID of the reservation
            reason: Reason for release (logged in transaction)
            
        Returns:
            Amount of credits released back to user
        """
        client = supabase_service.client
        if not client:
            return 0
        
        result = client.schema("stripe").rpc(
            "release_reservation",
            {
                "p_reservation_id": reservation_id,
                "p_reason": reason,
            }
        ).execute()
        
        return result.data or 0

    async def get_reservation(
        self,
        reservation_id: Optional[str] = None,
        job_id: Optional[str] = None,
    ) -> Optional[CreditReservation]:
        """
        Get reservation details by ID or job_id.
        
        Args:
            reservation_id: UUID of the reservation
            job_id: Job ID associated with the reservation
            
        Returns:
            CreditReservation if found, None otherwise
        """
        client = supabase_service.client
        if not client:
            return None
        
        result = client.schema("stripe").rpc(
            "get_reservation",
            {
                "p_reservation_id": reservation_id,
                "p_job_id": job_id,
            }
        ).execute()
        
        if result.data and len(result.data) > 0:
            data = result.data[0]
            return CreditReservation(
                id=data.get("id"),
                user_id=data.get("user_id"),
                job_id=data.get("job_id"),
                reserved_amount=data.get("reserved_amount"),
                estimated_amount=data.get("estimated_amount"),
                actual_amount=data.get("actual_amount"),
                status=data.get("status"),
                model_id=data.get("model_id"),
                created_at=data.get("created_at"),
                settled_at=data.get("settled_at"),
            )
        
        return None


# Singleton instance
credit_service = CreditService()

