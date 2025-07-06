"""Agent API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.service.agent_service import AgentService
from src.models.schemas import Agent, AgentCreate, AgentUpdate, ListResponse
from src.auth import get_optional_user, TokenData

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/", response_model=Agent, status_code=201)
async def create_agent(
    agent_data: AgentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Create a new agent."""
    service = AgentService(db)
    return await service.create_agent(agent_data)


@router.get("/{agent_id}", response_model=Agent)
async def get_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Get an agent by ID."""
    service = AgentService(db)
    return await service.get_agent(agent_id)


@router.get("/", response_model=ListResponse)
async def get_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    agent_type: Optional[str] = Query(None, alias="type"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Get list of agents with optional filtering."""
    service = AgentService(db)

    agents = await service.get_agents(
        skip=skip, limit=limit, status=status, agent_type=agent_type
    )

    total = await service.count_agents(status=status, agent_type=agent_type)

    return ListResponse(
        items=agents, total=total, page=skip // limit + 1, per_page=limit
    )


@router.put("/{agent_id}", response_model=Agent)
async def update_agent(
    agent_id: int,
    agent_data: AgentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Update an agent."""
    service = AgentService(db)
    return await service.update_agent(agent_id, agent_data)


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Delete an agent."""
    service = AgentService(db)
    await service.delete_agent(agent_id)


@router.get("/{agent_id}/templates", response_model=List[dict])
async def get_agent_templates(
    agent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Get templates for an agent."""
    service = AgentService(db)
    agent = await service.get_agent_with_templates(agent_id)
    return agent.templates


@router.get("/{agent_id}/conversations", response_model=List[dict])
async def get_agent_conversations(
    agent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Get conversations for an agent."""
    service = AgentService(db)
    agent = await service.get_agent_with_conversations(agent_id)
    return agent.conversations
