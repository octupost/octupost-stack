"""Supabase client for database operations."""

from typing import Any, Optional
import sentry_sdk
from supabase import create_client, Client

from app.config import get_settings
from app.services.asset_naming import generate_asset_name


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
    ) -> Optional[dict[str, Any]]:
        """
        Create a new asset record with in_queue status.

        Args:
            owner_id: UUID of the asset owner (user)
            asset_type: Type of asset (image, video, avatar_video, speech, music, soundtrack)
            source: Source of asset (local_upload, generative_ai, public_url)
            generation_params: Parameters used for generation (prompt, model, etc.)
            workplace_id: Optional workplace to associate with the asset
            media_type: Fundamental media category (image, audio, video). 
                       If not provided, derived from asset_type.

        Returns:
            The created asset record, or None if Supabase is not configured
        """
        if not self.client:
            return None

        # Resolve workplace: prefer provided; otherwise fall back to personal workspace for the owner
        resolved_workplace_id = workplace_id or self.get_personal_workplace_id(owner_id)

        # Generate a user-friendly name from the prompt (for AI-generated assets)
        prompt = (generation_params or {}).get("prompt")
        asset_name = generate_asset_name(
            asset_type=asset_type,
            source=source,
            prompt=prompt,
        )

        # Derive media_type from asset_type if not provided
        if media_type is None:
            media_type = self._derive_media_type(asset_type)

        data = {
            "owner_id": owner_id,
            "name": asset_name,
            "type": asset_type,
            "media_type": media_type,
            "source": source,
            "generation_status": "in_queue",
            "generation_params": generation_params or {},
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
            query = query.eq("type", asset_type)

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

    @staticmethod
    def _derive_media_type(asset_type: str) -> str:
        """
        Derive the fundamental media_type from a specific asset_type.
        
        Args:
            asset_type: Specific asset type (image, video, avatar_video, speech, music, soundtrack)
            
        Returns:
            Fundamental media type (image, audio, video)
        """
        if asset_type in ("video", "avatar_video"):
            return "video"
        elif asset_type == "image":
            return "image"
        elif asset_type in ("speech", "music", "soundtrack"):
            return "audio"
        else:
            # Fallback for unknown types
            return "video"


    # =========================================================================
    # Model Config Operations
    # =========================================================================
    
    def get_model_config(self, endpoint: str) -> Optional[dict[str, Any]]:
        """
        Get model configuration from model_configs table.
        
        This includes admin-defined param_defaults which are used
        to set default values for parameters (especially hidden ones).
        
        Args:
            endpoint: Model endpoint (e.g., "fal-ai/veo3.1")
            
        Returns:
            Model config dict including param_defaults, or None if not found
        """
        if not self.client:
            return None
        
        try:
            result = (
                self.client.schema("octupost")
                .table("model_configs")
                .select("*")
                .eq("endpoint", endpoint)
                .eq("is_active", True)
                .limit(1)
                .execute()
            )
            
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None
    
    def get_model_param_defaults(self, endpoint: str) -> dict[str, Any]:
        """
        Get admin-defined param_defaults for a model.
        
        These are default values set in the admin panel that should
        always be sent (for hidden params) or used as initial values
        (for visible params).
        
        Args:
            endpoint: Model endpoint (e.g., "fal-ai/veo3.1")
            
        Returns:
            Dictionary of parameter defaults, or empty dict if not found
        """
        config = self.get_model_config(endpoint)
        if config:
            return config.get("param_defaults", {})
        return {}


# Singleton instance
supabase_service = SupabaseService()

