"""Application configuration using pydantic-settings.

Note: This configuration should stay aligned with the centralized constants
defined in packages/shared/src/config/constants.ts for consistency across
the entire Octupost platform.

Centralized values (from @octupost/shared):
  - Domain: octupost.com
  - Cookie Domain: .octupost.com
  - Ports: app=3000, studio=3001, social=3002, api=8000, mixpost=8001
  - Production URLs: app.octupost.com, studio.octupost.com, etc.
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


# =============================================================================
# Centralized Constants (should match @octupost/shared/config)
# =============================================================================

DOMAIN = "octupost.com"
COOKIE_DOMAIN = f".{DOMAIN}"

PORTS = {
    "app": 3000,
    "studio": 3001,
    "social": 3002,
    "api": 8000,
    "mixpost": 8001,
}

# Default CORS origins matching the centralized config
DEFAULT_CORS_ORIGINS = ",".join([
    f"http://localhost:{PORTS['app']}",
    f"http://localhost:{PORTS['studio']}",
    f"http://localhost:{PORTS['social']}",
    f"https://app.{DOMAIN}",
    f"https://studio.{DOMAIN}",
    f"https://social.{DOMAIN}",
])


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=("../.env.local", "../.env.development", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra env vars from shared .env files
    )

    # Fal AI Configuration
    fal_key: str = ""

    # Inngest Configuration
    inngest_event_key: str = ""
    inngest_signing_key: str = ""

    # Supabase Configuration
    # The service role key is needed for server-side operations that bypass RLS.
    # Falls back to NEXT_PUBLIC_ prefix for URL since .env is shared with frontend.
    supabase_url: str = ""
    next_public_supabase_url: str = ""  # Fallback if SUPABASE_URL not set
    supabase_service_role_key: str = ""
    
    @property
    def effective_supabase_url(self) -> str:
        """Get effective Supabase URL, preferring SUPABASE_URL over NEXT_PUBLIC_SUPABASE_URL."""
        return self.supabase_url or self.next_public_supabase_url

    # Redis Configuration (optional)
    redis_url: Optional[str] = None

    # Server Configuration (aligned with centralized PORTS)
    host: str = "0.0.0.0"
    port: int = PORTS["api"]
    debug: bool = False

    # CORS Configuration (uses centralized origins by default)
    cors_origins: str = DEFAULT_CORS_ORIGINS

    # Sentry Configuration
    sentry_dsn: str = ""
    environment: str = "development"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
