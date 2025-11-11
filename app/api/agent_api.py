from fastapi import APIRouter, Depends, HTTPException, status , Query
from typing import List
from models import Agent, AgentConfig
from schemas import AgentCreateRequest
from services.agent_service import AgentService
from dependencies import get_agent_service
from core import AGENT_CONFIG_SPEC

router = APIRouter(prefix="/agents", tags=["Agents"])

@router.post("/", response_model=Agent, status_code=status.HTTP_201_CREATED)
async def create_agent(agent_data: AgentCreateRequest, service: AgentService = Depends(get_agent_service)):
    """Create a new agent with its configuration."""
    try:
        print("Received agent creation request with data:", agent_data)
        return await service.create_agent(
                    user_id="get_it_from_token",
                    name=agent_data.name,
                    description=agent_data.description,
                    config=agent_data.config, 
                )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[Agent])
async def list_user_agents(service: AgentService = Depends(get_agent_service)):
    """Get all agents."""
    return await service.list_user_agents(user_id="get_it_from_token")


@router.get("/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str, service: AgentService = Depends(get_agent_service)):
    """Get one agent by ID."""
    agent = await service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.put("/{agent_id}", response_model=Agent)
async def update_agent(agent_id: str, update_data: AgentCreateRequest, service: AgentService = Depends(get_agent_service)):
    """
    Update an existing agent (e.g., name, description, or config).
    """
    existing_agent = await service.get_agent(agent_id)
    if not existing_agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    await service.update_agent(agent_id, update_data)
    updated_agent = await service.get_agent(agent_id)
    return updated_agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: str, service: AgentService = Depends(get_agent_service)):
    """Delete an agent by ID."""
    await service.delete_agent(agent_id)
    return {"message": "Agent deleted successfully"}

@router.get("/config/options")
async def get_agent_config_options(provider: str | None = Query(None)):
    """
    Return config options for agent creation.
    If provider is given, return only model options for that provider.
    """
    if provider:
        return {
            "provider": provider,
            "models": AGENT_CONFIG_SPEC["model"]["choices_by_provider"].get(provider, [])
        }
    return AGENT_CONFIG_SPEC
