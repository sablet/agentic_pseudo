"""Agent service layer."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.exceptions import not_found_exception
from src.models.database_models import Agent, AgentTemplate
from src.models.schemas import (
    AgentCreate, 
    AgentUpdate, 
    AgentMetaInfo,
    ContextStatus,
    WaitingInfo,
    ConversationMessage,
    ParentAgentSummary,
    ChildAgentSummary
)


class AgentService:
    """Service for managing agents."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_agent(self, agent_data: AgentCreate) -> Agent:
        """Create a new agent."""
        agent_dict = agent_data.model_dump()
        agent_dict['agent_id'] = str(uuid4())
        
        # If parent_agent_id is provided, calculate level
        if agent_dict.get('parent_agent_id'):
            parent = await self.get_agent(agent_dict['parent_agent_id'])
            agent_dict['level'] = parent.level + 1
        
        db_agent = Agent(**agent_dict)
        self.db.add(db_agent)
        await self.db.commit()
        await self.db.refresh(db_agent)
        return db_agent

    async def get_agent(self, agent_id: int) -> Agent:
        """Get an agent by ID."""
        query = select(Agent).where(Agent.id == agent_id)
        result = await self.db.execute(query)
        agent = result.scalar_one_or_none()

        if not agent:
            raise not_found_exception("Agent", agent_id)

        return agent

    async def get_agents(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        agent_type: Optional[str] = None,
    ) -> List[Agent]:
        """Get list of agents with optional filtering."""
        query = select(Agent)

        if status:
            query = query.where(Agent.status == status)
        if agent_type:
            query = query.where(Agent.type == agent_type)

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_agent(self, agent_id: int, agent_data: AgentUpdate) -> Agent:
        """Update an agent."""
        # Check if agent exists
        await self.get_agent(agent_id)

        # Update agent
        update_data = agent_data.model_dump(exclude_unset=True)
        if update_data:
            query = update(Agent).where(Agent.id == agent_id).values(**update_data)
            await self.db.execute(query)
            await self.db.commit()

        # Return updated agent
        return await self.get_agent(agent_id)

    async def delete_agent(self, agent_id: int) -> bool:
        """Delete an agent."""
        # Check if agent exists
        await self.get_agent(agent_id)

        # Delete agent
        query = delete(Agent).where(Agent.id == agent_id)
        await self.db.execute(query)
        await self.db.commit()

        return True

    async def get_agent_with_templates(self, agent_id: int) -> Agent:
        """Get an agent with its templates."""
        query = (
            select(Agent)
            .options(selectinload(Agent.templates))
            .where(Agent.id == agent_id)
        )

        result = await self.db.execute(query)
        agent = result.scalar_one_or_none()

        if not agent:
            raise not_found_exception("Agent", agent_id)

        return agent

    async def get_agent_with_conversations(self, agent_id: int) -> Agent:
        """Get an agent with its conversations."""
        query = (
            select(Agent)
            .options(selectinload(Agent.conversations))
            .where(Agent.id == agent_id)
        )

        result = await self.db.execute(query)
        agent = result.scalar_one_or_none()

        if not agent:
            raise not_found_exception("Agent", agent_id)

        return agent

    async def count_agents(
        self, status: Optional[str] = None, agent_type: Optional[str] = None
    ) -> int:
        """Count agents with optional filtering."""
        query = select(Agent.id)

        if status:
            query = query.where(Agent.status == status)
        if agent_type:
            query = query.where(Agent.type == agent_type)

        result = await self.db.execute(query)
        return len(result.scalars().all())

    async def get_agent_by_agent_id(self, agent_id: str) -> Agent:
        """Get an agent by agent_id (UUID)."""
        query = select(Agent).where(Agent.agent_id == agent_id)
        result = await self.db.execute(query)
        agent = result.scalar_one_or_none()

        if not agent:
            raise not_found_exception("Agent", agent_id)

        return agent

    async def get_agent_meta_info(self, agent_id: int) -> AgentMetaInfo:
        """Get detailed agent metadata."""
        agent = await self.get_agent(agent_id)
        
        # Build context status (mock data for now)
        context_status = [
            ContextStatus(
                id="ctx1",
                name="Data Analysis",
                type="file",
                required=True,
                status="sufficient",
                description="Market analysis data",
                current_value=None
            )
        ]
        
        # Build waiting info (mock data for now)
        waiting_for = []
        if agent.status.value == "waiting":
            waiting_for.append(
                WaitingInfo(
                    type="context",
                    description="Waiting for additional data",
                    estimated_time="2 hours"
                )
            )
        
        # Build conversation history (mock data for now)
        conversation_history = [
            ConversationMessage(
                id="msg1",
                role="user",
                content="Please analyze the market data",
                timestamp=datetime.utcnow()
            )
        ]
        
        # Get parent agent summary
        parent_summary = None
        if agent.parent_agent_id:
            parent = await self.get_agent(agent.parent_agent_id)
            parent_summary = ParentAgentSummary(
                agent_id=parent.agent_id,
                name=parent.name,
                purpose=parent.purpose or "",
                level=parent.level
            )
        
        # Get child agent summaries
        children = await self.get_child_agents(agent_id)
        child_summaries = [
            ChildAgentSummary(
                agent_id=child.agent_id,
                name=child.name,
                purpose=child.purpose or "",
                status=child.status,
                level=child.level
            )
            for child in children
        ]
        
        return AgentMetaInfo(
            agent_id=agent.agent_id,
            purpose=agent.purpose or "",
            description=agent.description or "",
            level=agent.level,
            context_status=context_status,
            waiting_for=waiting_for,
            execution_log=["Agent created", "Initialization complete"],
            conversation_history=conversation_history,
            parent_agent_summary=parent_summary,
            child_agent_summaries=child_summaries
        )

    async def update_agent_context(
        self, agent_id: int, context_data: Dict[str, Any]
    ) -> Agent:
        """Update agent context."""
        agent = await self.get_agent(agent_id)
        
        # Update context field
        current_context = agent.context or []
        current_context.extend(context_data.get('new_context', []))
        
        update_data = {'context': current_context}
        query = update(Agent).where(Agent.id == agent_id).values(**update_data)
        await self.db.execute(query)
        await self.db.commit()
        
        return await self.get_agent(agent_id)

    async def execute_agent(
        self, agent_id: int, execution_params: Dict[str, Any]
    ) -> Dict[str, str]:
        """Start agent execution."""
        # Update agent status to 'doing'
        await self.update_agent_status(agent_id, "doing")
        
        # In a real implementation, this would trigger actual agent execution
        # For now, return a mock response
        return {
            "message": "Agent execution started",
            "status": "doing",
            "execution_id": str(uuid4())
        }

    async def update_agent_status(self, agent_id: int, status: str) -> Agent:
        """Update agent status."""
        from src.models.database_models import AgentStatus
        from fastapi import HTTPException
        
        # Validate status
        try:
            status_enum = AgentStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status: {status}"
            )
        
        query = update(Agent).where(Agent.id == agent_id).values(status=status_enum)
        await self.db.execute(query)
        await self.db.commit()
        
        return await self.get_agent(agent_id)

    async def get_agent_hierarchy(self, root_agent_id: Optional[int] = None) -> List[Agent]:
        """Get agent hierarchy."""
        if root_agent_id:
            # Get hierarchy starting from a specific root
            query = select(Agent).where(Agent.parent_agent_id == root_agent_id)
        else:
            # Get all root agents (no parent)
            query = select(Agent).where(Agent.parent_agent_id.is_(None))
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_child_agents(self, agent_id: int) -> List[Agent]:
        """Get child agents."""
        query = select(Agent).where(Agent.parent_agent_id == agent_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_parent_agent(self, agent_id: int) -> Optional[Agent]:
        """Get parent agent."""
        agent = await self.get_agent(agent_id)
        
        if not agent.parent_agent_id:
            return None
        
        return await self.get_agent(agent.parent_agent_id)
