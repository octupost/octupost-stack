"""
FAL Queue Service

Handles asynchronous queue submission and polling for FAL AI requests.
This service provides:
1. submit_to_queue: Submit a request and wait for FAL to confirm (IN_QUEUE/IN_PROGRESS)
2. poll_until_complete: Poll a submitted request until completion

The key difference from subscribe_async:
- submit_to_queue returns immediately after FAL confirms the request is valid
- poll_until_complete can be called separately (e.g., from Inngest worker)

This allows the API to:
1. Validate the request with FAL before returning to the user
2. Return HTTP 202 Accepted once FAL confirms the request
3. Let Inngest handle the polling for completion
"""

import asyncio
from dataclasses import dataclass
from typing import Any, Callable, Optional

import fal_client


@dataclass
class QueueSubmitResult:
    """Result of submitting a request to FAL queue."""
    request_id: str
    status: str  # "IN_QUEUE" or "IN_PROGRESS"
    queue_position: Optional[int] = None
    status_url: Optional[str] = None
    response_url: Optional[str] = None
    cancel_url: Optional[str] = None


class FalQueueError(Exception):
    """Raised when FAL queue operations fail."""
    pass


class FalValidationError(FalQueueError):
    """Raised when FAL rejects the request (validation error)."""
    pass


async def submit_to_queue(
    endpoint: str,
    arguments: dict[str, Any],
    timeout_seconds: float = 30.0,
) -> QueueSubmitResult:
    """
    Submit a request to FAL queue and wait for initial confirmation.

    This function:
    1. Submits the request to FAL's queue
    2. Waits for FAL to return IN_QUEUE or IN_PROGRESS status
    3. Returns immediately after confirmation (doesn't wait for completion)

    If FAL rejects the request (validation error, rate limit, etc.),
    this function raises an exception immediately.

    Args:
        endpoint: FAL model endpoint (e.g., "fal-ai/flux/dev")
        arguments: Request parameters
        timeout_seconds: Max time to wait for queue confirmation

    Returns:
        QueueSubmitResult with request_id and status

    Raises:
        FalValidationError: If FAL rejects the request
        FalQueueError: If queue submission fails
        asyncio.TimeoutError: If timeout waiting for confirmation
    """
    try:
        # Submit to FAL queue
        handler = await fal_client.submit_async(endpoint, arguments=arguments)

        # Get initial status to confirm FAL accepted the request
        # This will raise if the request is invalid
        status = await asyncio.wait_for(
            handler.status(),
            timeout=timeout_seconds,
        )

        return QueueSubmitResult(
            request_id=handler.request_id,
            status=getattr(status, "status", "UNKNOWN"),
            queue_position=getattr(status, "queue_position", None),
            status_url=getattr(handler, "status_url", None),
            response_url=getattr(handler, "response_url", None),
            cancel_url=getattr(handler, "cancel_url", None),
        )

    except asyncio.TimeoutError:
        raise FalQueueError(f"Timeout waiting for FAL queue confirmation after {timeout_seconds}s")
    except Exception as e:
        error_str = str(e).lower()
        if "validation" in error_str or "value_error" in error_str or "required" in error_str:
            raise FalValidationError(f"FAL validation error: {e}")
        raise FalQueueError(f"FAL queue submission failed: {e}")


async def poll_until_complete(
    request_id: str,
    endpoint: str,
    model_id: str,
    mode: str,
    original_params: dict[str, Any],
    on_progress: Optional[Callable[[dict[str, Any]], None]] = None,
    poll_interval: float = 2.0,
    timeout_seconds: float = 600.0,
) -> dict[str, Any]:
    """
    Poll a FAL request until completion and normalize the response.

    Called by Inngest worker after initial queue submission.
    Uses status_async to poll for progress and result_async to fetch final result.
    Normalizes the response using inbound_schema before returning.

    Args:
        request_id: FAL request ID from submit_to_queue
        endpoint: FAL model endpoint
        model_id: Model identifier (for response normalization)
        mode: Generation mode (for response normalization)
        original_params: Original user parameters (for dimension defaults)
        on_progress: Optional callback for progress updates
        poll_interval: Seconds between status checks
        timeout_seconds: Max time to wait for completion

    Returns:
        Normalized response dict with "outputs" array

    Raises:
        FalQueueError: If polling fails or timeout
    """
    import time
    start_time = time.monotonic()

    while True:
        elapsed = time.monotonic() - start_time
        if elapsed > timeout_seconds:
            raise FalQueueError(f"Timeout waiting for FAL completion after {timeout_seconds}s")

        try:
            # Check current status
            status = await fal_client.status_async(endpoint, request_id, with_logs=True)

            # Check if completed using isinstance
            if isinstance(status, fal_client.Completed):
                # Fetch the raw FAL result
                raw_result = await fal_client.result_async(endpoint, request_id)

                # Normalize response using inbound_schema
                from app.gateway import transform_from_provider
                return transform_from_provider(model_id, mode, raw_result, original_params)

            # Report progress if callback provided
            if on_progress:
                if isinstance(status, fal_client.Queued):
                    status_info = {
                        "status": "in_queue",
                        "queue_position": getattr(status, "queue_position", None),
                        "logs": [],
                    }
                elif isinstance(status, fal_client.InProgress):
                    # Extract logs - handle both list of dicts and list of strings
                    raw_logs = getattr(status, "logs", [])
                    logs = []
                    for log in raw_logs:
                        if isinstance(log, dict):
                            logs.append(log.get("message", ""))
                        elif isinstance(log, str):
                            logs.append(log)
                    status_info = {
                        "status": "in_progress",
                        "queue_position": None,
                        "logs": logs,
                    }
                else:
                    # Unknown status type, treat as in_progress
                    status_info = {
                        "status": "in_progress",
                        "queue_position": None,
                        "logs": [],
                    }
                on_progress(status_info)

            # Wait before next poll
            await asyncio.sleep(poll_interval)

        except FalQueueError:
            raise
        except Exception as e:
            raise FalQueueError(f"FAL polling failed: {e}")
