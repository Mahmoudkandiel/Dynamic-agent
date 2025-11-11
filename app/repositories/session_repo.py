from models.session import Session  # Import your Session model
from utils import PyObjectId       # Import your ObjectId helper
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone

class SessionRepo:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["sessions"]

    async def create(self, session: Session) -> Session:
        """
        Insert a new session into MongoDB.
        """
        print("Creating session:", session)
        await self.collection.insert_one(session.model_dump(by_alias=True,round_trip=True))
        return session

    async def get_by_id(self, thread_id: str) -> Optional[Session]:
        """Retrieve a session by its thread_id (which is the _id)."""
        print("Getting session by ID:", thread_id)
        doc = await self.collection.find_one({"_id": thread_id})
        print("Fetched document:", doc)
        return Session(**doc) if doc else None

    async def get_by_agent(self, agent_id: str) -> List[Session]:
        """
        Retrieve all sessions for a specific agent_id.
        """
        cursor = self.collection.find({"agent_id": (agent_id)})
        sessions_list = await cursor.sort("updated_at", -1).to_list(length=100)
        return [Session(**doc) for doc in sessions_list]

    async def update(self, thread_id: str) -> bool:
        """
        Update the updated_at timestamp for a session.
        """
        result = await self.collection.update_one(
            {"_id": thread_id},
            {"$set": {"updated_at": datetime.now(timezone.utc)}}
        )
        return result.modified_count > 0

    async def update_title(self, thread_id: str, new_title: str) -> bool:
        """Update the user-visible title of a session."""
        result = await self.collection.update_one(
            {"_id": PyObjectId(thread_id)},
            {"$set": {"title": new_title}}
        )
        return result.modified_count > 0

    async def delete(self, thread_id: str) -> bool:
        """Delete a session by its thread_id."""
        result = await self.collection.delete_one({"_id": PyObjectId(thread_id)})
        return result.deleted_count > 0