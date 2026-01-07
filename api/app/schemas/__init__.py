"""
Schemas Module

API request/response schemas for FastAPI.

Contains:
- api.py: Job schemas, error schemas
- generated.py: Auto-generated schemas from registry
"""

from .api import (
    # Enums
    JobStatus,
    # Job responses
    JobResponse,
    JobStatusResponse,
    # Error
    ErrorResponse,
    # Simplified schemas
    GenerateRequest,
    GenerateOutput,
    GenerateResponse,
    JobCreatedResponse,
    # API Key schemas
    CreateKeyRequest,
    CreateKeyResponse,
    ApiKeyMetadataResponse,
)

from .generated import (
    get_generated_models,
)

__all__ = [
    # Enums
    "JobStatus",
    # Job responses
    "JobResponse",
    "JobStatusResponse",
    # Error
    "ErrorResponse",
    # Simplified
    "GenerateRequest",
    "GenerateOutput",
    "GenerateResponse",
    "JobCreatedResponse",
    # API Key schemas
    "CreateKeyRequest",
    "CreateKeyResponse",
    "ApiKeyMetadataResponse",
    # Generated
    "get_generated_models",
]
