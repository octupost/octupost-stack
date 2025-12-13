"""
Unified Inngest function for AI generation.

This function handles all generation types using the centralized
generation service and model registry.
"""

import inngest
import sentry_sdk

from app.inngest.client import inngest_client
from app.services.generation_service import generation_service
from app.services.supabase_client import supabase_service
from app.services.job_store import job_store
from app.models.schemas import JobStatus
from app.registry import get_model


def _get_result_url(result: dict, gen_type: str) -> str | None:
    """Extract the primary URL from a generation result."""
    if gen_type == "text-to-image":
        images = result.get("images", [])
        return images[0].get("url") if images else None
    elif gen_type in ("text-to-video", "image-to-video"):
        video = result.get("video", {})
        return video.get("url")
    elif gen_type == "text-to-speech":
        audio = result.get("audio", {})
        return audio.get("url")
    return None


def _get_result_metadata(result: dict, gen_type: str) -> dict:
    """Extract metadata from a generation result."""
    if gen_type == "text-to-image":
        images = result.get("images", [])
        first_image = images[0] if images else {}
        return {
            "width": first_image.get("width"),
            "height": first_image.get("height"),
            "content_type": first_image.get("content_type", "image/png"),
            "seed": result.get("seed"),
            "all_images": images,
        }
    elif gen_type in ("text-to-video", "image-to-video"):
        video = result.get("video", {})
        return {
            "width": video.get("width"),
            "height": video.get("height"),
            "duration": video.get("duration"),
            "content_type": video.get("content_type", "video/mp4"),
            "seed": result.get("seed"),
        }
    elif gen_type == "text-to-speech":
        audio = result.get("audio", {})
        return {
            "duration": audio.get("duration"),
            "content_type": audio.get("content_type", "audio/wav"),
        }
    return {}


async def _run_generation(
    ctx: inngest.Context,
    job_id: str | None,
    asset_id: str | None,
    model_id: str,
    params: dict,
    gen_type: str,
) -> dict:
    """
    Common generation logic for all types.
    
    Args:
        ctx: Inngest context
        job_id: Job identifier
        asset_id: Asset identifier
        model_id: Model identifier from registry
        params: Generation parameters
        gen_type: Generation type for logging
        
    Returns:
        Result dictionary
    """
    sentry_sdk.set_context(
        "job",
        {
            "job_id": job_id,
            "asset_id": asset_id,
            "model_id": model_id,
            "type": gen_type,
        },
    )

    # Update job status to processing
    if job_id:
        job_store.update_job_status(job_id, JobStatus.PROCESSING, progress=10)

    # Update asset status to processing
    if asset_id:
        await ctx.step.run(
            "update-asset-processing",
            lambda: supabase_service.update_asset_status(asset_id, "processing", progress=10),
        )

    try:
        # Update progress before generation
        if job_id:
            job_store.update_job_status(job_id, JobStatus.PROCESSING, progress=30)

        # Generate using the unified service
        async def _generate():
            return await generation_service.generate(model_id, params, validate=False)

        result = await ctx.step.run(f"generate-{gen_type}", _generate)

        # Update progress after generation
        if job_id:
            job_store.update_job_status(job_id, JobStatus.PROCESSING, progress=80)

        # Update asset with success status and result URL
        if asset_id:
            url = _get_result_url(result, gen_type)
            metadata = _get_result_metadata(result, gen_type)
            
            await ctx.step.run(
                "update-asset-success",
                lambda: supabase_service.update_asset_status(
                    asset_id,
                    "success",
                    url=url,
                    metadata=metadata,
                ),
            )

        # Update job status to completed
        if job_id:
            job_store.update_job_status(
                job_id, JobStatus.COMPLETED, progress=100, result=result
            )

        return {
            "status": "completed",
            "result": result,
            "job_id": job_id,
            "asset_id": asset_id,
        }

    except Exception as e:
        # Update job status to failed
        if job_id:
            job_store.update_job_status(job_id, JobStatus.FAILED, error=str(e))

        # Update asset with failed status
        if asset_id:
            await ctx.step.run(
                "update-asset-failed",
                lambda: supabase_service.update_asset_status(
                    asset_id,
                    "failed",
                    metadata={"error": str(e)},
                ),
            )
        raise


# =============================================================================
# Individual Event Handlers (for backward compatibility with existing events)
# =============================================================================


@inngest_client.create_function(
    fn_id="generate-image-v2",
    trigger=inngest.TriggerEvent(event="ai/image.generate"),
    retries=2,
)
async def generate_image_fn(ctx: inngest.Context) -> dict:
    """Handle text-to-image generation via Inngest."""
    event_data = ctx.event.data
    job_id = event_data.get("job_id")
    asset_id = event_data.get("asset_id")
    model_id = event_data.get("model", "fal-ai/gpt-image-1-mini")
    
    # Extract generation params (exclude metadata fields)
    params = {k: v for k, v in event_data.items() 
              if k not in ("job_id", "asset_id", "model") and v is not None}
    
    return await _run_generation(
        ctx=ctx,
        job_id=job_id,
        asset_id=asset_id,
        model_id=model_id,
        params=params,
        gen_type="text-to-image",
    )


@inngest_client.create_function(
    fn_id="generate-video-v2",
    trigger=inngest.TriggerEvent(event="ai/video.generate"),
    retries=2,
)
async def generate_video_fn(ctx: inngest.Context) -> dict:
    """Handle text-to-video generation via Inngest."""
    event_data = ctx.event.data
    job_id = event_data.get("job_id")
    asset_id = event_data.get("asset_id")
    model_id = event_data.get("model", "fal-ai/infinity-star/text-to-video")
    
    # Extract generation params
    params = {k: v for k, v in event_data.items() 
              if k not in ("job_id", "asset_id", "model") and v is not None}
    
    return await _run_generation(
        ctx=ctx,
        job_id=job_id,
        asset_id=asset_id,
        model_id=model_id,
        params=params,
        gen_type="text-to-video",
    )


@inngest_client.create_function(
    fn_id="generate-video-from-image-v2",
    trigger=inngest.TriggerEvent(event="ai/video-from-image.generate"),
    retries=2,
)
async def generate_video_from_image_fn(ctx: inngest.Context) -> dict:
    """Handle image-to-video generation via Inngest."""
    event_data = ctx.event.data
    job_id = event_data.get("job_id")
    asset_id = event_data.get("asset_id")
    model_id = event_data.get("model", "fal-ai/minimax-video/image-to-video")
    
    # Extract generation params
    params = {k: v for k, v in event_data.items() 
              if k not in ("job_id", "asset_id", "model") and v is not None}
    
    return await _run_generation(
        ctx=ctx,
        job_id=job_id,
        asset_id=asset_id,
        model_id=model_id,
        params=params,
        gen_type="image-to-video",
    )


@inngest_client.create_function(
    fn_id="generate-speech-v2",
    trigger=inngest.TriggerEvent(event="ai/speech.generate"),
    retries=2,
)
async def generate_speech_fn(ctx: inngest.Context) -> dict:
    """Handle text-to-speech generation via Inngest."""
    event_data = ctx.event.data
    job_id = event_data.get("job_id")
    asset_id = event_data.get("asset_id")
    model_id = event_data.get("model", "fal-ai/kokoro")
    
    # Extract generation params
    params = {k: v for k, v in event_data.items() 
              if k not in ("job_id", "asset_id", "model") and v is not None}
    
    return await _run_generation(
        ctx=ctx,
        job_id=job_id,
        asset_id=asset_id,
        model_id=model_id,
        params=params,
        gen_type="text-to-speech",
    )

