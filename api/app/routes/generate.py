"""Generation API routes."""

from typing import Any, Optional

import inngest
import sentry_sdk
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field

from app.inngest.client import inngest_client
from app.models.schemas import (
    ErrorResponse,
    JobResponse,
    JobStatus,
)
from app.registry import get_model, is_valid_model, validate_params, calculate_cost, GenerationType
from app.services.job_store import job_store
from app.services.supabase_client import supabase_service
from app.services.credit_service import (
    credit_service,
    estimate_duration_from_text,
    get_text_from_params,
    BUFFER_MULTIPLIER,
)


# Credit conversion: 1 USD = 100 credits
USD_TO_CREDITS = 100


router = APIRouter()


# =============================================================================
# Request Models (flexible - validation happens via registry)
# =============================================================================

class GenerationRequest(BaseModel):
    """Unified generation request model."""
    model: str = Field(..., description="Model endpoint from provider.json")
    params: dict[str, Any] = Field(default_factory=dict, description="Generation parameters")


class FlexibleVideoRequest(BaseModel):
    """
    Flexible video generation request.
    
    Accepts any parameters - validation happens dynamically based on the model.
    """
    model: str = Field(..., description="Model endpoint from provider.json")
    prompt: str = Field(..., min_length=1, max_length=5000, description="Generation prompt")
    duration: Optional[int] = Field(default=None, description="Video duration in seconds")
    aspect_ratio: Optional[str] = Field(default=None, description="Video aspect ratio")
    resolution: Optional[str] = Field(default=None, description="Video resolution")
    negative_prompt: Optional[str] = Field(default=None, description="Negative prompt")
    enhance_prompt: Optional[bool] = Field(default=None, description="Enable prompt enhancement")
    enable_audio: Optional[bool] = Field(default=None, description="Enable audio generation")
    fps: Optional[int] = Field(default=None, description="Frames per second")
    seed: Optional[int] = Field(default=None, ge=0, description="Random seed")
    
    # Allow any additional parameters
    class Config:
        extra = "allow"


class FlexibleImageToVideoRequest(BaseModel):
    """
    Flexible image-to-video generation request.
    """
    model: str = Field(..., description="Model endpoint from provider.json")
    image_url: str = Field(..., description="URL of the source image")
    prompt: str = Field(..., min_length=1, max_length=5000, description="Motion prompt")
    duration: Optional[int] = Field(default=None, description="Video duration in seconds")
    aspect_ratio: Optional[str] = Field(default=None, description="Video aspect ratio")
    resolution: Optional[str] = Field(default=None, description="Video resolution")
    negative_prompt: Optional[str] = Field(default=None, description="Negative prompt")
    enhance_prompt: Optional[bool] = Field(default=None, description="Enable prompt enhancement")
    enable_audio: Optional[bool] = Field(default=None, description="Enable audio generation")
    seed: Optional[int] = Field(default=None, ge=0, description="Random seed")
    
    class Config:
        extra = "allow"


class FlexibleImageRequest(BaseModel):
    """Flexible image generation request."""
    model: str = Field(default="fal-ai/gpt-image-1-mini", description="Model endpoint")
    prompt: str = Field(..., min_length=1, max_length=5000, description="Generation prompt")
    aspect_ratio: Optional[str] = Field(default=None, description="Image aspect ratio")
    resolution: Optional[str] = Field(default=None, description="Image resolution/quality")
    background: Optional[str] = Field(default=None, description="Background type")
    seed: Optional[int] = Field(default=None, ge=0, description="Random seed")
    
    class Config:
        extra = "allow"


class FlexibleSpeechRequest(BaseModel):
    """Flexible text-to-speech generation request."""
    model: str = Field(default="fal-ai/minimax/speech-2.6-hd", description="Model endpoint")
    text: str = Field(..., min_length=1, max_length=10000, description="Text to speak")
    voice: Optional[str] = Field(default=None, description="Voice identifier")
    speech_speed: Optional[float] = Field(default=None, alias="speed", description="Speech speed")
    voice_emotion: Optional[str] = Field(default=None, description="Voice emotion")
    # ElevenLabs-specific parameters
    stability: Optional[float] = Field(default=None, ge=0, le=1, description="ElevenLabs voice stability (0-1)")
    similarity_boost: Optional[float] = Field(default=None, ge=0, le=1, description="ElevenLabs similarity boost (0-1)")
    style: Optional[float] = Field(default=None, ge=0, le=1, description="ElevenLabs style exaggeration (0-1)")
    
    class Config:
        extra = "allow"
        populate_by_name = True  # Allow both speech_speed and speed


