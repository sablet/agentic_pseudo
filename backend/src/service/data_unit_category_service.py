"""Data unit category service for managing data unit categories."""

from typing import List, Optional
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.models.database_models import DataUnitCategory, DataUnit
from src.models.schemas import (
    DataUnitCategoryCreate,
    DataUnitCategoryUpdate,
    DataUnitCategory as DataUnitCategorySchema
)


class DataUnitCategoryService:
    """Service for managing data unit categories."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_category(self, category_data: DataUnitCategoryCreate) -> DataUnitCategory:
        """Create a new data unit category."""
        db_category = DataUnitCategory(
            category_id=str(uuid4()),
            name=category_data.name,
            editable=category_data.editable
        )
        
        self.db.add(db_category)
        await self.db.commit()
        await self.db.refresh(db_category)
        
        return db_category

    async def get_category(self, category_id: str) -> Optional[DataUnitCategory]:
        """Get a data unit category by category_id."""
        result = await self.db.execute(
            select(DataUnitCategory).filter(DataUnitCategory.category_id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_category_by_id(self, id: int) -> Optional[DataUnitCategory]:
        """Get a data unit category by database id."""
        result = await self.db.execute(
            select(DataUnitCategory).filter(DataUnitCategory.id == id)
        )
        return result.scalar_one_or_none()

    async def get_categories(
        self, 
        skip: int = 0, 
        limit: int = 100,
        editable_only: Optional[bool] = None
    ) -> List[DataUnitCategory]:
        """Get a list of data unit categories with optional filtering."""
        query = select(DataUnitCategory)
        
        if editable_only is not None:
            query = query.filter(DataUnitCategory.editable == editable_only)
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_category(
        self, 
        category_id: str, 
        category_data: DataUnitCategoryUpdate
    ) -> Optional[DataUnitCategory]:
        """Update a data unit category."""
        db_category = await self.get_category(category_id)
        if not db_category:
            return None

        # Update only provided fields
        update_data = category_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)

        await self.db.commit()
        await self.db.refresh(db_category)
        
        return db_category

    async def delete_category(self, category_id: str) -> bool:
        """Delete a data unit category."""
        db_category = await self.get_category(category_id)
        if not db_category:
            return False

        # Check if category has associated data units
        count_result = await self.db.execute(
            select(func.count(DataUnit.id)).filter(DataUnit.category_id == db_category.id)
        )
        data_units_count = count_result.scalar()
        
        if data_units_count > 0:
            # Cannot delete category with associated data units
            return False

        await self.db.delete(db_category)
        await self.db.commit()
        
        return True

    async def get_units_by_category(self, category_id: str) -> List[DataUnit]:
        """Get all data units for a specific category."""
        db_category = await self.get_category(category_id)
        if not db_category:
            return []

        result = await self.db.execute(
            select(DataUnit).filter(DataUnit.category_id == db_category.id)
        )
        return result.scalars().all()

    async def initialize_default_categories(self) -> List[DataUnitCategory]:
        """Initialize default data unit categories."""
        default_categories = [
            "market_analysis_report",
            "competitor_comparison_table",
            "customer_segment_data", 
            "pricing_strategy_document",
            "feature_analysis_matrix",
            "market_share_data",
            "user_survey_results",
            "financial_projections",
            "risk_assessment_report",
            "technical_specifications",
            "compliance_checklist",
            "performance_metrics",
            "user_feedback_summary",
            "integration_requirements",
            "training_materials",
            "business_requirements_document"
        ]
        
        created_categories = []
        for category_name in default_categories:
            # Check if category already exists
            existing_result = await self.db.execute(
                select(DataUnitCategory).filter(DataUnitCategory.name == category_name)
            )
            existing = existing_result.scalar_one_or_none()
            
            if not existing:
                db_category = DataUnitCategory(
                    category_id=str(uuid4()),
                    name=category_name,
                    editable=False  # Default categories are not editable
                )
                self.db.add(db_category)
                created_categories.append(db_category)
        
        if created_categories:
            await self.db.commit()
            for category in created_categories:
                await self.db.refresh(category)
        
        return created_categories