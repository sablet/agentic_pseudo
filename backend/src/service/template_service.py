"""Template service layer."""

from typing import List, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.exceptions import not_found_exception
from src.models.database_models import Template
from src.models.schemas import TemplateCreate, TemplateUpdate


class TemplateService:
    """Service for managing templates."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_template(self, template_data: TemplateCreate) -> Template:
        """Create a new template."""
        db_template = Template(**template_data.model_dump())
        self.db.add(db_template)
        await self.db.commit()
        await self.db.refresh(db_template)
        return db_template

    async def get_template(self, template_id: int) -> Template:
        """Get a template by ID."""
        query = select(Template).where(Template.id == template_id)
        result = await self.db.execute(query)
        template = result.scalar_one_or_none()

        if not template:
            raise not_found_exception("Template", template_id)

        return template

    async def get_templates(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        is_public: Optional[bool] = None,
        agent_id: Optional[int] = None,
    ) -> List[Template]:
        """Get list of templates with optional filtering."""
        query = select(Template)

        if category:
            query = query.where(Template.category == category)
        if is_public is not None:
            query = query.where(Template.is_public == is_public)
        if agent_id:
            query = query.where(Template.agent_id == agent_id)

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_template(
        self, template_id: int, template_data: TemplateUpdate
    ) -> Template:
        """Update a template."""
        # Check if template exists
        await self.get_template(template_id)

        # Update template
        update_data = template_data.model_dump(exclude_unset=True)
        if update_data:
            query = (
                update(Template).where(Template.id == template_id).values(**update_data)
            )
            await self.db.execute(query)
            await self.db.commit()

        # Return updated template
        return await self.get_template(template_id)

    async def delete_template(self, template_id: int) -> bool:
        """Delete a template."""
        # Check if template exists
        await self.get_template(template_id)

        # Delete template
        query = delete(Template).where(Template.id == template_id)
        await self.db.execute(query)
        await self.db.commit()

        return True

    async def get_template_with_agent(self, template_id: int) -> Template:
        """Get a template with its agent."""
        query = (
            select(Template)
            .options(selectinload(Template.agent))
            .where(Template.id == template_id)
        )

        result = await self.db.execute(query)
        template = result.scalar_one_or_none()

        if not template:
            raise not_found_exception("Template", template_id)

        return template

    async def get_public_templates(
        self, skip: int = 0, limit: int = 100, category: Optional[str] = None
    ) -> List[Template]:
        """Get public templates."""
        query = select(Template).where(Template.is_public == True)

        if category:
            query = query.where(Template.category == category)

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def count_templates(
        self,
        category: Optional[str] = None,
        is_public: Optional[bool] = None,
        agent_id: Optional[int] = None,
    ) -> int:
        """Count templates with optional filtering."""
        query = select(Template.id)

        if category:
            query = query.where(Template.category == category)
        if is_public is not None:
            query = query.where(Template.is_public == is_public)
        if agent_id:
            query = query.where(Template.agent_id == agent_id)

        result = await self.db.execute(query)
        return len(result.scalars().all())
