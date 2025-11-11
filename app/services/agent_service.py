from models.agent import Agent, AgentConfig
from repositories.agent_repo import AgentRepo
from datetime import datetime, timezone
from typing import Optional, List


class AgentService:
    def __init__(self, repo: AgentRepo):
        self.repo = repo

    async def create_agent(self, user_id: str, name: str, description: Optional[str], config: AgentConfig):
        """Create and store a new agent."""
        agent = Agent(
            user_id=user_id,
            name=name,
            description=description,
            config=config,
        )
        await self.repo.insert(agent)
        return agent

    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Fetch one agent by ID."""
        return await self.repo.get_by_id(agent_id)

    async def list_user_agents(self, user_id: str) -> List[Agent]:
        """Fetch all agents belonging to a user."""
        return await self.repo.get_by_user(user_id)

    async def update_agent(self, agent_id: str, update_data: dict):
        """Update agent details (like adding new configs)."""
        data = update_data.model_dump()
        data["updated_at"] = datetime.now(timezone.utc)
        await self.repo.update(agent_id,data)

    async def delete_agent(self, agent_id: str):
        """Remove an agent."""
        await self.repo.delete(agent_id)
