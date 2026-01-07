"""
Simple Agent for Octupost - State-Based Approach

The agent updates a typed session state. After each turn, read the state to see what changed.
"""

import os
import json
import asyncio
from datetime import datetime
from typing import List, Literal, Optional, Any
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.models.openrouter import OpenRouter
from agno.tools import tool
import httpx


# =============================================================================
# CONFIGURATION
# =============================================================================

GROK_CODE_FAST_1 = OpenRouter(id="x-ai/grok-code-fast-1", max_tokens=30000)
OPUS_4_5 = OpenRouter(id="anthropic/claude-opus-4.5", max_tokens=30000)
SONNET_4_5 = OpenRouter(id="anthropic/claude-sonnet-4.5", max_tokens=30000)
MISTRAL_DEVSTRAIL_2512 = OpenRouter(id="mistralai/devstral-2512:free", max_tokens=30000)
MAIN_MODEL = OPUS_4_5

# Supabase Database Configuration (required for session persistence)
SUPABASE_PROJECT_REF = os.getenv("SUPABASE_PROJECT_REF")
SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")

if not SUPABASE_PROJECT_REF or not SUPABASE_DB_PASSWORD:
    raise RuntimeError(
        "Missing Supabase credentials. "
        "Set SUPABASE_PROJECT_REF and SUPABASE_DB_PASSWORD environment variables."
    )

DB_URL = f"postgresql://postgres:{SUPABASE_DB_PASSWORD}@db.{SUPABASE_PROJECT_REF}.supabase.co:5432/postgres"
db = PostgresDb(db_url=DB_URL)
print(f"[Agno] Connected to Supabase: {SUPABASE_PROJECT_REF}")


# =============================================================================
# GENERATION API CONFIGURATION
# =============================================================================

API_BASE_URL = os.getenv("OCTUPOST_API_URL", "http://localhost:8000")

GENERATION_DEFAULTS = {
    "tts_model": "elevenlabs/eleven_turbo_v2_5",
    "tts_voice_id": "CwhRBWXzGAHq8TQ4Fs17",
    "tts_speed": 1.0,
}

POLL_INTERVAL_SECONDS = 2.0
POLL_MAX_ATTEMPTS = 150  # 5 minutes max


# =============================================================================
# STATE MODELS - The source of truth
# =============================================================================

class VoiceoverState(BaseModel):
    """Voiceover for a scene - text is set in planning, url after generation"""
    text: str = Field(..., description="The voiceover text")
    url: Optional[str] = Field(None, description="Generated audio URL")
    duration: Optional[float] = Field(None, description="Audio duration in seconds")


class HeroImageState(BaseModel):
    """Hero image configuration for a scene"""
    prompt: str = Field(..., description="Image generation prompt")
    position: Literal["upperHalf", "full"] = Field("upperHalf", description="Position")
    aspect_ratio: str = Field("16:9", description="Aspect ratio")
    url: Optional[str] = Field(None, description="Generated image URL")


class AvatarState(BaseModel):
    """Avatar configuration for a scene"""
    position: Literal["lowerHalf", "full"] = Field("lowerHalf", description="Position")
    url: Optional[str] = Field(None, description="Generated avatar video URL")


class SceneState(BaseModel):
    """A single scene in the video"""
    scene_id: int = Field(..., description="Scene number (1-based)")
    voiceover: VoiceoverState = Field(..., description="Voiceover config")
    hero_image: Optional[HeroImageState] = Field(None, description="Hero image config")
    avatar: Optional[AvatarState] = Field(None, description="Avatar config")
    reasoning: str = Field("", description="Why this scene exists")


class VideoProjectState(BaseModel):
    """
    The complete project state - this is what the agent updates.

    Workflow:
    1. planning -> scenes_ready: Agent creates scenes with voiceover text
    2. scenes_ready -> generating: User approves, agent generates voiceovers
    3. generating -> complete: All voiceovers generated
    """
    phase: Literal["planning", "scenes_ready", "generating", "complete"] = Field(
        "planning", description="Current workflow phase"
    )
    title: Optional[str] = Field(None, description="Video title")
    scenes: List[SceneState] = Field(default_factory=list, description="All scenes")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")


# =============================================================================
# HELPER: Get typed state from agent
# =============================================================================

def _get_typed_state(agent: Agent) -> VideoProjectState:
    """Get session_state as a typed VideoProjectState"""
    if agent.session_state is None:
        agent.session_state = {}

    raw = agent.session_state.get("project")
    if raw is None:
        return VideoProjectState()

    if isinstance(raw, dict):
        return VideoProjectState(**raw)
    return raw


def _save_typed_state(agent: Agent, state: VideoProjectState):
    """Save typed state back to session"""
    if agent.session_state is None:
        agent.session_state = {}

    state.updated_at = datetime.now().isoformat()
    agent.session_state["project"] = state.model_dump()


# =============================================================================
# TOOLS - State manipulation
# =============================================================================

@tool
def get_project(agent: Agent) -> dict:
    """
    Get the current project state.

    Returns:
        The complete project state including phase, title, and all scenes.
        Check 'phase' to know where you are in the workflow.
    """
    state = _get_typed_state(agent)
    return state.model_dump()


