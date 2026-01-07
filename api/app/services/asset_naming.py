"""
Asset Naming Utilities

Auto-generates user-friendly names for assets based on available data:
- Generated assets: Uses first words from the prompt with model/voice info
- Uploaded files: Cleans up the filename
- URL imports: Extracts filename from URL path
- All assets: Include type prefix and short ID for clarity

Format: [Type] {content} - {model/voice}_{shortId}
Example: [Speech] Welcome intro - Sarah_x7k2
"""

import re
import random
import string
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse, unquote


MAX_NAME_LENGTH = 60
SHORT_ID_LENGTH = 4

# Type prefix mapping for asset types
TYPE_PREFIXES = {
    "image": "[Image]",
    "video": "[Video]",
    "avatar_video": "[Avatar]",
    "avatar_image": "[Avatar]",
    "speech": "[Speech]",
    "music": "[Music]",
    "sound_effect": "[SFX]",
}

# Friendly display names for common AI models
MODEL_DISPLAY_NAMES = {
    # Video models
    "fal-ai/minimax/video-01": "MiniMax",
    "fal-ai/minimax/video-01-live": "MiniMax",
    "fal-ai/kling-video/v1/standard/text-to-video": "Kling",
    "fal-ai/kling-video/v1.5/pro/text-to-video": "Kling Pro",
    "fal-ai/kling-video/v1.6/pro/text-to-video": "Kling Pro",
    "fal-ai/luma-dream-machine": "Luma",
    "fal-ai/hunyuan-video": "Hunyuan",
    "fal-ai/veo2": "Veo2",
    "fal-ai/wan-t2v": "Wan",
    # Image models
    "fal-ai/flux/dev": "Flux",
    "fal-ai/flux-pro": "Flux Pro",
    "fal-ai/flux-pro/v1.1": "Flux Pro",
    "fal-ai/flux-pro/v1.1-ultra": "Flux Ultra",
    "fal-ai/recraft-v3": "Recraft",
    "fal-ai/ideogram/v2": "Ideogram",
    "fal-ai/ideogram/v2/turbo": "Ideogram",
    "openai/gpt-image-1": "GPT Image",
    "openai/gpt-image-1-mini": "GPT Image",
    # Audio/Music models
    "fal-ai/stable-audio": "Stable Audio",
    "udio/v1": "Udio",
    "suno/v3": "Suno",
    # TTS models
    "elevenlabs-v2": "ElevenLabs",
    "elevenlabs-v3": "ElevenLabs",
    "elevenlabs-turbo": "ElevenLabs",
}


def _capitalize(s: str) -> str:
    """Capitalize first letter of a string."""
    return s[0].upper() + s[1:] if s else s


def _truncate(s: str, max_length: int) -> str:
    """Truncate string to max length, adding ellipsis if needed."""
    if len(s) <= max_length:
        return s
    return s[:max_length - 1].rstrip() + "…"


def _clean_filename(filename: str) -> str:
    """
    Clean up a filename for display.
    - Removes extension
    - Removes timestamp prefixes
    - Replaces underscores/dashes with spaces
    - Splits camelCase
    """
    name = filename
    
    # Remove extension
    name = re.sub(r'\.[^.]+$', '', name)
    
    # Remove common timestamp prefixes (13-digit timestamp followed by dash)
    name = re.sub(r'^\d{10,13}-', '', name)
    
    # Remove UUID prefixes
    name = re.sub(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}-?', '', name, flags=re.IGNORECASE)
    
    # Replace underscores and dashes with spaces
    name = re.sub(r'[_-]', ' ', name)
    
    # Split camelCase (e.g., "myVideo" -> "my Video")
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
    
    # Clean up multiple spaces
    name = re.sub(r'\s+', ' ', name).strip()
    
    # If the result is empty or just numbers, return empty
    if not name or re.match(r'^\d+$', name):
        return ""
    
    return name


def _extract_filename_from_url(url: str) -> Optional[str]:
    """
    Extract filename from a URL.
    Handles various URL formats and CDN patterns.
    """
    try:
        parsed = urlparse(url)
        pathname = parsed.path
        
        # Get the last segment of the path
        segments = [s for s in pathname.split('/') if s]
        if not segments:
            return None
        
        last_segment = segments[-1]
        
        # Check if it looks like a filename (has extension)
        if re.search(r'\.[a-z0-9]{2,5}$', last_segment, re.IGNORECASE):
            # Decode URL encoding (e.g., %20 -> space)
            decoded = unquote(last_segment)
            cleaned = _clean_filename(decoded)
            
            # If cleaned result is meaningful (not just hash/uuid), use it
            if cleaned and len(cleaned) > 2 and not re.match(r'^[a-f0-9]+$', cleaned, re.IGNORECASE):
                return cleaned
        
        return None
    except Exception:
        return None


