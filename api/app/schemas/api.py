"""
API Schemas

Pydantic schemas for API request/response models.

Merged from:
- models/schemas.py
- octupost/schemas/request.py
- octupost/schemas/response.py
"""

from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, model_validator


# =============================================================================
# Enums
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
# Error Models
# =============================================================================


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict[str, Any]] = Field(None, description="Additional error details")


# =============================================================================
# Simplified Request Schema (GenerateRequest)
# =============================================================================


class GenerateRequest(BaseModel):
    """
    Simplified, user-friendly generation request.

    This schema provides a unified interface for all generation types.
    The generation mode is explicitly specified by the caller.
    """

    # Required: Model
    model: str = Field(
        ...,
        description="Model ID (semantic like 'openai/gpt-image-1-mini' or 'google/veo-3.1')",
        examples=["openai/gpt-image-1-mini", "google/veo-3.1", "kling/v2.0"],
    )

    # Required: Mode
    mode: str = Field(
        ...,
        description="Generation mode (e.g., 'text-to-image', 'image-to-image', 'text-to-video')",
        examples=["text-to-image", "image-to-image", "text-to-video", "image-to-video"],
    )
    
    # Content (at least one required)
    prompt: Optional[str] = Field(None, max_length=4000, description="Text prompt for image/video generation")
    text: Optional[str] = Field(None, max_length=10000, description="Text for speech synthesis (TTS)")
    script: Optional[str] = Field(None, max_length=5000, description="Script for avatar/talking head videos")
    negative_prompt: Optional[str] = Field(None, max_length=1000, description="What to avoid in generation")
    
    # Media Inputs (determine mode)
    first_frame_url: Optional[str] = Field(None, description="Image URL for first frame -> triggers image-to-video mode")
    last_frame_url: Optional[str] = Field(None, description="Image URL for last frame -> with first_frame_url triggers first-last-frame mode")
    reference_image_urls: Optional[list[str]] = Field(None, description="Reference image URLs -> triggers reference-to-video mode")
    image_url: Optional[str] = Field(None, description="Image URL -> triggers image-to-image mode")
    video_url: Optional[str] = Field(None, description="Video URL -> triggers extend/retake mode")
    
    # Universal Parameters
    aspect_ratio: Optional[str] = Field(
        None,
        description="Aspect ratio: portrait, landscape, square, or numeric (16:9)",
        examples=["portrait", "landscape", "square", "16:9", "9:16"],
    )
    resolution: Optional[str] = Field(None, description="Resolution tier: 720p, 1080p, 4k", examples=["720p", "1080p", "4k"])
    duration: Optional[int] = Field(None, ge=1, le=120, description="Duration in seconds (video/audio)")
    
    # Audio/Speech Parameters
    voice: Optional[str] = Field(None, description="Voice name or ID", examples=["rachel", "adam", "sarah", "af_bella"])
    language: Optional[str] = Field(None, description="ISO 639-1 language code", examples=["en", "es", "fr", "de", "tr"])
    
    # Advanced Parameters
    seed: Optional[int] = Field(None, ge=0, description="Random seed for reproducibility")
    enhance_prompt: Optional[bool] = Field(None, description="Enable AI prompt enhancement")
    guidance_scale: Optional[float] = Field(None, ge=1.0, le=20.0, description="Guidance scale for generation")
    num_inference_steps: Optional[int] = Field(None, ge=1, le=100, description="Number of inference steps")
    num_images: Optional[int] = Field(None, ge=1, le=4, description="Number of images to generate")
    
    # Voice-specific settings
    stability: Optional[float] = Field(None, ge=0.0, le=1.0, description="Voice stability (ElevenLabs)")
    similarity_boost: Optional[float] = Field(None, ge=0.0, le=1.0, description="Voice similarity boost (ElevenLabs)")
    style: Optional[float] = Field(None, ge=0.0, le=1.0, description="Voice style exaggeration (ElevenLabs)")
    speed: Optional[float] = Field(None, ge=0.5, le=2.0, description="Speech speed multiplier")
    
    # Video-specific settings
    extend: Optional[bool] = Field(None, description="Extend source video instead of retaking")
    
    @model_validator(mode="after")
    def validate_content(self):
        """Ensure at least one content field is provided."""
        if not any([self.prompt, self.text, self.script]):
            raise ValueError("At least one of prompt, text, or script is required")
        return self
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in self.model_dump().items() if v is not None}


