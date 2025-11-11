from pydantic import BaseModel

class ChatCreateRequest(BaseModel):
    agent_id: str

class ChatMessage(BaseModel):
    message: str
