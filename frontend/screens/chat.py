# screens/chat_screen.py

import streamlit as st
from utils.chat_api import create_chat, list_agent_sessions
from utils.agent_api import get_agents, get_config_options, update_agent # Need update_agent
from components.session_sidebar import session_sidebar
from components.agent_config_editor import agent_config_editor
from components.chat_history import chat_history_display

# Initialize necessary session states
if "current_agent" not in st.session_state:
    st.session_state["current_agent"] = None
if "active_session_id" not in st.session_state:
    st.session_state["active_session_id"] = None
if "show_config_editor" not in st.session_state:
    st.session_state["show_config_editor"] = False


def chat_screen():
    agent = st.session_state.get("current_agent")

    if not agent:
        st.error("No agent selected. Returning to dashboard.")
        # Optional: Add a button to go back to the dashboard
        if st.button("Go to Dashboard"):
            del st.session_state["current_agent"]
            st.rerun()
        return

    agent_id = agent.get("_id") or agent.get("id")
    agent_name = agent.get("name", "Unnamed Agent")

    st.title(f"💬 Chatting with {agent_name}")
    
    # --- Sidebar Management ---
    with st.sidebar:
        session_sidebar(agent_id)
        
    # --- Main Area Layout ---
    
    # 1. Configuration Editor Toggle
    if st.session_state["show_config_editor"]:
        agent_config_editor(agent)
    else:
        # 2. Chat Interface
        if not st.session_state["active_session_id"]:
            # If no active session, try to list and select one, or force creation.
            st.info("No active chat session. Start a new chat from the sidebar.")
            return

        session_id = st.session_state["active_session_id"]
        
        # Display chat history
        chat_history_display(session_id)
        
        # Chat Input and Send Message Logic
        if prompt := st.chat_input("Ask your agent..."):
            # Ensure the session state is updated with the user message immediately
            # We don't want to use st.chat_message here, as the history component will handle rendering.
            
            # Use st.spinner for API latency
            with st.spinner(f"Agent {agent_name} is thinking..."):
                try:
                    from utils.chat_api import send_message # Import locally for use here
                    response = send_message(session_id, prompt)
                    
                    # Rerun to fetch updated history, including the new user message and agent response
                    st.rerun() 
                    
                except Exception as e:
                    st.error(f"Error sending message: {e}")
                    # Rerunning may show the user's message but not the AI response on failure