# =============================================================================
# Helper Functions
# =============================================================================

def _get_generation_type(model_id: str) -> str:
    """Get the generation type for a model."""
    model = get_model(model_id)
    if model:
        return model.get("type", "unknown")
    return "unknown"


def _get_asset_type(gen_type: str) -> str:
    """
    Map generation type to specific asset type.
    Used as fallback when frontend doesn't provide asset_type.
    
    Returns: image, video, avatar_video, speech, music, soundtrack
    """
    mapping = {
        "text-to-image": "image",
        "text-to-video": "video",
        "image-to-video": "video",
        "text-to-speech": "speech",
        "text-to-audio": "soundtrack",
        "text-to-music": "music",
        "video-to-audio": "soundtrack",
        "avatar": "avatar_video",
        "reference-to-video": "video",
        "first-last-frame-to-video": "video",
        "retake": "video",
    }
    return mapping.get(gen_type, "video")


def _get_media_type(asset_type: str) -> str:
    """
    Derive the fundamental media_type from a specific asset_type.
    Used as fallback when frontend doesn't provide media_type.
    
    Returns: image, audio, video
    """
    if asset_type in ("video", "avatar_video"):
        return "video"
    elif asset_type == "image":
        return "image"
    elif asset_type in ("speech", "music", "soundtrack"):
        return "audio"
    else:
        return "video"


def _get_event_name(gen_type: str) -> str:
    """Get the Inngest event name for a generation type."""
    mapping = {
        "text-to-image": "ai/image.generate",
        "text-to-video": "ai/video.generate",
        "image-to-video": "ai/video-from-image.generate",
        "text-to-speech": "ai/speech.generate",
        "text-to-audio": "ai/audio.generate",
        "text-to-music": "ai/music.generate",
        "video-to-audio": "ai/video-audio.generate",
        "avatar": "ai/avatar.generate",
        "reference-to-video": "ai/video-from-image.generate",
        "first-last-frame-to-video": "ai/video-from-image.generate",
        "retake": "ai/video.generate",
    }
    return mapping.get(gen_type, "ai/generate")


def _needs_credit_reservation(model_id: str, params: dict[str, Any]) -> bool:
    """
    Check if a model requires credit reservation based on billing_strategy.
    
    Reads from model's billing_strategy field in provider.json.
    Defaults to "direct" if not specified.
    
    Args:
        model_id: The model identifier
        params: Generation parameters (unused, kept for API compatibility)
        
    Returns:
        True if the model needs credit reservation
    """
    model = get_model(model_id)
    if not model:
        return False
    
    # Read billing strategy from config (default: direct)
    billing_strategy = model.get("billing_strategy", "direct")
    
    return billing_strategy == "reservation"


def _calculate_credits_for_model(
    model_id: str, 
    params: dict[str, Any]
) -> tuple[int, bool, Optional[float]]:
    """
    Calculate credits needed for a generation request.
    
    Uses the registry's calculate_cost function and converts USD to credits.
    For models with unknown duration, estimates from text input.
    
    Args:
        model_id: The model identifier
        params: Generation parameters (duration, resolution, etc.)
        
    Returns:
        Tuple of (credits_needed, needs_reservation, estimated_duration)
    """
    model = get_model(model_id)
    if not model:
        return 0, False, None
    
    needs_reservation = _needs_credit_reservation(model_id, params)
    model_type = model.get("type", "")
    estimated_duration: Optional[float] = None
    
    if needs_reservation:
        # Estimate duration from text input
        text = get_text_from_params(params)
        estimated_duration = estimate_duration_from_text(text, model_type)
        duration = estimated_duration
    else:
        # Use user-specified duration or default
        duration = params.get("duration", 1)
    
    # Calculate cost in USD
    cost_usd = calculate_cost(model_id, quantity=duration, params=params)
    
    # Convert to credits (1 USD = 100 credits)
    credits = int(cost_usd * USD_TO_CREDITS)
    
    # Minimum 1 credit for any generation
    return max(credits, 1), needs_reservation, estimated_duration


