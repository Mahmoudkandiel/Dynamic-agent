from models import Session, AgentConfig
from repositories import SessionRepo, AgentRepo
from datetime import datetime, timezone
from utils.checkpointer import get_memory   
from langchain_core.messages import AIMessage,BaseMessage
from langchain_core.runnables import RunnableConfig
from typing import List, Dict, Any
from graph import build_agent
import time


class ChatService:
    def __init__(self, session_repo: SessionRepo, agent_repo: AgentRepo):
        self.session_repo = session_repo
        self.agent_repo = agent_repo
        self.graph_cache = {}


    async def create(self, agent_id: str):
        session = Session(
            agent_id=agent_id,
        )
        session = await self.session_repo.create(session)
        return session


    async def send_message(self, session_id: str, message: str):
        session = await self.session_repo.get_by_id(session_id)
        agent = await self.agent_repo.get_by_id(session.agent_id)

        if session_id not in self.graph_cache:
            self.graph_cache[session_id] = build_agent(agent.config)
        
        graph = self.graph_cache[session_id]
        

        result = await graph.ainvoke(
            {"messages": [{"role": "user", "content": message}]},
            config={"configurable": {"thread_id": str(session_id)}},
            context=agent.config
            )

       
        ai_responses = [
            msg.content for msg in result["messages"]
            if isinstance(msg, AIMessage)
        ]

        latest_ai_response = ai_responses[-1] if ai_responses else None
        

        await self.session_repo.update(session_id)

        return latest_ai_response

    
    async def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Fetches the full message history from the LangGraph checkpointer 
        using the session_id as the thread_id.
        """
        
        checkpointer = get_memory()
        config: RunnableConfig = {
            "configurable": {
                "thread_id": str(session_id)
            }
        }


        checkpoint = await checkpointer.aget(config)




        if not checkpoint:
            return []
        
        messages: List[BaseMessage] = checkpoint.get("channel_values", {}).get("messages", [])
        
        history = []
        for msg in messages:
            
            role = "ai" if isinstance(msg, AIMessage) else "user"
            
            history.append({
                "role": role,
                "content": msg.content,
                "timestamp": datetime.now(timezone.utc).isoformat() 
            })
        
        return history

    async def list_agent_sessions(self, agent_id: str) -> List[Session]:
        """ 
        Retrieves all active chat sessions belonging to a specific user.
        (Assuming SessionRepo handles filtering by user_id)
        """
        sessions = await self.session_repo.get_by_agent(agent_id)
        return sessions