def _extract_prompt_excerpt(prompt: str, max_words: int = 4) -> str:
    """
    Extract prompt excerpt for naming.
    Takes first N meaningful words from a prompt.
    """
    # Remove special characters and extra whitespace
    cleaned = re.sub(r"[^\w\s'-]", " ", prompt)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # Split into words and take first N
    words = cleaned.split(" ")[:max_words]

    # Join and capitalize first letter
    excerpt = " ".join(words)
    return _capitalize(excerpt)


def _generate_short_id(asset_id: Optional[str] = None) -> str:
    """
    Generate a short ID from an asset UUID.
    Uses first 4 characters of the UUID (without dashes).
    """
    if asset_id:
        # Use first 4 chars of UUID (after removing dashes)
        return asset_id.replace("-", "")[:SHORT_ID_LENGTH].lower()
    # Generate random 4-char alphanumeric
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choice(chars) for _ in range(SHORT_ID_LENGTH))


def _get_model_display_name(model_id: Optional[str]) -> Optional[str]:
    """
    Get a friendly display name for an AI model.
    """
    if not model_id:
        return None

    # Check known models first
    if model_id in MODEL_DISPLAY_NAMES:
        return MODEL_DISPLAY_NAMES[model_id]

    # Extract last part of model ID and clean it up
    # e.g., "fal-ai/flux-pro/v1.1" -> "Flux Pro V1 1"
    parts = model_id.split("/")
    last_part = parts[-1]
    # Replace dashes/underscores with spaces and title case
    cleaned = re.sub(r"[-_]", " ", last_part)
    cleaned = cleaned.title()[:15]  # Max 15 chars for model name

    return cleaned if cleaned else None


def generate_asset_name(
    asset_type: str,
    source: str,
    prompt: Optional[str] = None,
    filename: Optional[str] = None,
    url: Optional[str] = None,
    model: Optional[str] = None,
    voice: Optional[str] = None,
    asset_id: Optional[str] = None,
) -> str:
    """
    Generate a user-friendly name for an asset.

    Format: [Type] {content} - {model/voice}_{shortId}

    Args:
        asset_type: Type of asset (video, image, audio, speech, sound_effect)
        source: Source of asset (generative_ai, local_upload, public_url)
        prompt: Generation prompt (for AI-generated assets)
        filename: Original filename (for uploads)
        url: Asset URL (for URL imports)
        model: AI model ID (for AI-generated assets)
        voice: Voice name (for speech assets)
        asset_id: Asset UUID (for generating short ID)

    Returns:
        Generated name string

    Examples:
        >>> generate_asset_name('speech', 'generative_ai', prompt='Welcome to our channel', voice='Sarah', asset_id='abc12345')
        '[Speech] Welcome to our - Sarah_abc1'

        >>> generate_asset_name('image', 'generative_ai', prompt='Sunset over ocean', model='fal-ai/flux/dev', asset_id='xyz98765')
        '[Image] Sunset over ocean - Flux_xyz9'

        >>> generate_asset_name('video', 'local_upload', filename='my_vacation_video.mp4', asset_id='def45678')
        '[Video] my vacation video_def4'
    """
    date_str = datetime.now().strftime("%b %d")  # e.g., "Dec 13"

    # Build name parts
    parts = []

    # 1. Type prefix
    prefix = TYPE_PREFIXES.get(asset_type, f"[{_capitalize(asset_type)}]")
    parts.append(prefix)

    # 2. Content name
    content_name = ""

    # Generated assets: Use first words of prompt
    if source == "generative_ai" and prompt:
        content_name = _extract_prompt_excerpt(prompt, 4)

    # Local uploads: Clean up filename
    if not content_name and source == "local_upload" and filename:
        content_name = _clean_filename(filename)

    # URL imports: Try to extract filename from URL
    if not content_name and source == "public_url" and url:
        content_name = _extract_filename_from_url(url) or ""

    # Fallback: Also check filename/url regardless of source
    if not content_name and filename:
        content_name = _clean_filename(filename)

    if not content_name and url:
        content_name = _extract_filename_from_url(url) or ""

    # 3. Model/voice indicator (for AI-generated assets)
    if asset_type in ("speech", "avatar_video"):
        model_name = voice or _get_model_display_name(model)
    else:
        model_name = _get_model_display_name(model)

    # 4. Combine content and model
    if content_name:
        if model_name and source == "generative_ai":
            parts.append(f"{content_name} - {model_name}")
        else:
            parts.append(content_name)
    else:
        # Final fallback: Date (with model if available)
        if model_name and source == "generative_ai":
            parts.append(f"{date_str} - {model_name}")
        else:
            parts.append(date_str)

    # Build name without short ID first
    name = " ".join(parts)

    # Truncate to leave room for short ID suffix (_xxxx = 5 chars)
    max_content_length = MAX_NAME_LENGTH - 5
    name = _truncate(name, max_content_length)

    # 5. Add short ID suffix
    short_id = _generate_short_id(asset_id)
    name = f"{name}_{short_id}"

    return name

















