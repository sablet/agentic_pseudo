"""Data unit API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import TokenData, get_optional_user
from src.database import get_db
from src.models.schemas import DataUnit, DataUnitCreate, DataUnitUpdate, ListResponse
from src.service.data_unit_service import DataUnitService

router = APIRouter(prefix="/data-units", tags=["data-units"])


@router.post("/", response_model=DataUnit, status_code=201)
async def create_data_unit(
    data_unit_data: DataUnitCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Create a new data unit."""
    service = DataUnitService(db)
    return await service.create_data_unit(data_unit_data)


@router.get("/{data_unit_id}", response_model=DataUnit)
async def get_data_unit(
    data_unit_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Get a data unit by ID."""
    service = DataUnitService(db)
    return await service.get_data_unit(data_unit_id)


@router.get("/", response_model=ListResponse)
async def get_data_units(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    data_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Get list of data units with optional filtering."""
    service = DataUnitService(db)

    data_units = await service.get_data_units(
        skip=skip, limit=limit, data_type=data_type, is_active=is_active
    )

    total = await service.count_data_units(data_type=data_type, is_active=is_active)

    return ListResponse(
        items=data_units, total=total, page=skip // limit + 1, per_page=limit
    )


@router.put("/{data_unit_id}", response_model=DataUnit)
async def update_data_unit(
    data_unit_id: int,
    data_unit_data: DataUnitUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Update a data unit."""
    service = DataUnitService(db)
    return await service.update_data_unit(data_unit_id, data_unit_data)


@router.delete("/{data_unit_id}", status_code=204)
async def delete_data_unit(
    data_unit_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Delete a data unit."""
    service = DataUnitService(db)
    await service.delete_data_unit(data_unit_id)


@router.get("/active/", response_model=ListResponse)
async def get_active_data_units(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    data_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Get active data units."""
    service = DataUnitService(db)

    data_units = await service.get_active_data_units(
        skip=skip, limit=limit, data_type=data_type
    )

    total = await service.count_data_units(data_type=data_type, is_active=True)

    return ListResponse(
        items=data_units, total=total, page=skip // limit + 1, per_page=limit
    )


@router.patch("/{data_unit_id}/deactivate", response_model=DataUnit)
async def deactivate_data_unit(
    data_unit_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Deactivate a data unit."""
    service = DataUnitService(db)
    return await service.deactivate_data_unit(data_unit_id)


@router.patch("/{data_unit_id}/activate", response_model=DataUnit)
async def activate_data_unit(
    data_unit_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Activate a data unit."""
    service = DataUnitService(db)
    return await service.activate_data_unit(data_unit_id)
