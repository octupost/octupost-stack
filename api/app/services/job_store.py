"""Persistent job store using Supabase for tracking generation jobs."""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional
import sentry_sdk
from ulid import ULID

from app.schemas import JobStatus


class JobStoreError(Exception):
    """Raised when job store operations fail."""
    pass


class JobStore:
    """
    Supabase-backed job store for tracking job status.

    Stores jobs in the octupost.jobs table for persistence across
    server restarts and page refreshes. Supports Realtime subscriptions
    for instant frontend updates.

    NO FALLBACKS: In development mode, all errors are raised immediately.
    Supabase MUST be configured for this to work.
    """

    def __init__(self):
        self._client = None
        self._checked_config = False

    def _ensure_configured(self) -> None:
        """Ensure Supabase is configured. Raises if not."""
        if not self._checked_config:
            from app.config import get_settings
            settings = get_settings()
            effective_url = settings.effective_supabase_url
            if not effective_url or not settings.supabase_service_role_key:
                raise JobStoreError(
                    "Supabase is NOT configured. "
                    "Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables. "
                    "No fallback - this is required for job storage."
                )
            self._checked_config = True

    @property
    def client(self):
        """Get or create Supabase client. Raises if not configured."""
        self._ensure_configured()
        if self._client is None:
            from supabase import create_client
            from app.config import get_settings
            settings = get_settings()
            self._client = create_client(
                settings.effective_supabase_url,
                settings.supabase_service_role_key,
            )
        return self._client

    def create_job(
        self,
        job_type: str,
        request_data: dict[str, Any],
        owner_id: Optional[str] = None,
        asset_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> str:
        """
        Create a new job and return its ID.

        Args:
            job_type: Type of generation job (text-to-image, text-to-video, avatar, etc.)
            request_data: The original request parameters
            owner_id: UUID of the job owner (user)
            asset_id: UUID of the associated asset
            idempotency_key: Client-provided key for request deduplication

        Returns:
            Unique job ID (ULID)

        Raises:
            JobStoreError: If job creation fails (NO FALLBACK)
        """
        if not owner_id:
            raise JobStoreError("owner_id is required - anonymous jobs not supported")

        job_id = str(ULID())
        now = datetime.now(timezone.utc)

        # Extract model from request_data
        model = request_data.get("model", "unknown")

        # Extract credit info
        credits_estimated = request_data.get("credits")

        # Build params (exclude metadata fields)
        metadata_fields = {"model", "credits"}
        params = {k: v for k, v in request_data.items() if k not in metadata_fields}

        data = {
            "id": job_id,
            "owner_id": owner_id,
            "type": job_type,
            "status": "pending",
            "progress": 0,
            "model": model,
            "params": params,
            "asset_id": asset_id,
            "credits_estimated": credits_estimated,
            "idempotency_key": idempotency_key,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        try:
            self.client.schema("octupost").table("jobs").insert(data).execute()
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise JobStoreError(f"Failed to create job in Supabase: {e}") from e

        sentry_sdk.set_context("job", {
            "operation": "create_job",
            "job_id": job_id,
            "owner_id": owner_id,
            "type": job_type,
            "model": model,
        })

        return job_id

    def get_job(self, job_id: str) -> Optional[dict[str, Any]]:
        """
        Get job by ID.

        Args:
            job_id: The job ID to look up

        Returns:
            Job data or None if not found

        Raises:
            JobStoreError: If database query fails (NO FALLBACK)
        """
        try:
            result = (
                self.client.schema("octupost")
                .table("jobs")
                .select("*")
                .eq("id", job_id)
                .execute()
            )

            if result.data:
                db_job = result.data[0]
                return self._db_to_legacy_format(db_job)

            return None

        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise JobStoreError(f"Failed to get job from Supabase: {e}") from e

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

        Raises:
            JobStoreError: If database update fails (NO FALLBACK)
        """
        now = datetime.now(timezone.utc)

        data: dict[str, Any] = {
            "status": status.value,
            "updated_at": now.isoformat(),
        }

        if progress is not None:
            data["progress"] = progress
        if result is not None:
            data["result"] = result
        if error is not None:
            data["error"] = error

        try:
            update_result = (
                self.client.schema("octupost")
                .table("jobs")
                .update(data)
                .eq("id", job_id)
                .execute()
            )

            sentry_sdk.add_breadcrumb(
                category="job",
                message=f"Job {job_id} updated to {status.value}",
                level="info",
            )

            # Return True if we updated at least one row
            return len(update_result.data) > 0 if update_result.data else False

        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise JobStoreError(f"Failed to update job in Supabase: {e}") from e

    def set_job_asset(self, job_id: str, asset_id: str) -> bool:
        """
        Set the asset_id for a job after asset creation.

        Args:
            job_id: The job ID
            asset_id: The asset ID to associate

        Returns:
            True if updated successfully

        Raises:
            JobStoreError: If database update fails (NO FALLBACK)
        """
        try:
            result = self.client.schema("octupost").table("jobs").update({
                "asset_id": asset_id,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }).eq("id", job_id).execute()

            return len(result.data) > 0 if result.data else False

        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise JobStoreError(f"Failed to set job asset in Supabase: {e}") from e

    def set_fal_request_id(self, job_id: str, fal_request_id: str) -> bool:
        """
        Store FAL's request_id for debugging and cancellation.

        Args:
            job_id: The job ID
            fal_request_id: FAL's internal request ID

        Returns:
            True if updated successfully

        Raises:
            JobStoreError: If database update fails (NO FALLBACK)
        """
        try:
            result = self.client.schema("octupost").table("jobs").update({
                "fal_request_id": fal_request_id,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }).eq("id", job_id).execute()

            sentry_sdk.add_breadcrumb(
                category="job",
                message=f"Job {job_id} linked to FAL request {fal_request_id}",
                level="info",
            )

            return len(result.data) > 0 if result.data else False

        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise JobStoreError(f"Failed to set FAL request_id in Supabase: {e}") from e

    def set_reservation_id(self, job_id: str, reservation_id: str) -> bool:
        """
        Store the credit reservation ID for a job.

        Args:
            job_id: The job ID
            reservation_id: The credit reservation UUID

        Returns:
            True if updated successfully

        Raises:
            JobStoreError: If database update fails (NO FALLBACK)
        """
        try:
            result = self.client.schema("octupost").table("jobs").update({
                "reservation_id": reservation_id,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }).eq("id", job_id).execute()

            return len(result.data) > 0 if result.data else False

        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise JobStoreError(f"Failed to set reservation_id in Supabase: {e}") from e

    def update_credits_actual(self, job_id: str, credits_actual: int) -> bool:
        """
        Update the actual credits used after generation completes.

        Args:
            job_id: The job ID
            credits_actual: The actual credits charged

        Returns:
            True if updated successfully

        Raises:
            JobStoreError: If database update fails (NO FALLBACK)
        """
        try:
            result = self.client.schema("octupost").table("jobs").update({
                "credits_actual": credits_actual,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }).eq("id", job_id).execute()

            return len(result.data) > 0 if result.data else False

        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise JobStoreError(f"Failed to update credits_actual in Supabase: {e}") from e

    def update_heartbeat(self, job_id: str, timeout_seconds: int = 600) -> bool:
        """
        Update job heartbeat and extend stale_at deadline.

        Called by Inngest worker during polling to indicate job is still active.
        If no heartbeat is received by stale_at, the job will be marked as failed
        by the pg_cron stale job detection.

        Args:
            job_id: The job ID
            timeout_seconds: Seconds until job is considered stale (default 10 min)

        Returns:
            True if updated successfully

        Raises:
            JobStoreError: If database update fails (NO FALLBACK)
        """
        now = datetime.now(timezone.utc)
        stale_at = now + timedelta(seconds=timeout_seconds)

        try:
            result = self.client.schema("octupost").table("jobs").update({
                "last_heartbeat": now.isoformat(),
                "stale_at": stale_at.isoformat(),
                "updated_at": now.isoformat(),
            }).eq("id", job_id).execute()

            return len(result.data) > 0 if result.data else False

        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise JobStoreError(f"Failed to update heartbeat in Supabase: {e}") from e

    def find_existing_job(self, owner_id: str, idempotency_key: str) -> Optional[dict[str, Any]]:
        """
        Find an existing job by idempotency key.

        Used to prevent duplicate job creation when the same request is submitted
        multiple times (network retries, double-clicks, etc.).

        Args:
            owner_id: User ID
            idempotency_key: Client-provided idempotency key

        Returns:
            Job data if found, None otherwise

        Raises:
            JobStoreError: If database query fails (NO FALLBACK)
        """
        try:
            result = (
                self.client.schema("octupost")
                .table("jobs")
                .select("*")
                .eq("owner_id", owner_id)
                .eq("idempotency_key", idempotency_key)
                .execute()
            )

            if result.data:
                return self._db_to_legacy_format(result.data[0])
            return None

        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise JobStoreError(f"Failed to find job by idempotency key: {e}") from e

    def cancel_job(self, job_id: str) -> bool:
        """
        Atomically cancel a pending or processing job.

        Uses atomic conditional update to prevent race conditions:
        - Only cancels if current status is 'pending' or 'processing'
        - Returns False if job already completed/failed/cancelled

        Args:
            job_id: The job ID to cancel

        Returns:
            True if job was cancelled, False if not found or not cancellable
        """
        now = datetime.now(timezone.utc)

        try:
            # Atomic update with status check - prevents TOCTOU race condition
            result = (
                self.client.schema("octupost")
                .table("jobs")
                .update({
                    "status": JobStatus.CANCELLED.value,
                    "updated_at": now.isoformat(),
                })
                .eq("id", job_id)
                .in_("status", ["pending", "processing"])  # Only cancel if cancellable
                .execute()
            )

            # Returns True only if a row was actually updated
            return len(result.data) > 0

        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise JobStoreError(f"Failed to cancel job: {e}") from e

    def list_jobs(
        self,
        limit: int = 50,
        status: Optional[JobStatus] = None,
        owner_id: Optional[str] = None,
        job_type: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        List jobs with optional filtering.

        Args:
            limit: Maximum number of jobs to return
            status: Filter by status
            owner_id: Filter by owner (user) ID
            job_type: Filter by job type

        Returns:
            List of job data

        Raises:
            JobStoreError: If database query fails (NO FALLBACK)
        """
        if not owner_id:
            raise JobStoreError("owner_id is required - anonymous job listing not supported")

        try:
            query = (
                self.client.schema("octupost")
                .table("jobs")
                .select("*")
                .eq("owner_id", owner_id)
                .order("created_at", desc=True)
                .limit(limit)
            )

            if status:
                query = query.eq("status", status.value)
            if job_type:
                query = query.eq("type", job_type)

            result = query.execute()

            if result.data:
                return [self._db_to_legacy_format(job) for job in result.data]
            return []

        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise JobStoreError(f"Failed to list jobs from Supabase: {e}") from e

    def _db_to_legacy_format(self, db_job: dict[str, Any]) -> dict[str, Any]:
        """
        Convert database job format to legacy format for backward compatibility.
        
        Args:
            db_job: Job record from Supabase
            
        Returns:
            Job in legacy format expected by existing code
        """
        # Convert status string to JobStatus enum
        status_str = db_job.get("status", "pending")
        try:
            status = JobStatus(status_str)
        except ValueError:
            status = JobStatus.PENDING
        
        # Parse timestamps
        created_at = db_job.get("created_at")
        updated_at = db_job.get("updated_at")
        
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        
        return {
            "job_id": db_job.get("id"),
            "type": db_job.get("type"),
            "status": status,
            "progress": db_job.get("progress", 0),
            "request": db_job.get("params", {}),
            "result": db_job.get("result"),
            "error": db_job.get("error"),
            "created_at": created_at or datetime.now(timezone.utc),
            "updated_at": updated_at or datetime.now(timezone.utc),
            "owner_id": db_job.get("owner_id"),
            "asset_id": db_job.get("asset_id"),
            "model": db_job.get("model"),
            "reservation_id": db_job.get("reservation_id"),
        }


# Create singleton instance
job_store = JobStore()
