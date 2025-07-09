"""Agent template API endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models.schemas import (
    AgentTemplate,
    AgentTemplateCreate,
    AgentTemplateUpdate,
    ListResponse,
    ErrorResponse
)
from src.service.agent_template_service import AgentTemplateService

router = APIRouter(prefix="/api/v1/agent-templates", tags=["agent-templates"])


@router.post("/", response_model=AgentTemplate)
async def create_agent_template(
    template_data: AgentTemplateCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new agent template."""
    try:
        service = AgentTemplateService(db)
        db_template = await service.create_template(template_data)
        return db_template
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_agent_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    purpose_category: Optional[str] = Query(None),
    delegation_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List agent templates with optional filtering."""
    try:
        service = AgentTemplateService(db)
        templates = await service.get_templates(
            skip=skip,
            limit=limit,
            purpose_category=purpose_category,
            delegation_type=delegation_type
        )
        # Convert to dict to avoid Pydantic enum conversion issues
        return [
            {
                "id": t.id,
                "template_id": t.template_id,
                "name": t.name,
                "description": t.description,
                "delegation_type": t.delegation_type,
                "purpose_category": t.purpose_category,
                "context_categories": t.context_categories,
                "execution_engine": t.execution_engine.value if hasattr(t.execution_engine, 'value') else t.execution_engine,
                "parameters": t.parameters,
                "usage_count": t.usage_count,
                "created_at": t.created_at.isoformat(),
                "updated_at": t.updated_at.isoformat()
            }
            for t in templates
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/popular")
async def get_popular_templates(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get popular templates ordered by usage count."""
    try:
        service = AgentTemplateService(db)
        templates = await service.get_popular_templates(limit=limit)
        # Convert to dict to avoid Pydantic enum conversion issues
        return [
            {
                "id": t.id,
                "template_id": t.template_id,
                "name": t.name,
                "description": t.description,
                "delegation_type": t.delegation_type,
                "purpose_category": t.purpose_category,
                "context_categories": t.context_categories,
                "execution_engine": t.execution_engine.value if hasattr(t.execution_engine, 'value') else t.execution_engine,
                "parameters": t.parameters,
                "usage_count": t.usage_count,
                "created_at": t.created_at.isoformat(),
                "updated_at": t.updated_at.isoformat()
            }
            for t in templates
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{template_id}", response_model=AgentTemplate)
async def get_agent_template(
    template_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific agent template by template_id."""
    try:
        service = AgentTemplateService(db)
        db_template = await service.get_template(template_id)
        
        if not db_template:
            raise HTTPException(status_code=404, detail="Agent template not found")
        
        return db_template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{template_id}", response_model=AgentTemplate)
async def update_agent_template(
    template_id: str,
    template_data: AgentTemplateUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an agent template."""
    try:
        service = AgentTemplateService(db)
        db_template = await service.update_template(template_id, template_data)
        
        if not db_template:
            raise HTTPException(status_code=404, detail="Agent template not found")
        
        return db_template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{template_id}")
async def delete_agent_template(
    template_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete an agent template."""
    try:
        service = AgentTemplateService(db)
        success = await service.delete_template(template_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Agent template not found")
        
        return {"message": "Agent template deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{template_id}/increment-usage", response_model=AgentTemplate)
async def increment_template_usage(
    template_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Increment usage count for a template."""
    try:
        service = AgentTemplateService(db)
        db_template = await service.increment_usage(template_id)
        
        if not db_template:
            raise HTTPException(status_code=404, detail="Agent template not found")
        
        return db_template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/category/{category}")
async def get_templates_by_category(
    category: str,
    db: AsyncSession = Depends(get_db)
):
    """Get templates by purpose category."""
    try:
        service = AgentTemplateService(db)
        templates = await service.get_templates_by_category(category)
        # Convert to dict to avoid Pydantic enum conversion issues
        return [
            {
                "id": t.id,
                "template_id": t.template_id,
                "name": t.name,
                "description": t.description,
                "delegation_type": t.delegation_type,
                "purpose_category": t.purpose_category,
                "context_categories": t.context_categories,
                "execution_engine": t.execution_engine.value if hasattr(t.execution_engine, 'value') else t.execution_engine,
                "parameters": t.parameters,
                "usage_count": t.usage_count,
                "created_at": t.created_at.isoformat(),
                "updated_at": t.updated_at.isoformat()
            }
            for t in templates
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))