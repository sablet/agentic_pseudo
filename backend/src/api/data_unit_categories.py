"""Data unit category API endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models.schemas import (
    DataUnitCategory,
    DataUnitCategoryCreate,
    DataUnitCategoryUpdate,
    DataUnit,
    ListResponse,
    ErrorResponse
)
from src.service.data_unit_category_service import DataUnitCategoryService

router = APIRouter(prefix="/api/v1/data-unit-categories", tags=["data-unit-categories"])


@router.post("/")
async def create_data_unit_category(
    category_data: DataUnitCategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new data unit category."""
    try:
        service = DataUnitCategoryService(db)
        db_category = await service.create_category(category_data)
        return db_category
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_data_unit_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    editable_only: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List data unit categories with optional filtering."""
    try:
        service = DataUnitCategoryService(db)
        categories = await service.get_categories(
            skip=skip,
            limit=limit,
            editable_only=editable_only
        )
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{category_id}")
async def get_data_unit_category(
    category_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific data unit category by category_id."""
    try:
        service = DataUnitCategoryService(db)
        db_category = await service.get_category(category_id)
        
        if not db_category:
            raise HTTPException(status_code=404, detail="Data unit category not found")
        
        return db_category
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{category_id}")
async def update_data_unit_category(
    category_id: str,
    category_data: DataUnitCategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a data unit category."""
    try:
        service = DataUnitCategoryService(db)
        db_category = await service.update_category(category_id, category_data)
        
        if not db_category:
            raise HTTPException(status_code=404, detail="Data unit category not found")
        
        return db_category
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{category_id}")
async def delete_data_unit_category(
    category_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a data unit category."""
    try:
        service = DataUnitCategoryService(db)
        success = await service.delete_category(category_id)
        
        if not success:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete category with associated data units or category not found"
            )
        
        return {"message": "Data unit category deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{category_id}/units")
async def get_units_by_category(
    category_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all data units for a specific category."""
    try:
        service = DataUnitCategoryService(db)
        units = await service.get_units_by_category(category_id)
        return units
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/initialize-defaults")
async def initialize_default_categories(
    db: AsyncSession = Depends(get_db)
):
    """Initialize default data unit categories."""
    try:
        service = DataUnitCategoryService(db)
        created_categories = await service.initialize_default_categories()
        return created_categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))