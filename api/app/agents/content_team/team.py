"""AI Content Team - Stock Footage Video Creation.

This module implements the Content Team as defined in:
docs/AI_CONTENT_TEAM_SIMPLIFIED.md

Team Structure:
    Researcher → Writer → Producer → Editor → RVE Agent → RVE Timeline

Flow:
    1. Researcher: Gathers information using DuckDuckGo, YouTube, Wikipedia
    2. Writer: Creates script with ~10 stock-footage-friendly scenes
    3. Producer: Finds stock videos from Pexels/Pixabay for each scene
    4. Editor: Assembles into RVE Timeline JSON format
    5. RVE Agent: Handles human feedback and timeline modifications

Session State:
    The team uses Agno's session_state to persist the RVE timeline,
    script, and assets across interactions, enabling iterative editing.
"""

from copy import deepcopy
from typing import Optional

from agno.agent import Agent
from agno.compression.manager import CompressionManager
from agno.db.postgres import PostgresDb
from agno.models.openrouter import OpenRouter
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.wikipedia import WikipediaTools
from agno.tools.youtube import YouTubeTools

from .tools import PexelsSearchTool, PixabaySearchTool
from .state import (
    DEFAULT_SESSION_STATE,
    set_script,
    set_assets,
    update_timeline,
    get_script,
    get_assets,
    get_timeline,
    get_project_context,
    set_project_brief,
)
from .rve_agent import create_rve_agent


# Free model from OpenRouter
DEFAULT_MODEL = "amazon/nova-2-lite-v1:free"


def create_researcher(
    model: OpenRouter,
    db: Optional[PostgresDb] = None,
) -> Agent:
    """Create the Researcher agent.
    
    Purpose: Gather information for content creation using free research tools.
    Uses context compression to reduce token usage from verbose search results.
    """
    return Agent(
        name="Researcher",
        role="Research and gather information for video content",
        model=model,
        tools=[
            DuckDuckGoTools(),      # FREE web search
            YouTubeTools(),         # FREE YouTube search
            WikipediaTools(),       # FREE Wikipedia
        ],
        instructions=[
            "Search for relevant, recent information on the topic",
            "Extract 5-10 key facts that would make compelling video content",
            "Identify trending angles and hooks",
            "Suggest 3 hook ideas for the video opening",
            "Note visual concepts that could be found in stock footage",
            "Keep output concise and actionable for the Writer agent",
        ],
        markdown=True,
        db=db,
        compress_tool_results=True,  # Compress verbose search results
    )


def create_writer(
    model: OpenRouter,
    db: Optional[PostgresDb] = None,
) -> Agent:
    """Create the Writer agent.
    
    Purpose: Create scripts with scene descriptions optimized for stock footage search.
    Saves the script to session_state using set_script().
    """
    return Agent(
        name="Writer",
        role="Write video scripts with stock-footage-friendly scenes",
        model=model,
        tools=[
            set_script,  # Save script to session_state
            get_project_context,  # Read project context
        ],
        instructions=[
            "Create exactly 10 scenes for the video",
            "Each scene should be 3-6 seconds long",
            "Write scene descriptions that match common stock footage",
            "Use generic, searchable visual concepts",
            "Avoid overly specific scenes that won't match stock footage",
            "Include voice-over text for each scene",
            
            # Stock-friendly scene guidelines
            "GOOD scenes: 'person working at laptop', 'city skyline at sunset', 'team meeting in office'",
            "BAD scenes: 'specific celebrity', 'branded product close-up', 'unique location'",
            
            # State management
            "IMPORTANT: After creating the script, call set_script() to save it to session state.",
            
            # Output format
            """Output your script in this JSON format and save it with set_script():
{
  "title": "Video Title",
  "hook": "Opening hook text to grab attention",
  "scenes": [
    {
      "scene_number": 1,
      "duration": 5,
      "visual_description": "Person typing on laptop in modern office",
      "search_keywords": ["person laptop", "office work", "typing computer"],
      "voice_over": "In today's digital world..."
    }
  ],
  "total_duration": 50
}""",
        ],
        markdown=True,
        db=db,
    )


