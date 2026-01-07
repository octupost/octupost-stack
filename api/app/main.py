"""
Octupost API - FastAPI Application

All routes merged into single file for simplicity.
"""

import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Optional

import inngest
import inngest.fast_api
import sentry_sdk
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Header, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field
from scalar_fastapi import get_scalar_api_reference, Layout
from sentry_sdk.integrations.fastapi import FastApiIntegration

try:
    from sentry_sdk.integrations.inngest import InngestIntegration
except ImportError:
    InngestIntegration = None

from app.config import get_settings
from app.billing import (
    credit_service,
    stripe_service,
    calculate_credits as calculate_credits_from_pricing_config,
    get_pricing_config_for_model,
    PLANS,
    CREDIT_PACKAGES,
    PlanType,
    IntervalType,
    PackageType,
)
from app.gateway import resolve_request
from app.registry import (
    get_friendly_name,
    get_capabilities,
)
from app.media_types import derive_media_type
from app.schemas import (
    ErrorResponse,
    JobResponse,
    JobStatus,
    JobStatusResponse,
    get_generated_models,
    CreateKeyRequest,
    CreateKeyResponse,
    ApiKeyMetadataResponse,
)
from app.services.job_store import job_store
from app.services.supabase_client import supabase_service
from app.services.api_key_service import api_key_service
from app.auth import AuthContext, get_auth_context, get_optional_auth


logger = logging.getLogger(__name__)


# =============================================================================
# Sentry Setup
# =============================================================================

settings = get_settings()
if settings.sentry_dsn:
    is_dev_env = settings.environment.lower() == "development"

    def _before_send(event, hint):
        """Scrub sensitive request details before sending to Sentry."""
        request = event.get("request")
        if request:
            request.pop("cookies", None)
            headers = request.get("headers") or {}
            headers = {
                k: v for k, v in headers.items() if k.lower() not in {"authorization", "cookie"}
            }
            if headers:
                request["headers"] = headers
            else:
                request.pop("headers", None)
        return event

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[
            FastApiIntegration(),
            *([InngestIntegration()] if InngestIntegration else []),
        ],
        traces_sample_rate=1.0 if is_dev_env else 0.2,
        profiles_sample_rate=1.0 if is_dev_env else 0.1,
        environment=settings.environment,
        release=os.getenv("SENTRY_RELEASE") or os.getenv("VERCEL_GIT_COMMIT_SHA"),
        send_default_pii=False,
        before_send=_before_send,
    )


# =============================================================================
# Inngest Client & Functions (imported from inngest_worker)
# =============================================================================

from app.inngest_worker import inngest_client, all_functions


# =============================================================================
# Lifespan
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    settings = get_settings()

    if settings.fal_key:
        os.environ["FAL_KEY"] = settings.fal_key
    if settings.elevenlabs_api_key:
        os.environ["ELEVENLABS_API_KEY"] = settings.elevenlabs_api_key

    yield


# =============================================================================
# Generation Routes
# =============================================================================

generate_router = APIRouter()


class GenerationRequest(BaseModel):
    """Unified generation request model with nested params."""
    model: str = Field(..., description="Model ID (semantic like 'openai/gpt-image-1-mini')")
    mode: str = Field(..., description="Generation mode (e.g., 'image-to-image', 'text-to-video')")
    params: dict[str, Any] = Field(default_factory=dict, description="Generation parameters")
    idempotency_key: Optional[str] = Field(None, description="Client-provided key for request deduplication")


# derive_media_type is now imported from app.types (centralized in packages/shared/src/types/types.json)


class PricingConfigError(Exception):
    """Raised when pricing configuration is missing or invalid."""
    pass


def _calculate_credits_for_model(model_id: str, params: dict[str, Any]) -> int:
    """Calculate credits needed for a generation request using registry.py."""
    from app.registry import get_capabilities

    caps = get_capabilities(model_id)
    if not caps:
        raise PricingConfigError(f"Model '{model_id}' not found in registry. Please contact support.")

    pricing_config = get_pricing_config_for_model(model_id)

    if not pricing_config:
        raise PricingConfigError(f"Pricing configuration missing for model '{model_id}'. Please contact support.")

    if pricing_config.get("base_unit_price", 0) <= 0:
        raise PricingConfigError(f"Invalid pricing for model '{model_id}'. Please contact support.")

    credits = calculate_credits_from_pricing_config(pricing_config, params)
    return credits


def _validate_request_params(model_id: str, params: dict[str, Any]) -> None:
    """Validate request parameters against the model's requirements using registry.py."""
    from app.registry import get_capabilities

    caps = get_capabilities(model_id)
    if not caps:
        raise HTTPException(
            status_code=400,
            detail={"error": "validation_error", "message": f"Unknown model: {model_id}", "errors": [f"Unknown model: {model_id}"]}
        )


