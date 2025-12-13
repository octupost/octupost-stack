"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager

import sentry_sdk
import inngest.fast_api
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration

# Inngest integration is optional; fall back gracefully if the extra is missing.
try:
    from sentry_sdk.integrations.inngest import InngestIntegration
except ImportError:
    InngestIntegration = None

from app.config import get_settings
from app.routes import generate, jobs
from app.inngest.client import inngest_client
from app.inngest.functions import all_functions

# Initialize Sentry
settings = get_settings()
if settings.sentry_dsn:
    is_dev_env = settings.environment.lower() == "development"

    def _before_send(event, hint):
        """Scrub sensitive request details before sending to Sentry."""
        request = event.get("request")
        if request:
            request.pop("cookies", None)
            headers = request.get("headers") or {}
            # Drop authorization-like headers
            headers = {
                k: v for k, v in headers.items() if k.lower() not in {"authorization", "cookie"}
            }
            if headers:
                request["headers"] = headers
            else:
                request.pop("headers", None)
        return event

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[
            FastApiIntegration(),
            *( [InngestIntegration()] if InngestIntegration else [] ),
        ],
        traces_sample_rate=1.0 if is_dev_env else 0.2,
        profiles_sample_rate=1.0 if is_dev_env else 0.1,
        environment=settings.environment,
        release=os.getenv("SENTRY_RELEASE") or os.getenv("VERCEL_GIT_COMMIT_SHA"),
        send_default_pii=False,
        before_send=_before_send,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    settings = get_settings()
    
    # Set Fal AI key in environment
    if settings.fal_key:
        os.environ["FAL_KEY"] = settings.fal_key
    
    # Set OpenAI API key for Agno agents
    if settings.openai_api_key:
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key
    
    # Set OpenRouter API key for Content Team agents
    if settings.openrouter_api_key:
        os.environ["OPENROUTER_API_KEY"] = settings.openrouter_api_key
    
    yield
    
    # Cleanup on shutdown (if needed)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Octupost API",
        description="AI Generation Backend for Octupost - Text-to-Image, Text-to-Video, Image-to-Video, and Text-to-Speech",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API routes
    app.include_router(generate.router, prefix="/api/generate", tags=["Generation"])
    app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])

    # Register Inngest webhook handler
    inngest.fast_api.serve(
        app,
        inngest_client,
        all_functions,
    )

    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "api"}

    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with API information."""
        return {
            "service": "Octupost API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health",
        }

    return app


# Create the application instance
app = create_app()

