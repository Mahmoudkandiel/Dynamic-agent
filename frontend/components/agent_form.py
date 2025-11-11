import streamlit as st
from frontend.utils.agent_api import create_agent, get_config_options

def agent_form(on_created):
    st.subheader("🧩 Create New Agent")
    name = st.text_input("Agent Name")
    desc = st.text_area("Description")
    providers = ["openai", "anthropic", "custom"]
    provider = st.selectbox("Provider", providers)
    options = get_config_options(provider)
    models = options.get("models", [])
    model = st.selectbox("Model", models if models else ["default"])
    
    if st.button("Create Agent"):
        data = {
            "name": name,
            "description": desc,
            "config": {"provider": provider, "model": model},
        }
        agent = create_agent(data)
        st.success(f"✅ Agent '{name}' created!")
        on_created(agent)
