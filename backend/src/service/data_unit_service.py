"""Data unit service layer."""

from typing import List, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import not_found_exception
from src.models.database_models import DataUnit
from src.models.schemas import DataUnitCreate, DataUnitUpdate


class DataUnitService:
    """Service for managing data units."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_data_unit(self, data_unit_data: DataUnitCreate) -> DataUnit:
        """Create a new data unit."""
        db_data_unit = DataUnit(**data_unit_data.model_dump())
        self.db.add(db_data_unit)
        await self.db.commit()
        await self.db.refresh(db_data_unit)
        return db_data_unit

    async def get_data_unit(self, data_unit_id: int) -> DataUnit:
        """Get a data unit by ID."""
        query = select(DataUnit).where(DataUnit.id == data_unit_id)
        result = await self.db.execute(query)
        data_unit = result.scalar_one_or_none()

        if not data_unit:
            raise not_found_exception("DataUnit", data_unit_id)

        return data_unit

    async def get_data_units(
        self,
        skip: int = 0,
        limit: int = 100,
        data_type: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> List[DataUnit]:
        """Get list of data units with optional filtering."""
        query = select(DataUnit)

        if data_type:
            query = query.where(DataUnit.data_type == data_type)
        if is_active is not None:
            query = query.where(DataUnit.is_active == is_active)

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_data_unit(
        self, data_unit_id: int, data_unit_data: DataUnitUpdate
    ) -> DataUnit:
        """Update a data unit."""
        # Check if data unit exists
        await self.get_data_unit(data_unit_id)

        # Update data unit
        update_data = data_unit_data.model_dump(exclude_unset=True)
        if update_data:
            query = (
                update(DataUnit)
                .where(DataUnit.id == data_unit_id)
                .values(**update_data)
            )
            await self.db.execute(query)
            await self.db.commit()

        # Return updated data unit
        return await self.get_data_unit(data_unit_id)

    async def delete_data_unit(self, data_unit_id: int) -> bool:
        """Delete a data unit."""
        # Check if data unit exists
        await self.get_data_unit(data_unit_id)

        # Delete data unit
        query = delete(DataUnit).where(DataUnit.id == data_unit_id)
        await self.db.execute(query)
        await self.db.commit()

        return True

    async def get_active_data_units(
        self, skip: int = 0, limit: int = 100, data_type: Optional[str] = None
    ) -> List[DataUnit]:
        """Get active data units."""
        query = select(DataUnit).where(DataUnit.is_active == True)

        if data_type:
            query = query.where(DataUnit.data_type == data_type)

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def deactivate_data_unit(self, data_unit_id: int) -> DataUnit:
        """Deactivate a data unit."""
        # Check if data unit exists
        await self.get_data_unit(data_unit_id)

        # Deactivate data unit
        query = (
            update(DataUnit).where(DataUnit.id == data_unit_id).values(is_active=False)
        )
        await self.db.execute(query)
        await self.db.commit()

        # Return updated data unit
        return await self.get_data_unit(data_unit_id)

    async def activate_data_unit(self, data_unit_id: int) -> DataUnit:
        """Activate a data unit."""
        # Check if data unit exists
        await self.get_data_unit(data_unit_id)

        # Activate data unit
        query = (
            update(DataUnit).where(DataUnit.id == data_unit_id).values(is_active=True)
        )
        await self.db.execute(query)
        await self.db.commit()

        # Return updated data unit
        return await self.get_data_unit(data_unit_id)

    async def count_data_units(
        self, data_type: Optional[str] = None, is_active: Optional[bool] = None
    ) -> int:
        """Count data units with optional filtering."""
        query = select(DataUnit.id)

        if data_type:
            query = query.where(DataUnit.data_type == data_type)
        if is_active is not None:
            query = query.where(DataUnit.is_active == is_active)

        result = await self.db.execute(query)
        return len(result.scalars().all())
