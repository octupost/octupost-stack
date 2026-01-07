"""
Inngest Worker

Background job orchestration with Inngest.
All Inngest client setup and function handlers in one file.

Credit Handling (Reservation Pattern):
- Credits are RESERVED before generation starts (in the API route)
- FAL validates the request BEFORE returning to user
- Inngest polls FAL for completion with real progress
- On success: settle reservation with actual credits
- On failure: release reservation (full refund)

Response Format:
- All providers return normalized responses with consistent structure:
  {
      "outputs": [{ url, content_type, file_name, file_size, width, height, duration }],
      "media_type": "image" | "video" | "audio",
      # Extra fields preserved as-is (timestamps, seed, etc.)
  }

Error Handling (NO FALLBACKS for development):
- All errors are raised immediately, not masked
- Fal errors are parsed and stored with full structure
- Retries are DISABLED in development mode
"""

import json
from typing import Any

import inngest
import sentry_sdk

from app.config import get_settings
from app.services.supabase_client import supabase_service
from app.services.job_store import job_store
from app.services.fal_queue import poll_until_complete, FalQueueError
from app.billing import credit_service
from app.schemas import JobStatus


def _extract_fal_error(exception: Exception) -> dict[str, Any]:
    """
    Extract structured error information from Fal API exceptions.

    Fal returns structured errors like:
    {
        "detail": [
            {"loc": ["body", "prompt"], "msg": "field required", "type": "value_error.missing"}
        ]
    }

    This function preserves that structure for better debugging.
    """
    error_info: dict[str, Any] = {
        "message": str(exception),
        "type": type(exception).__name__,
    }

    # Try to extract structured error details
    exc_str = str(exception)

    # Check if it's a JSON-like error from Fal
    if "detail" in exc_str:
        try:
            # Try to parse JSON from the exception message
            # Fal errors often look like: "Error: {'detail': [...]}"
            start = exc_str.find("{")
            end = exc_str.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = exc_str[start:end].replace("'", '"')
                parsed = json.loads(json_str)
                if isinstance(parsed, dict):
                    error_info["fal_detail"] = parsed.get("detail", [])
                    # Extract field-level errors
                    if error_info["fal_detail"]:
                        field_errors = []
                        for err in error_info["fal_detail"]:
                            if isinstance(err, dict):
                                loc = err.get("loc", [])
                                field = loc[-1] if loc else "unknown"
                                field_errors.append({
                                    "field": field,
                                    "message": err.get("msg", "Unknown error"),
                                    "type": err.get("type", "unknown"),
                                })
                        if field_errors:
                            error_info["field_errors"] = field_errors
        except (json.JSONDecodeError, ValueError):
            pass

    # Check for common error patterns
    if "rate limit" in exc_str.lower():
        error_info["is_rate_limit"] = True
        error_info["is_retryable"] = True
    elif "timeout" in exc_str.lower():
        error_info["is_timeout"] = True
        error_info["is_retryable"] = True
    elif "validation" in exc_str.lower() or "value_error" in exc_str.lower():
        error_info["is_validation_error"] = True
        error_info["is_retryable"] = False
    elif "not found" in exc_str.lower() or "404" in exc_str:
        error_info["is_not_found"] = True
        error_info["is_retryable"] = False

    return error_info


# =============================================================================
# Inngest Client
# =============================================================================

settings = get_settings()
IS_DEVELOPMENT = settings.debug

inngest_client = inngest.Inngest(
    app_id="api",
    is_production=not IS_DEVELOPMENT,
)

# Retry configuration:
# - Development: 0 retries (fail fast, see errors immediately)
# - Production: 2 retries (handle transient failures)
INNGEST_RETRIES = 0 if IS_DEVELOPMENT else 2


# =============================================================================
# Poll Event Handler
# =============================================================================


