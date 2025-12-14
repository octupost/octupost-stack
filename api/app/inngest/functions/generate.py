"""
Unified Inngest function for AI generation.

This function handles all generation types using the centralized
generation service and model registry.

Credit Handling:
- For models with known duration: direct deduction, refund on failure
- For models with unknown duration (avatar, speech): reservation system
  - Credits are reserved before generation
  - After generation: settle with actual cost (refund excess or charge difference)
  - On failure: release full reservation back to user
"""

import inngest
import sentry_sdk

from app.inngest.client import inngest_client
from app.services.generation_service import generation_service
from app.services.supabase_client import supabase_service
from app.services.job_store import job_store
from app.services.credit_service import credit_service
from app.models.schemas import JobStatus
from app.registry import get_model, calculate_cost

# Credit conversion: 1 USD = 100 credits
USD_TO_CREDITS = 100


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
    elif gen_type in ("text-to-video", "image-to-video", "avatar"):
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


def _calculate_actual_credits(model_id: str, actual_duration: float, params: dict) -> int:
    """
    Calculate actual credits based on generation result duration.
    
    Used for settling credit reservations after generation completes.
    
    Args:
        model_id: Model identifier
        actual_duration: Actual duration from generation result
        params: Original generation parameters
        
    Returns:
        Actual credits to charge
    """
    if not actual_duration or actual_duration <= 0:
        return 0
    
    # Calculate cost using actual duration
    cost_usd = calculate_cost(model_id, quantity=actual_duration, params=params)
    credits = int(cost_usd * USD_TO_CREDITS)
    
    return max(credits, 1)


