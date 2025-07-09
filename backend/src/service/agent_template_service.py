"""Agent template service for managing agent templates."""

from typing import List, Optional
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.database_models import AgentTemplate
from src.models.schemas import (
    AgentTemplateCreate,
    AgentTemplateUpdate,
    AgentTemplate as AgentTemplateSchema
)


class AgentTemplateService:
    """Service for managing agent templates."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_template(self, template_data: AgentTemplateCreate) -> AgentTemplate:
        """Create a new agent template."""
        db_template = AgentTemplate(
            template_id=str(uuid4()),
            name=template_data.name,
            description=template_data.description,
            delegation_type=template_data.delegation_type,
            purpose_category=template_data.purpose_category,
            context_categories=template_data.context_categories,
            execution_engine=template_data.execution_engine,
            parameters=template_data.parameters,
            usage_count=0
        )
        
        self.db.add(db_template)
        await self.db.commit()
        await self.db.refresh(db_template)
        
        return db_template

    async def get_template(self, template_id: str) -> Optional[AgentTemplate]:
        """Get an agent template by template_id."""
        result = await self.db.execute(
            select(AgentTemplate).filter(AgentTemplate.template_id == template_id)
        )
        return result.scalar_one_or_none()

    async def get_template_by_id(self, id: int) -> Optional[AgentTemplate]:
        """Get an agent template by database id."""
        result = await self.db.execute(
            select(AgentTemplate).filter(AgentTemplate.id == id)
        )
        return result.scalar_one_or_none()

    async def get_templates(
        self, 
        skip: int = 0, 
        limit: int = 100,
        purpose_category: Optional[str] = None,
        delegation_type: Optional[str] = None
    ) -> List[AgentTemplate]:
        """Get a list of agent templates with optional filtering."""
        query = select(AgentTemplate)
        
        if purpose_category:
            query = query.filter(AgentTemplate.purpose_category == purpose_category)
        
        if delegation_type:
            query = query.filter(AgentTemplate.delegation_type == delegation_type)
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_template(
        self, 
        template_id: str, 
        template_data: AgentTemplateUpdate
    ) -> Optional[AgentTemplate]:
        """Update an agent template."""
        db_template = await self.get_template(template_id)
        if not db_template:
            return None

        # Update only provided fields
        update_data = template_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_template, field, value)

        await self.db.commit()
        await self.db.refresh(db_template)
        
        return db_template

    async def delete_template(self, template_id: str) -> bool:
        """Delete an agent template."""
        db_template = await self.get_template(template_id)
        if not db_template:
            return False

        await self.db.delete(db_template)
        await self.db.commit()
        
        return True

    async def increment_usage(self, template_id: str) -> Optional[AgentTemplate]:
        """Increment usage count for a template."""
        db_template = await self.get_template(template_id)
        if not db_template:
            return None

        db_template.usage_count += 1
        await self.db.commit()
        await self.db.refresh(db_template)
        
        return db_template

    async def get_templates_by_category(self, category: str) -> List[AgentTemplate]:
        """Get templates by purpose category."""
        result = await self.db.execute(
            select(AgentTemplate).filter(AgentTemplate.purpose_category == category)
        )
        return result.scalars().all()

    async def get_popular_templates(self, limit: int = 10) -> List[AgentTemplate]:
        """Get templates ordered by usage count."""
        result = await self.db.execute(
            select(AgentTemplate).order_by(AgentTemplate.usage_count.desc()).limit(limit)
        )
        return result.scalars().all()