@inngest_client.create_function(
    fn_id="generate-poll",
    trigger=inngest.TriggerEvent(event="ai/generate.poll"),
    retries=INNGEST_RETRIES,  # 0 in dev (fail fast), 2 in prod
)
async def generate_poll_fn(ctx: inngest.Context) -> dict:
    """
    Poll a FAL request that was already submitted and validated.

    New workflow:
    1. FAL request was submitted in API route (validated there)
    2. This function polls until completion with real progress updates
    3. On success: settle credit reservation
    4. On failure: release credit reservation (full refund)

    Event data:
    - job_id: Job ID in our system
    - asset_id: Asset ID for the result
    - model: Model ID (e.g., "fal-ai/flux/dev")
    - endpoint: FAL endpoint
    - fal_request_id: FAL's request ID for polling
    - user_id: User who initiated the request
    - reservation_id: Credit reservation ID
    - credits_estimated: Estimated credits for this job
    """
    event_data = ctx.event.data
    job_id = event_data.get("job_id")
    asset_id = event_data.get("asset_id")
    model_id = event_data.get("model")
    endpoint = event_data.get("endpoint")
    fal_request_id = event_data.get("fal_request_id")
    user_id = event_data.get("user_id")
    reservation_id = event_data.get("reservation_id")
    credits_estimated = event_data.get("credits_estimated", 0)
    mode = event_data.get("mode", "")  # Generation mode for response normalization
    original_params = event_data.get("original_params", {})  # For dimension defaults

    # Validate required fields
    if not fal_request_id:
        raise ValueError("fal_request_id is required for polling")
    if not endpoint:
        raise ValueError("endpoint is required for polling")
    if not model_id:
        raise ValueError("model is required for polling")

    sentry_sdk.set_context("job", {
        "job_id": job_id,
        "asset_id": asset_id,
        "model_id": model_id,
        "mode": mode,
        "fal_request_id": fal_request_id,
        "user_id": user_id,
        "reservation_id": reservation_id,
        "credits_estimated": credits_estimated,
    })

    # Set initial heartbeat - job is considered stale if no heartbeat in 10 minutes
    if job_id:
        job_store.update_heartbeat(job_id, timeout_seconds=600)

    # Progress tracking - starts at 5% (already in queue from API)
    last_progress = 5

    def on_progress(update: dict[str, Any]) -> None:
        """Update job progress based on real FAL status."""
        nonlocal last_progress

        status = update.get("status", "")
        logs = update.get("logs", [])
        queue_position = update.get("queue_position")

        # Calculate progress based on status and logs
        if status == "in_queue":
            # In queue: 5-10% based on queue position
            if queue_position is not None and queue_position > 0:
                progress = max(5, 10 - min(queue_position, 5))
            else:
                progress = 10
        elif status == "in_progress":
            # In progress: 15-90% based on log count
            # Each log entry = ~5% progress, max 90%
            log_progress = len(logs) * 5
            progress = min(15 + log_progress, 90)
        else:
            progress = last_progress

        # Only update if progress increased
        if progress > last_progress and job_id:
            last_progress = progress
            job_store.update_job_status(job_id, JobStatus.PROCESSING, progress=progress)
            # Extend heartbeat deadline on each progress update
            job_store.update_heartbeat(job_id, timeout_seconds=600)

    try:
        # Poll FAL until completion (response is normalized via inbound_schema)
        async def _poll():
            return await poll_until_complete(
                request_id=fal_request_id,
                endpoint=endpoint,
                model_id=model_id,
                mode=mode,
                original_params=original_params,
                on_progress=on_progress,
                timeout_seconds=600.0,  # 10 minute timeout
            )

        result = await ctx.step.run("poll-fal", _poll)

        # Extract URL and metadata from response
        outputs = result.get("outputs", [])
        primary_output = outputs[0] if outputs else {}
        url = primary_output.get("url")

        # Build metadata
        metadata = {
            **primary_output,
            "all_outputs": outputs,
        }
        # Preserve extra fields
        for key in ["timestamps", "seed", "prompt", "text", "voice", "model"]:
            if key in result:
                metadata[key] = result[key]

        # Update asset with success
        if asset_id:
            await ctx.step.run(
                "update-asset-success",
                lambda: supabase_service.update_asset_status(
                    asset_id,
                    "success",
                    url=url,
                    metadata=metadata,
                ),
            )

        # Update job to completed
        if job_id:
            job_store.update_job_status(
                job_id, JobStatus.COMPLETED, progress=100, result=result
            )

        # Settle credit reservation - charge what we estimated
        if reservation_id and user_id:
            actual_credits = credits_estimated

            async def settle():
                await credit_service.settle_reservation(reservation_id, actual_credits)
                if job_id:
                    job_store.update_credits_actual(job_id, actual_credits)

            await ctx.step.run("settle-reservation", settle)

        return {
            "status": "completed",
            "result": result,
            "job_id": job_id,
            "asset_id": asset_id,
            "fal_request_id": fal_request_id,
        }

    except Exception as e:
        # Extract structured error
        error_info = _extract_fal_error(e)

        # Capture in Sentry
        sentry_sdk.capture_exception(e, extra={
            "job_id": job_id,
            "asset_id": asset_id,
            "model_id": model_id,
            "fal_request_id": fal_request_id,
            "user_id": user_id,
            "reservation_id": reservation_id,
            "error_info": error_info,
        })

        error_json = json.dumps(error_info)

        # Update job to failed
        if job_id:
            job_store.update_job_status(job_id, JobStatus.FAILED, error=error_json)

        # Update asset to failed
        if asset_id:
            await ctx.step.run(
                "update-asset-failed",
                lambda: supabase_service.update_asset_status(
                    asset_id,
                    "failed",
                    metadata={"error": error_info},
                ),
            )

        # Release credit reservation (full refund)
        if reservation_id and user_id:
            error_msg = error_info.get("message", str(e))[:100]

            async def release():
                await credit_service.release_reservation(
                    reservation_id,
                    reason=f"Generation failed: {error_msg}",
                )

            await ctx.step.run("release-reservation", release)

        raise


