"""RVE Session State Management.

This module defines the session state structure and tools for managing
the RVE timeline across agent interactions using Agno's built-in session_state.

Usage:
    from app.agents.content_team.state import (
        DEFAULT_SESSION_STATE,
        get_timeline,
        update_timeline,
        set_script,
        set_assets,
    )
"""

from copy import deepcopy
from datetime import datetime
from typing import Any, Optional

from agno.run import RunContext


# =============================================================================
# Default Session State Structure
# =============================================================================

DEFAULT_SESSION_STATE = {
    # RVE Timeline - matches frontend Overlay[] structure
    "timeline": {
        "overlays": [],
        "durationInFrames": 0,
        "width": 1920,
        "height": 1080,
        "fps": 30,
    },
    
    # Script from Writer agent
    "script": None,
    
    # Assets from Producer agent
    "assets": [],
    
    # Project metadata
    "project": {
        "brief": None,
        "aspect_ratio": "16:9",
        "target_duration": 60,
        "created_at": None,
        "last_modified": None,
    },
    
    # Revision history for undo support (last 10 timelines)
    "revision_history": [],
}


# Maximum number of revisions to keep in history
MAX_REVISION_HISTORY = 10


# =============================================================================
# State Tools - These are used by agents via RunContext
# =============================================================================

def get_timeline(run_context: RunContext) -> dict:
    """Get the current RVE timeline from session state.
    
    Args:
        run_context: The Agno RunContext containing session_state
        
    Returns:
        The current timeline dict with overlays, dimensions, fps, etc.
    """
    return run_context.session_state.get("timeline", DEFAULT_SESSION_STATE["timeline"])


def update_timeline(run_context: RunContext, timeline: dict) -> str:
    """Update the RVE timeline in session state.
    
    Automatically saves the previous timeline to revision history
    before applying the update.
    
    Args:
        run_context: The Agno RunContext containing session_state
        timeline: The new timeline dict to save
        
    Returns:
        Confirmation message with timeline stats
    """
    # Save current timeline to revision history before updating
    current = run_context.session_state.get("timeline")
    if current and current.get("overlays"):
        history = run_context.session_state.get("revision_history", [])
        history.append(deepcopy(current))
        # Keep only the last N revisions
        run_context.session_state["revision_history"] = history[-MAX_REVISION_HISTORY:]
    
    # Update the timeline
    run_context.session_state["timeline"] = timeline
    
    # Update project metadata
    run_context.session_state["project"]["last_modified"] = datetime.now().isoformat()
    
    overlay_count = len(timeline.get("overlays", []))
    duration_frames = timeline.get("durationInFrames", 0)
    fps = timeline.get("fps", 30)
    duration_seconds = duration_frames / fps if fps > 0 else 0
    
    return f"Timeline updated: {overlay_count} overlays, {duration_seconds:.1f}s duration"


def set_script(run_context: RunContext, script: dict) -> str:
    """Store the script in session state.
    
    Called by the Writer agent after creating a script.
    
    Args:
        run_context: The Agno RunContext containing session_state
        script: The script dict with title, hook, scenes, etc.
        
    Returns:
        Confirmation message
    """
    run_context.session_state["script"] = script
    
    title = script.get("title", "Untitled")
    scene_count = len(script.get("scenes", []))
    total_duration = script.get("total_duration", 0)
    
    return f"Script saved: '{title}' with {scene_count} scenes ({total_duration}s)"


def set_assets(run_context: RunContext, assets: list) -> str:
    """Store the assets in session state.
    
    Called by the Producer agent after finding stock footage.
    
    Args:
        run_context: The Agno RunContext containing session_state
        assets: List of asset dicts with video URLs, durations, etc.
        
    Returns:
        Confirmation message
    """
    run_context.session_state["assets"] = assets
    
    return f"Assets saved: {len(assets)} video clips found"


def get_script(run_context: RunContext) -> Optional[dict]:
    """Get the current script from session state.
    
    Args:
        run_context: The Agno RunContext containing session_state
        
    Returns:
        The script dict or None if not set
    """
    return run_context.session_state.get("script")