# =============================================================================
# Simplified Response Schemas
# =============================================================================


class GenerateOutput(BaseModel):
    """Generated media output."""
    
    url: str = Field(..., description="URL of the generated media")
    content_type: str = Field(..., description="MIME type (e.g., 'video/mp4', 'image/png', 'audio/mpeg')")
    width: Optional[int] = Field(None, description="Width in pixels (for images/videos)")
    height: Optional[int] = Field(None, description="Height in pixels (for images/videos)")
    duration: Optional[float] = Field(None, description="Duration in seconds (for videos/audio)")
    file_name: Optional[str] = Field(None, description="Original file name")
    file_size: Optional[int] = Field(None, description="File size in bytes")


class GenerateResponse(BaseModel):
    """Simplified generation response."""
    
    id: str = Field(..., description="Unique job/generation ID")
    status: Literal["pending", "processing", "completed", "failed", "cancelled"] = Field(..., description="Current status")
    model: str = Field(..., description="Friendly model name used")
    mode: str = Field(..., description="Inferred generation mode (e.g., 'text-to-video')")
    output: Optional[GenerateOutput] = Field(None, description="Generated output (present when completed)")
    outputs: Optional[list[GenerateOutput]] = Field(None, description="Multiple outputs (for batch generation)")
    credits_used: Optional[int] = Field(None, description="Number of credits consumed")
    error: Optional[str] = Field(None, description="Error message (present when failed)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the job was created")
    completed_at: Optional[datetime] = Field(None, description="When the job completed")
    asset_id: Optional[str] = Field(None, description="Associated asset ID (for authenticated users)")
    progress: Optional[int] = Field(None, ge=0, le=100, description="Progress percentage (for long-running jobs)")


class JobCreatedResponse(BaseModel):
    """Response when a new generation job is created."""

    job_id: str = Field(..., description="Unique job identifier for polling status")
    asset_id: Optional[str] = Field(None, description="Associated asset ID (for authenticated users)")
    status: Literal["pending"] = Field(default="pending", description="Initial status (always 'pending')")
    model: str = Field(..., description="Resolved model endpoint")
    mode: str = Field(..., description="Inferred generation mode")
    credits_estimated: Optional[int] = Field(None, description="Estimated credits for this generation")
    message: str = Field(default="Job created successfully", description="Status message")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Job creation timestamp")


# =============================================================================
# API Key Management Schemas
# =============================================================================


class CreateKeyRequest(BaseModel):
    """Request to create a new API key."""

    name: str = Field(
        default="Default",
        max_length=100,
        description="Human-readable name for the key",
        examples=["Production", "Development", "Testing"],
    )


class CreateKeyResponse(BaseModel):
    """Response when an API key is created."""

    key: str = Field(
        ...,
        description="The API key. Store this securely - it will only be shown once.",
        examples=["oct_sk_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"],
    )
    key_id: str = Field(..., description="Unique key identifier for management operations")
    message: str = Field(
        default="Store this key securely. It will not be shown again.",
        description="Important security notice",
    )


class ApiKeyMetadataResponse(BaseModel):
    """API key metadata (without the secret)."""

    id: str = Field(..., description="Unique key identifier")
    name: str = Field(..., description="Human-readable name")
    key_prefix: str = Field(
        ...,
        description="First 16 characters of the key for identification",
        examples=["oct_sk_a1b2c3d4"],
    )
    created_at: datetime = Field(..., description="When the key was created")
    last_used_at: Optional[datetime] = Field(None, description="When the key was last used")
    is_active: bool = Field(..., description="Whether the key is active")

