"""Application configuration using pydantic-settings.

Note: This configuration should stay aligned with the centralized constants
defined in packages/shared/src/config/constants.ts for consistency across
the entire Octupost platform.

Centralized values (from @octupost/shared):
  - Domain: octupost.com
  - Cookie Domain: .octupost.com
  - Ports: app=3000, studio=3001, social=3002 (mixpost), api=8000
  - Production URLs: app.octupost.com, social.octupost.com, api.octupost.com
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
    "social": 3002,  # Mixpost runs here
    "api": 8000,
}

# Default CORS origins matching the centralized config
DEFAULT_CORS_ORIGINS = ",".join([
    f"http://localhost:{PORTS['app']}",
    f"http://localhost:{PORTS['social']}",
    f"https://app.{DOMAIN}",
    "https://os.agno.com",  # Agno playground
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

    # OpenAI Configuration (for Agno agents)
    openai_api_key: str = ""
    
    # OpenRouter Configuration (for free LLM models)
    openrouter_api_key: str = ""
    
    # Stock Footage API Keys
    pexels_api_key: str = ""
    pixabay_api_key: str = ""

    # Inngest Configuration
    inngest_event_key: str = ""
    inngest_signing_key: str = ""

    # Supabase Configuration
    # The service role key is needed for server-side operations that bypass RLS.
    # Falls back to NEXT_PUBLIC_ prefix for URL since .env is shared with frontend.
    supabase_url: str = ""
    next_public_supabase_url: str = ""  # Fallback if SUPABASE_URL not set
    supabase_service_role_key: str = ""
    
    # Supabase Direct Database Connection (for Agno PostgresDb)
    # These are used to construct the PostgreSQL connection URL for Agno agents
    supabase_project_ref: str = ""  # e.g., "xyzabc123" from your project URL
    supabase_db_password: str = ""  # Database password for postgres user
    
    @property
    def effective_supabase_url(self) -> str:
        """Get effective Supabase URL, preferring SUPABASE_URL over NEXT_PUBLIC_SUPABASE_URL."""
        return self.supabase_url or self.next_public_supabase_url
    
    @property
    def supabase_db_url(self) -> Optional[str]:
        """
        Get the direct PostgreSQL connection URL for Supabase.
        
        Used by Agno PostgresDb for agent session/memory persistence.
        Returns None if required credentials are not configured.
        
        Uses direct connection (port 5432) for full Postgres feature support.
        """
        if not self.supabase_project_ref or not self.supabase_db_password:
            return None
        return f"postgresql://postgres:{self.supabase_db_password}@db.{self.supabase_project_ref}.supabase.co:5432/postgres"

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

    # Stripe Configuration
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_publishable_key: str = ""  # For reference (mainly used in frontend)

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
