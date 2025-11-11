import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from utils import PyObjectId

class Session(BaseModel):
    thread_id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    agent_id: str 
    title: str = Field(default="New Chat")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        populate_by_name = True
        # json_encoders = {PyObjectId: str} 
        arbitrary_types_allowed = True
    