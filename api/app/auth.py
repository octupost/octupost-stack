"""Authentication dependencies for FastAPI endpoints."""

import logging
from dataclasses import dataclass
from typing import Literal, Optional

import jwt
from jwt import PyJWKClient
import sentry_sdk
from fastapi import Header, HTTPException

from app.config import get_settings
from app.services.api_key_service import api_key_service

logger = logging.getLogger(__name__)

# JWKS client for ES256 token verification (cached)
_jwks_client: Optional[PyJWKClient] = None


def _get_jwks_client() -> Optional[PyJWKClient]:
    """Get or create JWKS client for Supabase public key verification."""
    global _jwks_client
    if _jwks_client is None:
        settings = get_settings()
        supabase_url = settings.effective_supabase_url
        if supabase_url:
            jwks_url = f"{supabase_url}/auth/v1/.well-known/jwks.json"
            _jwks_client = PyJWKClient(jwks_url, cache_keys=True, lifespan=3600)
            logger.info(f"JWKS client initialized: {jwks_url}")
    return _jwks_client


@dataclass
class AuthContext:
    """
    Authentication context for API requests.

    Provides unified access to user identity regardless of auth method.
    """
    user_id: str
    workspace_id: Optional[str]
    auth_method: Literal["api_key", "header", "jwt"]
    api_key_id: Optional[str] = None
    project_id: Optional[str] = None


def verify_supabase_jwt(token: str) -> Optional[str]:
    """
    Verify a Supabase JWT and return the user_id.

    Supports both:
    - ES256 (asymmetric) - Modern Supabase projects, uses JWKS public key
    - HS256/HS384/HS512 (symmetric) - Legacy, uses JWT secret

    Returns None if verification fails.
    """
    settings = get_settings()

    try:
        # First, decode header to check the algorithm
        header = jwt.get_unverified_header(token)
        alg = header.get("alg", "unknown")

        # ES256 (Elliptic Curve) - use JWKS public key
        if alg in ["ES256", "ES384", "ES512", "RS256", "RS384", "RS512"]:
            jwks_client = _get_jwks_client()
            if not jwks_client:
                logger.warning("JWT verification failed: JWKS client not configured")
                return None

            # Get the signing key from JWKS
            signing_key = jwks_client.get_signing_key_from_jwt(token)

            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=[alg],
                audience="authenticated",
            )
            return payload.get("sub")

        # HS256/HS384/HS512 (symmetric) - use JWT secret
        elif alg in ["HS256", "HS384", "HS512"]:
            if not settings.supabase_jwt_secret:
                logger.warning("JWT verification failed: No JWT secret configured")
                return None

            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256", "HS384", "HS512"],
                audience="authenticated",
            )
            return payload.get("sub")

        else:
            logger.warning(f"JWT verification failed: Unsupported algorithm {alg}")
            return None

    except jwt.ExpiredSignatureError:
        logger.warning("JWT verification failed: Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"JWT verification failed: {type(e).__name__} - {e}")
        return None
    except Exception as e:
        logger.warning(f"JWT verification failed: {type(e).__name__} - {e}")
        return None


async def get_auth_context(
    authorization: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id", include_in_schema=False),
    x_workspace_id: Optional[str] = Header(None, alias="X-Workspace-Id", include_in_schema=False),
    x_project_id: Optional[str] = Header(None, alias="X-Project-Id", include_in_schema=False),
) -> AuthContext:
    """
    Triple authentication support:
    1. Bearer token (API key oct_sk_*) - for external developers
    2. Bearer token (Supabase JWT) - for frontend with JWT auth
    3. X-User-Id header - for internal frontend (legacy)

    Raises:
        HTTPException(401): If no valid authentication provided
    """
    # Try Bearer token (API key or JWT)
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]

        # Check if it's an API key (starts with oct_sk_)
        if token.startswith("oct_sk_"):
            key_info = await api_key_service.validate_key(token)

            if key_info:
                sentry_sdk.set_user({"id": key_info.user_id})
                sentry_sdk.set_tag("auth_method", "api_key")

                return AuthContext(
                    user_id=key_info.user_id,
                    workspace_id=x_workspace_id,
                    auth_method="api_key",
                    api_key_id=key_info.key_id,
                    project_id=x_project_id,
                )

            raise HTTPException(status_code=401, detail="Invalid API key")

        # Try as Supabase JWT
        user_id = verify_supabase_jwt(token)
        if user_id:
            sentry_sdk.set_user({"id": user_id})
            sentry_sdk.set_tag("auth_method", "jwt")

            return AuthContext(
                user_id=user_id,
                workspace_id=x_workspace_id,
                auth_method="jwt",
                project_id=x_project_id,
            )

        raise HTTPException(status_code=401, detail="Invalid token")

    # Fall back to X-User-Id header (internal frontend - legacy)
    if x_user_id:
        sentry_sdk.set_user({"id": x_user_id})
        sentry_sdk.set_tag("auth_method", "header")

        return AuthContext(
            user_id=x_user_id,
            workspace_id=x_workspace_id,
            auth_method="header",
            project_id=x_project_id,
        )

    raise HTTPException(status_code=401, detail="Authentication required")


async def get_optional_auth(
    authorization: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id", include_in_schema=False),
    x_workspace_id: Optional[str] = Header(None, alias="X-Workspace-Id", include_in_schema=False),
    x_project_id: Optional[str] = Header(None, alias="X-Project-Id", include_in_schema=False),
) -> Optional[AuthContext]:
    """
    Same as get_auth_context but returns None instead of raising.

    Use for endpoints that work with or without authentication.
    """
    # Try API key first (Bearer token)
    if authorization and authorization.startswith("Bearer "):
        api_key = authorization[7:]
        key_info = await api_key_service.validate_key(api_key)

        if key_info:
            sentry_sdk.set_user({"id": key_info.user_id})
            sentry_sdk.set_tag("auth_method", "api_key")

            return AuthContext(
                user_id=key_info.user_id,
                workspace_id=x_workspace_id,
                auth_method="api_key",
                api_key_id=key_info.key_id,
                project_id=x_project_id,
            )

        # User attempted to authenticate with an invalid key - reject
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Fall back to X-User-Id header (internal frontend)
    if x_user_id:
        sentry_sdk.set_user({"id": x_user_id})
        sentry_sdk.set_tag("auth_method", "header")

        return AuthContext(
            user_id=x_user_id,
            workspace_id=x_workspace_id,
            auth_method="header",
            project_id=x_project_id,
        )

    return None
