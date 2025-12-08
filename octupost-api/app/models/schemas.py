"""Pydantic schemas for API request/response models.

Note: Model-specific enums have been removed in favor of the centralized
model registry. Validation of model IDs and parameters now happens via
the registry module.

See: app/registry/ for model definitions and validation functions.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# =============================================================================
# Enums (only job/status enums remain - model enums moved to registry)
# =============================================================================


class JobStatus(str, Enum):
    """Status of a generation job."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# =============================================================================
# Job Response Models
# =============================================================================


class JobResponse(BaseModel):
    """Response model for job creation."""

    job_id: str = Field(..., description="Unique job identifier")
    asset_id: Optional[str] = Field(None, description="Associated asset ID if user is authenticated")
    status: JobStatus = Field(default=JobStatus.PENDING, description="Current job status")
    message: str = Field(default="Job created successfully", description="Status message")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Job creation timestamp")


class JobStatusResponse(BaseModel):
    """Response model for job status queries."""

    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    progress: Optional[int] = Field(None, ge=0, le=100, description="Progress percentage")
    result: Optional[dict[str, Any]] = Field(None, description="Generation result when completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Job creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


# =============================================================================
# Result Models
# =============================================================================


class ImageResult(BaseModel):
    """Result model for a generated image."""

    url: str = Field(..., description="URL of the generated image")
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")
    content_type: str = Field(default="image/png", description="MIME type of the image")


class TextToImageResult(BaseModel):
    """Result model for text-to-image generation."""

    images: list[ImageResult] = Field(..., description="List of generated images")
    seed: int = Field(..., description="Seed used for generation")
    prompt: str = Field(..., description="Prompt used for generation")


class VideoResult(BaseModel):
    """Result model for a generated video."""

    url: str = Field(..., description="URL of the generated video")
    duration: float = Field(..., description="Video duration in seconds")
    width: int = Field(..., description="Video width in pixels")
    height: int = Field(..., description="Video height in pixels")
    content_type: str = Field(default="video/mp4", description="MIME type of the video")


class TextToVideoResult(BaseModel):
    """Result model for text-to-video generation."""

    video: VideoResult = Field(..., description="Generated video")
    seed: int = Field(..., description="Seed used for generation")
    prompt: str = Field(..., description="Prompt used for generation")


class ImageToVideoResult(BaseModel):
    """Result model for image-to-video generation."""

    video: VideoResult = Field(..., description="Generated video")
    seed: int = Field(..., description="Seed used for generation")
    source_image: str = Field(..., description="Source image URL")


class AudioResult(BaseModel):
    """Result model for generated audio."""

    url: str = Field(..., description="URL of the generated audio")
    duration: float = Field(..., description="Audio duration in seconds")
    content_type: str = Field(default="audio/wav", description="MIME type of the audio")


class TextToSpeechResult(BaseModel):
    """Result model for text-to-speech generation."""

    audio: AudioResult = Field(..., description="Generated audio")
    text: str = Field(..., description="Input text")
    voice: str = Field(..., description="Voice used")


# =============================================================================
# Error Models
# =============================================================================


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict[str, Any]] = Field(None, description="Additional error details")


# =============================================================================
# Legacy Request Models (kept for backward compatibility)
# These are now defined in generate.py routes with string model fields
# instead of enum fields. The schemas below are kept for reference/import.
# =============================================================================


class TextToImageRequest(BaseModel):
    """Request model for text-to-image generation."""

    model: str = Field(default="fal-ai/gpt-image-1-mini", description="Model identifier from registry")
    prompt: str = Field(..., min_length=1, max_length=2000, description="The generation prompt")
    width: int = Field(default=1024, ge=256, le=2048, description="Output image width")
    height: int = Field(default=1024, ge=256, le=2048, description="Output image height")
    aspect_ratio: Optional[str] = Field(None, description="Aspect ratio (overrides width/height)")
    num_images: int = Field(default=1, ge=1, le=4, description="Number of images to generate")
    negative_prompt: Optional[str] = Field(None, max_length=1000, description="What to avoid in generation")
    seed: Optional[int] = Field(None, ge=0, description="Random seed for reproducibility")
    guidance_scale: float = Field(default=7.5, ge=1.0, le=20.0, description="Guidance scale for generation")
    num_inference_steps: int = Field(default=4, ge=1, le=50, description="Number of inference steps")


class TextToVideoRequest(BaseModel):
    """Request model for text-to-video generation."""

    model: str = Field(default="fal-ai/infinity-star/text-to-video", description="Model identifier from registry")
    prompt: str = Field(..., min_length=1, max_length=2000, description="The generation prompt")
    aspect_ratio: str = Field(default="16:9", description="Video aspect ratio")
    duration: int = Field(default=4, ge=2, le=16, description="Video duration in seconds")
    negative_prompt: Optional[str] = Field(None, max_length=1000, description="What to avoid in generation")
    seed: Optional[int] = Field(None, ge=0, description="Random seed for reproducibility")
    guidance_scale: float = Field(default=5.0, ge=1.0, le=20.0, description="Guidance scale")
    num_inference_steps: int = Field(default=30, ge=10, le=50, description="Number of inference steps")


class ImageToVideoRequest(BaseModel):
    """Request model for image-to-video generation."""

    model: str = Field(default="fal-ai/minimax-video/image-to-video", description="Model identifier from registry")
    image_url: str = Field(..., description="URL of the source image")
    prompt: str = Field(..., min_length=1, max_length=2000, description="Motion/animation prompt")
    negative_prompt: Optional[str] = Field(None, max_length=1000, description="What to avoid")
    duration: int = Field(default=4, ge=2, le=10, description="Video duration in seconds")
    seed: Optional[int] = Field(None, ge=0, description="Random seed for reproducibility")


class TextToSpeechRequest(BaseModel):
    """Request model for text-to-speech generation."""

    model: str = Field(default="fal-ai/kokoro", description="Model identifier from registry")
    text: str = Field(..., min_length=1, max_length=5000, description="Text to convert to speech")
    voice: str = Field(default="af_bella", description="Voice identifier")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed multiplier")
