# main_app_file (e.g., dashboard.py)

import streamlit as st
from components.agent_card import agent_card_grid
# Import the new component
from components.create_agent_form import create_agent_form 
from utils.agent_api import get_agents, delete_agent



def dashboard_screen():
    st.title("🧠 AI Agent Dashboard")
    
    # --- Top Bar: Add Agent Button and Description ---
    col_desc, col_button = st.columns([4, 1])
    
    with col_desc:
        st.write("Manage and interact with your AI agents.")

    with col_button:
        if st.button("➕ Add Agent", key="add_agent_btn"):
            st.session_state["show_create_agent"] = True
            st.rerun() # Fixed: Use st.rerun()

    # --- Conditional Display of Form/Dashboard ---
    if st.session_state["show_create_agent"]:
        # Display the creation form component
        create_agent_form()
    else:
        # Display the agent cards
        agents = get_agents() or []

        # Define callback functions
        def on_chat(agent):
            st.session_state["current_agent"] = agent
            st.session_state["screen"] = "chat" # <--- ADD THIS LINE FOR SCREEN SWITCH
            st.success(f"Opened chat with {agent.get('name', 'Agent')}")
            st.rerun()

        def on_edit(agent):
            st.session_state["edit_agent"] = agent
            st.info(f"Editing {agent.get('name', 'Agent')}")
            st.rerun() # Fixed: Use st.rerun()

        def on_delete(agent):
            agent_id = agent.get("_id") or agent.get("id")
            if agent_id:
                delete_agent(agent_id)
                st.warning(f"Deleted {agent.get('name', 'Agent')}")
                st.rerun() # Fixed: Use st.rerun()
            else:
                st.error("Could not find agent ID to delete.")


        if not agents:
            st.info("No agents found. Click 'Add Agent' to get started!")
            return

        # Display the agent card grid
        agent_card_grid(agents, on_chat, on_edit, on_delete)
        
# If you run your app using 'streamlit run main_app_file.py'
# dashboard_screen()