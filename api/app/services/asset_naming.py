"""
Asset Naming Utilities

Auto-generates user-friendly names for assets based on available data:
- Generated assets: Uses first words from the prompt
- Uploaded files: Cleans up the filename
- URL imports: Extracts filename from URL path
- Fallback: Type + date format
"""

import re
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse, unquote


MAX_NAME_LENGTH = 50


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


def _extract_prompt_excerpt(prompt: str, max_words: int = 5) -> str:
    """
    Extract prompt excerpt for naming.
    Takes first N meaningful words from a prompt.
    """
    # Remove special characters and extra whitespace
    cleaned = re.sub(r"[^\w\s'-]", ' ', prompt)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # Split into words and take first N
    words = cleaned.split(' ')[:max_words]
    
    # Join and capitalize first letter
    excerpt = ' '.join(words)
    return _capitalize(excerpt)


def generate_asset_name(
    asset_type: str,
    source: str,
    prompt: Optional[str] = None,
    filename: Optional[str] = None,
    url: Optional[str] = None,
) -> str:
    """
    Generate a user-friendly name for an asset.
    
    Args:
        asset_type: Type of asset (video, image, audio, speech, soundtrack)
        source: Source of asset (generative_ai, local_upload, public_url)
        prompt: Generation prompt (for AI-generated assets)
        filename: Original filename (for uploads)
        url: Asset URL (for URL imports)
    
    Returns:
        Generated name string
    
    Examples:
        >>> generate_asset_name('video', 'generative_ai', prompt='A cinematic sunset over calm ocean')
        'A cinematic sunset over calm'
        
        >>> generate_asset_name('video', 'local_upload', filename='my_vacation_video.mp4')
        'my vacation video'
        
        >>> generate_asset_name('image', 'public_url', url='https://example.com/sunset-beach.jpg')
        'sunset beach'
    """
    type_label = _capitalize(asset_type)
    date_str = datetime.now().strftime("%b %d")  # e.g., "Dec 13"

    # 1. Generated assets: Use first words of prompt
    if source == "generative_ai" and prompt:
        excerpt = _extract_prompt_excerpt(prompt, 5)
        if excerpt:
            return _truncate(excerpt, MAX_NAME_LENGTH)

    # 2. Local uploads: Clean up filename
    if source == "local_upload" and filename:
        cleaned = _clean_filename(filename)
        if cleaned:
            return _truncate(cleaned, MAX_NAME_LENGTH)

    # 3. URL imports: Try to extract filename from URL
    if source == "public_url" and url:
        extracted = _extract_filename_from_url(url)
        if extracted:
            return _truncate(extracted, MAX_NAME_LENGTH)

    # 4. Fallback: Also check filename/url regardless of source
    if filename:
        cleaned = _clean_filename(filename)
        if cleaned:
            return _truncate(cleaned, MAX_NAME_LENGTH)
    
    if url:
        extracted = _extract_filename_from_url(url)
        if extracted:
            return _truncate(extracted, MAX_NAME_LENGTH)

    # 5. Final fallback: Type + Date
    return f"{type_label} - {date_str}"