async def _create_generation_job(
    model_id: str,
    mode: str,
    params: dict[str, Any],
    user_id: Optional[str],
    workplace_id: Optional[str],
    skip_validation: bool = False,
    original_params: Optional[dict[str, Any]] = None,
    idempotency_key: Optional[str] = None,
    project_id: Optional[str] = None,
) -> JobResponse:
    """
    Create a generation job with FAL queue validation.

    New workflow:
    1. Check for existing job with same idempotency_key (if provided)
    2. Validate model and calculate credits
    3. Create job record (status: pending)
    4. Reserve credits (not deduct)
    5. Create asset
    6. Transform and submit to FAL queue (validates request)
    7. If FAL accepts: store fal_request_id, send to Inngest for polling
    8. If FAL rejects: release reservation, fail job, return error
    9. Return HTTP 202 with status: processing
    """
    from app.registry import get_capabilities
    from app.gateway import transform_for_provider
    from app.services.fal_queue import submit_to_queue, FalValidationError, FalQueueError

    if user_id:
        sentry_sdk.set_user({"id": user_id})
    else:
        sentry_sdk.set_user(None)

    # Check for existing job with same idempotency_key (prevents duplicate requests)
    if idempotency_key and user_id:
        existing_job = job_store.find_existing_job(user_id, idempotency_key)
        if existing_job:
            return JobResponse(
                job_id=existing_job["job_id"],
                asset_id=existing_job.get("asset_id"),
                status=existing_job["status"],
                message="Existing job returned (idempotent request)"
            )

    # Use registry.py for model validation (single source of truth)
    caps = get_capabilities(model_id)
    if not caps or not caps.is_active:
        raise HTTPException(status_code=400, detail=f"Invalid or disabled model: {model_id}")

    if not skip_validation:
        _validate_request_params(model_id, params)

    # Use original params for billing (before outbound_schema transformation)
    # The pricing matrix uses semantic keys like "aspect_ratio", not transformed keys like "image_size"
    billing_params = original_params if original_params is not None else params
    try:
        credits_needed = _calculate_credits_for_model(model_id, billing_params)
    except PricingConfigError as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "pricing_config_error", "message": str(e), "support_message": "Please contact support."}
        )

    # Use registry.py for model metadata
    gen_type = caps._infer_model_type()
    asset_type = caps.output_asset_type
    media_type = caps.output_media_type or derive_media_type(asset_type)

    # Create job first (status: pending)
    job_id = job_store.create_job(
        job_type=gen_type,
        request_data={"model": model_id, "credits": credits_needed, **params},
        owner_id=user_id,
        idempotency_key=idempotency_key,
    )

    # Reserve credits until job completes
    reservation_id = None
    if user_id and credits_needed > 0:
        reservation_id = await credit_service.reserve_credits(
            user_id=user_id,
            estimated_amount=credits_needed,
            job_id=job_id,
            model_id=model_id,
        )
        if not reservation_id:
            job_store.update_job_status(job_id, JobStatus.FAILED, error="Insufficient credits")
            balance = await credit_service.get_balance(user_id)
            raise HTTPException(
                status_code=402,
                detail={"error": "insufficient_credits", "message": "Insufficient credits", "credits_needed": credits_needed, "credits_available": balance}
            )
        # Store reservation_id in job for later settlement
        job_store.set_reservation_id(job_id, reservation_id)

    # Create asset
    asset_id = None
    if user_id:
        asset = supabase_service.create_asset(
            owner_id=user_id, asset_type=asset_type, media_type=media_type, source="generative_ai",
            generation_params={"model": model_id, **params}, workplace_id=workplace_id,
            project_id=project_id,
        )
        asset_id = asset.get("id") if asset else None
        if asset_id:
            job_store.set_job_asset(job_id, asset_id)

    # Transform parameters for FAL using the explicit mode
    endpoint, fal_params = transform_for_provider(model_id, mode, params)

    # Submit to FAL queue and wait for confirmation
    # This validates the request BEFORE we return to the user
    try:
        queue_result = await submit_to_queue(endpoint, fal_params, timeout_seconds=30.0)

        # FAL accepted the request - store fal_request_id
        job_store.set_fal_request_id(job_id, queue_result.request_id)

        # Update job to processing (FAL confirmed it's in queue)
        queue_msg = f"Queue position: {queue_result.queue_position}" if queue_result.queue_position else "Processing started"
        job_store.update_job_status(job_id, JobStatus.PROCESSING, progress=5)

        if asset_id:
            supabase_service.update_asset_status(asset_id, status="processing", progress=5)

    except (FalValidationError, FalQueueError) as exc:
        # FAL rejected the request - release reservation and fail
        error_msg = str(exc)

        if reservation_id:
            await credit_service.release_reservation(reservation_id, f"fal_rejected: {error_msg[:100]}")

        job_store.update_job_status(job_id, JobStatus.FAILED, error=error_msg)

        if asset_id:
            try:
                supabase_service.update_asset_status(asset_id, status="failed", metadata={"error": error_msg})
            except Exception:
                pass

        # Return the actual FAL error to the user
        raise HTTPException(
            status_code=400,
            detail={"error": "fal_validation_error", "message": error_msg, "job_id": job_id}
        )

    except Exception as exc:
        # Unexpected error - release reservation and fail
        error_msg = str(exc)

        if reservation_id:
            await credit_service.release_reservation(reservation_id, f"unexpected_error: {error_msg[:100]}")

        job_store.update_job_status(job_id, JobStatus.FAILED, error=error_msg)

        if asset_id:
            try:
                supabase_service.update_asset_status(asset_id, status="failed", metadata={"error": error_msg})
            except Exception:
                pass

        raise HTTPException(status_code=503, detail=f"Failed to submit generation: {error_msg}")

    # Send to Inngest for polling completion
    event_data = {
        "job_id": job_id,
        "asset_id": asset_id,
        "model": model_id,
        "endpoint": endpoint,
        "fal_request_id": queue_result.request_id,
        "user_id": user_id,
        "reservation_id": reservation_id,
        "credits_estimated": credits_needed,
        "mode": mode,  # For response normalization
        "original_params": params,  # For dimension defaults in normalization
    }

    try:
        await inngest_client.send(inngest.Event(name="ai/generate.poll", data=event_data))

        if user_id and credits_needed > 0:
            supabase_service.log_generation_cost(
                user_id=user_id, job_id=job_id, model_id=model_id, generation_type=gen_type, credits_charged=credits_needed, input_params=params
            )
    except Exception as exc:
        # Inngest failed but FAL already has the request - log error but don't fail
        # The job is still processing in FAL
        sentry_sdk.capture_exception(exc)
        logger.error(f"Failed to send Inngest event for job {job_id}: {exc}")

    return JobResponse(
        job_id=job_id,
        asset_id=asset_id,
        status=JobStatus.PROCESSING,  # Not PENDING - FAL confirmed it's in queue
        message=f"{gen_type.replace('-', ' ').title()} generation in progress"
    )


@generate_router.post("", response_model=JobResponse, status_code=202, responses={400: {"model": ErrorResponse}}, include_in_schema=False)
async def generate(
    request: GenerationRequest,
    auth: Optional[AuthContext] = Depends(get_optional_auth),
) -> JobResponse:
    """Create a generation job using any model. Returns HTTP 202 Accepted."""
    user_id = auth.user_id if auth else None
    workspace_id = auth.workspace_id if auth else None
    project_id = auth.project_id if auth else None

    # Build request dict with model, mode, and params for gateway
    request_dict = {"model": request.model, "mode": request.mode, **request.params}
    resolved = resolve_request(request_dict)

    if not resolved.is_valid:
        raise HTTPException(status_code=400, detail={"error": "validation_error", "message": "Invalid request", "errors": resolved.errors})

    logger.debug(f"Resolved request: {resolved.friendly_name} -> {resolved.endpoint} (mode: {resolved.mode})")
    # IMPORTANT: Pass ORIGINAL params (request.params), NOT resolved.params!
    # resolve_request already transforms params via transform_for_provider (applies value_map, etc.)
    # _create_generation_job also calls transform_for_provider, which would fail on already-transformed values.
    # Example: Nano Banana's resolution "2048p" gets mapped to "2K" - if passed twice, "2K" fails enum validation.
    return await _create_generation_job(
        model_id=resolved.endpoint,
        mode=resolved.mode,
        params=request.params,
        user_id=user_id,
        workplace_id=workspace_id,
        skip_validation=True,
        original_params=request.params,
        idempotency_key=request.idempotency_key,
        project_id=project_id,
    )


