"""AgentOS - Production runtime for Octupost AI agents.

This module sets up AgentOS with the Stock Footage Content Team.
The team creates videos using stock footage from Pexels and Pixabay.

Run with: python agent_os.py
Connect to Control Plane at: https://os.agno.com

Team Structure (5 Agents):
    Researcher → Writer → Producer → Editor → RVE Agent → RVE Timeline

Flow:
    1. Researcher: DuckDuckGo, YouTube, Wikipedia for research
    2. Writer: Creates 10-scene script with stock-friendly descriptions  
    3. Producer: Finds stock videos from Pexels/Pixabay
    4. Editor: Assembles into RVE Timeline JSON
    5. RVE Agent: Handles human feedback and timeline modifications

Session State:
    The team uses Agno's session_state to persist the RVE timeline,
    script, and assets across interactions for iterative editing.
"""

from agno.db.postgres import PostgresDb
from agno.os import AgentOS

from app.agents.content_team import (
    create_content_team,
    get_content_team_agents,
)
from app.config import get_settings

settings = get_settings()

GEMINI_2_FLASH_MODEL = "google/gemini-2.0-flash-001:free" 
#1.05M context $0.10/M input tokens$0.40/M output tokens $0.70/M audio tokens
OPENAI_MODEL = "openai/gpt-oss-120b"
#131K context $0.039/M input tokens $0.19/M output tokens
GROK_CODE_FAST_MODEL = "x-ai/grok-code-fast-1" 
#256K context $0.20/M input tokens $1.50/M output tokens
ANTHROPIC_OPUS_4_5_MODEL = "anthropic/claude-opus-4.5" 
#200,000 context $5/M input tokens #$25/M output tokens #$10/K web search
AMAZON_NOVA_2_LITE_MODEL = "amazon/nova-2-lite-v1:free"

TEAM_MODEL = GROK_CODE_FAST_MODEL

# Database for session persistence (uses your existing Supabase)
db = None
if settings.supabase_db_url:
    print("✅ Database URL configured, connecting to Supabase...")
    db = PostgresDb(
        db_url=settings.supabase_db_url, 
        db_schema="agno",
    )
    print(f"✅ Database connected: {db}")
else:
    print("⚠️  WARNING: No database URL configured!")
    print("   Sessions will NOT be persisted.")
    print("   Set SUPABASE_PROJECT_REF and SUPABASE_DB_PASSWORD in your .env file")

# Check for required API keys
if not settings.openrouter_api_key:
    print("⚠️  WARNING: OPENROUTER_API_KEY not configured!")
    print("   Agents will not work without an OpenRouter API key.")

if not settings.pexels_api_key and not settings.pixabay_api_key:
    print("⚠️  WARNING: No stock footage API keys configured!")
    print("   Set PEXELS_API_KEY and/or PIXABAY_API_KEY in your .env file")
    print("   Producer agent will not be able to find stock videos.")
else:
    if settings.pexels_api_key:
        print("✅ Pexels API key configured")
    if settings.pixabay_api_key:
        print("✅ Pixabay API key configured")

# Create the Content Team with all 5 agents
content_team = create_content_team(
    openrouter_api_key=settings.openrouter_api_key,
    pexels_api_key=settings.pexels_api_key,
    pixabay_api_key=settings.pixabay_api_key,
    db=db,
)

# Get individual agents for direct access
agents = get_content_team_agents(
    openrouter_api_key=settings.openrouter_api_key,
    pexels_api_key=settings.pexels_api_key,
    pixabay_api_key=settings.pixabay_api_key,
    db=db,
)

researcher = agents["researcher"]
writer = agents["writer"]
producer = agents["producer"]
editor = agents["editor"]
rve_agent = agents["rve_agent"]

# Create AgentOS with the team and individual agents
agent_os = AgentOS(
    id="octupost-content-team",
    description="Octupost AI Content Team - Stock Footage Video Creation with Session State",
    agents=[researcher, writer, producer, editor, rve_agent],
    teams=[content_team],
)

app = agent_os.get_app()

if __name__ == "__main__":
    print("\n🎬 Starting Octupost Content Team AgentOS...")
    print("   Connect to Control Plane at: https://os.agno.com")
    print("\n   Team: Stock Footage Content Team")
    print("   Agents: Researcher, Writer, Producer, Editor, RVE Agent")
    print("   Mode: coordinate (sequential workflow with session state)")
    print("\n   Session State: Timeline, script, and assets persist across interactions")
    print("\n   Example prompts:")
    print('   "Create a 60-second video about productivity tips for remote workers"')
    print('   "Make scene 3 longer and change the text to be more engaging"')
    print('   "Undo that last change"')
    print()
    
    agent_os.serve(app="agent_os:app", reload=True, port=7777)
