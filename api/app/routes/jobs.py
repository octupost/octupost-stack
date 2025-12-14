"""Job management API routes."""

from typing import Optional

import sentry_sdk
from fastapi import APIRouter, HTTPException, Header, Query

from app.models.schemas import (
    ErrorResponse,
    JobStatus,
    JobStatusResponse,
)
from app.services.job_store import job_store


def _set_user_context(user_id: Optional[str]) -> None:
    """Set user context in Sentry for error tracking."""
    if user_id:
        sentry_sdk.set_user({"id": user_id})
    else:
        sentry_sdk.set_user(None)


router = APIRouter()


@router.get(
    "/{job_id}",
    response_model=JobStatusResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get job status",
    description="Retrieve the current status and result of a generation job",
)
async def get_job_status(
    job_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
) -> JobStatusResponse:
    """
    Get the status of a generation job.

    Returns the current status, progress percentage, and result/error
    depending on the job state.
    """
    _set_user_context(x_user_id)
    job = job_store.get_job(job_id)
    # #region agent log
    import json
    with open("/Users/serhatcamici/dev/octupost-stack/.cursor/debug.log", "a") as f:
        f.write(json.dumps({"location":"jobs.py:get_job_status","message":"API get_job_status called","data":{"job_id":job_id,"job_found":job is not None,"status":job["status"].value if job else None,"progress":job.get("progress") if job else None,"has_result":job.get("result") is not None if job else None,"job_store_id":id(job_store)},"timestamp":__import__("time").time()*1000,"sessionId":"debug-session","hypothesisId":"A,B"})+"\n")
    # #endregion

    if not job:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "not_found",
                "message": f"Job {job_id} not found",
            },
        )

    return JobStatusResponse(
        job_id=job["job_id"],
        status=job["status"],
        progress=job.get("progress"),
        result=job.get("result"),
        error=job.get("error"),
        created_at=job["created_at"],
        updated_at=job["updated_at"],
    )


@router.post(
    "/{job_id}/cancel",
    response_model=JobStatusResponse,
    responses={
        404: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
    },
    summary="Cancel a job",
    description="Cancel a pending or processing job",
)
async def cancel_job(
    job_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
) -> JobStatusResponse:
    """
    Cancel a generation job.

    Only jobs in 'pending' or 'processing' status can be cancelled.
    """
    _set_user_context(x_user_id)
    job = job_store.get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "not_found",
                "message": f"Job {job_id} not found",
            },
        )

    if job["status"] not in [JobStatus.PENDING, JobStatus.PROCESSING]:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_state",
                "message": f"Cannot cancel job with status '{job['status'].value}'",
            },
        )

    job_store.cancel_job(job_id)
    job = job_store.get_job(job_id)

    return JobStatusResponse(
        job_id=job["job_id"],
        status=job["status"],
        progress=job.get("progress"),
        result=job.get("result"),
        error=job.get("error"),
        created_at=job["created_at"],
        updated_at=job["updated_at"],
    )


@router.get(
    "",
    response_model=list[JobStatusResponse],
    summary="List jobs",
    description="List recent generation jobs with optional status filter",
)
async def list_jobs(
    limit: int = Query(default=50, ge=1, le=100, description="Maximum jobs to return"),
    status: Optional[JobStatus] = Query(default=None, description="Filter by status"),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
) -> list[JobStatusResponse]:
    """
    List recent generation jobs.

    Jobs are sorted by creation time (newest first).
    """
    _set_user_context(x_user_id)
    jobs = job_store.list_jobs(limit=limit, status=status)

    return [
        JobStatusResponse(
            job_id=job["job_id"],
            status=job["status"],
            progress=job.get("progress"),
            result=job.get("result"),
            error=job.get("error"),
            created_at=job["created_at"],
            updated_at=job["updated_at"],
        )
        for job in jobs
    ]


@router.post(
    "/{job_id}/callback",
    include_in_schema=False,
    summary="Internal callback for Inngest",
    description="Called by Inngest when a job completes or fails",
)
async def job_callback(job_id: str, status: str, result: Optional[dict] = None, error: Optional[str] = None):
    """
    Internal callback endpoint for Inngest to update job status.

    This is called automatically when an Inngest function completes.
    """
    job = job_store.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Map string status to enum
    status_map = {
        "completed": JobStatus.COMPLETED,
        "failed": JobStatus.FAILED,
        "processing": JobStatus.PROCESSING,
    }
    job_status = status_map.get(status, JobStatus.FAILED)

    job_store.update_job_status(
        job_id=job_id,
        status=job_status,
        progress=100 if job_status == JobStatus.COMPLETED else None,
        result=result,
        error=error,
    )

    return {"ok": True}

