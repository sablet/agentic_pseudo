"""Agent API endpoints."""

from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import TokenData, get_optional_user
from src.database import get_db
from src.models.schemas import (
    Agent, 
    AgentCreate, 
    AgentUpdate, 
    AgentMetaInfo,
    ListResponse
)
from src.service.agent_service import AgentService

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


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


@router.get("/by-agent-id/{agent_id}", response_model=Agent)
async def get_agent_by_agent_id(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Get an agent by agent_id (UUID)."""
    service = AgentService(db)
    return await service.get_agent_by_agent_id(agent_id)


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

    # Convert SQLAlchemy objects to Pydantic schemas
    agent_schemas = [Agent.model_validate(agent) for agent in agents]

    return ListResponse(
        items=agent_schemas, total=total, page=skip // limit + 1, per_page=limit
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


@router.get("/{agent_id}/meta-info", response_model=AgentMetaInfo)
async def get_agent_meta_info(
    agent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Get detailed agent metadata."""
    service = AgentService(db)
    return await service.get_agent_meta_info(agent_id)


@router.put("/{agent_id}/context", response_model=Agent)
async def update_agent_context(
    agent_id: int,
    context_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Update agent context."""
    service = AgentService(db)
    return await service.update_agent_context(agent_id, context_data)


@router.post("/{agent_id}/execute")
async def execute_agent(
    agent_id: int,
    execution_params: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Start agent execution."""
    service = AgentService(db)
    return await service.execute_agent(agent_id, execution_params or {})


@router.put("/{agent_id}/status", response_model=Agent)
async def update_agent_status(
    agent_id: int,
    status_data: Dict[str, str],
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Update agent status."""
    if "status" not in status_data:
        raise HTTPException(status_code=400, detail="Status field is required")
    
    service = AgentService(db)
    return await service.update_agent_status(agent_id, status_data["status"])


@router.get("/hierarchy", response_model=List[Agent])
async def get_agent_hierarchy(
    root_agent_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Get agent hierarchy."""
    service = AgentService(db)
    return await service.get_agent_hierarchy(root_agent_id)


@router.get("/{agent_id}/children", response_model=List[Agent])
async def get_child_agents(
    agent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Get child agents."""
    service = AgentService(db)
    return await service.get_child_agents(agent_id)


@router.get("/{agent_id}/parent", response_model=Optional[Agent])
async def get_parent_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Get parent agent."""
    service = AgentService(db)
    return await service.get_parent_agent(agent_id)