def get_assets(run_context: RunContext) -> list:
    """Get the current assets from session state.
    
    Args:
        run_context: The Agno RunContext containing session_state
        
    Returns:
        List of asset dicts
    """
    return run_context.session_state.get("assets", [])


def get_project_context(run_context: RunContext) -> dict:
    """Get a summary of the current project state.
    
    Useful for providing context to agents about the current state
    of the video project.
    
    Args:
        run_context: The Agno RunContext containing session_state
        
    Returns:
        Summary dict with project info, script status, assets count, etc.
    """
    state = run_context.session_state
    
    timeline = state.get("timeline", {})
    script = state.get("script")
    assets = state.get("assets", [])
    project = state.get("project", {})
    history = state.get("revision_history", [])
    
    return {
        "project": {
            "brief": project.get("brief"),
            "aspect_ratio": project.get("aspect_ratio", "16:9"),
            "target_duration": project.get("target_duration", 60),
            "created_at": project.get("created_at"),
            "last_modified": project.get("last_modified"),
        },
        "script": {
            "has_script": script is not None,
            "title": script.get("title") if script else None,
            "scene_count": len(script.get("scenes", [])) if script else 0,
        },
        "assets": {
            "count": len(assets),
        },
        "timeline": {
            "overlay_count": len(timeline.get("overlays", [])),
            "duration_frames": timeline.get("durationInFrames", 0),
            "fps": timeline.get("fps", 30),
            "width": timeline.get("width", 1920),
            "height": timeline.get("height", 1080),
        },
        "revisions_available": len(history),
    }


def undo_last_change(run_context: RunContext) -> str:
    """Restore the previous timeline from revision history.
    
    Args:
        run_context: The Agno RunContext containing session_state
        
    Returns:
        Confirmation message or error if no history available
    """
    history = run_context.session_state.get("revision_history", [])
    
    if not history:
        return "No previous revisions available to undo"
    
    # Pop the last revision and restore it
    previous = history.pop()
    run_context.session_state["timeline"] = previous
    run_context.session_state["revision_history"] = history
    run_context.session_state["project"]["last_modified"] = datetime.now().isoformat()
    
    overlay_count = len(previous.get("overlays", []))
    remaining = len(history)
    
    return f"Restored previous timeline ({overlay_count} overlays). {remaining} revisions remaining."


def set_project_brief(run_context: RunContext, brief: str, aspect_ratio: str = "16:9", target_duration: int = 60) -> str:
    """Set the project brief and initial parameters.
    
    Called at the start of a new video project.
    
    Args:
        run_context: The Agno RunContext containing session_state
        brief: The user's content request/brief
        aspect_ratio: Target aspect ratio (16:9, 9:16, 1:1)
        target_duration: Target video duration in seconds
        
    Returns:
        Confirmation message
    """
    run_context.session_state["project"]["brief"] = brief
    run_context.session_state["project"]["aspect_ratio"] = aspect_ratio
    run_context.session_state["project"]["target_duration"] = target_duration
    run_context.session_state["project"]["created_at"] = datetime.now().isoformat()
    
    # Set timeline dimensions based on aspect ratio
    dimensions = {
        "16:9": {"width": 1920, "height": 1080},
        "9:16": {"width": 1080, "height": 1920},
        "1:1": {"width": 1080, "height": 1080},
        "4:5": {"width": 1080, "height": 1350},
    }
    
    dims = dimensions.get(aspect_ratio, dimensions["16:9"])
    run_context.session_state["timeline"]["width"] = dims["width"]
    run_context.session_state["timeline"]["height"] = dims["height"]
    
    return f"Project initialized: '{brief[:50]}...' ({aspect_ratio}, {target_duration}s target)"


def clear_project(run_context: RunContext) -> str:
    """Clear all project state and start fresh.
    
    Args:
        run_context: The Agno RunContext containing session_state
        
    Returns:
        Confirmation message
    """
    # Reset to default state
    for key, value in DEFAULT_SESSION_STATE.items():
        run_context.session_state[key] = deepcopy(value)
    
    return "Project cleared. Ready for a new video."