def _validate_request_params(model_id: str, params: dict[str, Any]) -> None:
    """
    Validate request parameters against the model's schema.
    
    Args:
        model_id: The model identifier
        params: Parameters to validate
        
    Raises:
        HTTPException: If validation fails
    """
    # #region agent log
    _debug_log("generate.py:validation_start", "Starting parameter validation", {
        "model_id": model_id,
        "params_keys": list(params.keys()),
        "params_values": {k: (v[:50] if isinstance(v, str) and len(v) > 50 else v) for k, v in params.items()}
    }, "H1,H2")
    # #endregion
    
    validation = validate_params(model_id, params)
    
    # #region agent log
    _debug_log("generate.py:validation_result", "Validation completed", {
        "model_id": model_id,
        "valid": validation["valid"],
        "errors": validation.get("errors", [])
    }, "H1,H2")
    # #endregion
    
    if not validation["valid"]:
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "validation_error",
                "message": "Invalid parameters",
                "errors": validation["errors"]
            }
        )


async def _create_generation_job(
    model_id: str,
    params: dict[str, Any],
    user_id: Optional[str],
    workplace_id: Optional[str],
    skip_validation: bool = False,
) -> JobResponse:
    """
    Common logic for creating a generation job.
    
    For models with unknown output duration (avatar, speech), uses credit reservation
    system to reserve credits upfront and settle after generation completes.
    
    Args:
        model_id: The model identifier
        params: Generation parameters
        user_id: Optional user ID for asset tracking
        workplace_id: Optional workplace ID
        skip_validation: Skip parameter validation (for unified endpoint)
        
    Returns:
        JobResponse with job and asset IDs
        
    Raises:
        HTTPException 402: If insufficient credits
    """
    # Set user context in Sentry for error tracking
    if user_id:
        sentry_sdk.set_user({"id": user_id})
    else:
        sentry_sdk.set_user(None)
    
    # Validate model
    if not is_valid_model(model_id):
        raise HTTPException(status_code=400, detail=f"Invalid or disabled model: {model_id}")
    
    # Validate parameters dynamically
    if not skip_validation:
        _validate_request_params(model_id, params)
    
    # Calculate credits needed (may include estimation for unknown duration models)
    credits_needed, needs_reservation, estimated_duration = _calculate_credits_for_model(model_id, params)
    
    # #region agent log
    _debug_log("generate.py:credits_calc", "Credits calculated", {
        "credits_needed": credits_needed,
        "needs_reservation": needs_reservation,
        "estimated_duration": estimated_duration,
        "model_id": model_id
    }, "H1")
    # #endregion
    
    # For reservations, calculate the reserved amount (with buffer)
    reserved_amount = int(credits_needed * BUFFER_MULTIPLIER) if needs_reservation else credits_needed
    
    # Check credits availability (use reserved_amount for models needing reservation)
    check_amount = reserved_amount if needs_reservation else credits_needed
    
    if user_id and check_amount > 0:
        # #region agent log
        _debug_log("generate.py:credit_check", "Checking credit balance", {
            "user_id": user_id,
            "check_amount": check_amount
        }, "H3")
        # #endregion
        
        has_credits = await credit_service.has_sufficient_credits(user_id, check_amount)
        if not has_credits:
            balance = await credit_service.get_balance(user_id)
            raise HTTPException(
                status_code=402,
                detail={
                    "error": "insufficient_credits",
                    "message": "Insufficient credits for this generation",
                    "credits_needed": check_amount,
                    "credits_available": balance,
                    "estimated_duration": estimated_duration if needs_reservation else None,
                }
            )
    
    # Get generation type from registry
    gen_type = _get_generation_type(model_id)
    event_name = _get_event_name(gen_type)
    
    # Get asset_type and media_type from frontend params, or derive from gen_type
    asset_type = params.get("asset_type") or _get_asset_type(gen_type)
    media_type = params.get("media_type") or _get_media_type(asset_type)
    
    # Create job record first (need job_id for credits)
    # Pass owner_id for persistent storage in Supabase
    job_id = job_store.create_job(
        job_type=gen_type,
        request_data={
            "model": model_id, 
            "credits": credits_needed,
            "needs_reservation": needs_reservation,
            "estimated_duration": estimated_duration,
            **params
        },
        owner_id=user_id,
    )
    # Handle credits: reserve or deduct
    reservation_id: Optional[str] = None
    
    if user_id and check_amount > 0:
        if needs_reservation:
            # #region agent log
            _debug_log("generate.py:reserve_start", "Starting credit reservation", {
                "user_id": user_id,
                "credits_needed": credits_needed,
                "job_id": job_id,
                "model_id": model_id
            }, "H1")
            # #endregion
            
            # Reserve credits for models with unknown duration
            try:
                reservation_id = await credit_service.reserve_credits(
                    user_id=user_id,
                    estimated_amount=credits_needed,
                    job_id=job_id,
                    model_id=model_id,
                )
            except Exception as reserve_exc:
                # #region agent log
                _debug_log("generate.py:reserve_error", "Credit reservation FAILED with exception", {
                    "error": str(reserve_exc),
                    "error_type": type(reserve_exc).__name__
                }, "H1")
                # #endregion
                raise
            
            # #region agent log
            _debug_log("generate.py:reserve_done", "Credit reservation completed", {
                "reservation_id": reservation_id
            }, "H1")
            # #endregion
            
            if not reservation_id:
                # Race condition - someone else used credits
                job_store.update_job_status(job_id, JobStatus.FAILED, error="Insufficient credits for reservation")
                raise HTTPException(
                    status_code=402,
                    detail={
                        "error": "insufficient_credits",
                        "message": "Credits were used by another request",
                    }
                )
        else:
            # Direct deduction for models with known duration
            deducted = await credit_service.deduct_credits(
                user_id=user_id,
                amount=credits_needed,
                model_id=model_id,
                job_id=job_id,
                description=f"{gen_type} generation",
            )
            if not deducted:
                # Race condition - someone else used credits
                job_store.update_job_status(job_id, JobStatus.FAILED, error="Insufficient credits")
                raise HTTPException(
                    status_code=402,
                    detail={
                        "error": "insufficient_credits",
                        "message": "Credits were used by another request",
                    }
                )
    
    # Create asset record if user is authenticated
    asset_id = None
    if user_id:
        asset = supabase_service.create_asset(
            owner_id=user_id,
            asset_type=asset_type,
            media_type=media_type,
            source="generative_ai",
            generation_params={"model": model_id, **params},
            workplace_id=workplace_id,
        )
        asset_id = asset.get("id") if asset else None
        
        # Link the asset to the job for querying
        if asset_id:
            job_store.set_job_asset(job_id, asset_id)
    
    # Prepare event data
    # Include reservation_id for settlement, or credits_used for direct refund
    event_data = {
        "job_id": job_id,
        "asset_id": asset_id,
        "model": model_id,
        "user_id": user_id,
        "credits_used": credits_needed,  # Estimated credits (for both refund and settlement)
        "reservation_id": reservation_id,  # None if direct deduction
        "estimated_duration": estimated_duration,  # For logging/debugging
        **params,
    }
    
    # #region agent log
    _debug_log("generate.py:inngest_send_start", "Sending event to Inngest", {
        "event_name": event_name,
        "job_id": job_id,
        "asset_id": asset_id
    }, "H2")
    # #endregion
    
    # Send event to Inngest
    try:
        await inngest_client.send(
            inngest.Event(name=event_name, data=event_data)
        )
        
        # #region agent log
        _debug_log("generate.py:inngest_send_success", "Event sent to Inngest successfully", {
            "event_name": event_name,
            "job_id": job_id
        }, "H2")
        # #endregion
    except Exception as exc:
        # #region agent log
        _debug_log("generate.py:inngest_send_failed", "Failed to send event to Inngest", {
            "error": str(exc),
            "error_type": type(exc).__name__,
            "event_name": event_name,
            "job_id": job_id
        }, "H2")
        # #endregion
        
        error_message = f"Failed to enqueue {gen_type} generation job"
        job_store.update_job_status(job_id, JobStatus.FAILED, error=str(exc))
        
        # Release reservation or refund credits on failure
        if user_id:
            if reservation_id:
                await credit_service.release_reservation(
                    reservation_id, 
                    reason=f"Failed to enqueue job: {str(exc)[:100]}"
                )
            elif credits_needed > 0:
                await credit_service.refund_credits(
                    user_id=user_id,
                    amount=credits_needed,
                    job_id=job_id,
                    description=f"Failed to enqueue job: {str(exc)[:100]}",
                )
        
        if asset_id:
            try:
                supabase_service.update_asset_status(
                    asset_id, status="failed", metadata={"error": str(exc)}
                )
            except Exception:
                pass  # Best effort
        raise HTTPException(status_code=503, detail=error_message)
    
    # #region agent log
    _debug_log("generate.py:success", "Generation job created successfully", {
        "job_id": job_id,
        "asset_id": asset_id,
        "gen_type": gen_type,
        "model_id": model_id
    }, "H1")
    # #endregion
    
    return JobResponse(
        job_id=job_id,
        asset_id=asset_id,
        status=JobStatus.PENDING,
        message=f"{gen_type.replace('-', ' ').title()} generation job created",
    )


