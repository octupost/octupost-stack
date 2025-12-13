"""
Agno Playground - Interactive Agent Testing UI

Run with: streamlit run playground.py
Or use: npm run playground (from root)
"""

import os
from pathlib import Path

# Load environment variables from root .env.local BEFORE any other imports
from dotenv import load_dotenv

# Try to load from root directory (one level up from api)
root_env = Path(__file__).resolve().parent.parent / ".env.local"
if root_env.exists():
    load_dotenv(root_env, override=True)
else:
    # Fallback to local .env.local
    local_env = Path(__file__).resolve().parent / ".env.local"
    if local_env.exists():
        load_dotenv(local_env, override=True)

import streamlit as st
from agno.agent import Agent
from agno.models.openai import OpenAIChat

# Page configuration
st.set_page_config(
    page_title="Agno Playground",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    .main-header {
        color: #00d4ff;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .agent-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .response-box {
        background: rgba(0, 212, 255, 0.1);
        border-left: 4px solid #00d4ff;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# Agent Definitions
# =============================================================================

def get_available_agents() -> dict[str, Agent]:
    """Get all available agents for testing."""
    
    agents = {}
    
    # Baby Agent (simple test)
    try:
        from app.agents.baby_agent import baby_agent
        agents["Baby Agent"] = baby_agent
    except Exception as e:
        st.sidebar.warning(f"Could not load Baby Agent: {e}")
    
    # Add more agents here as you create them
    # Example:
    # try:
    #     from app.agents.my_agent import my_agent
    #     agents["My Agent"] = my_agent
    # except Exception as e:
    #     st.sidebar.warning(f"Could not load My Agent: {e}")
    
    return agents


def create_custom_agent(model_id: str, instructions: str) -> Agent:
    """Create a custom agent on-the-fly for testing."""
    return Agent(
        name="CustomAgent",
        model=OpenAIChat(id=model_id),
        instructions=[instructions] if instructions else ["You are a helpful assistant."],
        markdown=True,
    )


# =============================================================================
# UI Components
# =============================================================================

def render_sidebar():
    """Render the sidebar with agent selection and settings."""
    
    st.sidebar.markdown("## 🤖 Agno Playground")
    st.sidebar.markdown("---")
    
    # Agent selection
    agents = get_available_agents()
    agent_names = list(agents.keys()) + ["🔧 Custom Agent"]
    
    selected_agent = st.sidebar.selectbox(
        "Select Agent",
        agent_names,
        index=0
    )
    
    # Custom agent configuration
    custom_agent = None
    if selected_agent == "🔧 Custom Agent":
        st.sidebar.markdown("### Custom Agent Settings")
        
        model_id = st.sidebar.selectbox(
            "Model",
            ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
            index=0
        )
        
        instructions = st.sidebar.text_area(
            "Instructions",
            value="You are a helpful assistant.",
            height=100
        )
        
        custom_agent = create_custom_agent(model_id, instructions)
    
    # Settings
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Settings")
    
    stream_enabled = st.sidebar.checkbox("Enable Streaming", value=True)
    show_debug = st.sidebar.checkbox("Show Debug Info", value=False)
    
    return {
        "selected_agent": selected_agent,
        "agents": agents,
        "custom_agent": custom_agent,
        "stream_enabled": stream_enabled,
        "show_debug": show_debug,
    }


def render_chat_interface(config: dict):
    """Render the main chat interface."""
    
    st.markdown('<p class="main-header">🤖 Agno Playground</p>', unsafe_allow_html=True)
    st.markdown("Test and debug your Agno agents interactively")
    st.markdown("---")
    
    # Get the active agent
    if config["selected_agent"] == "🔧 Custom Agent":
        agent = config["custom_agent"]
        st.info("Using custom agent configuration")
    else:
        agent = config["agents"].get(config["selected_agent"])
        if agent:
            st.success(f"Using: **{config['selected_agent']}**")
    
    if not agent:
        st.error("No agent selected or available")
        return
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask the agent something..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    if config["stream_enabled"]:
                        # Streaming response
                        response_placeholder = st.empty()
                        full_response = ""
                        
                        for chunk in agent.run(prompt, stream=True):
                            if hasattr(chunk, 'content') and chunk.content:
                                full_response += chunk.content
                                response_placeholder.markdown(full_response + "▌")
                        
                        response_placeholder.markdown(full_response)
                        response = full_response
                    else:
                        # Non-streaming response
                        result = agent.run(prompt)
                        response = result.content if hasattr(result, 'content') else str(result)
                        st.markdown(response)
                    
                    # Add assistant response to history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    st.error(f"Error: {e}")
                    if config["show_debug"]:
                        st.exception(e)
    
    # Debug info
    if config["show_debug"]:
        with st.expander("🔍 Debug Info"):
            st.json({
                "agent_name": agent.name if hasattr(agent, 'name') else "Unknown",
                "model": str(agent.model) if hasattr(agent, 'model') else "Unknown",
                "message_count": len(st.session_state.messages),
            })
    
    # Clear chat button
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()


# =============================================================================
# Main App
# =============================================================================

def main():
    """Main application entry point."""
    
    # Check for OpenAI API key
    import os
    if not os.getenv("OPENAI_API_KEY"):
        st.error("⚠️ OPENAI_API_KEY not set. Please set it in your .env.local file.")
        st.code("export OPENAI_API_KEY=your_key_here")
        st.stop()
    
    # Render sidebar and get config
    config = render_sidebar()
    
    # Render main chat interface
    render_chat_interface(config)


if __name__ == "__main__":
    main()

