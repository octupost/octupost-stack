"""Prompt-Overlay Mapping State Management.

This module handles the mapping between prompts (agent instructions) and
timeline overlays (RVE elements). Every overlay traces back to a prompt.

Architecture:
    Scene → Prompt → Overlay
    
    - Scene: High-level concept from script
    - Prompt: Specific instruction to generate/find media
    - Overlay: Timeline element with content
"""

from copy import deepcopy
from datetime import datetime
from typing import Any, Optional, Literal
from uuid import uuid4

from agno.run import RunContext


# =============================================================================
# Prompt Types and Status
# =============================================================================

PromptType = Literal["video", "image", "audio", "music", "voiceover", "text", "caption", "sticker"]
PromptStatus = Literal["pending", "searching", "generating", "resolved", "failed"]
OverlayStatus = Literal["prompt", "generating", "generated", "stock", "uploaded", "error"]


# =============================================================================
# Prompt Management Tools
# =============================================================================

def generate_prompt_id() -> str:
    """Generate a unique prompt ID."""
    return f"prompt_{uuid4().hex[:8]}"


def create_prompt(
    run_context: RunContext,
    prompt_type: PromptType,
    instruction: str,
    scene_index: Optional[int] = None,
    keywords: Optional[list[str]] = None,
    style: Optional[str] = None,
    duration: Optional[float] = None,
    provider: Optional[str] = None,
    position: Optional[str] = None,
    extra_params: Optional[dict] = None,
) -> str:
    """Create a new prompt for content that needs to be resolved.
    
    A prompt is an instruction that will be resolved into a timeline overlay.
    
    Args:
        run_context: The Agno RunContext containing session_state
        prompt_type: Type of content ("video", "image", "audio", "text", etc.)
        instruction: What to generate/find (the actual prompt text)
        scene_index: Which scene this belongs to (None for global like music)
        keywords: Search keywords for stock footage
        style: Style preference for AI generation
        duration: Desired duration in seconds
        provider: Preferred provider ("falai", "pexels", "pixabay")
        position: Position for text/captions ("top", "center", "bottom")
        extra_params: Any additional parameters
        
    Returns:
        Confirmation message with the prompt ID
    """
    prompt_id = generate_prompt_id()
    
    # Build params dict
    params = {}
    if keywords:
        params["keywords"] = keywords
    if style:
        params["style"] = style
    if duration:
        params["duration"] = duration
    if provider:
        params["provider"] = provider
    if position:
        params["position"] = position
    if extra_params:
        params.update(extra_params)
    
    prompt = {
        "id": prompt_id,
        "sceneIndex": scene_index,
        "type": prompt_type,
        "instruction": instruction,
        "params": params,
        "status": "pending",
        "resolvedOverlayId": None,
        "createdBy": "agent",
        "createdAt": datetime.now().isoformat(),
        "resolvedAt": None,
        "errorMessage": None,
    }
    
    # Add to prompts list
    prompts = run_context.session_state.get("prompts", [])
    prompts.append(prompt)
    run_context.session_state["prompts"] = prompts
    
    return f"Created prompt {prompt_id} ({prompt_type}): {instruction[:50]}..."