# Model categories for grouping
MODEL_CATEGORIES: dict[str, str] = {
    "google/veo-3.1": "Video Generation", "google/veo-3.1/fast": "Video Generation",
    "kling/video/v2.6/pro": "Video Generation", "openai/sora-2": "Video Generation",
    "minimax/hailuo-2.3/standard": "Video Generation", "ltx/2/fast": "Video Generation",
    "longcat/video/distilled": "Video Generation",
    "openai/gpt-image-1-mini": "Image Generation", "openai/gpt-image-1.5": "Image Generation",
    "google/nano-banana-pro": "Image Generation", "black-forest-labs/flux-2": "Image Generation",
    "bytedance/seedream-v4.5": "Image Generation", "fal-ai/z-image/turbo": "Image Generation",
    "elevenlabs/eleven_multilingual_v2": "Text-to-Speech", "elevenlabs/eleven_v3": "Text-to-Speech",
    "elevenlabs/eleven_turbo_v2_5": "Text-to-Speech",
    "minimax/music/v2": "Music Generation", "beatoven/music-generation": "Music Generation",
    "elevenlabs/sound-effect-generation-v2": "Sound Effects", "beatoven/sound-effect-generation": "Sound Effects",
    "kling-video/ai-avatar/v2/pro": "Avatar", "kling-video/ai-avatar/v2/standard": "Avatar", "veed/fabric-1.0": "Avatar",
}

MODEL_DISPLAY_NAMES: dict[str, str] = {
    "google/veo-3.1": "Google Veo 3.1", "google/veo-3.1/fast": "Google Veo 3.1 Fast",
    "kling/video/v2.6/pro": "Kling Pro", "openai/sora-2": "OpenAI Sora 2",
    "minimax/hailuo-2.3/standard": "Minimax Hailuo", "ltx/2/fast": "LTX 2 Fast",
    "longcat/video/distilled": "Longcat Distilled",
    "openai/gpt-image-1-mini": "OpenAI GPT Image Mini", "openai/gpt-image-1.5": "OpenAI GPT Image 1.5",
    "google/nano-banana-pro": "Google Nano Banana Pro", "black-forest-labs/flux-2": "Flux 2",
    "bytedance/seedream-v4.5": "Bytedance Seedream", "fal-ai/z-image/turbo": "Z-Image Turbo",
    "elevenlabs/eleven_multilingual_v2": "ElevenLabs V2", "elevenlabs/eleven_v3": "ElevenLabs V3",
    "elevenlabs/eleven_turbo_v2_5": "ElevenLabs Turbo",
    "minimax/music/v2": "Minimax Music", "beatoven/music-generation": "Beatoven Music",
    "elevenlabs/sound-effect-generation-v2": "ElevenLabs Sound Effects", "beatoven/sound-effect-generation": "Beatoven Sound Effects",
    "kling-video/ai-avatar/v2/pro": "Kling Avatar Pro", "kling-video/ai-avatar/v2/standard": "Kling Avatar Standard", "veed/fabric-1.0": "Veed Fabric",
}

MODE_DISPLAY_NAMES = {
    "text-to-video": "Text to Video", "image-to-video": "Image to Video",
    "first-last-frame-to-video": "First & Last Frame to Video", "extend-video": "Extend Video",
    "reference-to-video": "Reference to Video", "text-to-image": "Text to Image",
    "image-to-image": "Image to Image", "text-to-speech": "Text to Speech",
    "text-to-music": "Text to Music", "text-to-sound-effect": "Text to Sound Effect",
    "speech-to-avatar": "Speech to Avatar", "text-to-avatar": "Text to Avatar",
}


def _get_model_display_name(model_id: str) -> str:
    if model_id in MODEL_DISPLAY_NAMES:
        return MODEL_DISPLAY_NAMES[model_id]
    parts = model_id.split("/")
    if len(parts) >= 2:
        provider = parts[0].replace("-", " ").title()
        model_name = parts[1].replace("-", " ").replace("_", " ").title()
        return f"{provider} {model_name}"
    return model_id.replace("/", " ").replace("-", " ").title()


def _get_model_tag(model_id: str) -> str:
    return _get_model_display_name(model_id)


def _format_mode_display(mode: str) -> str:
    if mode in MODE_DISPLAY_NAMES:
        return MODE_DISPLAY_NAMES[mode]
    return mode.replace("-", " ").title()


def get_tag_groups() -> list[dict]:
    """Get tag groups for OpenAPI x-tagGroups extension."""
    category_models: dict[str, list[str]] = {}
    for model_id, category in MODEL_CATEGORIES.items():
        if category not in category_models:
            category_models[category] = []
        display_name = _get_model_display_name(model_id)
        if display_name not in category_models[category]:
            category_models[category].append(display_name)

    category_order = ["Video Generation", "Image Generation", "Text-to-Speech", "Music Generation", "Sound Effects", "Avatar"]
    tag_groups = []
    for category in category_order:
        if category in category_models:
            tag_groups.append({"name": category, "tags": sorted(category_models[category])})
    for category, models in category_models.items():
        if category not in category_order:
            tag_groups.append({"name": category, "tags": sorted(models)})
    return tag_groups


# Dynamically create endpoints for each model
_generated_models = get_generated_models()


async def _handle_model_specific_request(request: BaseModel, user_id: Optional[str], workplace_id: Optional[str]) -> JobResponse:
    """Handle a model-specific request from generated schemas."""
    request_dict = request.model_dump(exclude_none=True)
    model_id = request_dict.pop("model")
    mode = request_dict.pop("mode", "")
    params = request_dict
    return await _create_generation_job(model_id=model_id, mode=mode, params=params, user_id=user_id, workplace_id=workplace_id, skip_validation=True)