async def _run_generation(
    ctx: inngest.Context,
    job_id: str | None,
    asset_id: str | None,
    model_id: str,
    params: dict,
    gen_type: str,
    user_id: str | None = None,
    credits_used: int = 0,
    reservation_id: str | None = None,
) -> dict:
    """
    Common generation logic for all types.
    
    Handles both direct credit deduction (known duration) and credit reservation
    (unknown duration) systems.
    
    Args:
        ctx: Inngest context
        job_id: Job identifier
        asset_id: Asset identifier
        model_id: Model identifier from registry
        params: Generation parameters
        gen_type: Generation type for logging
        user_id: User ID for credit refunds
        credits_used: Credits deducted/estimated for this generation
        reservation_id: Credit reservation ID (for models with unknown duration)
        
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
            "user_id": user_id,
            "credits_used": credits_used,
            "reservation_id": reservation_id,
        },
    )

    # Update job status to processing
    if job_id:
        job_store.update_job_status(job_id, JobStatus.PROCESSING, progress=10)
        # #region agent log
        import json
        with open("/Users/serhatcamici/dev/octupost-stack/.cursor/debug.log", "a") as f:
            f.write(json.dumps({"location":"generate.py:_run_generation","message":"Inngest set status PROCESSING","data":{"job_id":job_id,"job_store_id":id(job_store),"gen_type":gen_type},"timestamp":__import__("time").time()*1000,"sessionId":"debug-session","hypothesisId":"A,E"})+"\n")
        # #endregion

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

        # Extract metadata including actual duration
        metadata = _get_result_metadata(result, gen_type)
        
        # Settle credit reservation if applicable
        if reservation_id and user_id:
            actual_duration = metadata.get("duration", 0)
            actual_credits = _calculate_actual_credits(model_id, actual_duration, params)
            
            async def settle():
                settlement = await credit_service.settle_reservation(
                    reservation_id=reservation_id,
                    actual_amount=actual_credits,
                )
                return settlement
            
            settlement_result = await ctx.step.run("settle-reservation", settle)
            
            # Log settlement for debugging
            if settlement_result:
                sentry_sdk.set_context("settlement", {
                    "reservation_id": reservation_id,
                    "actual_duration": actual_duration,
                    "actual_credits": actual_credits,
                    "refunded": settlement_result.refunded,
                    "charged_extra": settlement_result.charged_extra,
                })

        # Update asset with success status and result URL
        if asset_id:
            url = _get_result_url(result, gen_type)
            
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
            # #region agent log
            import json
            with open("/Users/serhatcamici/dev/octupost-stack/.cursor/debug.log", "a") as f:
                f.write(json.dumps({"location":"generate.py:_run_generation","message":"Inngest set status COMPLETED","data":{"job_id":job_id,"job_store_id":id(job_store),"gen_type":gen_type,"has_result":result is not None},"timestamp":__import__("time").time()*1000,"sessionId":"debug-session","hypothesisId":"A,E"})+"\n")
            # #endregion

        return {
            "status": "completed",
            "result": result,
            "job_id": job_id,
            "asset_id": asset_id,
        }

    except Exception as e:
        # Capture exception in Sentry with full context
        sentry_sdk.capture_exception(e, extra={
            "job_id": job_id,
            "asset_id": asset_id,
            "model_id": model_id,
            "gen_type": gen_type,
            "user_id": user_id,
            "credits_used": credits_used,
            "reservation_id": reservation_id,
        })
        
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
        
        # Handle credit refund/release on failure
        if user_id and job_id:
            if reservation_id:
                # Release reservation - return all reserved credits
                async def release():
                    return await credit_service.release_reservation(
                        reservation_id=reservation_id,
                        reason=f"Generation failed: {str(e)[:100]}",
                    )
                await ctx.step.run("release-reservation", release)
            elif credits_used > 0:
                # Direct refund for models without reservation
                async def refund():
                    await credit_service.refund_credits(
                        user_id=user_id,
                        amount=credits_used,
                        job_id=job_id,
                        description=f"Generation failed: {str(e)[:100]}",
                    )
                await ctx.step.run("refund-credits", refund)
        
        raise


# =============================================================================
# Individual Event Handlers (for backward compatibility with existing events)
# =============================================================================


# Metadata fields to exclude from generation params
_METADATA_FIELDS = {
    "job_id", "asset_id", "model", "user_id", 
    "credits_used", "reservation_id", "estimated_duration"
}


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
    user_id = event_data.get("user_id")
    credits_used = event_data.get("credits_used", 0)
    reservation_id = event_data.get("reservation_id")
    
    # Extract generation params (exclude metadata fields)
    params = {k: v for k, v in event_data.items() 
              if k not in _METADATA_FIELDS and v is not None}
    
    return await _run_generation(
        ctx=ctx,
        job_id=job_id,
        asset_id=asset_id,
        model_id=model_id,
        params=params,
        gen_type="text-to-image",
        user_id=user_id,
        credits_used=credits_used,
        reservation_id=reservation_id,
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
    user_id = event_data.get("user_id")
    credits_used = event_data.get("credits_used", 0)
    reservation_id = event_data.get("reservation_id")
    
    # Extract generation params
    params = {k: v for k, v in event_data.items() 
              if k not in _METADATA_FIELDS and v is not None}
    
    return await _run_generation(
        ctx=ctx,
        job_id=job_id,
        asset_id=asset_id,
        model_id=model_id,
        params=params,
        gen_type="text-to-video",
        user_id=user_id,
        credits_used=credits_used,
        reservation_id=reservation_id,
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
    user_id = event_data.get("user_id")
    credits_used = event_data.get("credits_used", 0)
    reservation_id = event_data.get("reservation_id")
    
    # Extract generation params
    params = {k: v for k, v in event_data.items() 
              if k not in _METADATA_FIELDS and v is not None}
    
    return await _run_generation(
        ctx=ctx,
        job_id=job_id,
        asset_id=asset_id,
        model_id=model_id,
        params=params,
        gen_type="image-to-video",
        user_id=user_id,
        credits_used=credits_used,
        reservation_id=reservation_id,
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
    user_id = event_data.get("user_id")
    credits_used = event_data.get("credits_used", 0)
    reservation_id = event_data.get("reservation_id")
    
    # Extract generation params
    params = {k: v for k, v in event_data.items() 
              if k not in _METADATA_FIELDS and v is not None}
    
    return await _run_generation(
        ctx=ctx,
        job_id=job_id,
        asset_id=asset_id,
        model_id=model_id,
        params=params,
        gen_type="text-to-speech",
        user_id=user_id,
        credits_used=credits_used,
        reservation_id=reservation_id,
    )


@inngest_client.create_function(
    fn_id="generate-avatar-v2",
    trigger=inngest.TriggerEvent(event="ai/avatar.generate"),
    retries=2,
)
async def generate_avatar_fn(ctx: inngest.Context) -> dict:
    """Handle avatar generation via Inngest."""
    event_data = ctx.event.data
    job_id = event_data.get("job_id")
    asset_id = event_data.get("asset_id")
    model_id = event_data.get("model", "argil/avatars/text-to-video")
    user_id = event_data.get("user_id")
    credits_used = event_data.get("credits_used", 0)
    reservation_id = event_data.get("reservation_id")
    
    # Extract generation params
    params = {k: v for k, v in event_data.items() 
              if k not in _METADATA_FIELDS and v is not None}
    
    return await _run_generation(
        ctx=ctx,
        job_id=job_id,
        asset_id=asset_id,
        model_id=model_id,
        params=params,
        gen_type="avatar",
        user_id=user_id,
        credits_used=credits_used,
        reservation_id=reservation_id,
    )

