# app.py

import streamlit as st
from screens.dashboard import dashboard_screen
from screens.chat import chat_screen
# from screens.chat_screen import chat_screen  (later)

st.set_page_config(page_title="AI Agent App", layout="wide")

# --- CENTRALIZED SESSION STATE INITIALIZATION ---

# Navigation
if "screen" not in st.session_state:
    st.session_state.screen = "dashboard"

# Dashboard State
if "show_create_agent" not in st.session_state:
    st.session_state["show_create_agent"] = False

# Chat/Agent State
if "current_agent" not in st.session_state:
    st.session_state["current_agent"] = None

if "active_session_id" not in st.session_state:
    st.session_state["active_session_id"] = None
    
# Agent Editing State (used in chat screen)
if "show_config_editor" not in st.session_state:
    st.session_state["show_config_editor"] = False

# --- APPLICATION ROUTING ---

if st.session_state.screen == "dashboard":
    # The dashboard_screen function will now safely access st.session_state["show_create_agent"]
    dashboard_screen()
elif st.session_state.screen == "chat":
    chat_screen()