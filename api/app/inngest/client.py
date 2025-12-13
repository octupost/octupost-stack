"""Inngest client configuration."""

import inngest

from app.config import get_settings


# Create Inngest client
inngest_client = inngest.Inngest(
    app_id="api",
    is_production=not get_settings().debug,
)

