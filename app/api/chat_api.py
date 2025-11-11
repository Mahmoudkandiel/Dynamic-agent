from fastapi import APIRouter, Depends, HTTPException, status
from schemas import ChatCreateRequest,ChatMessage
from dependencies import get_chat_service
from services import ChatService
from typing import List, Dict, Any
from models import Session


router = APIRouter(prefix="/chats", tags=["chats"])

@router.post("/{agent_id}")
async def create_chat(
    agent_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    try:
        return await chat_service.create(agent_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post("/message/{session_id}")
async def send_message(
    session_id: str,
    data: ChatMessage,
    chat_service: ChatService = Depends(get_chat_service)
):
    message = data.message
    result = await chat_service.send_message(session_id, message)
    return {"response": result}


@router.get("/{session_id}/history")
async def get_chat_history(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
) -> List[Dict[str, Any]]: # Return type matching the service method
    """Get the message history for a given chat session."""
    try:
        history = await chat_service.get_history(session_id)
        if not history:
            history = []            
            # raise HTTPException(status_code=404, detail="Chat session not found or empty.")
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")
    
@router.get("/{agent_id}", response_model=List[Session]) # Use List[Session] if you want full session objects
async def list_agent_chats(agent_id : str ,chat_service: ChatService = Depends(get_chat_service)):
    """List all active chat sessions for the current user."""
    try:
        sessions = await chat_service.list_agent_sessions(agent_id)
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))