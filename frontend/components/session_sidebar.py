# components/session_sidebar.py

import streamlit as st
from utils.chat_api import list_agent_sessions, create_chat
from typing import Dict, Any

# --- Callback Function ---
def update_active_session(session_map):
    """Callback triggered when the radio button value changes."""
    # Get the key (e.g., "Chat #1...") from the radio button state
    selected_key = st.session_state["session_radio"]
    # Get the actual session ID from the map
    new_session_id = session_map.get(selected_key)
    
    # Only update and rerun if the ID is new
    if new_session_id and new_session_id != st.session_state.get("active_session_id"):
        st.session_state["active_session_id"] = new_session_id
        st.rerun()

def session_sidebar(agent_id: str):
    st.header("Chat Sessions")
    
    # --- 1. New Chat Button ---
    if st.button("➕ Start New Chat", use_container_width=True):
        try:
            new_session = create_chat(agent_id)
            st.session_state["active_session_id"] = new_session.get("_id")
            print("Created new session: ", new_session)
            print("Updated active_session_id to: ", st.session_state["active_session_id"])
            st.success("New chat session started.")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to start new chat: {e}")

    st.markdown("---")
    st.subheader("Active Sessions")

    # --- 2. Session List ---
    try:
        sessions = list_agent_sessions(agent_id)
    except Exception as e:
        st.error(f"Could not load sessions: {e}")
        sessions = []

    if not sessions:
        st.info("No active sessions for this agent.")
        return

    session_map = {f"Chat #{i+1} (ID: {s.get('_id', 'N/A')[:4]}...)": s.get("_id") 
                   for i, s in enumerate(sessions)}
    
    # Determine the key for the current active session
    initial_key = next((key for key, sid in session_map.items() 
                        if sid == st.session_state.get("active_session_id")), 
                        list(session_map.keys())[0])
    
    # If no active_session_id is set, initialize it to the first session found
    if not st.session_state.get("active_session_id"):
        st.session_state["active_session_id"] = session_map.get(initial_key)

    # Create a radio selection for sessions with a callback
    st.radio(
        "Select a conversation:",
        options=list(session_map.keys()),
        index=list(session_map.keys()).index(initial_key),
        key="session_radio",
        on_change=update_active_session, # <-- NEW: Attach callback function
        args=(session_map,)             # <-- Pass session_map to the callback
    )

    # --- Removed the manual if/st.rerun() block ---
    # The logic is now in update_active_session

    st.markdown("---")

    # --- 3. Edit Agent Config Button ---
    if st.button("✏️ Edit Agent Configuration", use_container_width=True):
        st.session_state["show_config_editor"] = not st.session_state["show_config_editor"]
        st.rerun()