def create_scene_prompts(
    run_context: RunContext,
    scene_index: int,
    visual_instruction: str,
    text_content: Optional[str] = None,
    keywords: Optional[list[str]] = None,
    duration: float = 5.0,
    use_stock: bool = True,
) -> str:
    """Create all prompts needed for a single scene.
    
    This is a convenience method that creates:
    - Video/Image prompt for the visual
    - Text prompt for voiceover/caption (if provided)
    
    Args:
        run_context: The Agno RunContext
        scene_index: The scene number (0-indexed)
        visual_instruction: What the visual should show
        text_content: Optional voiceover or caption text
        keywords: Search keywords for stock footage
        duration: Scene duration in seconds
        use_stock: If True, prefer stock footage; if False, prefer AI generation
        
    Returns:
        Confirmation with created prompt IDs
    """
    created = []
    
    # Video prompt
    video_prompt_id = generate_prompt_id()
    video_prompt = {
        "id": video_prompt_id,
        "sceneIndex": scene_index,
        "type": "video",
        "instruction": visual_instruction,
        "params": {
            "keywords": keywords or [visual_instruction],
            "duration": duration,
            "provider": "pexels" if use_stock else "falai",
        },
        "status": "pending",
        "resolvedOverlayId": None,
        "createdBy": "agent",
        "createdAt": datetime.now().isoformat(),
        "resolvedAt": None,
        "errorMessage": None,
    }
    created.append(video_prompt_id)
    
    prompts = run_context.session_state.get("prompts", [])
    prompts.append(video_prompt)
    
    # Text prompt (if provided)
    if text_content:
        text_prompt_id = generate_prompt_id()
        text_prompt = {
            "id": text_prompt_id,
            "sceneIndex": scene_index,
            "type": "text",
            "instruction": text_content,
            "params": {
                "position": "bottom",
                "duration": duration,
            },
            "status": "pending",
            "resolvedOverlayId": None,
            "createdBy": "agent",
            "createdAt": datetime.now().isoformat(),
            "resolvedAt": None,
            "errorMessage": None,
        }
        prompts.append(text_prompt)
        created.append(text_prompt_id)
    
    run_context.session_state["prompts"] = prompts
    
    return f"Created {len(created)} prompts for scene {scene_index}: {', '.join(created)}"


def resolve_prompt(
    run_context: RunContext,
    prompt_id: str,
    src: Optional[str] = None,
    content: Optional[str] = None,
    from_frame: int = 0,
    duration_frames: int = 150,
    row: int = 0,
    position: Optional[dict] = None,
    styles: Optional[dict] = None,
    extra_data: Optional[dict] = None,
) -> str:
    """Resolve a prompt by creating its overlay in the timeline.
    
    This links a prompt to a timeline overlay. The overlay will have
    a `promptId` field pointing back to this prompt.
    
    Args:
        run_context: The Agno RunContext
        prompt_id: The prompt ID to resolve
        src: URL for video/image/audio content
        content: Text content for text/caption overlays
        from_frame: Start frame in timeline
        duration_frames: Duration in frames
        row: Timeline row
        position: Dict with left, top, width, height
        styles: Style overrides
        extra_data: Additional overlay properties
        
    Returns:
        Confirmation with overlay ID
    """
    prompts = run_context.session_state.get("prompts", [])
    prompt = next((p for p in prompts if p["id"] == prompt_id), None)
    
    if not prompt:
        return f"Error: Prompt {prompt_id} not found"
    
    if prompt["status"] == "resolved":
        return f"Error: Prompt {prompt_id} already resolved to overlay {prompt['resolvedOverlayId']}"
    
    # Get timeline
    timeline = run_context.session_state.get("timeline", {})
    overlays = timeline.get("overlays", [])
    
    # Generate overlay ID
    overlay_id = max([o.get("id", 0) for o in overlays], default=0) + 1
    
    # Get timeline dimensions for default positioning
    width = timeline.get("width", 1080)
    height = timeline.get("height", 1920)
    fps = timeline.get("fps", 30)
    
    # Default positions based on overlay type
    default_positions = {
        "video": {"left": 0, "top": 0, "width": width, "height": height},
        "image": {"left": 0, "top": 0, "width": width, "height": height},
        "text": {"left": 50, "top": height - 300, "width": width - 100, "height": 200},
        "caption": {"left": 50, "top": height - 350, "width": width - 100, "height": 250},
        "sound": {"left": 0, "top": 0, "width": width, "height": 100},
        "music": {"left": 0, "top": 0, "width": width, "height": 100},
        "sticker": {"left": width - 250, "top": 50, "width": 200, "height": 200},
    }
    
    pos = position or default_positions.get(prompt["type"], default_positions["video"])
    
    # Determine status based on how it was resolved
    if src:
        # Has a URL - either stock or generated
        status = "stock" if "pexels" in src or "pixabay" in src else "generated"
    elif content:
        # Text content - resolved immediately
        status = "generated"
    else:
        # No content yet - still a prompt
        status = "prompt"
    
    # Build overlay
    overlay = {
        "id": overlay_id,
        "type": prompt["type"] if prompt["type"] != "music" else "sound",
        "promptId": prompt_id,  # THE KEY LINK
        "status": status,
        "prompt": prompt["instruction"],
        "src": src,
        "content": content or prompt["instruction"],
        "from": from_frame,
        "durationInFrames": duration_frames,
        "row": row,
        "rotation": 0,
        "isDragging": False,
        **pos,
        "styles": styles or {},
    }
    
    # Merge extra data
    if extra_data:
        overlay.update(extra_data)
    
    # Add to timeline
    overlays.append(overlay)
    timeline["overlays"] = overlays
    
    # Update timeline duration if needed
    end_frame = from_frame + duration_frames
    if end_frame > timeline.get("durationInFrames", 0):
        timeline["durationInFrames"] = end_frame
    
    run_context.session_state["timeline"] = timeline
    
    # Update prompt status
    prompt["status"] = "resolved"
    prompt["resolvedOverlayId"] = overlay_id
    prompt["resolvedAt"] = datetime.now().isoformat()
    
    return f"Resolved prompt {prompt_id} → overlay {overlay_id} ({prompt['type']}, {status})"


