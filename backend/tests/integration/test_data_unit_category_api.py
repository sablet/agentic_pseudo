"""Integration tests for DataUnitCategory API endpoints."""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.main import app
from src.database import get_db, async_engine
from src.models.database_models import Base, DataUnitCategory, DataUnit
from src.models.schemas import DataUnitCategoryCreate, DataUnitCategoryUpdate


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Setup database before each test."""
    # Drop all tables and recreate them for each test
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture
def sample_category_data():
    """Create sample data unit category data."""
    return {
        "name": "Test Category",
        "editable": True
    }


@pytest.fixture
def sample_category_update():
    """Create sample data unit category update data."""
    return {
        "name": "Updated Test Category",
        "editable": False
    }


class TestDataUnitCategoryAPI:
    """Integration tests for DataUnitCategory API endpoints."""

    def test_create_data_unit_category(self, client, sample_category_data):
        """Test creating a new data unit category."""
        response = client.post("/api/v1/data-unit-categories/", json=sample_category_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == sample_category_data["name"]
        assert data["editable"] == sample_category_data["editable"]
        assert "category_id" in data
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_data_unit_category_invalid_data(self, client):
        """Test creating data unit category with invalid data."""
        invalid_data = {
            "name": "",  # Empty name
            "editable": "invalid_boolean"
        }
        
        response = client.post("/api/v1/data-unit-categories/", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_list_data_unit_categories(self, client, sample_category_data):
        """Test listing data unit categories."""
        # Create a category first
        client.post("/api/v1/data-unit-categories/", json=sample_category_data)
        
        response = client.get("/api/v1/data-unit-categories/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        category = data[0]
        assert "category_id" in category
        assert "name" in category
        assert "editable" in category

    def test_list_data_unit_categories_with_pagination(self, client, sample_category_data):
        """Test listing data unit categories with pagination."""
        # Create multiple categories
        for i in range(5):
            category_data = sample_category_data.copy()
            category_data["name"] = f"Category {i}"
            client.post("/api/v1/data-unit-categories/", json=category_data)
        
        response = client.get("/api/v1/data-unit-categories/?skip=2&limit=2")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) <= 2

    def test_list_data_unit_categories_with_filters(self, client, sample_category_data):
        """Test listing data unit categories with filters."""
        # Create editable category
        editable_data = sample_category_data.copy()
        editable_data["editable"] = True
        client.post("/api/v1/data-unit-categories/", json=editable_data)
        
        # Create non-editable category
        non_editable_data = sample_category_data.copy()
        non_editable_data["name"] = "Non-editable Category"
        non_editable_data["editable"] = False
        client.post("/api/v1/data-unit-categories/", json=non_editable_data)
        
        response = client.get("/api/v1/data-unit-categories/?editable_only=true")
        assert response.status_code == 200
        
        data = response.json()
        for category in data:
            assert category["editable"] == True

    def test_get_data_unit_category(self, client, sample_category_data):
        """Test getting a specific data unit category."""
        # Create category first
        create_response = client.post("/api/v1/data-unit-categories/", json=sample_category_data)
        created_category = create_response.json()
        category_id = created_category["category_id"]
        
        response = client.get(f"/api/v1/data-unit-categories/{category_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["category_id"] == category_id
        assert data["name"] == sample_category_data["name"]

    def test_get_data_unit_category_not_found(self, client):
        """Test getting non-existent data unit category."""
        response = client.get("/api/v1/data-unit-categories/nonexistent-id")
        assert response.status_code == 404

    def test_update_data_unit_category(self, client, sample_category_data, sample_category_update):
        """Test updating a data unit category."""
        # Create category first
        create_response = client.post("/api/v1/data-unit-categories/", json=sample_category_data)
        created_category = create_response.json()
        category_id = created_category["category_id"]
        
        response = client.put(f"/api/v1/data-unit-categories/{category_id}", json=sample_category_update)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == sample_category_update["name"]
        assert data["editable"] == sample_category_update["editable"]

    def test_update_data_unit_category_not_found(self, client, sample_category_update):
        """Test updating non-existent data unit category."""
        response = client.put("/api/v1/data-unit-categories/nonexistent-id", json=sample_category_update)
        assert response.status_code == 404

    def test_delete_data_unit_category(self, client, sample_category_data):
        """Test deleting a data unit category."""
        # Create category first
        create_response = client.post("/api/v1/data-unit-categories/", json=sample_category_data)
        created_category = create_response.json()
        category_id = created_category["category_id"]
        
        response = client.delete(f"/api/v1/data-unit-categories/{category_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "deleted successfully" in data["message"]
        
        # Verify category is deleted
        get_response = client.get(f"/api/v1/data-unit-categories/{category_id}")
        assert get_response.status_code == 404

    def test_delete_data_unit_category_not_found(self, client):
        """Test deleting non-existent data unit category."""
        response = client.delete("/api/v1/data-unit-categories/nonexistent-id")
        assert response.status_code == 400  # Cannot delete

    def test_initialize_default_categories(self, client):
        """Test initializing default data unit categories."""
        response = client.post("/api/v1/data-unit-categories/initialize-defaults")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # Should create at least one default category
        
        # Check that default categories are created
        for category in data:
            assert "category_id" in category
            assert "name" in category
            assert "editable" in category

    def test_data_unit_category_database_constraints(self, client, sample_category_data):
        """Test database constraints for data unit categories."""
        # Create category
        create_response = client.post("/api/v1/data-unit-categories/", json=sample_category_data)
        assert create_response.status_code == 200
        
        # Try to create category with same name (should succeed - name not unique)
        response = client.post("/api/v1/data-unit-categories/", json=sample_category_data)
        assert response.status_code == 200

    def test_data_unit_category_editable_validation(self, client, sample_category_data):
        """Test editable field validation."""
        # Test with valid boolean values
        category_data = sample_category_data.copy()
        category_data["editable"] = False
        response = client.post("/api/v1/data-unit-categories/", json=category_data)
        assert response.status_code == 200
        
        # Test with invalid boolean value
        category_data["editable"] = "invalid"
        response = client.post("/api/v1/data-unit-categories/", json=category_data)
        assert response.status_code == 422

    def test_data_unit_category_name_validation(self, client):
        """Test name field validation."""
        # Test with empty name
        invalid_data = {
            "name": "",
            "editable": True
        }
        response = client.post("/api/v1/data-unit-categories/", json=invalid_data)
        assert response.status_code == 422
        
        # Test with very long name
        long_name_data = {
            "name": "x" * 256,  # Exceeds max length
            "editable": True
        }
        response = client.post("/api/v1/data-unit-categories/", json=long_name_data)
        assert response.status_code == 422

    def test_data_unit_category_partial_update(self, client, sample_category_data):
        """Test partial update of data unit category."""
        # Create category first
        create_response = client.post("/api/v1/data-unit-categories/", json=sample_category_data)
        created_category = create_response.json()
        category_id = created_category["category_id"]
        
        # Update only name
        partial_update = {"name": "Partially Updated Category"}
        response = client.put(f"/api/v1/data-unit-categories/{category_id}", json=partial_update)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Partially Updated Category"
        assert data["editable"] == sample_category_data["editable"]  # Should remain unchanged

    def test_data_unit_category_response_format(self, client, sample_category_data):
        """Test that response format is consistent."""
        response = client.post("/api/v1/data-unit-categories/", json=sample_category_data)
        assert response.status_code == 200
        
        data = response.json()
        
        # Check required fields are present
        required_fields = ["id", "category_id", "name", "editable", "created_at", "updated_at"]
        for field in required_fields:
            assert field in data
        
        # Check data types
        assert isinstance(data["id"], int)
        assert isinstance(data["category_id"], str)
        assert isinstance(data["name"], str)
        assert isinstance(data["editable"], bool)
        assert isinstance(data["created_at"], str)
        assert isinstance(data["updated_at"], str)