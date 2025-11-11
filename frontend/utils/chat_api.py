# utils/chat_api.py

import requests
from typing import List, Dict, Any, Optional

# Assuming your BASE_URL is consistent across all utility files
BASE_URL = "http://Backend:8000"

def create_chat(agent_id: str) -> Dict[str, Any]:
    """
    Creates a new chat session for a given agent.
    Returns the new Session object (which includes the session_id).
    API Endpoint: POST /chats/{agent_id}
    """
    # Note: Using POST with an empty body, as the agent_id is in the path
    res = requests.post(f"{BASE_URL}/chats/{agent_id}")
    print("Create chat response: ", res.text)
    res.raise_for_status()
    return res.json()

def send_message(session_id: str, message: str) -> Dict[str, str]:
    """
    Sends a message to an active chat session and gets the agent's response.
    API Endpoint: POST /chats/message/{session_id}
    """
    data = {"message": message} # Matches the ChatMessage schema (e.g., {"message": "..."})
    res = requests.post(f"{BASE_URL}/chats/message/{session_id}", json=data)
    res.raise_for_status()
    # The API returns {"response": result}
    return res.json()

def get_chat_history(session_id: str) -> List[Dict[str, Any]]:
    """
    Fetches the message history for a specific chat session.
    API Endpoint: GET /chats/{session_id}/history
    """
    res = requests.get(f"{BASE_URL}/chats/{session_id}/history")
    res.raise_for_status()
    # Returns a list of message dicts: [{"role": "user", "content": "..."}, ...]
    return res.json()

def list_agent_sessions(agent_id: str) -> List[Dict[str, Any]]:
    """
    Fetches all chat sessions associated with a specific agent ID.
    API Endpoint: GET /chats?agent_id={agent_id}
    """
    res = requests.get(f"{BASE_URL}/chats/{agent_id}", params={"agent_id": agent_id})
    res.raise_for_status()
    return res.json()