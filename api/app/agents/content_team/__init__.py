"""AI Content Team for stock footage video creation.

This module exports the Content Team, individual agents, and state management.

Usage:
    from app.agents.content_team import create_content_team
    
    team = create_content_team(
        openrouter_api_key="...",
        pexels_api_key="...",
        pixabay_api_key="...",
    )
    
    result = await team.run("Create a video about productivity tips")

Session State:
    The team uses Agno's session_state to persist the RVE timeline
    across interactions. Use DEFAULT_SESSION_STATE as the initial state
    structure.
"""

from .team import (
    create_content_team,
    create_editor,
    create_producer,
    create_researcher,
    create_writer,
    get_content_team_agents,
)
from .tools import PexelsSearchTool, PixabaySearchTool
from .state import (
    DEFAULT_SESSION_STATE,
    get_timeline,
    update_timeline,
    set_script,
    set_assets,
    get_script,
    get_assets,
    get_project_context,
    undo_last_change,
    set_project_brief,
    clear_project,
    get_overlay_by_id,
    update_overlay,
    remove_overlay,
    add_overlay,
)
from .rve_agent import create_rve_agent

__all__ = [
    # Team factory
    "create_content_team",
    
    # Agent factories
    "create_researcher",
    "create_writer", 
    "create_producer",
    "create_editor",
    "create_rve_agent",
    "get_content_team_agents",
    
    # Tools
    "PexelsSearchTool",
    "PixabaySearchTool",
    
    # State management
    "DEFAULT_SESSION_STATE",
    "get_timeline",
    "update_timeline",
    "set_script",
    "set_assets",
    "get_script",
    "get_assets",
    "get_project_context",
    "undo_last_change",
    "set_project_brief",
    "clear_project",
    "get_overlay_by_id",
    "update_overlay",
    "remove_overlay",
    "add_overlay",
]
