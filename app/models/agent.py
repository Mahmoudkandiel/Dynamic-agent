from pydantic import BaseModel,Field
from datetime import datetime,timezone
from typing import List, Optional, Literal, Dict
from utils import PyObjectId


class CollectionSchema(BaseModel):
    name: str
    fields: Dict[str, str]

class DatabaseConfig(BaseModel):
    db_type: Literal["mongodb", "postgres", "mysql"]
    connection_string: str
    db_name: Optional[str] = None
    schema: List[CollectionSchema]

class AgentConfig(BaseModel):
    model: str
    model_provider: Literal["azure_openai", "anthropic", "google"] = "azure_openai"
    temperature: float = Field(..., ge=0, le=1, description="Model randomness factor")
    prompt: str
    tools: List[str]
    database_config: Optional[DatabaseConfig] = None

class Agent(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    name: str
    description: Optional[str] = None
    config: AgentConfig
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


    class Config:
        populate_by_name = True
        json_encoders = {PyObjectId: str} 
        # arbitrary_types_allowed = True