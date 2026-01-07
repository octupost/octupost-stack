"""Supabase client for database operations."""

import uuid
from typing import Any, Optional
import sentry_sdk
from supabase import create_client, Client

from app.config import get_settings
from app.services.asset_naming import generate_asset_name
from app.media_types import derive_media_type


class SupabaseService:
    """
    Supabase service for managing assets in the database.
    
    Uses service role key to bypass RLS for server-side operations.
    When Supabase is not configured, operations gracefully return None/empty.
    """

    _client: Optional[Client] = None
    _checked_config: bool = False
    _is_configured: bool = False

    @property
    def is_configured(self) -> bool:
        """Check if Supabase credentials are configured."""
        if not self._checked_config:
            settings = get_settings()
            # Use effective_supabase_url which falls back to NEXT_PUBLIC_SUPABASE_URL
            effective_url = settings.effective_supabase_url
            self._is_configured = bool(
                effective_url and settings.supabase_service_role_key
            )
            self._checked_config = True
            if not self._is_configured:
                print(
                    "[SupabaseService] Supabase not configured - "
                    "asset tracking disabled. Set SUPABASE_URL (or NEXT_PUBLIC_SUPABASE_URL) and "
                    "SUPABASE_SERVICE_ROLE_KEY to enable."
                )
        return self._is_configured

    @property
    def client(self) -> Optional[Client]:
        """Get or create Supabase client. Returns None if not configured."""
        if not self.is_configured:
            return None
        if self._client is None:
            settings = get_settings()
            self._client = create_client(
                settings.effective_supabase_url,
                settings.supabase_service_role_key,
            )
        return self._client

    def create_asset(
        self,
        owner_id: str,
        asset_type: str,
        source: str = "generative_ai",
        generation_params: Optional[dict[str, Any]] = None,
        workplace_id: Optional[str] = None,
        media_type: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> Optional[dict[str, Any]]:
        """
        Create a new asset record with in_queue status.

        Args:
            owner_id: UUID of the asset owner (user)
            asset_type: Type of asset (image, video, avatar_video, speech, music, sound_effect)
            source: Source of asset (local_upload, generative_ai, public_url)
            generation_params: Parameters used for generation (prompt, model, etc.)
            workplace_id: Optional workplace to associate with the asset
            media_type: Fundamental media category (image, audio, video).
                       If not provided, derived from asset_type.
            project_id: Optional project to link the asset to

        Returns:
            The created asset record, or None if Supabase is not configured
        """
        if not self.client:
            return None

        # Resolve workplace: 1) explicit workplace_id, 2) project's workspace, 3) personal workspace
        if workplace_id:
            resolved_workplace_id = workplace_id
        elif project_id:
            resolved_workplace_id = self.get_workspace_id_from_project(project_id) or self.get_personal_workplace_id(owner_id)
        else:
            resolved_workplace_id = self.get_personal_workplace_id(owner_id)

        # Pre-generate asset ID for use in naming
        asset_id = str(uuid.uuid4())

        # Extract generation params for naming
        gen_params = generation_params or {}
        prompt = gen_params.get("prompt")
        model = gen_params.get("model")
        voice = gen_params.get("voice") or gen_params.get("voice_id")

        # Generate a user-friendly name with type prefix, model/voice, and short ID
        asset_name = generate_asset_name(
            asset_type=asset_type,
            source=source,
            prompt=prompt,
            model=model,
            voice=voice,
            asset_id=asset_id,
        )

        # Derive media_type from asset_type if not provided
        if media_type is None:
            media_type = derive_media_type(asset_type)

        data = {
            "id": asset_id,
            "owner_id": owner_id,
            "name": asset_name,
            "asset_type": asset_type,
            "media_type": media_type,
            "source": source,
            "generation_status": "in_queue",
            "generation_params": gen_params,
        }

        result = (
            self.client.schema("octupost")
            .table("assets")
            .insert(data)
            .execute()
        )

        asset = result.data[0] if result.data else {}

        sentry_sdk.set_context(
            "asset",
            {
                "operation": "create_asset",
                "owner_id": owner_id,
                "asset_id": asset.get("id") if asset else None,
                "workplace_id": resolved_workplace_id,
                "asset_type": asset_type,
            },
        )

        if not asset:
            sentry_sdk.capture_message(
                "[SupabaseService] Asset creation returned empty result",
                level="warning",
            )

        # Link asset to workplace if we have one
        if asset and resolved_workplace_id:
            try:
                self.link_asset_to_workplace(asset["id"], resolved_workplace_id)
            except Exception as exc:
                # Avoid failing asset creation due to linkage issues
                sentry_sdk.capture_exception(exc)
                print(f"[SupabaseService] Failed to link asset to workplace: {exc}")

        # Link asset to project if provided
        if asset and project_id:
            try:
                self.link_asset_to_project(asset["id"], project_id)
            except Exception as exc:
                # Avoid failing asset creation due to linkage issues
                sentry_sdk.capture_exception(exc)
                print(f"[SupabaseService] Failed to link asset to project: {exc}")

        return asset

    def link_asset_to_workplace(self, asset_id: str, workplace_id: str) -> None:
        """
        Insert or upsert a workplace->asset association.
        """
        if not self.client:
            return

        sentry_sdk.set_context(
            "asset",
            {
                "operation": "link_asset_to_workplace",
                "asset_id": asset_id,
                "workplace_id": workplace_id,
            },
        )

        (
            self.client.schema("octupost")
            .table("workplace_assets")
            .upsert(
                {
                    "asset_id": asset_id,
                    "workplace_id": workplace_id,
                },
                on_conflict="workplace_id,asset_id",
            )
            .execute()
        )

    def link_asset_to_project(self, asset_id: str, project_id: str) -> None:
        """
        Insert or upsert a project->asset association.

        Uses upsert to avoid duplicate errors if the link already exists.
        """
        if not self.client:
            return

        sentry_sdk.set_context(
            "asset",
            {
                "operation": "link_asset_to_project",
                "asset_id": asset_id,
                "project_id": project_id,
            },
        )

        (
            self.client.schema("octupost")
            .table("project_assets")
            .upsert(
                {
                    "asset_id": asset_id,
                    "project_id": project_id,
                },
                on_conflict="project_id,asset_id",
            )
            .execute()
        )

    def get_personal_workplace_id(self, owner_id: str) -> Optional[str]:
        """
        Fetch the personal workspace for the given owner, if it exists.
        """
        if not self.client:
            return None

        sentry_sdk.set_context(
            "asset",
            {
                "operation": "get_personal_workplace_id",
                "owner_id": owner_id,
            },
        )

        result = (
            self.client.schema("octupost")
            .table("workplaces")
            .select("id")
            .eq("owner_id", owner_id)
            .eq("is_personal", True)
            .limit(1)
            .execute()
        )

        if result.data:
            return result.data[0]["id"]
        return None

    def get_workspace_id_from_project(self, project_id: str) -> Optional[str]:
        """
        Fetch the workspace_id for a given project from workplace_projects table.
        Returns None if project has no workspace association.
        """
        if not self.client:
            return None

        result = (
            self.client.schema("octupost")
            .table("workplace_projects")
            .select("workplace_id")
            .eq("project_id", project_id)
            .limit(1)
            .execute()
        )

        if result.data and len(result.data) > 0:
            return result.data[0].get("workplace_id")
        return None

    def update_asset_status(
        self,
        asset_id: str,
        status: str,
        url: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        progress: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Update asset generation status and optionally set result data.

        Args:
            asset_id: UUID of the asset
            status: New status (in_queue, processing, success, failed)
            url: URL of the generated asset (set on success)
            metadata: Additional metadata (dimensions, duration, file_size_bytes, etc.)
            progress: Generation progress percentage (0-100)

        Returns:
            The updated asset record, or empty dict if not configured
        """
        if not self.client:
            return {}

        sentry_sdk.set_context(
            "asset",
            {
                "operation": "update_asset_status",
                "asset_id": asset_id,
                "status": status,
            },
        )

        data: dict[str, Any] = {"generation_status": status}

        if url is not None:
            data["url"] = url
        
        # Merge progress into metadata if provided
        if metadata is not None or progress is not None:
            merged_metadata = metadata or {}
            if progress is not None:
                merged_metadata["progress"] = progress
            data["metadata"] = merged_metadata

        result = (
            self.client.schema("octupost")
            .table("assets")
            .update(data)
            .eq("id", asset_id)
            .execute()
        )

        if not result.data:
            sentry_sdk.capture_message(
                "[SupabaseService] Asset update returned empty result",
                level="warning",
            )
            return {}

        return result.data[0]

    def get_asset(self, asset_id: str) -> Optional[dict[str, Any]]:
        """
        Get an asset by ID.

        Args:
            asset_id: UUID of the asset

        Returns:
            The asset record or None if not found/not configured
        """
        if not self.client:
            return None

        sentry_sdk.set_context(
            "asset",
            {
                "operation": "get_asset",
                "asset_id": asset_id,
            },
        )

        result = (
            self.client.schema("octupost")
            .table("assets")
            .select("*")
            .eq("id", asset_id)
            .is_("deleted_at_utc", "null")
            .execute()
        )

        return result.data[0] if result.data else None

    def list_user_assets(
        self,
        owner_id: str,
        asset_type: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        List assets for a user.

        Args:
            owner_id: UUID of the owner
            asset_type: Optional filter by type
            limit: Maximum number of results

        Returns:
            List of asset records, or empty list if not configured
        """
        if not self.client:
            return []

        sentry_sdk.set_context(
            "asset",
            {
                "operation": "list_user_assets",
                "owner_id": owner_id,
                "asset_type": asset_type,
            },
        )

        query = (
            self.client.schema("octupost")
            .table("assets")
            .select("*")
            .eq("owner_id", owner_id)
            .is_("deleted_at_utc", "null")
            .order("created_at_utc", desc=True)
            .limit(limit)
        )

        if asset_type:
            query = query.eq("asset_type", asset_type)

        result = query.execute()
        return result.data or []

    def soft_delete_asset(self, asset_id: str) -> bool:
        """
        Soft delete an asset.

        Args:
            asset_id: UUID of the asset

        Returns:
            True if deleted, False if not found/not configured
        """
        if not self.client:
            return False

        sentry_sdk.set_context(
            "asset",
            {
                "operation": "soft_delete_asset",
                "asset_id": asset_id,
            },
        )

        from datetime import datetime, timezone

        result = (
            self.client.schema("octupost")
            .table("assets")
            .update({"deleted_at_utc": datetime.now(timezone.utc).isoformat()})
            .eq("id", asset_id)
            .execute()
        )

        return len(result.data) > 0 if result.data else False

    # derive_media_type is now imported from app.types (centralized in packages/shared/src/types/types.json)

    # =========================================================================
    # Generation Cost Logging
    # =========================================================================

    def log_generation_cost(
        self,
        user_id: str,
        job_id: str,
        model_id: str,
        generation_type: str,
        credits_charged: int,
        input_params: dict,
    ) -> None:
        """
        Log a generation charge for cost monitoring.
        
        This data can be cross-referenced with Fal's Usage API to verify pricing accuracy.
        
        Args:
            user_id: User who was charged
            job_id: Associated job ID
            model_id: Model endpoint used
            generation_type: Type of generation (text-to-video, etc.)
            credits_charged: Credits that were deducted
            input_params: Parameters that affect pricing (duration, resolution, etc.)
        """
        if not self.client:
            return
        
        try:
            self.client.schema("octupost").table("generation_cost_log").insert({
                "user_id": user_id,
                "job_id": job_id,
                "model_id": model_id,
                "generation_type": generation_type,
                "credits_charged": credits_charged,
                "input_params": input_params,
            }).execute()
        except Exception as e:
            # Non-critical - don't fail generation, but log for monitoring
            sentry_sdk.capture_exception(e)

# Singleton instance
supabase_service = SupabaseService()

