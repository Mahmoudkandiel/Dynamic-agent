# dependencies/agent.py
from db import db
from repositories import AgentRepo ,SessionRepo
from services import AgentService , ChatService

session_repo = SessionRepo(db)
agent_repo = AgentRepo(db)
agent_service = AgentService(agent_repo)
chat_service = ChatService(session_repo, agent_repo)


def get_agent_service() -> AgentService:
    return agent_service

def get_chat_service() -> ChatService:
    return chat_service