def create_producer(
    model: OpenRouter,
    pexels_api_key: str,
    pixabay_api_key: str,
    db: Optional[PostgresDb] = None,
) -> Agent:
    """Create the Producer agent.
    
    Purpose: Find stock videos for each scene. NO AI generation - stock only.
    Saves assets to session_state using set_assets().
    Uses context compression to handle many stock footage API calls efficiently.
    """
    tools = [
        get_script,  # Read script from session_state
        set_assets,  # Save assets to session_state
        get_project_context,  # Read project context
    ]
    
    if pexels_api_key:
        tools.append(PexelsSearchTool(api_key=pexels_api_key))
    if pixabay_api_key:
        tools.append(PixabaySearchTool(api_key=pixabay_api_key))
    
    return Agent(
        name="Producer",
        role="Find stock footage for each scene",
        model=model,
        tools=tools,
        instructions=[
            # State management
            "FIRST: Call get_script() to retrieve the script from session state.",
            
            "For each scene in the script, search stock footage using the keywords",
            "Find exactly 1 video per scene (10 total for 10 scenes)",
            "Match the requested aspect_ratio (landscape for 16:9, portrait for 9:16, square for 1:1)",
            "Prefer videos 5-15 seconds long",
            "Verify video quality (prefer HD/720p+)",
            "Return video URLs, durations, and attribution for each scene",
            
            # Search strategy
            "Try the primary search keyword first",
            "If no good results, try alternative keywords from the scene",
            "If still no results, broaden the search with more generic terms",
            "NEVER skip a scene - always find something that works",
            "Try Pexels first, then Pixabay as fallback",
            
            # State management
            "IMPORTANT: After finding all assets, call set_assets() to save them to session state.",
            
            # Output format
            """Output assets in this JSON format and save with set_assets():
{
  "assets": [
    {
      "scene_number": 1,
      "source": "pexels",
      "video_url": "https://videos.pexels.com/...",
      "video_id": "12345",
      "duration": 8,
      "width": 1920,
      "height": 1080,
      "attribution": "Video by John Doe from Pexels",
      "search_query_used": "person laptop office"
    }
  ]
}""",
        ],
        markdown=True,
        db=db,
        compress_tool_results=True,  # Compress verbose stock API responses
    )


def create_editor(
    model: OpenRouter,
    db: Optional[PostgresDb] = None,
) -> Agent:
    """Create the Editor agent.
    
    Purpose: Assemble assets into RVE Timeline format for the video player.
    Saves the timeline to session_state using update_timeline().
    """
    return Agent(
        name="Editor",
        role="Assemble stock footage into RVE Timeline",
        model=model,
        tools=[
            get_script,  # Read script from session_state
            get_assets,  # Read assets from session_state
            update_timeline,  # Save timeline to session_state
            get_project_context,  # Read project context
        ],
        instructions=[
            # State management
            "FIRST: Call get_script() and get_assets() to retrieve data from session state.",
            
            "Create RVE Timeline JSON from the script and assets",
            "Place each video clip on the timeline in sequence",
            "Set correct start times based on scene durations",
            "Trim clips to match scene duration using videoStartTime",
            "Add text overlays for voice-over captions",
            "Ensure all clips are properly sequenced",
            
            # State management
            "IMPORTANT: After assembling the timeline, call update_timeline() to save it.",
            
            # RVE Timeline format - matches frontend Overlay[] structure
            """Output valid RVE Timeline JSON and save with update_timeline():
{
  "overlays": [
    {
      "id": 1,
      "type": "video",
      "src": "https://videos.pexels.com/...",
      "content": "Scene 1",
      "from": 0,
      "durationInFrames": 150,
      "row": 0,
      "left": 0,
      "top": 0,
      "width": 1920,
      "height": 1080,
      "rotation": 0,
      "isDragging": false,
      "videoStartTime": 0,
      "styles": {
        "objectFit": "cover",
        "volume": 0.5
      }
    },
    {
      "id": 2,
      "type": "text",
      "content": "In today's digital world...",
      "from": 0,
      "durationInFrames": 150,
      "row": 1,
      "left": 100,
      "top": 800,
      "width": 1720,
      "height": 200,
      "rotation": 0,
      "isDragging": false,
      "styles": {
        "fontSize": "48px",
        "fontWeight": "bold",
        "color": "#ffffff",
        "backgroundColor": "rgba(0,0,0,0.5)",
        "fontFamily": "Inter",
        "fontStyle": "normal",
        "textDecoration": "none",
        "textAlign": "center"
      }
    }
  ],
  "durationInFrames": 1500,
  "width": 1920,
  "height": 1080,
  "fps": 30
}""",
        ],
        markdown=True,
        db=db,
    )