# =============================================================================
# Timeline Manipulation Helpers
# =============================================================================

def get_overlay_by_id(run_context: RunContext, overlay_id: int) -> Optional[dict]:
    """Get a specific overlay from the timeline by ID.
    
    Args:
        run_context: The Agno RunContext containing session_state
        overlay_id: The overlay ID to find
        
    Returns:
        The overlay dict or None if not found
    """
    timeline = run_context.session_state.get("timeline", {})
    overlays = timeline.get("overlays", [])
    
    for overlay in overlays:
        if overlay.get("id") == overlay_id:
            return overlay
    
    return None


def update_overlay(run_context: RunContext, overlay_id: int, updates: dict) -> str:
    """Update a specific overlay in the timeline.
    
    Saves to revision history before making changes.
    
    Args:
        run_context: The Agno RunContext containing session_state
        overlay_id: The overlay ID to update
        updates: Dict of properties to update
        
    Returns:
        Confirmation message or error if overlay not found
    """
    timeline = run_context.session_state.get("timeline", {})
    overlays = timeline.get("overlays", [])
    
    for i, overlay in enumerate(overlays):
        if overlay.get("id") == overlay_id:
            # Save to history first
            history = run_context.session_state.get("revision_history", [])
            history.append(deepcopy(timeline))
            run_context.session_state["revision_history"] = history[-MAX_REVISION_HISTORY:]
            
            # Apply updates
            overlays[i] = {**overlay, **updates}
            run_context.session_state["timeline"]["overlays"] = overlays
            run_context.session_state["project"]["last_modified"] = datetime.now().isoformat()
            
            return f"Overlay {overlay_id} updated: {list(updates.keys())}"
    
    return f"Overlay {overlay_id} not found"


def remove_overlay(run_context: RunContext, overlay_id: int) -> str:
    """Remove an overlay from the timeline.
    
    Args:
        run_context: The Agno RunContext containing session_state
        overlay_id: The overlay ID to remove
        
    Returns:
        Confirmation message or error if overlay not found
    """
    timeline = run_context.session_state.get("timeline", {})
    overlays = timeline.get("overlays", [])
    
    # Find and remove the overlay
    for i, overlay in enumerate(overlays):
        if overlay.get("id") == overlay_id:
            # Save to history first
            history = run_context.session_state.get("revision_history", [])
            history.append(deepcopy(timeline))
            run_context.session_state["revision_history"] = history[-MAX_REVISION_HISTORY:]
            
            # Remove overlay
            removed = overlays.pop(i)
            run_context.session_state["timeline"]["overlays"] = overlays
            run_context.session_state["project"]["last_modified"] = datetime.now().isoformat()
            
            return f"Removed overlay {overlay_id} (type: {removed.get('type')})"
    
    return f"Overlay {overlay_id} not found"


def add_overlay(run_context: RunContext, overlay: dict) -> str:
    """Add a new overlay to the timeline.
    
    Args:
        run_context: The Agno RunContext containing session_state
        overlay: The overlay dict to add
        
    Returns:
        Confirmation message with the new overlay ID
    """
    timeline = run_context.session_state.get("timeline", {})
    overlays = timeline.get("overlays", [])
    
    # Save to history first
    if overlays:
        history = run_context.session_state.get("revision_history", [])
        history.append(deepcopy(timeline))
        run_context.session_state["revision_history"] = history[-MAX_REVISION_HISTORY:]
    
    # Generate ID if not provided
    if "id" not in overlay:
        existing_ids = [o.get("id", 0) for o in overlays]
        overlay["id"] = max(existing_ids, default=0) + 1
    
    # Add overlay
    overlays.append(overlay)
    run_context.session_state["timeline"]["overlays"] = overlays
    run_context.session_state["project"]["last_modified"] = datetime.now().isoformat()
    
    return f"Added overlay {overlay['id']} (type: {overlay.get('type')})"

