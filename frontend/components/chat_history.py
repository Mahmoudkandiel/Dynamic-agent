# components/chat_history.py

import streamlit as st
from utils.chat_api import get_chat_history
from typing import List, Dict, Any

def chat_history_display(session_id: str):
    st.subheader("Conversation History")
    
    # Fetch history using the utility function
    try:
        messages: List[Dict[str, Any]] = get_chat_history(session_id)
    except Exception as e:
        st.error(f"Failed to load chat history: {e}")
        messages = []

    if not messages:
        st.info("Start the conversation by typing a message below.")
        return

    # Display messages in reverse order for chronological display in Streamlit
    for message in messages:
        role = message.get("role")
        content = message.get("content")
        
        # Streamlit roles are 'user' or 'assistant'
        if role == 'user':
            display_role = 'user'
        elif role == 'ai':
            display_role = 'assistant'
        else:
            # Handle other possible LangChain roles if needed (e.g., 'system', 'tool')
            continue 

        with st.chat_message(display_role):
            st.write(content)