"""Agent service layer."""

from typing import List, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.exceptions import not_found_exception
from src.models.database_models import Agent
from src.models.schemas import AgentCreate, AgentUpdate


class AgentService:
    """Service for managing agents."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_agent(self, agent_data: AgentCreate) -> Agent:
        """Create a new agent."""
        db_agent = Agent(**agent_data.model_dump())
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