def _create_model_endpoint(model_key: str, model_schema: type):
    """Create a POST endpoint for a specific model."""
    parts = model_key.split(":")
    model_id = parts[0]
    mode = parts[1] if len(parts) > 1 else None
    # Use friendly name for URL (e.g., "z-image-turbo" instead of "fal-ai-z-image-turbo")
    friendly_name = get_friendly_name(model_id)
    safe_path = friendly_name
    if mode:
        safe_path = f"{safe_path}/{mode}"
    model_tag = _get_model_tag(model_id)
    model_desc = model_schema.__doc__ or f"Generate content using {model_id}"
    mode_display = _format_mode_display(mode) if mode else "Generate"

    @generate_router.post(f"/models/{safe_path}", response_model=JobResponse, status_code=202, responses={400: {"model": ErrorResponse}}, summary=mode_display, description=model_desc, tags=[model_tag])
    async def model_endpoint(request: model_schema, auth: Optional[AuthContext] = Depends(get_optional_auth)) -> JobResponse:
        user_id = auth.user_id if auth else None
        workspace_id = auth.workspace_id if auth else None
        return await _handle_model_specific_request(request, user_id, workspace_id)

    model_endpoint.__name__ = f"generate_{safe_path.replace('/', '_').replace('-', '_')}"
    return model_endpoint


for _model_key, _model_schema in _generated_models.items():
    _create_model_endpoint(_model_key, _model_schema)


# =============================================================================
# Jobs Routes
# =============================================================================

jobs_router = APIRouter()


@jobs_router.get("/{job_id}", response_model=JobStatusResponse, responses={404: {"model": ErrorResponse}})
async def get_job_status(job_id: str, auth: Optional[AuthContext] = Depends(get_optional_auth)) -> JobStatusResponse:
    """Get the status of a generation job."""
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": f"Job {job_id} not found"})
    return JobStatusResponse(job_id=job["job_id"], status=job["status"], progress=job.get("progress"), result=job.get("result"), error=job.get("error"), created_at=job["created_at"], updated_at=job["updated_at"])


@jobs_router.post("/{job_id}/cancel", response_model=JobStatusResponse, responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}})
async def cancel_job(job_id: str, auth: Optional[AuthContext] = Depends(get_optional_auth)) -> JobStatusResponse:
    """Cancel a generation job."""
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": f"Job {job_id} not found"})
    if job["status"] not in [JobStatus.PENDING, JobStatus.PROCESSING]:
        raise HTTPException(status_code=400, detail={"error": "invalid_state", "message": f"Cannot cancel job with status '{job['status'].value}'"})

    # Get reservation_id before cancelling (needed for credit release)
    reservation_id = job.get("reservation_id")

    job_store.cancel_job(job_id)

    # Release credit reservation if exists
    if reservation_id:
        try:
            await credit_service.release_reservation(reservation_id, "user_cancelled")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            # Log but don't fail - job is already cancelled

    # Soft delete associated asset
    asset_id = job.get("asset_id")
    if asset_id:
        try:
            supabase_service.soft_delete_asset(asset_id)
        except Exception as e:
            sentry_sdk.capture_exception(e)

    job = job_store.get_job(job_id)
    return JobStatusResponse(job_id=job["job_id"], status=job["status"], progress=job.get("progress"), result=job.get("result"), error=job.get("error"), created_at=job["created_at"], updated_at=job["updated_at"])


@jobs_router.get("", response_model=list[JobStatusResponse])
async def list_jobs(
    limit: int = Query(default=50, ge=1, le=100),
    status: Optional[JobStatus] = Query(default=None),
    job_type: Optional[str] = Query(default=None),
    auth: Optional[AuthContext] = Depends(get_optional_auth),
) -> list[JobStatusResponse]:
    """List recent generation jobs."""
    user_id = auth.user_id if auth else None
    jobs = job_store.list_jobs(limit=limit, status=status, owner_id=user_id, job_type=job_type)
    return [JobStatusResponse(job_id=job["job_id"], status=job["status"], progress=job.get("progress"), result=job.get("result"), error=job.get("error"), created_at=job["created_at"], updated_at=job["updated_at"]) for job in jobs]


@jobs_router.post("/{job_id}/callback", include_in_schema=False)
async def job_callback(job_id: str, status: str, result: Optional[dict] = None, error: Optional[str] = None):
    """Internal callback endpoint for Inngest."""
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    status_map = {"completed": JobStatus.COMPLETED, "failed": JobStatus.FAILED, "processing": JobStatus.PROCESSING}
    job_status = status_map.get(status, JobStatus.FAILED)
    job_store.update_job_status(job_id=job_id, status=job_status, progress=100 if job_status == JobStatus.COMPLETED else None, result=result, error=error)
    return {"ok": True}


# =============================================================================
# Billing Routes
# =============================================================================

billing_router = APIRouter()


class SubscriptionCheckoutRequest(BaseModel):
    plan: PlanType
    interval: IntervalType
    success_url: str
    cancel_url: str


class CreditsCheckoutRequest(BaseModel):
    package: PackageType
    success_url: str
    cancel_url: str


class SetupCheckoutRequest(BaseModel):
    success_url: str
    cancel_url: str


class PortalRequest(BaseModel):
    return_url: str


class CheckoutResponse(BaseModel):
    url: str


class BalanceResponse(BaseModel):
    balance: int


class BalanceDetailResponse(BaseModel):
    total_balance: int
    monthly_balance: int
    extra_balance: int
    monthly_reset_at: Optional[str]


class SubscriptionResponse(BaseModel):
    plan: str
    status: str
    stripe_customer_id: Optional[str]
    current_period_end: Optional[str]


class PlansResponse(BaseModel):
    plans: dict


class PackagesResponse(BaseModel):
    packages: dict


async def _get_user_subscription(user_id: str) -> Optional[dict]:
    client = supabase_service.client
    if not client:
        return None
    try:
        result = client.schema("stripe").table("subscriptions").select("*").eq("user_id", user_id).maybe_single().execute()
        return result.data
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return None


async def _get_user_by_customer_id(customer_id: str) -> Optional[str]:
    client = supabase_service.client
    if not client:
        return None
    try:
        result = client.schema("stripe").table("subscriptions").select("user_id").eq("stripe_customer_id", customer_id).maybe_single().execute()
        return result.data.get("user_id") if result.data else None
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return None


async def _ensure_subscription_record(user_id: str, customer_id: str) -> None:
    client = supabase_service.client
    if not client:
        return
    client.schema("stripe").table("subscriptions").upsert({"user_id": user_id, "stripe_customer_id": customer_id, "plan": "free", "status": "active"}, on_conflict="user_id").execute()
    await credit_service.initialize_user_balance(user_id)