def get_pending_prompts(run_context: RunContext, prompt_type: Optional[str] = None) -> list[dict]:
    """Get prompts that haven't been resolved yet.
    
    Args:
        run_context: The Agno RunContext
        prompt_type: Optional filter by type
        
    Returns:
        List of pending prompt dicts
    """
    prompts = run_context.session_state.get("prompts", [])
    pending = [p for p in prompts if p["status"] == "pending"]
    
    if prompt_type:
        pending = [p for p in pending if p["type"] == prompt_type]
    
    return pending


def get_prompts_for_scene(run_context: RunContext, scene_index: int) -> list[dict]:
    """Get all prompts for a specific scene.
    
    Args:
        run_context: The Agno RunContext
        scene_index: The scene number
        
    Returns:
        List of prompt dicts for that scene
    """
    prompts = run_context.session_state.get("prompts", [])
    return [p for p in prompts if p.get("sceneIndex") == scene_index]


def get_prompt_by_id(run_context: RunContext, prompt_id: str) -> Optional[dict]:
    """Get a specific prompt by ID.
    
    Args:
        run_context: The Agno RunContext
        prompt_id: The prompt ID
        
    Returns:
        The prompt dict or None
    """
    prompts = run_context.session_state.get("prompts", [])
    return next((p for p in prompts if p["id"] == prompt_id), None)


def update_prompt_instruction(
    run_context: RunContext,
    prompt_id: str,
    new_instruction: str,
    new_keywords: Optional[list[str]] = None,
) -> str:
    """Update a prompt's instruction (for regeneration).
    
    If the prompt was already resolved, this also updates the linked overlay
    and marks it for regeneration.
    
    Args:
        run_context: The Agno RunContext
        prompt_id: The prompt ID to update
        new_instruction: The new instruction text
        new_keywords: Optional new search keywords
        
    Returns:
        Confirmation message
    """
    prompts = run_context.session_state.get("prompts", [])
    prompt = next((p for p in prompts if p["id"] == prompt_id), None)
    
    if not prompt:
        return f"Error: Prompt {prompt_id} not found"
    
    old_instruction = prompt["instruction"]
    prompt["instruction"] = new_instruction
    
    if new_keywords:
        prompt["params"]["keywords"] = new_keywords
    
    # If already resolved, update the overlay too
    if prompt["status"] == "resolved" and prompt["resolvedOverlayId"]:
        timeline = run_context.session_state.get("timeline", {})
        overlays = timeline.get("overlays", [])
        
        overlay = next((o for o in overlays if o["id"] == prompt["resolvedOverlayId"]), None)
        if overlay:
            overlay["prompt"] = new_instruction
            overlay["status"] = "prompt"  # Mark for regeneration
            overlay["src"] = None  # Clear old content
            
            run_context.session_state["timeline"] = timeline
            
            return f"Updated prompt {prompt_id} and marked overlay {overlay['id']} for regeneration"
    
    return f"Updated prompt {prompt_id}: '{old_instruction[:30]}...' → '{new_instruction[:30]}...'"