# =============================================================================
# TTS Generation Handler
# =============================================================================


@inngest_client.create_function(
    fn_id="tts-generate",
    trigger=inngest.TriggerEvent(event="ai/tts.generate"),
    retries=INNGEST_RETRIES,
)
async def tts_generate_fn(ctx: inngest.Context) -> dict:
    """
    Generate TTS audio via FAL (ElevenLabs).

    This handler receives TTS requests that skipped the initial FAL submission
    (skip_fal=True in SPEECH_CONFIG). It:
    1. Submits to FAL queue for ElevenLabs TTS
    2. Polls until completion
    3. Settles/releases credit reservation

    Event data:
    - job_id: Job ID in our system
    - user_id: User who initiated the request
    - reservation_id: Credit reservation ID
    - credits_estimated: Estimated credits for this job
    - text: The text to convert to speech
    - voice_id: ElevenLabs voice ID
    - model: TTS model ID (e.g., "elevenlabs-v3")
    """
    from app.gateway import transform_for_provider
    from app.services.fal_queue import submit_to_queue, poll_until_complete, FalValidationError, FalQueueError

    event_data = ctx.event.data
    job_id = event_data.get("job_id")
    user_id = event_data.get("user_id")
    reservation_id = event_data.get("reservation_id")
    credits_estimated = event_data.get("credits_estimated", 0)

    # TTS-specific params
    text = event_data.get("text", "")
    voice_id = event_data.get("voice_id")
    model_id = event_data.get("model", "elevenlabs/eleven_v3")

    # Validate required fields
    if not text:
        raise ValueError("text is required for TTS")
    if not voice_id:
        raise ValueError("voice_id is required for TTS")

    sentry_sdk.set_context("job", {
        "job_id": job_id,
        "model_id": model_id,
        "user_id": user_id,
        "reservation_id": reservation_id,
        "credits_estimated": credits_estimated,
        "text_length": len(text),
    })

    # Set initial heartbeat
    if job_id:
        job_store.update_heartbeat(job_id, timeout_seconds=300)  # 5 min for TTS

    try:
        # Build params for FAL
        # Map agent params to registry params:
        # - agent sends "text", registry expects "speech_text"
        # - agent sends "voice_id", registry expects "voice"
        tts_params = {
            "speech_text": text,  # Registry maps this to FAL's "text"
            "voice": voice_id,    # Registry uses this as "voice"
        }

        # Transform params using registry's outbound_schema
        mode = "text-to-speech"
        endpoint, fal_params = transform_for_provider(model_id, mode, tts_params)

        # Step 1: Submit to FAL queue
        async def _submit():
            return await submit_to_queue(endpoint, fal_params, timeout_seconds=30.0)

        queue_result = await ctx.step.run("submit-to-fal", _submit)
        fal_request_id = queue_result.request_id

        if job_id:
            job_store.set_fal_request_id(job_id, fal_request_id)
            job_store.update_job_status(job_id, JobStatus.PROCESSING, progress=10)

        # Step 2: Poll until completion
        async def _poll():
            return await poll_until_complete(
                request_id=fal_request_id,
                endpoint=endpoint,
                model_id=model_id,
                mode=mode,
                original_params=tts_params,
                timeout_seconds=300.0,  # 5 min timeout for TTS
            )

        result = await ctx.step.run("poll-fal", _poll)

        # Extract URL from result
        outputs = result.get("outputs", [])
        primary_output = outputs[0] if outputs else {}
        url = primary_output.get("url")
        duration = primary_output.get("duration")

        # Update job to completed
        if job_id:
            job_store.update_job_status(
                job_id, JobStatus.COMPLETED, progress=100, result=result
            )

        # Settle credit reservation
        if reservation_id and user_id:
            actual_credits = credits_estimated

            async def settle():
                await credit_service.settle_reservation(reservation_id, actual_credits)
                if job_id:
                    job_store.update_credits_actual(job_id, actual_credits)

            await ctx.step.run("settle-reservation", settle)

        return {
            "status": "completed",
            "result": result,
            "job_id": job_id,
            "fal_request_id": fal_request_id,
            "url": url,
            "duration": duration,
        }

    except (FalValidationError, FalQueueError) as e:
        error_info = _extract_fal_error(e)

        sentry_sdk.capture_exception(e, extra={
            "job_id": job_id,
            "model_id": model_id,
            "user_id": user_id,
            "error_info": error_info,
        })

        error_json = json.dumps(error_info)

        # Update job to failed
        if job_id:
            job_store.update_job_status(job_id, JobStatus.FAILED, error=error_json)

        # Release credit reservation
        if reservation_id and user_id:
            error_msg = error_info.get("message", str(e))[:100]

            async def release():
                await credit_service.release_reservation(
                    reservation_id,
                    reason=f"TTS failed: {error_msg}",
                )

            await ctx.step.run("release-reservation", release)

        raise

    except Exception as e:
        error_info = _extract_fal_error(e)

        sentry_sdk.capture_exception(e, extra={
            "job_id": job_id,
            "model_id": model_id,
            "user_id": user_id,
        })

        error_json = json.dumps(error_info)

        if job_id:
            job_store.update_job_status(job_id, JobStatus.FAILED, error=error_json)

        if reservation_id and user_id:
            async def release():
                await credit_service.release_reservation(
                    reservation_id,
                    reason=f"TTS failed: {str(e)[:100]}",
                )

            await ctx.step.run("release-reservation", release)

        raise


# List of all Inngest functions to register
all_functions = [
    generate_poll_fn,
    tts_generate_fn,
]

__all__ = [
    "inngest_client",
    "generate_poll_fn",
    "tts_generate_fn",
    "all_functions",
]
