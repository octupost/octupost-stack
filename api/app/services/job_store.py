"""Persistent job store using Supabase for tracking generation jobs."""

from datetime import datetime, timezone
from typing import Any, Optional
import sentry_sdk
from ulid import ULID

from app.models.schemas import JobStatus


class JobStore:
    """
    Supabase-backed job store for tracking job status.
    
    Stores jobs in the octupost.jobs table for persistence across
    server restarts and page refreshes. Supports Realtime subscriptions
    for instant frontend updates.
    
    When Supabase is not configured, falls back to in-memory storage.
    """

    def __init__(self):
        # Fallback in-memory storage when Supabase is not configured
        self._fallback_jobs: dict[str, dict[str, Any]] = {}
        self._client = None
        self._checked_config = False
        self._is_configured = False

    @property
    def is_configured(self) -> bool:
        """Check if Supabase is configured for job storage."""
        if not self._checked_config:
            from app.config import get_settings
            settings = get_settings()
            effective_url = settings.effective_supabase_url
            self._is_configured = bool(
                effective_url and settings.supabase_service_role_key
            )
            self._checked_config = True
            if not self._is_configured:
                print(
                    "[JobStore] Supabase not configured - "
                    "using in-memory fallback. Jobs will not persist across restarts."
                )
        return self._is_configured

    @property
    def client(self):
        """Get or create Supabase client. Returns None if not configured."""
        if not self.is_configured:
            return None
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
    ) -> str:
        """
        Create a new job and return its ID.

        Args:
            job_type: Type of generation job (text-to-image, text-to-video, avatar, etc.)
            request_data: The original request parameters
            owner_id: UUID of the job owner (user)
            asset_id: UUID of the associated asset

        Returns:
            Unique job ID (ULID)
        """
        job_id = str(ULID())
        now = datetime.now(timezone.utc)
        
        # Extract model from request_data
        model = request_data.get("model", "unknown")
        
        # Extract credit info
        credits_estimated = request_data.get("credits")
        reservation_id = request_data.get("reservation_id")
        
        # Build params (exclude metadata fields)
        metadata_fields = {"model", "credits", "needs_reservation", "estimated_duration", "reservation_id"}
        params = {k: v for k, v in request_data.items() if k not in metadata_fields}

        if self.client and owner_id:
            try:
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
                    "reservation_id": reservation_id,
                    "created_at": now.isoformat(),
                    "updated_at": now.isoformat(),
                }
                
                self.client.schema("octupost").table("jobs").insert(data).execute()
                
                sentry_sdk.set_context("job", {
                    "operation": "create_job",
                    "job_id": job_id,
                    "owner_id": owner_id,
                    "type": job_type,
                    "model": model,
                })
                
            except Exception as e:
                sentry_sdk.capture_exception(e)
                print(f"[JobStore] Failed to create job in Supabase: {e}")
                # Fall through to in-memory fallback
        
        # Always maintain in-memory copy for backward compatibility
        # and as fallback when Supabase is not configured
        self._fallback_jobs[job_id] = {
            "job_id": job_id,
            "type": job_type,
            "status": JobStatus.PENDING,
            "progress": 0,
            "request": request_data,
            "result": None,
            "error": None,
            "created_at": now,
            "updated_at": now,
            "owner_id": owner_id,
            "asset_id": asset_id,
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
        # Try Supabase first
        if self.client:
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
                    # Convert to legacy format for backward compatibility
                    return self._db_to_legacy_format(db_job)
                    
            except Exception as e:
                sentry_sdk.capture_exception(e)
                print(f"[JobStore] Failed to get job from Supabase: {e}")
        
        # Fallback to in-memory
        return self._fallback_jobs.get(job_id)

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
        now = datetime.now(timezone.utc)
        
        # Update in Supabase
        if self.client:
            try:
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
                
                update_result = (
                    self.client.schema("octupost")
                    .table("jobs")
                    .update(data)
                    .eq("id", job_id)
                    .execute()
                )
                
                # Supabase update succeeded if we got here without exception
                sentry_sdk.add_breadcrumb(
                    category="job",
                    message=f"Job {job_id} updated to {status.value}",
                    level="info",
                )
                
            except Exception as e:
                sentry_sdk.capture_exception(e)
                print(f"[JobStore] Failed to update job in Supabase: {e}")

        # Also update in-memory fallback
        if job_id not in self._fallback_jobs:
            return False

        job = self._fallback_jobs[job_id]
        job["status"] = status
        job["updated_at"] = now

        if progress is not None:
            job["progress"] = progress
        if result is not None:
            job["result"] = result
        if error is not None:
            job["error"] = error

        return True

    def set_job_asset(self, job_id: str, asset_id: str) -> bool:
        """
        Set the asset_id for a job after asset creation.

        Args:
            job_id: The job ID
            asset_id: The asset ID to associate

        Returns:
            True if updated successfully
        """
        # Update in Supabase
        if self.client:
            try:
                self.client.schema("octupost").table("jobs").update({
                    "asset_id": asset_id,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }).eq("id", job_id).execute()
            except Exception as e:
                sentry_sdk.capture_exception(e)
                print(f"[JobStore] Failed to set job asset in Supabase: {e}")

        # Update in-memory fallback
        if job_id in self._fallback_jobs:
            self._fallback_jobs[job_id]["asset_id"] = asset_id
            return True
        return False

    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a pending job.

        Args:
            job_id: The job ID to cancel

        Returns:
            True if job was cancelled, False if not found or not cancellable
        """
        # Try to get current status first
        job = self.get_job(job_id)
        if not job:
            return False

        # Can only cancel pending or processing jobs
        current_status = job.get("status")
        if isinstance(current_status, JobStatus):
            if current_status not in [JobStatus.PENDING, JobStatus.PROCESSING]:
                return False
        elif isinstance(current_status, str):
            if current_status not in ["pending", "processing"]:
                return False
        else:
            return False

        # Update status to cancelled
        return self.update_job_status(job_id, JobStatus.CANCELLED)

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
        """
        # Try Supabase first
        if self.client and owner_id:
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
                print(f"[JobStore] Failed to list jobs from Supabase: {e}")
        
        # Fallback to in-memory
        jobs = list(self._fallback_jobs.values())

        # Filter by owner if provided
        if owner_id:
            jobs = [j for j in jobs if j.get("owner_id") == owner_id]
        
        # Filter by status if provided
        if status:
            jobs = [j for j in jobs if j["status"] == status]
        
        # Filter by type if provided
        if job_type:
            jobs = [j for j in jobs if j.get("type") == job_type]

        # Sort by created_at descending
        jobs.sort(key=lambda x: x["created_at"], reverse=True)

        return jobs[:limit]

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
        }


# Create singleton instance
job_store = JobStore()
