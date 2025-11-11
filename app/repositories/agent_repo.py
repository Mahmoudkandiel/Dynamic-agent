from models.agent import Agent
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId


class AgentRepo:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["agents"]

    async def insert(self, agent: Agent):
        """Insert a new agent into MongoDB."""
        await self.collection.insert_one(agent.model_dump(by_alias=True))
        return agent

    async def get_by_id(self, agent_id: str) -> Optional[Agent]:
        """Retrieve an agent by its ID."""
        print("Getting agent by ID:", agent_id)
        doc = await self.collection.find_one({"_id": agent_id})
        print("Fetched document:", doc)
        return Agent(**doc) if doc else None

    async def get_by_user(self, user_id: str) -> List[Agent]:
        """Retrieve all agents belonging to a user."""
        cursor = self.collection.find({"user_id": user_id})
        agents = await cursor.to_list(length=100)
        return [Agent(**doc) for doc in agents]

    async def update(self, agent_id: str, data: dict):
        """Update agent fields."""
        print("Updating agent ID:", agent_id, "with data:", data)
        await self.collection.update_one({"_id":(agent_id)}, {"$set": data})

    async def delete(self, agent_id: str):
        """Delete an agent."""
        await self.collection.delete_one({"_id":(agent_id)})