@tool
def set_title(title: str, agent: Agent) -> str:
    """
    Set the video title.

    Args:
        title: The video title

    Returns:
        Confirmation message
    """
    state = _get_typed_state(agent)
    state.title = title
    _save_typed_state(agent, state)
    return f"Title set to: {title}"


@tool
def add_scene(
    scene_id: int,
    voiceover_text: str,
    reasoning: str,
    hero_image_prompt: str = None,
    hero_image_position: str = "upperHalf",
    avatar_position: str = "lowerHalf",
    agent: Agent = None
) -> str:
    """
    Add a new scene to the project.

    Args:
        scene_id: Scene number (1, 2, 3, etc.)
        voiceover_text: The text for this scene's voiceover
        reasoning: Why this scene exists / what it accomplishes
        hero_image_prompt: Optional prompt for hero image
        hero_image_position: "upperHalf" or "full"
        avatar_position: "lowerHalf" or "full"

    Returns:
        Confirmation message
    """
    state = _get_typed_state(agent)

    # Check if scene already exists
    for existing in state.scenes:
        if existing.scene_id == scene_id:
            return f"Scene {scene_id} already exists. Use update_scene to modify it."

    scene = SceneState(
        scene_id=scene_id,
        voiceover=VoiceoverState(text=voiceover_text),
        reasoning=reasoning,
    )

    if hero_image_prompt:
        scene.hero_image = HeroImageState(
            prompt=hero_image_prompt,
            position=hero_image_position,
        )

    if avatar_position:
        scene.avatar = AvatarState(position=avatar_position)

    state.scenes.append(scene)
    state.scenes.sort(key=lambda s: s.scene_id)
    _save_typed_state(agent, state)

    return f"Added scene {scene_id}: {voiceover_text[:50]}..."


@tool
def set_phase(phase: str, agent: Agent) -> str:
    """
    Update the project phase.

    Args:
        phase: One of "planning", "scenes_ready", "generating", "complete"

    Returns:
        Confirmation message
    """
    valid_phases = ["planning", "scenes_ready", "generating", "complete"]
    if phase not in valid_phases:
        return f"Invalid phase. Must be one of: {valid_phases}"

    state = _get_typed_state(agent)
    old_phase = state.phase
    state.phase = phase
    _save_typed_state(agent, state)

    return f"Phase changed: {old_phase} -> {phase}"


@tool
def update_scene_voiceover(
    scene_id: int,
    url: str,
    duration: float,
    agent: Agent
) -> str:
    """
    Update a scene's voiceover with generated audio URL and duration.
    Call this AFTER generate_voiceover returns.

    Args:
        scene_id: The scene number to update
        url: The generated audio URL
        duration: The audio duration in seconds

    Returns:
        Confirmation message
    """
    state = _get_typed_state(agent)

    for scene in state.scenes:
        if scene.scene_id == scene_id:
            scene.voiceover.url = url
            scene.voiceover.duration = duration
            _save_typed_state(agent, state)
            return f"Scene {scene_id} voiceover updated: {duration:.1f}s"

    return f"Scene {scene_id} not found"


# =============================================================================
# TOOLS - Media generation
# =============================================================================

async def _poll_job_until_complete(job_id: str, client: httpx.AsyncClient) -> dict:
    """Poll job status until completion or failure."""
    for _ in range(POLL_MAX_ATTEMPTS):
        response = await client.get(f"{API_BASE_URL}/api/jobs/{job_id}")
        if response.status_code != 200:
            raise Exception(f"Failed to get job status: {response.text}")

        job_data = response.json()
        status = job_data.get("status")

        if status == "completed":
            return job_data
        elif status == "failed":
            error = job_data.get("error", "Unknown error")
            raise Exception(f"Generation failed: {error}")

        await asyncio.sleep(POLL_INTERVAL_SECONDS)

    raise Exception(f"Generation timed out after {POLL_MAX_ATTEMPTS * POLL_INTERVAL_SECONDS} seconds")


