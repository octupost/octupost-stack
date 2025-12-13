"""RVE Agent - React Video Editor Timeline Management.

This agent handles human feedback and modifies the RVE timeline
using the session state for persistence across interactions.

Usage:
    from app.agents.content_team.rve_agent import create_rve_agent
    
    rve_agent = create_rve_agent(model=model, db=db)
"""

from typing import Optional

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.models.openrouter import OpenRouter

from .state import (
    get_timeline,
    update_timeline,
    get_script,
    get_assets,
    get_project_context,
    undo_last_change,
    get_overlay_by_id,
    update_overlay,
    remove_overlay,
    add_overlay,
)


def create_rve_agent(
    model: OpenRouter,
    db: Optional[PostgresDb] = None,
) -> Agent:
    """Create the RVE Agent for timeline modifications.
    
    Purpose: Handle human feedback and modify the RVE timeline based on
    natural language requests. This agent is the human-in-the-loop component.
    
    Capabilities:
        - Swap clips by scene number or description
        - Modify text content and styling
        - Adjust timing and duration
        - Reorder scenes/overlays
        - Add/remove overlays
        - Undo changes
    
    Args:
        model: OpenRouter model instance
        db: Optional PostgresDb for session persistence
        
    Returns:
        Configured Agent instance
    """
    return Agent(
        name="RVE Agent",
        role="Modify RVE timeline based on human feedback and requests",
        model=model,
        db=db,
        
        tools=[
            # Read tools
            get_timeline,
            get_script,
            get_assets,
            get_project_context,
            get_overlay_by_id,
            
            # Write tools
            update_timeline,
            update_overlay,
            remove_overlay,
            add_overlay,
            undo_last_change,
        ],
        
        instructions=[
            # Role and context
            "You are the RVE (React Video Editor) Agent responsible for modifying video timelines.",
            "You work with an RVE timeline that contains overlays (video clips, text, images, audio, etc.).",
            "The timeline persists across conversations via session_state.",
            
            # Understanding the current state
            "ALWAYS start by calling get_project_context() to understand the current project state.",
            "Call get_timeline() to see the full timeline with all overlays.",
            "Each overlay has: id, type, from (start frame), durationInFrames, and type-specific properties.",
            
            # Handling requests
            "When the user asks to modify the video:",
            "1. First understand what they want to change",
            "2. Get the current timeline to find the relevant overlays",
            "3. Make the requested changes using update_overlay(), add_overlay(), or remove_overlay()",
            "4. Confirm what was changed",
            
            # Types of modifications
            "Common modification requests:",
            "- 'Make scene X longer/shorter' → adjust durationInFrames on that overlay",
            "- 'Change the text to...' → update the content property on text overlays",
            "- 'Swap scene X with Y' → swap the from/row values between overlays",
            "- 'Remove scene X' → call remove_overlay()",
            "- 'Add text saying...' → call add_overlay() with a text overlay",
            "- 'Undo that' → call undo_last_change()",
            
            # Timeline structure
            """RVE overlay types:
- video: src, videoStartTime, durationInFrames, styles (volume, filter, etc.)
- text: content, styles (fontSize, color, fontFamily, etc.)
- image: src, styles (objectFit, filter, etc.)
- sound: src, startFromSound, styles (volume, fadeIn, fadeOut)
- caption: captions[], styles, template
- sticker: content, category, styles""",
            
            # Best practices
            "Always preserve overlay IDs when updating.",
            "Frame calculations: frames = seconds × fps (usually 30 fps).",
            "After making changes, briefly summarize what was modified.",
            "If a request is unclear, ask for clarification before making changes.",
            
            # Output
            "After modifications, return the updated timeline structure.",
        ],
        
        markdown=True,
    )

