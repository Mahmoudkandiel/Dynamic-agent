from models import Session
from repositories import SessionRepo

from typing import Optional, List
from datetime import datetime, timezone




class SessionService:
    def __init__(
        self,
        session_repo: SessionRepo
    ):
        self.session_repo = session_repo 

    async def create_session(self, agent_id: str):
        """Create and store a new session."""
        session = Session(
            agent_id=agent_id,
        )
        await self.repo.insert(session)
        return session
    
    async def get_session(self,session_id: str) -> Optional[Session]:
        """Fetch one session by ID."""
        return await self.repo.get_by_id(session_id)
    
    async def list_agent_sessions(self, agent_id: str) -> List[Session]:
        """Fetch all sessions belonging to an agent."""
        return await self.repo.get_by_agent(agent_id)
    
    async def update_session_title(self, session_id: str, title : str):
        """Update session title."""
        update_data = {
            "title": title,
            "updated_at": datetime.now(timezone.utc)
            }
        await self.update_session(session_id, update_data)
    
    async def delete_session(self, session_id: str):
        """Remove a session."""
        await self.repo.delete(session_id)
    