def mark_prompt_failed(run_context: RunContext, prompt_id: str, error_message: str) -> str:
    """Mark a prompt as failed.
    
    Args:
        run_context: The Agno RunContext
        prompt_id: The prompt ID
        error_message: What went wrong
        
    Returns:
        Confirmation message
    """
    prompts = run_context.session_state.get("prompts", [])
    prompt = next((p for p in prompts if p["id"] == prompt_id), None)
    
    if not prompt:
        return f"Error: Prompt {prompt_id} not found"
    
    prompt["status"] = "failed"
    prompt["errorMessage"] = error_message
    
    return f"Marked prompt {prompt_id} as failed: {error_message}"


def retry_prompt(run_context: RunContext, prompt_id: str) -> str:
    """Reset a failed prompt to pending for retry.
    
    Args:
        run_context: The Agno RunContext
        prompt_id: The prompt ID
        
    Returns:
        Confirmation message
    """
    prompts = run_context.session_state.get("prompts", [])
    prompt = next((p for p in prompts if p["id"] == prompt_id), None)
    
    if not prompt:
        return f"Error: Prompt {prompt_id} not found"
    
    prompt["status"] = "pending"
    prompt["errorMessage"] = None
    prompt["resolvedAt"] = None
    
    return f"Reset prompt {prompt_id} to pending for retry"


# =============================================================================
# Overlay ↔ Prompt Helpers
# =============================================================================

def get_overlay_prompt(run_context: RunContext, overlay_id: int) -> Optional[dict]:
    """Get the prompt that created an overlay.
    
    Args:
        run_context: The Agno RunContext
        overlay_id: The overlay ID
        
    Returns:
        The prompt dict or None
    """
    timeline = run_context.session_state.get("timeline", {})
    overlays = timeline.get("overlays", [])
    
    overlay = next((o for o in overlays if o["id"] == overlay_id), None)
    if not overlay or not overlay.get("promptId"):
        return None
    
    return get_prompt_by_id(run_context, overlay["promptId"])


def regenerate_overlay(run_context: RunContext, overlay_id: int, new_instruction: Optional[str] = None) -> str:
    """Mark an overlay for regeneration.
    
    Args:
        run_context: The Agno RunContext
        overlay_id: The overlay ID to regenerate
        new_instruction: Optional new prompt instruction
        
    Returns:
        Confirmation message
    """
    timeline = run_context.session_state.get("timeline", {})
    overlays = timeline.get("overlays", [])
    
    overlay = next((o for o in overlays if o["id"] == overlay_id), None)
    if not overlay:
        return f"Error: Overlay {overlay_id} not found"
    
    # Update prompt if it has one
    if overlay.get("promptId"):
        prompt = get_prompt_by_id(run_context, overlay["promptId"])
        if prompt:
            if new_instruction:
                prompt["instruction"] = new_instruction
            prompt["status"] = "pending"
            prompt["resolvedAt"] = None
    
    # Mark overlay for regeneration
    if new_instruction:
        overlay["prompt"] = new_instruction
    overlay["status"] = "prompt"
    overlay["src"] = None
    
    run_context.session_state["timeline"] = timeline
    
    return f"Overlay {overlay_id} marked for regeneration"


def get_unresolved_overlays(run_context: RunContext) -> list[dict]:
    """Get overlays that still need content (status = 'prompt').
    
    Args:
        run_context: The Agno RunContext
        
    Returns:
        List of overlay dicts needing resolution
    """
    timeline = run_context.session_state.get("timeline", {})
    overlays = timeline.get("overlays", [])
    
    return [o for o in overlays if o.get("status") == "prompt"]


# =============================================================================
# Batch Operations
# =============================================================================

