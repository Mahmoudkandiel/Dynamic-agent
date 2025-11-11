from pydantic import BaseModel
from typing import List, Optional
from models import AgentConfig


class AgentCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    config: AgentConfig