def create_content_team(
    openrouter_api_key: str,
    pexels_api_key: str = "",
    pixabay_api_key: str = "",
    db: Optional[PostgresDb] = None,
    model_id: str = DEFAULT_MODEL,
) -> Team:
    """Create the Stock Footage Content Team with session state.
    
    This team coordinates 5 agents to create video content:
    1. Researcher - gathers information
    2. Writer - creates script with 10 scenes (saves to session_state)
    3. Producer - finds stock videos for each scene (saves to session_state)
    4. Editor - assembles into RVE Timeline (saves to session_state)
    5. RVE Agent - handles human feedback and modifications
    
    Session State:
        The team uses session_state to persist:
        - timeline: The RVE overlay array
        - script: The Writer's script with scenes
        - assets: The Producer's found videos
        - project: Metadata (brief, aspect_ratio, duration)
        - revision_history: For undo support
    
    Context Compression:
        Uses CompressionManager to automatically compress verbose tool results
        (search APIs, stock footage APIs) after a threshold is reached,
        reducing token usage while preserving key information.
    
    Args:
        openrouter_api_key: API key for OpenRouter (required)
        pexels_api_key: API key for Pexels stock videos (optional)
        pixabay_api_key: API key for Pixabay stock videos (optional)
        db: PostgresDb instance for session persistence (optional)
        model_id: OpenRouter model ID (default: amazon/nova-2-lite-v1:free)
    
    Returns:
        Configured Team instance ready to create stock footage videos
    """
    # Create shared model
    model = OpenRouter(id=model_id, api_key=openrouter_api_key)
    
    # Create compression manager for efficient context management
    # Uses the same free model to compress verbose tool results
    compression_manager = CompressionManager(
        model=model,
        compress_tool_results_limit=3,  # Compress after 3 tool calls
    )
    
    # Create all 5 agents
    researcher = create_researcher(model=model, db=db)
    writer = create_writer(model=model, db=db)
    producer = create_producer(
        model=model, 
        pexels_api_key=pexels_api_key,
        pixabay_api_key=pixabay_api_key,
        db=db,
    )
    editor = create_editor(model=model, db=db)
    rve_agent = create_rve_agent(model=model, db=db)
    
    # Create the coordinated team with session state and compression
    team = Team(
        name="Stock Footage Content Team",
        model=model,
        members=[researcher, writer, producer, editor, rve_agent],
        
        # Initialize session state for persistence
        session_state=deepcopy(DEFAULT_SESSION_STATE),
        
        # Enable context compression to reduce token usage
        compression_manager=compression_manager,
        
        instructions=[
            "You are a content creation team that makes videos using stock footage.",
            "You have access to shared session_state to pass data between agents.",
            
            # State-aware context
            "Current project context: {project}",
            "Script status: {script}",
            "Assets found: {assets}",
            "Timeline overlays: {timeline}",
            
            # Workflow
            "For NEW video requests, follow this workflow:",
            "1. Have Researcher gather information on the topic",
            "2. Have Writer create a 10-scene script and save with set_script()",
            "3. Have Producer find stock videos and save with set_assets()",
            "4. Have Editor assemble into RVE Timeline and save with update_timeline()",
            "5. Return the final RVE Timeline JSON",
            "",
            "For REVISION requests (modify existing video):",
            "1. Delegate to RVE Agent who can read and modify the timeline",
            "2. RVE Agent will make changes and save with update_timeline()",
            "3. Return the updated timeline",
            "",
            "Important guidelines:",
            "- All videos come from free stock sources (Pexels, Pixabay)",
            "- No AI generation - only stock footage",
            "- Each scene needs exactly one video",
            "- Final output must be valid RVE Timeline JSON",
            "- The timeline persists across conversations - users can ask for changes",
        ],
        share_member_interactions=True,
        show_members_responses=True,
        db=db,
        markdown=True,
    )
    
    return team


# Convenience function for direct usage
def get_content_team_agents(
    openrouter_api_key: str,
    pexels_api_key: str = "",
    pixabay_api_key: str = "",
    db: Optional[PostgresDb] = None,
    model_id: str = DEFAULT_MODEL,
) -> dict:
    """Get individual agents for use outside the team.
    
    Returns a dict with researcher, writer, producer, editor, rve_agent agents.
    """
    model = OpenRouter(id=model_id, api_key=openrouter_api_key)
    
    return {
        "researcher": create_researcher(model=model, db=db),
        "writer": create_writer(model=model, db=db),
        "producer": create_producer(
            model=model,
            pexels_api_key=pexels_api_key,
            pixabay_api_key=pixabay_api_key,
            db=db,
        ),
        "editor": create_editor(model=model, db=db),
        "rve_agent": create_rve_agent(model=model, db=db),
    }
