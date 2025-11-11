# components/create_agent_form.py

import streamlit as st
from utils.agent_api import get_config_options, create_agent, get_db_schema

def create_agent_form():
    """
    Displays the form for creating a new agent, pulling config options from the API,
    including temperature, prompt, tools, and an optional database tool.
    """
    st.subheader("➕ Create New Agent")
    
    # ----------------------------------------------------
    # *** 1. MODIFIED: CLEARING LOGIC ***
    # ----------------------------------------------------
    if st.session_state.get("clear_db_fields", False):
        st.session_state.db_enabled = False # <-- Clear the enabled state
        st.session_state.db_type = 'mongodb' # Assuming a default/clearing value
        st.session_state.db_conn_string = ''
        st.session_state.db_name = ''
        st.session_state.db_schema_options = []
        st.session_state.db_full_schema_data = [] # <-- Clear full data
        st.session_state.clear_db_fields = False

    # 1. Fetch Configuration Options
    try:
        config_spec = get_config_options()
        if not config_spec:
             st.error("API returned no configuration options.")
             return
             
        providers = config_spec.get("model_provider", {}).get("choices", [])
        model_choices_by_provider = config_spec.get("model", {}).get("choices_by_provider", {})
        temp_spec = config_spec.get("temperature", {})
        prompt_spec = config_spec.get("prompt", {})
        tools_spec = config_spec.get("tools", {})
        
    
        db_type_choices = config_spec.get("database_type", {}).get("choices")
        db_type_default = config_spec.get("database_type", {}).get("default")


    except Exception as e:
        st.error(f"Could not load agent configuration options from API: {e}")
        return

    # ----------------------------------------------------
    # *** 2. MODIFIED: OPTIONAL DATABASE CONFIG (MOVED BEFORE FORM) ***
    # ----------------------------------------------------
    st.subheader("🗂️ Database Configuration")
    st.write("Connect to a database to allow the agent to query and analyze data.")

    # State management for DB inputs
    st.session_state.setdefault('db_enabled', False) # New checkbox state
    st.session_state.setdefault('db_type', db_type_default) # New database type state
    st.session_state.setdefault('db_conn_string', '')
    st.session_state.setdefault('db_name',None)
    st.session_state.setdefault('db_schema_options', [])
    st.session_state.setdefault('db_full_schema_data', []) # <-- Store full data
    
    # Checkbox to enable/disable DB configuration
    st.checkbox(
        "Enable Database Tool", 
        value=st.session_state.db_enabled, 
        key="db_enabled"
    )

    if st.session_state.db_enabled:
        
        st.markdown("---")
        
        # New: Database Type Selection
        st.selectbox(
            "Database Type",
            options=db_type_choices,
            index=db_type_choices.index(db_type_default) if db_type_default in db_type_choices else 0,
            key="db_type",
            help="Select the type of database to connect to."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.text_input(
                "Connection String", 
                key="db_conn_string", 
                help="e.g., mongodb://user:pass@host:port/",
                value=st.session_state.db_conn_string
            )
        with col2:
            st.text_input("Database Name", key="db_name", value=st.session_state.db_name)

        if st.button("Get/Refresh Schema"):
            if not st.session_state.db_conn_string:
                st.warning("Please provide both Connection String and Database Name.")
            else:
                try:
                    with st.spinner(f"Fetching {st.session_state.db_type} schema..."):
                        # NOTE: get_db_schema likely needs the db_type, but the provided
                        # signature only takes conn_string and db_name. Sticking to original
                        # signature for now, but mentioning the context.
                        print("Fetching schema with:", 
                              st.session_state.db_type,
                              st.session_state.db_conn_string, 
                              st.session_state.db_name)
                        schema_data = get_db_schema(
                            st.session_state.db_type,
                            st.session_state.db_conn_string, 
                            st.session_state.db_name
                        )
                        print("-",st.session_state.db_name,"-")
                        print("Fetched schema data:", schema_data)
                        # Store both full data and just names
                        collections_list = schema_data.get("tables") or schema_data.get("collections", [])

                        print("Collections/Tables List:", collections_list)
                        
                        # Store the full list of objects
                        st.session_state.db_full_schema_data = collections_list
                        
                        # Store just the names for the multiselect
                        st.session_state.db_schema_options = [
                            collection.get("name") for collection in collections_list if collection.get("name")
                        ]
                        
                        st.success(f"Successfully fetched {len(st.session_state.db_schema_options)} collections!")
                        # No st.rerun() here to allow continuous interaction, but we'll show the multiselect below

                except Exception as e:
                    st.error(f"Failed to get schema: {e}")
                    st.session_state.db_schema_options = []
                    st.session_state.db_full_schema_data = []


        # Schema Selection Multiselect (MOVED HERE)
        if st.session_state.db_schema_options:
            st.write("**Database Schema Selection**")
            
            # This variable will contain the LIST OF SELECTED NAMES
            st.multiselect(
                "Select Collections/Tables to include",
                options=st.session_state.db_schema_options, # Use the list of names
                default=st.session_state.db_schema_options, 
                key="selected_schema_names", # New key for this multiselect
                help="Select the collections/tables the agent is allowed to query."
            )
        elif st.session_state.db_conn_string and st.session_state.db_name:
             st.info("Click 'Get/Refresh Schema' to fetch the available collections/tables.")
             
        st.markdown("---") # Visual separator before the main agent form

    # ----------------------------------------------------
    # 3. THE FORM (Contains agent inputs and the SUBMIT button)
    # ----------------------------------------------------
    form_container = st.container()

    with form_container:
        with st.form("create_agent_form", clear_on_submit=True):
            # --- Basic Information ---
            name = st.text_input("Agent Name", max_chars=50, key="new_agent_name")
            description = st.text_area("Description", max_chars=200, key="new_agent_desc")
            
            st.markdown("---")

            # --- Configuration ---
            st.write("**Agent Configuration**")
            
            # 1. Provider Selection
            selected_provider = st.selectbox(
                "Model Provider", 
                options=providers, 
                index=providers.index(config_spec.get("model_provider", {}).get("default")) 
                      if config_spec.get("model_provider", {}).get("default") in providers else 0,
                key="new_agent_provider"
            )
            
            # 2. Model Selection (Filtered by Provider)
            current_models = model_choices_by_provider.get(selected_provider, [])
            if current_models:
                selected_model = st.selectbox(
                    "Model Name", 
                    options=current_models, 
                    index=current_models.index(config_spec.get("model", {}).get("default"))
                          if config_spec.get("model", {}).get("default") in current_models else 0,
                    key="new_agent_model"
                )
            else:
                st.warning(f"No models available for provider: {selected_provider}")
                selected_model = None

            # 3. Temperature Slider
            selected_temperature = st.slider(
                "Temperature",
                min_value=temp_spec.get("min", 0.0),
                max_value=temp_spec.get("max", 1.0),
                value=temp_spec.get("default", 0.7),
                step=0.1,
                help=temp_spec.get("description", "Controls randomness in generation.")
            )

            # 4. Prompt Text Area
            selected_prompt = st.text_area(
                "System Prompt",
                value=prompt_spec.get("default", "You are a helpful assistant."),
                help=prompt_spec.get("description", "Base prompt for the agent.")
            )

            # 5. Tools Multiselect (Tools are AFTER Database Config)
            selected_tools = st.multiselect(
                "Enabled Tools",
                options=tools_spec.get("choices", []),
                default=tools_spec.get("default", []),
                help=tools_spec.get("description", "Enabled tools for the agent.")
            )
            
            st.markdown("---")
            
            # NOTE: Database Schema Selection multiselect has been MOVED OUT of the form
            # and placed conditionally after the "Get/Refresh Schema" button in section 2.
            
            # --- Submission Button (Must be st.form_submit_button) ---
            submitted = st.form_submit_button("Create Agent 💾")

            # --- Submission Logic ---
            if submitted:
                if not name or not selected_model:
                    st.error("Please provide a name and select a model.")
                else:
                    # Construct the base payload
                    agent_config = {
                        "model_provider": selected_provider,
                        "model": selected_model,
                        "temperature": selected_temperature,
                        "prompt": selected_prompt,
                        "tools": selected_tools,
                    }
                    
                    # *** 4. MODIFIED: Conditional Database Config inclusion ***
                    # Only include database config if the checkbox is checked AND 
                    # a connection string/db name are provided.
                    if st.session_state.db_enabled and st.session_state.db_conn_string:
                        
                        # Get the selected schema names from the session state key
                        selected_schema_names = st.session_state.get("selected_schema_names", [])

                        # Filter full data by selected names
                        full_schema_to_send = [
                            collection_obj for collection_obj in st.session_state.db_full_schema_data
                            if collection_obj.get("name") in selected_schema_names
                        ]
                        print("Filtered schema to send:", full_schema_to_send)

                        agent_config["database_config"] = {
                            "db_type": st.session_state.db_type, # New: Include database type
                            "connection_string": st.session_state.db_conn_string,
                            "db_name": st.session_state.db_name,
                            "schema": full_schema_to_send # <-- Send the filtered list of objects
                        }

                        print("Including database config in agent:", agent_config["database_config"])

                    agent_data = {
                        "name": name,
                        "description": description,
                        "config": agent_config
                    }
                    print("Creating agent with data:", agent_data)
                    st.toast("Attempting to create agent...")
                    try:
                        new_agent = create_agent(agent_data)
                        st.success(f"Successfully created agent: {new_agent.get('name')}")
                        
                        st.session_state.clear_db_fields = True
                        st.session_state["show_create_agent"] = False
                        st.rerun() 
                    except Exception as e:
                        st.error(f"Failed to create agent. Check API logs. Error: {e}")

        # ----------------------------------------------------
        # 5. THE CANCEL BUTTON (Must be OUTSIDE the st.form block)
        # ----------------------------------------------------
        
        col_space, col_cancel_btn = st.columns([1, 4]) 

        with col_cancel_btn:
            if st.button("Cancel", key="cancel_create_agent_final"):
                # *** 5. MODIFIED: CANCEL LOGIC ***
                st.session_state.clear_db_fields = True # This flag will trigger clearing all DB fields
                st.session_state["show_create_agent"] = False
                st.rerun()