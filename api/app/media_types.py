"""
Centralized Type Definitions

Single source of truth for media types, asset types, and related mappings.
These types are loaded from packages/shared/src/types/types.json and are
shared with the frontend TypeScript code.

Usage:
    from app.media_types import MEDIA_TYPES, ASSET_TYPES, derive_media_type
"""

import json
from pathlib import Path
from typing import Literal

# =============================================================================
# Load shared types from JSON
# =============================================================================

_TYPES_JSON_PATH = Path(__file__).parent.parent.parent / "packages" / "shared" / "src" / "types" / "types.json"

with open(_TYPES_JSON_PATH, "r") as f:
    _types_config = json.load(f)

# =============================================================================
# Constants
# =============================================================================

MEDIA_TYPES: tuple[str, ...] = tuple(_types_config["mediaTypes"])
"""All valid media types: ('image', 'video', 'audio')"""

ASSET_TYPES: tuple[str, ...] = tuple(_types_config["assetTypes"])
"""All valid asset types: ('image', 'video', 'avatar_video', 'avatar_image', 'speech', 'music', 'sound_effect')"""

COMPOSER_DISPLAY_SECTIONS: tuple[str, ...] = tuple(_types_config["composerDisplaySections"])
"""All valid composer display sections: ('image', 'video', 'avatar', 'speech', 'music', 'sound_effect')"""

ASSET_TYPE_TO_MEDIA_TYPE: dict[str, str] = _types_config["assetTypeToMediaType"]
"""Mapping from asset type to its fundamental media type"""

# =============================================================================
# Type Aliases (for type hints)
# =============================================================================

MediaType = Literal["image", "video", "audio"]
AssetType = Literal["image", "video", "avatar_video", "avatar_image", "speech", "music", "sound_effect"]
ComposerDisplaySection = Literal["image", "video", "avatar", "speech", "music", "sound_effect"]

# =============================================================================
# Helper Functions
# =============================================================================


def derive_media_type(asset_type: str) -> str:
    """
    Derive the fundamental media type from a specific asset type.

    Args:
        asset_type: The specific asset type (e.g., 'avatar_video', 'speech')

    Returns:
        The fundamental media type ('image', 'video', or 'audio')

    Examples:
        >>> derive_media_type("avatar_video")
        'video'
        >>> derive_media_type("speech")
        'audio'
        >>> derive_media_type("unknown")
        'video'
    """
    return ASSET_TYPE_TO_MEDIA_TYPE.get(asset_type, "video")


def is_valid_media_type(value: str) -> bool:
    """Check if a string is a valid media type."""
    return value in MEDIA_TYPES


def is_valid_asset_type(value: str) -> bool:
    """Check if a string is a valid asset type."""
    return value in ASSET_TYPES


def is_valid_composer_display_section(value: str) -> bool:
    """Check if a string is a valid composer display section."""
    return value in COMPOSER_DISPLAY_SECTIONS
