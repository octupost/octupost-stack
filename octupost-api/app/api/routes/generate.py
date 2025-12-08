"""Generation API routes."""

from typing import Any, Optional

import inngest
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field

from app.inngest.client import inngest_client
from app.models.schemas import (
    ErrorResponse,
    JobResponse,
    JobStatus,
)
from app.registry import get_model, is_valid_model, validate_params, GenerationType
from app.services.job_store import job_store
from app.services.supabase_client import supabase_service


router = APIRouter()


# =============================================================================
# Request Models (simplified - validation happens via registry)
# =============================================================================

class GenerationRequest(BaseModel):
    """Unified generation request model."""
    model: str = Field(..., description="Model identifier from registry")
    params: dict[str, Any] = Field(default_factory=dict, description="Generation parameters")


class TextToImageRequest(BaseModel):
    """Text-to-image generation request."""
    model: str = Field(default="fal-ai/gpt-image-1-mini", description="Model identifier")
    prompt: str = Field(..., min_length=1, max_length=2000)
    width: int = Field(default=1024, ge=256, le=2048)
    height: int = Field(default=1024, ge=256, le=2048)
    aspect_ratio: Optional[str] = Field(default=None)
    num_images: int = Field(default=1, ge=1, le=4)
    negative_prompt: Optional[str] = Field(default=None, max_length=1000)
    seed: Optional[int] = Field(default=None, ge=0)
    guidance_scale: float = Field(default=7.5, ge=1.0, le=20.0)
    num_inference_steps: int = Field(default=4, ge=1, le=50)


class TextToVideoRequest(BaseModel):
    """Text-to-video generation request."""
    model: str = Field(default="fal-ai/infinity-star/text-to-video", description="Model identifier")
    prompt: str = Field(..., min_length=1, max_length=2000)
    aspect_ratio: str = Field(default="16:9")
    duration: int = Field(default=4, ge=2, le=16)
    negative_prompt: Optional[str] = Field(default=None, max_length=1000)
    seed: Optional[int] = Field(default=None, ge=0)
    guidance_scale: float = Field(default=5.0, ge=1.0, le=20.0)
    num_inference_steps: int = Field(default=30, ge=10, le=50)


class ImageToVideoRequest(BaseModel):
    """Image-to-video generation request."""
    model: str = Field(default="fal-ai/minimax-video/image-to-video", description="Model identifier")
    image_url: str = Field(..., description="URL of the source image")
    prompt: str = Field(..., min_length=1, max_length=2000)
    duration: int = Field(default=4, ge=2, le=10)
    negative_prompt: Optional[str] = Field(default=None, max_length=1000)
    seed: Optional[int] = Field(default=None, ge=0)


class TextToSpeechRequest(BaseModel):
    """Text-to-speech generation request."""
    model: str = Field(default="fal-ai/kokoro", description="Model identifier")
    text: str = Field(..., min_length=1, max_length=5000)
    voice: str = Field(default="af_bella")
    speed: float = Field(default=1.0, ge=0.5, le=2.0)


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
    """Map generation type to asset type."""
    mapping = {
        "text-to-image": "image",
        "text-to-video": "video",
        "image-to-video": "video",
        "text-to-speech": "speech",
        "text-to-audio": "audio",
    }
    return mapping.get(gen_type, "unknown")


def _get_event_name(gen_type: str) -> str:
    """Get the Inngest event name for a generation type."""
    mapping = {
        "text-to-image": "ai/image.generate",
        "text-to-video": "ai/video.generate",
        "image-to-video": "ai/video-from-image.generate",
        "text-to-speech": "ai/speech.generate",
    }
    return mapping.get(gen_type, "ai/generate")


async def _create_generation_job(
    model_id: str,
    params: dict[str, Any],
    user_id: Optional[str],
    workplace_id: Optional[str],
) -> JobResponse:
    """
    Common logic for creating a generation job.
    
    Args:
        model_id: The model identifier
        params: Generation parameters
        user_id: Optional user ID for asset tracking
        workplace_id: Optional workplace ID
        
    Returns:
        JobResponse with job and asset IDs
    """
    # Validate model
    if not is_valid_model(model_id):
        raise HTTPException(status_code=400, detail=f"Invalid or disabled model: {model_id}")
    
    # Get generation type from registry
    gen_type = _get_generation_type(model_id)
    asset_type = _get_asset_type(gen_type)
    event_name = _get_event_name(gen_type)
    
    # Create job record
    job_id = job_store.create_job(
        job_type=gen_type,
        request_data={"model": model_id, **params},
    )
    
    # Create asset record if user is authenticated
    asset_id = None
    if user_id:
        asset = supabase_service.create_asset(
            owner_id=user_id,
            asset_type=asset_type,
            source="generative_ai",
            generation_params={"model": model_id, **params},
            workplace_id=workplace_id,
        )
        asset_id = asset.get("id") if asset else None
    
    # Prepare event data
    event_data = {
        "job_id": job_id,
        "asset_id": asset_id,
        "model": model_id,
        **params,
    }
    
    # Send event to Inngest
    try:
        await inngest_client.send(
            inngest.Event(name=event_name, data=event_data)
        )
    except Exception as exc:
        error_message = f"Failed to enqueue {gen_type} generation job"
        job_store.update_job_status(job_id, JobStatus.FAILED, error=str(exc))
        if asset_id:
            try:
                supabase_service.update_asset_status(
                    asset_id, status="failed", metadata={"error": str(exc)}
                )
            except Exception:
                pass  # Best effort
        raise HTTPException(status_code=503, detail=error_message)
    
    return JobResponse(
        job_id=job_id,
        asset_id=asset_id,
        status=JobStatus.PENDING,
        message=f"{gen_type.replace('-', ' ').title()} generation job created",
    )


# =============================================================================
# Unified Generation Endpoint
# =============================================================================

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
    Parameters are validated against the model's schema in the registry.
    """
    return await _create_generation_job(
        model_id=request.model,
        params=request.params,
        user_id=x_user_id,
        workplace_id=x_workplace_id,
    )


# =============================================================================
# Legacy Endpoints (for backward compatibility)
# =============================================================================

@router.post(
    "/image",
    response_model=JobResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Generate image from text",
    description="Start an async text-to-image generation job",
)
async def generate_image(
    request: TextToImageRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_workplace_id: Optional[str] = Header(None, alias="X-Workplace-Id"),
) -> JobResponse:
    """Create a text-to-image generation job."""
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
    request: TextToVideoRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_workplace_id: Optional[str] = Header(None, alias="X-Workplace-Id"),
) -> JobResponse:
    """Create a text-to-video generation job."""
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
    request: ImageToVideoRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_workplace_id: Optional[str] = Header(None, alias="X-Workplace-Id"),
) -> JobResponse:
    """Create an image-to-video generation job."""
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
    request: TextToSpeechRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_workplace_id: Optional[str] = Header(None, alias="X-Workplace-Id"),
) -> JobResponse:
    """Create a text-to-speech generation job."""
    params = request.model_dump(exclude={"model"}, exclude_none=True)
    return await _create_generation_job(
        model_id=request.model,
        params=params,
        user_id=x_user_id,
        workplace_id=x_workplace_id,
    )