# =============================================================================
# Unified Generation Endpoint
# =============================================================================

# #region agent log
def _debug_log(location: str, message: str, data: dict, hypothesis_id: str = ""):
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

@router.post(
    "",
    response_model=JobResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Generate content using any model",
    description="Unified endpoint for all generation types. Model determines the generation type.",
)
async def generate(
    request: GenerationRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_workplace_id: Optional[str] = Header(None, alias="X-Workplace-Id"),
) -> JobResponse:
    """
    Create a generation job using any model from the registry.
    
    The model ID determines the generation type (text-to-image, text-to-video, etc.).
    Parameters are validated dynamically against the model's schema in provider.json.
    """
    # #region agent log
    _debug_log("generate.py:entry", "Generate endpoint called", {
        "model": request.model,
        "user_id": x_user_id,
        "params_keys": list(request.params.keys()) if request.params else []
    }, "H1")
    # #endregion
    
    # Validate parameters against model's schema
    _validate_request_params(request.model, request.params)
    
    # #region agent log
    _debug_log("generate.py:validated", "Parameters validated, calling _create_generation_job", {
        "model": request.model
    }, "H1")
    # #endregion
    
    return await _create_generation_job(
        model_id=request.model,
        params=request.params,
        user_id=x_user_id,
        workplace_id=x_workplace_id,
        skip_validation=True,  # Already validated above
    )