async def _update_subscription(user_id: str, plan: Optional[str] = None, status: Optional[str] = None, stripe_subscription_id: Optional[str] = None, current_period_end: Optional[int] = None) -> None:
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
        updates["current_period_end"] = datetime.fromtimestamp(current_period_end).isoformat()
    client.schema("stripe").table("subscriptions").update(updates).eq("user_id", user_id).execute()


@billing_router.post("/checkout/subscription", response_model=CheckoutResponse)
async def create_subscription_checkout(request: SubscriptionCheckoutRequest, x_user_id: str = Header(..., alias="X-User-Id"), x_user_email: str = Header(..., alias="X-User-Email")):
    """Create a Stripe Checkout session for subscription."""
    subscription = await _get_user_subscription(x_user_id)
    customer_id = subscription.get("stripe_customer_id") if subscription else None
    customer_id = await stripe_service.get_or_create_customer(user_id=x_user_id, email=x_user_email, existing_customer_id=customer_id)
    await _ensure_subscription_record(x_user_id, customer_id)
    url = await stripe_service.create_subscription_checkout(customer_id=customer_id, plan=request.plan, interval=request.interval, success_url=request.success_url, cancel_url=request.cancel_url)
    return CheckoutResponse(url=url)


@billing_router.post("/checkout/credits", response_model=CheckoutResponse)
async def create_credits_checkout(request: CreditsCheckoutRequest, x_user_id: str = Header(..., alias="X-User-Id"), x_user_email: str = Header(..., alias="X-User-Email")):
    """Create a Stripe Checkout session for one-time credit purchase."""
    subscription = await _get_user_subscription(x_user_id)
    customer_id = subscription.get("stripe_customer_id") if subscription else None
    customer_id = await stripe_service.get_or_create_customer(user_id=x_user_id, email=x_user_email, existing_customer_id=customer_id)
    await _ensure_subscription_record(x_user_id, customer_id)
    url = await stripe_service.create_credits_checkout(customer_id=customer_id, package=request.package, success_url=request.success_url, cancel_url=request.cancel_url)
    return CheckoutResponse(url=url)


@billing_router.post("/checkout/setup", response_model=CheckoutResponse)
async def create_setup_checkout(request: SetupCheckoutRequest, x_user_id: str = Header(..., alias="X-User-Id"), x_user_email: str = Header(..., alias="X-User-Email")):
    """Create a Stripe Checkout session for card setup (free plan)."""
    subscription = await _get_user_subscription(x_user_id)
    customer_id = subscription.get("stripe_customer_id") if subscription else None
    customer_id = await stripe_service.get_or_create_customer(user_id=x_user_id, email=x_user_email, existing_customer_id=customer_id)
    await _ensure_subscription_record(x_user_id, customer_id)
    url = await stripe_service.create_setup_checkout(customer_id=customer_id, success_url=request.success_url, cancel_url=request.cancel_url)
    return CheckoutResponse(url=url)


@billing_router.post("/portal", response_model=CheckoutResponse)
async def create_portal_session(request: PortalRequest, auth: AuthContext = Depends(get_auth_context)):
    """Create a Stripe Customer Portal session."""
    subscription = await _get_user_subscription(auth.user_id)
    if not subscription or not subscription.get("stripe_customer_id"):
        raise HTTPException(status_code=404, detail="No subscription found")
    url = await stripe_service.create_portal_session(customer_id=subscription["stripe_customer_id"], return_url=request.return_url)
    return CheckoutResponse(url=url)


@billing_router.get("/balance", response_model=BalanceResponse)
async def get_credit_balance(auth: AuthContext = Depends(get_auth_context)):
    """Get current total credit balance for the user."""
    balance = await credit_service.get_balance(auth.user_id)
    return BalanceResponse(balance=balance)


@billing_router.get("/balance/detail", response_model=BalanceDetailResponse)
async def get_credit_balance_detail(auth: AuthContext = Depends(get_auth_context)):
    """Get detailed credit balance breakdown for the user."""
    detail = await credit_service.get_balance_detail(auth.user_id)
    monthly_reset_at_str = None
    if detail.monthly_reset_at:
        monthly_reset_at_str = detail.monthly_reset_at if isinstance(detail.monthly_reset_at, str) else detail.monthly_reset_at.isoformat()
    return BalanceDetailResponse(total_balance=detail.total_balance, monthly_balance=detail.monthly_balance, extra_balance=detail.extra_balance, monthly_reset_at=monthly_reset_at_str)


@billing_router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(auth: AuthContext = Depends(get_auth_context)):
    """Get current subscription info for the user."""
    subscription = await _get_user_subscription(auth.user_id)
    if not subscription:
        return SubscriptionResponse(plan="free", status="active", stripe_customer_id=None, current_period_end=None)
    return SubscriptionResponse(plan=subscription.get("plan", "free"), status=subscription.get("status", "active"), stripe_customer_id=subscription.get("stripe_customer_id"), current_period_end=subscription.get("current_period_end"))


@billing_router.get("/transactions")
async def get_transactions(auth: AuthContext = Depends(get_auth_context), limit: int = 50, offset: int = 0):
    """Get credit transaction history."""
    transactions = await credit_service.get_transactions(user_id=auth.user_id, limit=limit, offset=offset)
    return {"transactions": transactions}


@billing_router.get("/plans", response_model=PlansResponse)
async def get_plans():
    """Get available subscription plans."""
    plans_info = {}
    for plan_id, config in PLANS.items():
        plans_info[plan_id] = {"monthly_credits": config.monthly_credits, "has_monthly_price": config.price_id_monthly is not None, "has_yearly_price": config.price_id_yearly is not None}
    return PlansResponse(plans=plans_info)


@billing_router.get("/packages", response_model=PackagesResponse)
async def get_packages():
    """Get available credit packages."""
    packages_info = {}
    for pkg_id, config in CREDIT_PACKAGES.items():
        packages_info[pkg_id] = {"credits": config.credits, "price_usd": config.price_usd / 100}
    return PackagesResponse(packages=packages_info)


