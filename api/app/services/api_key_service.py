"""API Key service for external developer authentication."""

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import sentry_sdk

from app.services.supabase_client import supabase_service


@dataclass
class ApiKeyInfo:
    """Information about a validated API key."""
    key_id: str
    user_id: str
    name: str


@dataclass
class ApiKeyMetadata:
    """API key metadata (without the secret)."""
    id: str
    name: str
    key_prefix: str
    created_at: datetime
    last_used_at: Optional[datetime]
    is_active: bool


class ApiKeyService:
    """
    Service for managing API keys.

    API keys allow external developers to authenticate without
    exposing internal user IDs. Keys are stored as SHA-256 hashes.
    """

    PREFIX = "oct_sk_"

    def generate_key(self) -> tuple[str, str, str]:
        """
        Generate a new API key.

        Returns:
            Tuple of (plaintext_key, key_hash, key_prefix)
        """
        # Generate 24 bytes = 32 base64 characters
        secret = secrets.token_urlsafe(24)
        full_key = f"{self.PREFIX}{secret}"
        key_hash = self._hash_key(full_key)
        key_prefix = full_key[:16]  # "oct_sk_" + first 9 chars
        return full_key, key_hash, key_prefix

    def _hash_key(self, key: str) -> str:
        """Hash a key using SHA-256."""
        return hashlib.sha256(key.encode()).hexdigest()

    async def validate_key(self, key: str) -> Optional[ApiKeyInfo]:
        """
        Validate an API key and return the associated user info.

        Args:
            key: The full API key (oct_sk_...)

        Returns:
            ApiKeyInfo if valid, None otherwise
        """
        if not key.startswith(self.PREFIX):
            return None

        client = supabase_service.client
        if not client:
            return None

        key_hash = self._hash_key(key)

        try:
            result = (
                client.schema("octupost")
                .table("api_keys")
                .select("id, user_id, name")
                .eq("key_hash", key_hash)
                .eq("is_active", True)
                .limit(1)
                .execute()
            )

            if not result.data:
                return None

            row = result.data[0]

            # Update last_used_at asynchronously (fire and forget)
            self._update_last_used(row["id"])

            return ApiKeyInfo(
                key_id=row["id"],
                user_id=row["user_id"],
                name=row["name"],
            )

        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None

    def _update_last_used(self, key_id: str) -> None:
        """Update the last_used_at timestamp for a key."""
        client = supabase_service.client
        if not client:
            return

        try:
            (
                client.schema("octupost")
                .table("api_keys")
                .update({"last_used_at": datetime.utcnow().isoformat()})
                .eq("id", key_id)
                .execute()
            )
        except Exception as e:
            # Non-critical, don't fail the request
            sentry_sdk.capture_exception(e)

    async def create_key(
        self,
        user_id: str,
        name: str = "Default",
    ) -> tuple[str, str]:
        """
        Create a new API key for a user.

        Args:
            user_id: UUID of the user
            name: Human-readable name for the key

        Returns:
            Tuple of (plaintext_key, key_id)

        Raises:
            Exception if creation fails
        """
        client = supabase_service.client
        if not client:
            raise RuntimeError("Supabase not configured")

        full_key, key_hash, key_prefix = self.generate_key()

        sentry_sdk.set_context("api_key", {
            "operation": "create_key",
            "user_id": user_id,
            "key_prefix": key_prefix,
        })

        result = (
            client.schema("octupost")
            .table("api_keys")
            .insert({
                "user_id": user_id,
                "key_hash": key_hash,
                "key_prefix": key_prefix,
                "name": name,
            })
            .execute()
        )

        if not result.data:
            raise RuntimeError("Failed to create API key")

        key_id = result.data[0]["id"]
        return full_key, key_id

    async def revoke_key(self, key_id: str, user_id: str) -> bool:
        """
        Revoke an API key.

        Args:
            key_id: UUID of the key to revoke
            user_id: UUID of the user (for authorization)

        Returns:
            True if revoked, False if not found or not owned by user
        """
        client = supabase_service.client
        if not client:
            return False

        sentry_sdk.set_context("api_key", {
            "operation": "revoke_key",
            "key_id": key_id,
            "user_id": user_id,
        })

        try:
            result = (
                client.schema("octupost")
                .table("api_keys")
                .update({"is_active": False})
                .eq("id", key_id)
                .eq("user_id", user_id)  # Ensure user owns this key
                .eq("is_active", True)   # Only revoke active keys
                .execute()
            )

            return len(result.data) > 0 if result.data else False

        except Exception as e:
            sentry_sdk.capture_exception(e)
            return False

    async def list_keys(self, user_id: str) -> list[ApiKeyMetadata]:
        """
        List all API keys for a user (without secrets).

        Args:
            user_id: UUID of the user

        Returns:
            List of ApiKeyMetadata objects
        """
        client = supabase_service.client
        if not client:
            return []

        sentry_sdk.set_context("api_key", {
            "operation": "list_keys",
            "user_id": user_id,
        })

        try:
            result = (
                client.schema("octupost")
                .table("api_keys")
                .select("id, name, key_prefix, created_at, last_used_at, is_active")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )

            return [
                ApiKeyMetadata(
                    id=row["id"],
                    name=row["name"],
                    key_prefix=row["key_prefix"],
                    created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
                    last_used_at=(
                        datetime.fromisoformat(row["last_used_at"].replace("Z", "+00:00"))
                        if row["last_used_at"]
                        else None
                    ),
                    is_active=row["is_active"],
                )
                for row in (result.data or [])
            ]

        except Exception as e:
            sentry_sdk.capture_exception(e)
            return []


# Singleton instance
api_key_service = ApiKeyService()