# =============================================================================
# Type-Specific Endpoints (with dynamic validation)
# =============================================================================

@router.post(
    "/image",
    response_model=JobResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Generate image from text",
    description="Start an async text-to-image generation job",
)
async def generate_image(
    request: FlexibleImageRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_workplace_id: Optional[str] = Header(None, alias="X-Workplace-Id"),
) -> JobResponse:
    """Create a text-to-image generation job with dynamic validation."""
    # Get all params including extras
    params = request.model_dump(exclude={"model"}, exclude_none=True)
    
    return await _create_generation_job(
        model_id=request.model,
        params=params,
        user_id=x_user_id,
        workplace_id=x_workplace_id,
    )


@router.post(
    "/video",
    response_model=JobResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Generate video from text",
    description="Start an async text-to-video generation job",
)
async def generate_video(
    request: FlexibleVideoRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_workplace_id: Optional[str] = Header(None, alias="X-Workplace-Id"),
) -> JobResponse:
    """Create a text-to-video generation job with dynamic validation."""
    params = request.model_dump(exclude={"model"}, exclude_none=True)
    
    return await _create_generation_job(
        model_id=request.model,
        params=params,
        user_id=x_user_id,
        workplace_id=x_workplace_id,
    )


@router.post(
    "/video-from-image",
    response_model=JobResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Generate video from image",
    description="Start an async image-to-video generation job",
)
async def generate_video_from_image(
    request: FlexibleImageToVideoRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_workplace_id: Optional[str] = Header(None, alias="X-Workplace-Id"),
) -> JobResponse:
    """Create an image-to-video generation job with dynamic validation."""
    params = request.model_dump(exclude={"model"}, exclude_none=True)
    
    return await _create_generation_job(
        model_id=request.model,
        params=params,
        user_id=x_user_id,
        workplace_id=x_workplace_id,
    )


@router.post(
    "/speech",
    response_model=JobResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Generate speech from text",
    description="Start an async text-to-speech generation job",
)
async def generate_speech(
    request: FlexibleSpeechRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_workplace_id: Optional[str] = Header(None, alias="X-Workplace-Id"),
) -> JobResponse:
    """Create a text-to-speech generation job with dynamic validation."""
    params = request.model_dump(exclude={"model"}, exclude_none=True)
    
    return await _create_generation_job(
        model_id=request.model,
        params=params,
        user_id=x_user_id,
        workplace_id=x_workplace_id,
    )