@billing_router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    if not sig_header:
        logger.warning("[Webhook] Received webhook without signature header")
        raise HTTPException(status_code=400, detail="Missing signature")
    try:
        event = stripe_service.construct_webhook_event(payload, sig_header)
    except Exception as e:
        logger.error(f"[Webhook] Invalid signature: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid signature: {str(e)}")

    event_type = event.type
    event_id = event.id
    data = event.data.object

    logger.info(f"[Webhook] Received event: type={event_type}, id={event_id}")

    try:
        if event_type == "checkout.session.completed":
            await _handle_checkout_completed(data)
        elif event_type == "invoice.paid":
            await _handle_invoice_paid(data)
        elif event_type == "customer.subscription.updated":
            await _handle_subscription_updated(data)
        elif event_type == "customer.subscription.deleted":
            await _handle_subscription_deleted(data)
        elif event_type == "setup_intent.succeeded":
            logger.info(f"[Webhook] Setup intent succeeded: {event_id}")
        else:
            logger.info(f"[Webhook] Unhandled event type: {event_type}")
    except Exception as e:
        logger.error(f"[Webhook] Error processing event {event_type} ({event_id}): {str(e)}")
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Webhook processing failed")

    return {"received": True}


async def _handle_checkout_completed(session: dict):
    customer_id = session.get("customer")
    metadata = session.get("metadata", {})
    mode = session.get("mode")
    session_id = session.get("id", "unknown")

    logger.info(f"[Webhook] checkout.session.completed: session={session_id}, mode={mode}, customer={customer_id}, metadata={metadata}")

    user_id = await _get_user_by_customer_id(customer_id)
    if not user_id:
        logger.error(f"[Webhook] FAILED: Could not find user for customer_id={customer_id}. Session={session_id}. Credits NOT added!")
        sentry_sdk.capture_message(f"Webhook: User not found for customer_id={customer_id}", level="error")
        return

    logger.info(f"[Webhook] Found user_id={user_id} for customer_id={customer_id}")

    try:
        if mode == "subscription":
            plan = metadata.get("plan", "pro")
            subscription_id = session.get("subscription")
            await _update_subscription(user_id=user_id, plan=plan, status="active", stripe_subscription_id=subscription_id)
            await credit_service.grant_subscription_credits(user_id=user_id, plan=plan, stripe_subscription_id=subscription_id)
            logger.info(f"[Webhook] Subscription activated: user={user_id}, plan={plan}")
        elif mode == "payment" and metadata.get("type") == "credits":
            credits = int(metadata.get("credits", 0))
            package = metadata.get("package")
            payment_intent = session.get("payment_intent")
            if credits > 0:
                new_balance = await credit_service.add_credits(user_id=user_id, amount=credits, type="purchase", description=f"Credit pack: {package}", stripe_payment_id=payment_intent)
                logger.info(f"[Webhook] Credits added: user={user_id}, credits={credits}, package={package}, payment_intent={payment_intent}, new_balance={new_balance}")
            else:
                logger.warning(f"[Webhook] Credits purchase with 0 credits: session={session_id}, metadata={metadata}")
        elif mode == "setup":
            plan = metadata.get("plan", "free")
            if plan == "free":
                await _update_subscription(user_id=user_id, plan="free", status="active")
                await credit_service.grant_subscription_credits(user_id=user_id, plan="free")
                logger.info(f"[Webhook] Free plan setup completed: user={user_id}")
    except Exception as e:
        logger.error(f"[Webhook] FAILED to process checkout: session={session_id}, user={user_id}, error={str(e)}")
        sentry_sdk.capture_exception(e)
        raise  # Re-raise so Stripe knows to retry


async def _handle_invoice_paid(invoice: dict):
    subscription_id = invoice.get("subscription")
    customer_id = invoice.get("customer")
    if not subscription_id:
        return
    user_id = await _get_user_by_customer_id(customer_id)
    if not user_id:
        return
    subscription = await _get_user_subscription(user_id)
    if not subscription:
        return
    plan = subscription.get("plan", "free")
    billing_reason = invoice.get("billing_reason")
    if billing_reason == "subscription_cycle":
        await credit_service.grant_subscription_credits(user_id=user_id, plan=plan, stripe_subscription_id=subscription_id)


async def _handle_subscription_updated(subscription: dict):
    customer_id = subscription.get("customer")
    subscription_id = subscription.get("id")
    status = subscription.get("status")
    current_period_end = subscription.get("current_period_end")
    user_id = await _get_user_by_customer_id(customer_id)
    if not user_id:
        return
    status_map = {"active": "active", "past_due": "past_due", "canceled": "canceled", "unpaid": "past_due", "incomplete": "incomplete", "incomplete_expired": "canceled", "trialing": "active"}
    await _update_subscription(user_id=user_id, status=status_map.get(status, "active"), stripe_subscription_id=subscription_id, current_period_end=current_period_end)


async def _handle_subscription_deleted(subscription: dict):
    customer_id = subscription.get("customer")
    user_id = await _get_user_by_customer_id(customer_id)
    if not user_id:
        return
    await _update_subscription(user_id=user_id, plan="free", status="active", stripe_subscription_id=None)


# =============================================================================
# API Keys Routes
# =============================================================================

keys_router = APIRouter()


@keys_router.post("", response_model=CreateKeyResponse)
async def create_api_key(
    request: CreateKeyRequest,
    x_user_id: str = Header(..., alias="X-User-Id"),
) -> CreateKeyResponse:
    """
    Create a new API key for your account.

    **Important:** The full API key is only shown once. Store it securely.
    """
    try:
        full_key, key_id = await api_key_service.create_key(
            user_id=x_user_id,
            name=request.name,
        )
        return CreateKeyResponse(
            key=full_key,
            key_id=key_id,
        )
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Failed to create API key")


@keys_router.get("", response_model=list[ApiKeyMetadataResponse])
async def list_api_keys(
    x_user_id: str = Header(..., alias="X-User-Id"),
) -> list[ApiKeyMetadataResponse]:
    """
    List all API keys for your account.

    Returns key metadata including prefix (for identification) but not the full key.
    """
    keys = await api_key_service.list_keys(x_user_id)
    return [
        ApiKeyMetadataResponse(
            id=k.id,
            name=k.name,
            key_prefix=k.key_prefix,
            created_at=k.created_at,
            last_used_at=k.last_used_at,
            is_active=k.is_active,
        )
        for k in keys
    ]


@keys_router.delete("/{key_id}")
async def revoke_api_key(
    key_id: str,
    x_user_id: str = Header(..., alias="X-User-Id"),
) -> dict:
    """
    Revoke an API key.

    Once revoked, the key can no longer be used to authenticate requests.
    """
    success = await api_key_service.revoke_key(key_id=key_id, user_id=x_user_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="API key not found or already revoked",
        )
    return {"message": "API key revoked successfully"}


