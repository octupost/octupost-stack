"""In-memory job store for tracking generation jobs."""

from datetime import datetime
from typing import Any, Optional
from ulid import ULID

from app.models.schemas import JobStatus


class JobStore:
    """
    Simple in-memory job store for tracking job status.

    In production, this should be replaced with Redis or a database.
    """

    def __init__(self):
        self._jobs: dict[str, dict[str, Any]] = {}

    def create_job(self, job_type: str, request_data: dict[str, Any]) -> str:
        """
        Create a new job and return its ID.

        Args:
            job_type: Type of generation job (image, video, speech, etc.)
            request_data: The original request parameters

        Returns:
            Unique job ID
        """
        job_id = str(ULID())
        now = datetime.utcnow()

        self._jobs[job_id] = {
            "job_id": job_id,
            "type": job_type,
            "status": JobStatus.PENDING,
            "progress": 0,
            "request": request_data,
            "result": None,
            "error": None,
            "created_at": now,
            "updated_at": now,
        }

        return job_id

    def get_job(self, job_id: str) -> Optional[dict[str, Any]]:
        """
        Get job by ID.

        Args:
            job_id: The job ID to look up

        Returns:
            Job data or None if not found
        """
        return self._jobs.get(job_id)

    def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        progress: Optional[int] = None,
        result: Optional[dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> bool:
        """
        Update job status.

        Args:
            job_id: The job ID to update
            status: New status
            progress: Progress percentage (0-100)
            result: Result data if completed
            error: Error message if failed

        Returns:
            True if job was found and updated, False otherwise
        """
        if job_id not in self._jobs:
            return False

        job = self._jobs[job_id]
        job["status"] = status
        job["updated_at"] = datetime.utcnow()

        if progress is not None:
            job["progress"] = progress
        if result is not None:
            job["result"] = result
        if error is not None:
            job["error"] = error

        return True

    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a pending job.

        Args:
            job_id: The job ID to cancel

        Returns:
            True if job was cancelled, False if not found or not cancellable
        """
        job = self._jobs.get(job_id)
        if not job:
            return False

        # Can only cancel pending or processing jobs
        if job["status"] not in [JobStatus.PENDING, JobStatus.PROCESSING]:
            return False

        job["status"] = JobStatus.CANCELLED
        job["updated_at"] = datetime.utcnow()
        return True

    def list_jobs(
        self,
        limit: int = 50,
        status: Optional[JobStatus] = None,
    ) -> list[dict[str, Any]]:
        """
        List jobs with optional filtering.

        Args:
            limit: Maximum number of jobs to return
            status: Filter by status

        Returns:
            List of job data
        """
        jobs = list(self._jobs.values())

        # Filter by status if provided
        if status:
            jobs = [j for j in jobs if j["status"] == status]

        # Sort by created_at descending
        jobs.sort(key=lambda x: x["created_at"], reverse=True)

        return jobs[:limit]


# Create singleton instance
job_store = JobStore()

