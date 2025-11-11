# components/agent_config_editor.py

import streamlit as st
from utils.agent_api import update_agent, get_config_options, get_agent # Need get_agent to reload data

def agent_config_editor(agent: dict):
    st.subheader(f"⚙️ Editing: {agent.get('name', 'Agent')}")

    agent_id = agent.get("_id") or agent.get("id")
    current_config = agent.get("config", {})

    # 1. Fetch Configuration Options
    # Use st.cache_data for static data like config options
    @st.cache_data(ttl=3600)
    def fetch_config_spec():
        try:
            return get_config_options()
        except Exception as e:
            st.error(f"Could not load agent configuration options: {e}")
            return {}

    config_spec = fetch_config_spec()
    
    # If spec loading failed, return
    if not config_spec:
        st.warning("Cannot edit configuration due to API error.")
        return

    # Extract specs for defaults and choices
    providers = config_spec.get("model_provider", {}).get("choices", [])
    model_choices_by_provider = config_spec.get("model", {}).get("choices_by_provider", {})
    temp_spec = config_spec.get("temperature", {})
    prompt_spec = config_spec.get("prompt", {})
    tools_spec = config_spec.get("tools", {})
    
    # Helper to get the correct index for a selectbox
    def get_index(options, value):
        try:
            return options.index(value)
        except ValueError:
            return 0 # Default to the first option if the current value is invalid

    # Use a container to hold the form and the exit button
    editor_container = st.container()

    with editor_container:
        with st.form("edit_agent_form"):
            # --- Basic Information ---
            name = st.text_input("Agent Name", value=agent.get("name", ""), max_chars=50, key="edit_agent_name")
            description = st.text_area("Description", value=agent.get("description", ""), max_chars=200, key="edit_agent_desc")
            
            st.markdown("---")

            # --- Configuration Inputs ---
            
            # 1. Provider Selection
            current_provider = current_config.get("provider", providers[0] if providers else None)
            provider_index = get_index(providers, current_provider)
            selected_provider = st.selectbox("Model Provider", options=providers, index=provider_index, key="edit_agent_provider")
            
            # 2. Model Selection (Filtered by Provider)
            current_models = model_choices_by_provider.get(selected_provider, [])
            current_model = current_config.get("model", current_models[0] if current_models else None)
            model_index = get_index(current_models, current_model)
            selected_model = st.selectbox("Model Name", options=current_models, index=model_index, key="edit_agent_model")

            # 3. Temperature Slider
            selected_temperature = st.slider("Temperature",
                min_value=temp_spec.get("min", 0.0), max_value=temp_spec.get("max", 1.0),
                value=current_config.get("temperature", temp_spec.get("default", 0.7)),
                step=0.1)

            # 4. Prompt Text Area
            selected_prompt = st.text_area("System Prompt",
                value=current_config.get("prompt", prompt_spec.get("default", "You are a helpful assistant.")))

            # 5. Tools Multiselect
            selected_tools = st.multiselect("Enabled Tools", options=tools_spec.get("choices", []),
                default=current_config.get("tools", tools_spec.get("default", [])))

            st.markdown("<br>", unsafe_allow_html=True)
            
            # --- Submission (Must be st.form_submit_button and alone inside form) ---
            submitted = st.form_submit_button("Save Changes 💾", use_container_width=True)

            if submitted:
                if not name or not selected_model:
                    st.error("Name and Model are required.")
                else:
                    update_data = {
                        "name": name,
                        "description": description,
                        "config": {
                            "provider": selected_provider,
                            "model": selected_model,
                            "temperature": selected_temperature,
                            "prompt": selected_prompt,
                            "tools": selected_tools,
                        }
                    }
                    
                    try:
                        # 1. Update Agent
                        update_agent(agent_id, update_data)
                        
                        # 2. Reload Agent Data
                        # NOTE: Assuming you have or will add get_agent(agent_id) to agent_api.py
                        updated_agent = get_agent(agent_id) 
                        
                        st.session_state["current_agent"] = updated_agent # Reload current agent state
                        st.session_state["show_config_editor"] = False
                        st.success(f"Agent '{name}' updated successfully.")
                        st.rerun() 
                    except Exception as e:
                        st.error(f"Failed to update agent. Error: {e}")

    # ------------------------------------------------------------------
    # EXIT BUTTON: MUST BE OUTSIDE THE st.form BLOCK TO AVOID API EXCEPTION
    # ------------------------------------------------------------------
    
    st.markdown("---")
    
    # Placing the exit button below the form
    if st.button("Exit Editor", key="exit_edit_agent_final", use_container_width=True):
        st.session_state["show_config_editor"] = False
        st.rerun()