# =============================================================================
# Voices Routes (for Agent Voice Selection)
# =============================================================================

voices_router = APIRouter()


class VoiceResponse(BaseModel):
    """Voice response model."""
    elevenlabs_voice_id: str
    name: str
    category: str
    description: Optional[str]
    preview_url: Optional[str]
    labels: dict
    languages: list[dict]


class VoicesListResponse(BaseModel):
    """List of voices response."""
    voices: list[VoiceResponse]
    total: int


@voices_router.get("", response_model=VoicesListResponse)
async def list_voices(
    category: Optional[str] = Query(default=None, description="Filter by category: premade, professional, cloned"),
    language: Optional[str] = Query(default=None, description="Filter by language code: en, fr, de, etc."),
    auth: Optional[AuthContext] = Depends(get_optional_auth),
):
    """
    List available ElevenLabs voices for TTS.

    Returns default voices (user_id IS NULL) and user's cloned voices.
    Can filter by category and language.
    """
    client = supabase_service.client
    if not client:
        raise HTTPException(status_code=503, detail="Database not available")

    # Build query for voices
    query = (
        client.schema("octupost")
        .table("elevenlabs_voices")
        .select("*, languages:elevenlabs_voice_languages(*)")
    )

    # Filter: default voices OR user's own voices
    user_id = auth.user_id if auth else None
    if user_id:
        query = query.or_(f"user_id.is.null,user_id.eq.{user_id}")
    else:
        query = query.is_("user_id", None)

    # Filter by category
    if category:
        query = query.eq("category", category)

    # Filter by active only
    query = query.eq("is_active", True)

    # Execute query
    result = query.order("name").execute()

    voices = []
    for voice in result.data or []:
        # Filter by language if specified
        languages = voice.get("languages", [])
        if language:
            languages = [lang for lang in languages if lang.get("language_code") == language]
            if not languages:
                continue  # Skip voice if it doesn't support the requested language

        voices.append(VoiceResponse(
            elevenlabs_voice_id=voice["elevenlabs_voice_id"],
            name=voice["name"],
            category=voice["category"],
            description=voice.get("description"),
            preview_url=voice.get("preview_url"),
            labels=voice.get("labels", {}),
            languages=[{
                "language_code": lang.get("language_code"),
                "locale": lang.get("locale"),
                "accent": lang.get("accent"),
                "preview_url": lang.get("preview_url"),
            } for lang in languages],
        ))

    return VoicesListResponse(voices=voices, total=len(voices))


@voices_router.get("/{voice_id}")
async def get_voice(voice_id: str, auth: Optional[AuthContext] = Depends(get_optional_auth)):
    """
    Get a specific voice by ElevenLabs voice ID.
    """
    client = supabase_service.client
    if not client:
        raise HTTPException(status_code=503, detail="Database not available")

    # Query voice with languages
    query = (
        client.schema("octupost")
        .table("elevenlabs_voices")
        .select("*, languages:elevenlabs_voice_languages(*)")
        .eq("elevenlabs_voice_id", voice_id)
    )

    # Filter: default voices OR user's own voices
    user_id = auth.user_id if auth else None
    if user_id:
        query = query.or_(f"user_id.is.null,user_id.eq.{user_id}")
    else:
        query = query.is_("user_id", None)

    result = query.limit(1).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail=f"Voice not found: {voice_id}")

    voice = result.data[0]
    languages = voice.get("languages", [])

    return VoiceResponse(
        elevenlabs_voice_id=voice["elevenlabs_voice_id"],
        name=voice["name"],
        category=voice["category"],
        description=voice.get("description"),
        preview_url=voice.get("preview_url"),
        labels=voice.get("labels", {}),
        languages=[{
            "language_code": lang.get("language_code"),
            "locale": lang.get("locale"),
            "accent": lang.get("accent"),
            "preview_url": lang.get("preview_url"),
        } for lang in languages],
    )


# =============================================================================
# Capabilities Routes
# =============================================================================

capabilities_router = APIRouter()


@capabilities_router.get("/model-configs")
async def list_model_configs(
    section: Optional[str] = None,
    output_media_type: Optional[str] = None,
    model_type: Optional[str] = None,
    is_active: Optional[bool] = True,
):
    """
    Get model configurations in frontend-compatible format.

    This endpoint returns data directly from registry.py (single source of truth)
    in a format compatible with the frontend ModelConfig interface.

    Query Parameters:
    - section: Filter by composer_display_section (image, video, avatar, speech, music, sound_effect)
    - output_media_type: Filter by output media type (image, video, audio)
    - model_type: Filter by model type (text-to-video, image-to-video, etc.)
    - is_active: Filter by active status (default: True)
    """
    from app.registry import get_all_model_configs

    configs = get_all_model_configs()

    # Apply filters
    if section:
        configs = [c for c in configs if c["composer_display_section"] == section]
    if output_media_type:
        # Support comma-separated values
        media_types = [t.strip() for t in output_media_type.split(",")]
        configs = [c for c in configs if c["output_media_type"] in media_types]
    if model_type:
        # Support comma-separated values
        model_types = [t.strip() for t in model_type.split(",")]
        configs = [c for c in configs if c["model_type"] in model_types]
    if is_active is not None:
        configs = [c for c in configs if c["is_active"] == is_active]

    return {"configs": configs, "total": len(configs)}


@capabilities_router.get("/model-configs/{endpoint:path}")
async def get_model_config(endpoint: str):
    """
    Get a specific model configuration by endpoint.

    Returns the model config in frontend-compatible format.
    """
    from app.registry import get_model_config_by_endpoint

    config = get_model_config_by_endpoint(endpoint)
    if not config:
        raise HTTPException(
            status_code=404,
            detail={"error": "model_not_found", "message": f"Model not found: {endpoint}"}
        )
    return {"config": config}


# =============================================================================
# App Factory
# =============================================================================