@tool
def generate_voiceover(
    scene_id: int,
    agent: Agent
) -> str:
    """
    Generate voiceover audio for a scene. Uses the voiceover text from the scene.
    Automatically includes previous/next scene text for natural flow.

    Args:
        scene_id: The scene number to generate voiceover for

    Returns:
        JSON with url, duration, and job_id. Then call update_scene_voiceover with the result.

    Example:
        result = generate_voiceover(1)
        # Returns: {"url": "https://...", "duration": 3.5, "job_id": "..."}
        # Then call: update_scene_voiceover(1, result["url"], result["duration"])
    """
    state = _get_typed_state(agent)

    # Find the scene
    target_scene = None
    prev_text = None
    next_text = None

    for i, scene in enumerate(state.scenes):
        if scene.scene_id == scene_id:
            target_scene = scene
            if i > 0:
                prev_text = state.scenes[i - 1].voiceover.text
            if i < len(state.scenes) - 1:
                next_text = state.scenes[i + 1].voiceover.text
            break

    if not target_scene:
        return json.dumps({"error": f"Scene {scene_id} not found"})

    params = {
        "speech_text": target_scene.voiceover.text,
        "voice": GENERATION_DEFAULTS["tts_voice_id"],
        "speed": GENERATION_DEFAULTS["tts_speed"],
    }

    if prev_text:
        params["previous_text"] = prev_text
    if next_text:
        params["next_text"] = next_text

    async def _generate():
        async with httpx.AsyncClient(timeout=300.0) as client:
            payload = {
                "model": GENERATION_DEFAULTS["tts_model"],
                "mode": "text-to-speech",
                "params": params,
            }

            response = await client.post(
                f"{API_BASE_URL}/api/generate",
                json=payload,
            )

            if response.status_code not in (200, 201, 202):
                return json.dumps({
                    "error": f"Failed to submit: {response.text}",
                    "status_code": response.status_code
                })

            job_response = response.json()
            job_id = job_response.get("job_id")

            if not job_id:
                return json.dumps({"error": "No job_id returned"})

            try:
                result = await _poll_job_until_complete(job_id, client)

                outputs = result.get("result", {}).get("outputs", [])
                if outputs:
                    output = outputs[0]
                    return json.dumps({
                        "url": output.get("url"),
                        "duration": output.get("duration"),
                        "job_id": job_id,
                        "scene_id": scene_id,
                        "status": "completed"
                    })
                else:
                    return json.dumps({
                        "job_id": job_id,
                        "status": "completed",
                        "raw_result": result.get("result")
                    })

            except Exception as e:
                return json.dumps({"error": str(e), "job_id": job_id})

    return asyncio.run(_generate())


# =============================================================================
# AGENT
# =============================================================================

all_tools = [
    get_project,
    set_title,
    add_scene,
    set_phase,
    update_scene_voiceover,
    generate_voiceover,
]

dmac_agent = Agent(
    name="DMAC Video Creator",
    description="An agent that creates engaging videos. Uses state-based workflow.",
    model=MAIN_MODEL,
    db=db,
    tools=all_tools,
    add_session_state_to_context=True,
    # No output_schema - state is the source of truth
    instructions="""
You are a video creation agent. You manage a project state that tracks scenes and their voiceovers.

## WORKFLOW

**Start every turn by calling `get_project()` to see current state.**

### Phase 1: Planning (phase = "planning")
When user asks to create a video:
1. Call `get_project()` to check current state
2. Call `set_title(title)` to set the video title
3. Call `add_scene(...)` for each scene - include voiceover text and reasoning
4. Call `set_phase("scenes_ready")` when all scenes are added
5. Tell the user "I've created X scenes. Here's the plan: [summary]. Reply 'approved' to generate voiceovers."

### Phase 2: Generation (phase = "scenes_ready" and user approves)
When user says "approved", "generate", "go ahead", etc.:
1. Call `get_project()` to get scenes
2. Call `set_phase("generating")`
3. For EACH scene in order:
   a. Call `generate_voiceover(scene_id)` - this returns {url, duration}
   b. Parse the JSON result
   c. Call `update_scene_voiceover(scene_id, url, duration)` to save it
4. After all scenes are done, call `set_phase("complete")`
5. Tell the user "All voiceovers generated! The project is complete."

## TOOLS

- `get_project()` - Get full project state (always call first!)
- `set_title(title)` - Set video title
- `add_scene(scene_id, voiceover_text, reasoning, ...)` - Add a scene
- `set_phase(phase)` - Update workflow phase
- `generate_voiceover(scene_id)` - Generate audio for a scene (returns URL + duration)
- `update_scene_voiceover(scene_id, url, duration)` - Save generated audio to scene

## IMPORTANT

1. Always check `phase` in project state to know where you are
2. In Phase 1: Only create scenes, DO NOT generate any media
3. In Phase 2: Generate voiceovers one by one, update state after each
4. The state is the source of truth - all data lives there
5. If user wants changes, update the scenes and set phase back to "scenes_ready"

## EXAMPLE FLOW

User: "Create a 30 second video about AI"

You:
1. get_project() -> phase is "planning"
2. set_title("The Future of AI")
3. add_scene(1, "Artificial intelligence is transforming...", "Hook the viewer")
4. add_scene(2, "From healthcare to entertainment...", "Show breadth of impact")
5. add_scene(3, "The future is here...", "Call to action")
6. set_phase("scenes_ready")
7. Tell user the plan and ask for approval

User: "approved"

You:
1. get_project() -> phase is "scenes_ready", has 3 scenes
2. set_phase("generating")
3. generate_voiceover(1) -> {"url": "https://...", "duration": 8.5}
4. update_scene_voiceover(1, "https://...", 8.5)
5. generate_voiceover(2) -> {"url": "https://...", "duration": 10.2}
6. update_scene_voiceover(2, "https://...", 10.2)
7. generate_voiceover(3) -> {"url": "https://...", "duration": 6.3}
8. update_scene_voiceover(3, "https://...", 6.3)
9. set_phase("complete")
10. Tell user it's done
""",
)

all_agents = [dmac_agent]
all_teams = []
all_workflows = []
