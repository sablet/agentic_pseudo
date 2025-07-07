"""Template API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.service.template_service import TemplateService
from src.models.schemas import Template, TemplateCreate, TemplateUpdate, ListResponse
from src.auth import get_optional_user, TokenData

router = APIRouter(prefix="/templates", tags=["templates"])


@router.post("/", response_model=Template, status_code=201)
async def create_template(
    template_data: TemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Create a new template."""
    service = TemplateService(db)
    return await service.create_template(template_data)


@router.get("/{template_id}", response_model=Template)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Get a template by ID."""
    service = TemplateService(db)
    return await service.get_template(template_id)


@router.get("/", response_model=ListResponse)
async def get_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = Query(None),
    is_public: Optional[bool] = Query(None),
    agent_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Get list of templates with optional filtering."""
    service = TemplateService(db)

    templates = await service.get_templates(
        skip=skip,
        limit=limit,
        category=category,
        is_public=is_public,
        agent_id=agent_id,
    )

    total = await service.count_templates(
        category=category, is_public=is_public, agent_id=agent_id
    )

    return ListResponse(
        items=templates, total=total, page=skip // limit + 1, per_page=limit
    )


@router.put("/{template_id}", response_model=Template)
async def update_template(
    template_id: int,
    template_data: TemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Update a template."""
    service = TemplateService(db)
    return await service.update_template(template_id, template_data)


@router.delete("/{template_id}", status_code=204)
async def delete_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Delete a template."""
    service = TemplateService(db)
    await service.delete_template(template_id)


@router.get("/public/", response_model=ListResponse)
async def get_public_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Get public templates."""
    service = TemplateService(db)

    templates = await service.get_public_templates(
        skip=skip, limit=limit, category=category
    )

    total = await service.count_templates(category=category, is_public=True)

    return ListResponse(
        items=templates, total=total, page=skip // limit + 1, per_page=limit
    )
