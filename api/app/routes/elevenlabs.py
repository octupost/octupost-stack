"""ElevenLabs API routes for voice and model listing and TTS generation."""

from typing import Any, Optional

import inngest
import sentry_sdk
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field

from app.inngest.client import inngest_client
from app.models.schemas import JobResponse, JobStatus
from app.services.providers.elevenlabs_provider import elevenlabs_provider, ELEVENLABS_MODELS
from app.services.job_store import job_store
from app.services.supabase_client import supabase_service


router = APIRouter()


# =============================================================================
# Response Models
# =============================================================================

class VoiceResponse(BaseModel):
    """Voice information response."""
    id: str
    name: str
    category: str
    description: str = ""
    preview_url: Optional[str] = None
    labels: dict[str, Any] = {}


class VoiceDetailResponse(VoiceResponse):
    """Detailed voice information with settings."""
    settings: dict[str, Any] = {}


class ModelResponse(BaseModel):
    """TTS model information response."""
    id: str
    name: str
    description: str
    languages: int


class VoicesListResponse(BaseModel):
    """List of voices response."""
    voices: list[VoiceResponse]


class ModelsListResponse(BaseModel):
    """List of models response."""
    models: list[ModelResponse]


class TTSRequest(BaseModel):
    """Text-to-speech generation request."""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to convert to speech")
    voice_id: str = Field(..., description="ElevenLabs voice ID")
    model_id: str = Field(default="eleven_multilingual_v2", description="ElevenLabs model ID")
    stability: Optional[float] = Field(default=0.5, ge=0, le=1, description="Voice stability (0-1)")
    similarity_boost: Optional[float] = Field(default=0.75, ge=0, le=1, description="Similarity boost (0-1)")
    style: Optional[float] = Field(default=0.0, ge=0, le=1, description="Style exaggeration (0-1)")
    speed: Optional[float] = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed (0.5-2.0)")


# =============================================================================
# Routes
# =============================================================================

@router.get(
    "/voices",
    response_model=VoicesListResponse,
    summary="List available voices",
    description="Get all available ElevenLabs voices for text-to-speech",
)
async def list_voices() -> VoicesListResponse:
    """
    List all available ElevenLabs voices.
    
    Returns voices from the user's ElevenLabs account including:
    - Premade voices (default ElevenLabs voices)
    - Professional voices
    - Cloned voices (if the user has created any)
    """
    try:
        voices = await elevenlabs_provider.get_voices()
        return VoicesListResponse(
            voices=[VoiceResponse(**v) for v in voices]
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch voices: {str(e)}")


@router.get(
    "/voices/{voice_id}",
    response_model=VoiceDetailResponse,
    summary="Get voice details",
    description="Get detailed information for a specific voice including settings",
)
async def get_voice(voice_id: str) -> VoiceDetailResponse:
    """
    Get detailed information for a specific voice.
    
    Returns voice details including:
    - Name and description
    - Category (premade, professional, cloned)
    - Preview audio URL
    - Default voice settings
    """
    try:
        voice = await elevenlabs_provider.get_voice(voice_id)
        return VoiceDetailResponse(**voice)
    except ValueError as e:
        raise HTTPException(status_code=404 if "not found" in str(e).lower() else 500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch voice: {str(e)}")


@router.get(
    "/models",
    response_model=ModelsListResponse,
    summary="List available TTS models",
    description="Get all available ElevenLabs text-to-speech models",
)
async def list_models() -> ModelsListResponse:
    """
    List all available ElevenLabs TTS models.
    
    Returns models with their supported language counts:
    - eleven_v3: 72 languages (newest, best quality)
    - eleven_multilingual_v2: 29 languages (high quality)
    - eleven_flash_v2_5: 32 languages (fast, good quality)
    - eleven_turbo_v2_5: 32 languages (fastest multilingual)
    - eleven_turbo_v2: English only (fastest)
    """
    try:
        models = elevenlabs_provider.get_models()
        return ModelsListResponse(
            models=[ModelResponse(**m) for m in models]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch models: {str(e)}")


@router.post(
    "/tts",
    response_model=JobResponse,
    summary="Generate speech from text",
    description="Start an async ElevenLabs text-to-speech generation job",
)
async def generate_tts(
    request: TTSRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_workplace_id: Optional[str] = Header(None, alias="X-Workplace-Id"),
) -> JobResponse:
    """
    Generate speech from text using ElevenLabs.
    
    Creates an async job that will:
    1. Call ElevenLabs TTS API
    2. Upload the audio to Supabase storage
    3. Create an asset record
    4. Update job status
    """
    # Set user context in Sentry
    if x_user_id:
        sentry_sdk.set_user({"id": x_user_id})
    
    # Validate model
    if request.model_id not in ELEVENLABS_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid ElevenLabs model: {request.model_id}. Valid models: {list(ELEVENLABS_MODELS.keys())}"
        )
    
    # Build model ID with provider prefix
    full_model_id = f"elevenlabs/{request.model_id}"
    
    # Build params
    params = {
        "text": request.text,
        "voice_id": request.voice_id,
        "model_id": request.model_id,
        "stability": request.stability,
        "similarity_boost": request.similarity_boost,
        "style": request.style,
        "speed": request.speed,
    }
    
    # Create job record
    job_id = job_store.create_job(
        job_type="text-to-speech",
        request_data={
            "model": full_model_id,
            "provider": "elevenlabs",
            **params,
        },
        owner_id=x_user_id,
    )
    
    # Create asset record if user is authenticated
    asset_id = None
    if x_user_id:
        asset = supabase_service.create_asset(
            owner_id=x_user_id,
            asset_type="speech",
            media_type="audio",
            source="generative_ai",
            generation_params={"model": full_model_id, **params},
            workplace_id=x_workplace_id,
        )
        asset_id = asset.get("id") if asset else None
        
        if asset_id:
            job_store.set_job_asset(job_id, asset_id)
    
    # Prepare event data for Inngest
    event_data = {
        "job_id": job_id,
        "asset_id": asset_id,
        "model": full_model_id,
        "user_id": x_user_id,
        "provider": "elevenlabs",
        **params,
    }
    
    # Send to Inngest for async processing
    try:
        await inngest_client.send(
            inngest.Event(name="ai/speech.generate", data=event_data)
        )
    except Exception as exc:
        job_store.update_job_status(job_id, JobStatus.FAILED, error=str(exc))
        
        if asset_id:
            try:
                supabase_service.update_asset_status(
                    asset_id, status="failed", metadata={"error": str(exc)}
                )
            except Exception:
                pass
        
        raise HTTPException(
            status_code=503,
            detail=f"Failed to enqueue TTS job: {str(exc)}"
        )
    
    return JobResponse(
        job_id=job_id,
        asset_id=asset_id,
        status=JobStatus.PENDING,
        message="ElevenLabs TTS job created",
    )