def create_prompts_from_script(run_context: RunContext) -> str:
    """Create prompts for all scenes in the current script.
    
    Reads the script from session_state and creates video + text prompts
    for each scene.
    
    Args:
        run_context: The Agno RunContext
        
    Returns:
        Summary of created prompts
    """
    script = run_context.session_state.get("script")
    if not script:
        return "Error: No script found in session state"
    
    scenes = script.get("scenes", [])
    if not scenes:
        return "Error: Script has no scenes"
    
    created_count = 0
    fps = run_context.session_state.get("timeline", {}).get("fps", 30)
    
    for scene in scenes:
        scene_index = scene.get("scene_number", 0) - 1  # Convert to 0-indexed
        duration = scene.get("duration", 5)
        
        # Video prompt
        create_prompt(
            run_context,
            prompt_type="video",
            instruction=scene.get("visual_description", ""),
            scene_index=scene_index,
            keywords=scene.get("search_keywords", []),
            duration=duration,
            provider="pexels",  # Default to stock
        )
        created_count += 1
        
        # Text prompt for voiceover
        voiceover = scene.get("voice_over") or scene.get("voiceover")
        if voiceover:
            create_prompt(
                run_context,
                prompt_type="text",
                instruction=voiceover,
                scene_index=scene_index,
                duration=duration,
                position="bottom",
            )
            created_count += 1
    
    return f"Created {created_count} prompts from {len(scenes)} scenes"


def resolve_all_text_prompts(run_context: RunContext) -> str:
    """Resolve all pending text prompts into overlays.
    
    Text prompts don't need external resolution - we can create
    the overlays directly from the instruction.
    
    Args:
        run_context: The Agno RunContext
        
    Returns:
        Summary of resolved prompts
    """
    pending_text = get_pending_prompts(run_context, prompt_type="text")
    
    if not pending_text:
        return "No pending text prompts to resolve"
    
    fps = run_context.session_state.get("timeline", {}).get("fps", 30)
    resolved_count = 0
    
    # Calculate positions based on scene timing
    prompts = run_context.session_state.get("prompts", [])
    
    for prompt in pending_text:
        scene_index = prompt.get("sceneIndex", 0)
        duration_sec = prompt.get("params", {}).get("duration", 5)
        
        # Find the video overlay for this scene to get timing
        timeline = run_context.session_state.get("timeline", {})
        overlays = timeline.get("overlays", [])
        
        scene_video = next(
            (o for o in overlays 
             if o.get("type") == "video" 
             and get_prompt_by_id(run_context, o.get("promptId", "")).get("sceneIndex") == scene_index),
            None
        )
        
        from_frame = scene_video["from"] if scene_video else (scene_index * duration_sec * fps)
        duration_frames = int(duration_sec * fps)
        
        resolve_prompt(
            run_context,
            prompt_id=prompt["id"],
            content=prompt["instruction"],
            from_frame=int(from_frame),
            duration_frames=duration_frames,
            row=1,  # Text on row 1
            styles={
                "fontSize": "3rem",
                "fontWeight": "700",
                "color": "#FFFFFF",
                "backgroundColor": "rgba(0,0,0,0.5)",
                "textAlign": "center",
                "padding": "16px",
            }
        )
        resolved_count += 1
    
    return f"Resolved {resolved_count} text prompts into overlays"


def get_prompt_summary(run_context: RunContext) -> dict:
    """Get a summary of all prompts and their status.
    
    Args:
        run_context: The Agno RunContext
        
    Returns:
        Summary dict with counts by type and status
    """
    prompts = run_context.session_state.get("prompts", [])
    
    summary = {
        "total": len(prompts),
        "by_status": {},
        "by_type": {},
        "pending": [],
        "failed": [],
    }
    
    for prompt in prompts:
        status = prompt.get("status", "unknown")
        ptype = prompt.get("type", "unknown")
        
        summary["by_status"][status] = summary["by_status"].get(status, 0) + 1
        summary["by_type"][ptype] = summary["by_type"].get(ptype, 0) + 1
        
        if status == "pending":
            summary["pending"].append({
                "id": prompt["id"],
                "type": ptype,
                "instruction": prompt["instruction"][:50],
            })
        elif status == "failed":
            summary["failed"].append({
                "id": prompt["id"],
                "type": ptype,
                "error": prompt.get("errorMessage"),
            })
    
    return summary