API_DESCRIPTION = """
## Welcome to the Octupost API

Octupost provides a unified API for AI-powered media generation including **video**, **image**, **audio**, and **avatar** content.

### Quick Start

1. **Get your API key** from the Octupost dashboard under Settings > API Keys
2. **Choose a model** from our available options (Veo 3.1, Kling, Sora, Flux, ElevenLabs, etc.)
3. **Make a request** to the appropriate endpoint

### Authentication

All requests require authentication via an API key using the `Authorization` header:

```bash
curl -X POST "https://api.octupost.com/api/generate/models/google-veo-3.1/text-to-video" \\
  -H "Authorization: Bearer oct_sk_xxxxxxxxxxxx" \\
  -H "Content-Type: application/json" \\
  -d '{"model": "google/veo-3.1", "mode": "text-to-video", "prompt": "A sunset over mountains"}'
```

**API Key Format:** `oct_sk_` followed by a random string (e.g., `oct_sk_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`)

### Managing API Keys

- **Create a key:** `POST /api/keys` - Returns the full key (shown only once)
- **List your keys:** `GET /api/keys` - Returns key metadata (prefix, name, usage)
- **Revoke a key:** `DELETE /api/keys/{key_id}` - Permanently disables the key

### Response Format

All generation requests return a job ID that you can poll for status:

```json
{
  "job_id": "job_abc123",
  "asset_id": "asset_xyz789",
  "status": "pending",
  "message": "Video generation job created"
}
```

### Credit System

- Each generation consumes credits based on the model and parameters
- Check your balance at `/api/billing/balance`
- View models and pricing at `/api/capabilities/model-configs`

### Rate Limits

- Standard: 60 requests/minute
- Pro: 300 requests/minute

---

**Need help?** Contact support@octupost.com
"""


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Octupost API",
        description=API_DESCRIPTION,
        version="1.0.0",
        lifespan=lifespan,
        docs_url=None,
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(generate_router, prefix="/api/generate", tags=["Generation"])
    app.include_router(jobs_router, prefix="/api/jobs", tags=["Jobs"])
    app.include_router(billing_router, prefix="/api/billing", tags=["Billing"])
    app.include_router(keys_router, prefix="/api/keys", tags=["API Keys"])
    app.include_router(capabilities_router, prefix="/api/capabilities", tags=["Capabilities"])
    app.include_router(voices_router, prefix="/api/voices", tags=["Voices"])

    # Inngest
    inngest.fast_api.serve(app, inngest_client, all_functions)

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "healthy", "service": "api"}

    @app.get("/", tags=["Root"])
    async def root():
        return {"service": "Octupost API", "version": "1.0.0", "docs": "/docs", "health": "/health"}

    # Tag descriptions for better documentation
    TAG_DESCRIPTIONS = {
        # Router tags
        "Generation": "Create AI-generated content (videos, images, audio, avatars)",
        "Jobs": "Monitor and manage generation jobs",
        "Billing": "Credits, subscriptions, and payment management",
        "API Keys": "Create and manage API keys for authentication",
        "Capabilities": "Discover available models and their capabilities",
        "Health": "Service health and status checks",
        "Root": "API root and version information",
        # Model category tags
        "Google Veo 3.1": "Google's flagship video generation model with text-to-video, image-to-video, and extend capabilities. Supports up to 8 seconds at 1080p.",
        "Google Veo 3.1 Fast": "Faster variant of Veo 3.1 optimized for quicker generation times.",
        "Kling Pro": "Kuaishou's professional video generation with excellent motion quality.",
        "OpenAI Sora 2": "OpenAI's state-of-the-art video generation model.",
        "Minimax Hailuo": "MiniMax's video generation with prompt optimization.",
        "LTX 2 Fast": "Fast, high-quality video generation up to 4K resolution.",
        "Longcat Distilled": "Extended duration video generation up to 30 seconds.",
        "OpenAI GPT Image Mini": "Fast, cost-effective image generation.",
        "OpenAI GPT Image 1.5": "Enhanced image generation with better quality.",
        "Google Nano Banana Pro": "High-resolution image generation with web search capability.",
        "Flux 2": "Black Forest Labs' advanced image generation.",
        "Bytedance Seedream": "ByteDance's image generation model.",
        "Z-Image Turbo": "Ultra-fast image generation with prompt expansion.",
        "ElevenLabs V2": "Natural text-to-speech in 29 languages.",
        "ElevenLabs V3": "Latest ElevenLabs voice synthesis technology.",
        "ElevenLabs Turbo": "Fastest ElevenLabs speech synthesis.",
        "Minimax Music": "AI music generation with lyrics support.",
        "Beatoven Music": "Professional AI music composition.",
        "ElevenLabs Sound Effects": "AI-generated sound effects.",
        "Beatoven Sound Effects": "High-quality sound effect generation.",
        "Kling Avatar Pro": "Professional AI avatar video generation.",
        "Kling Avatar Standard": "Standard AI avatar video generation.",
        "Veed Fabric": "Fast avatar generation with text or audio input.",
    }

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(title=app.title, version=app.version, description=app.description, routes=app.routes)

        # Add tag descriptions
        existing_tags = {tag["name"]: tag for tag in openapi_schema.get("tags", [])}
        all_tags = []
        for tag_name, description in TAG_DESCRIPTIONS.items():
            if tag_name in existing_tags:
                existing_tags[tag_name]["description"] = description
                all_tags.append(existing_tags[tag_name])
            else:
                all_tags.append({"name": tag_name, "description": description})
        # Add any remaining tags not in our descriptions
        for tag_name, tag_data in existing_tags.items():
            if tag_name not in TAG_DESCRIPTIONS:
                all_tags.append(tag_data)
        openapi_schema["tags"] = all_tags

        openapi_schema["x-tagGroups"] = get_tag_groups()
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    # Custom CSS for Octupost branding
    SCALAR_CUSTOM_CSS = """
    :root {
        --scalar-color-1: #6366f1;
        --scalar-color-2: #818cf8;
        --scalar-color-3: #a5b4fc;
        --scalar-color-accent: #6366f1;
        --scalar-button-1: #6366f1;
        --scalar-button-1-hover: #4f46e5;
    }
    .dark-mode {
        --scalar-background-1: #0f0f23;
        --scalar-background-2: #1a1a2e;
        --scalar-background-3: #16213e;
    }
    .light-mode {
        --scalar-background-1: #ffffff;
        --scalar-background-2: #f8fafc;
        --scalar-background-3: #f1f5f9;
    }
    .scalar-card {
        border-radius: 12px;
    }
    .sidebar-heading {
        font-weight: 600;
    }
    """

    @app.get("/docs", include_in_schema=False)
    async def scalar_docs():
        return get_scalar_api_reference(
            openapi_url=app.openapi_url,
            title="Octupost API",
            layout=Layout.MODERN,
            dark_mode=True,
            show_sidebar=True,
            default_open_all_tags=False,
            hide_dark_mode_toggle=False,
            custom_css=SCALAR_CUSTOM_CSS,
        )

    return app


app = create_app()
