"""
AgentOS Server

Run with: python -m app.agent_os
Access at: http://localhost:7777
"""

from pathlib import Path
from dotenv import load_dotenv

# Load .env.local from project root
env_path = Path(__file__).parent.parent.parent / ".env.local"
load_dotenv(env_path)

from agno.os import AgentOS
from app.agents import all_workflows, all_agents, all_teams

# Create AgentOS with workflows, agents, and teams
agent_os = AgentOS(
    description="Octupost Video Script Agents",
    workflows=all_workflows,
    agents=all_agents,
    teams=all_teams,
)

# Get the FastAPI app (for deployment/imports)
app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="app.agent_os:app", port=7777)
