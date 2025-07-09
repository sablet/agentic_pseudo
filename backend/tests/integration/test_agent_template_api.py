"""Integration tests for AgentTemplate API endpoints."""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.main import app
from src.database import get_db, init_db
from src.models.database_models import AgentTemplate, ExecutionEngine
from src.models.schemas import AgentTemplateCreate, AgentTemplateUpdate


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Setup database before each test."""
    from src.database import async_engine
    from src.models.database_models import Base
    
    # Drop all tables and recreate them for each test
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture
def sample_template_data():
    """Create sample agent template data."""
    return {
        "name": "Test Template",
        "description": "A test template for integration testing",
        "delegation_type": "sequential",
        "purpose_category": "analysis",
        "context_categories": ["document", "code"],
        "execution_engine": "gemini-2.5-flash",
        "parameters": {"temperature": 0.7, "max_tokens": 1000}
    }


@pytest.fixture
def sample_template_update():
    """Create sample agent template update data."""
    return {
        "name": "Updated Test Template",
        "description": "An updated test template",
        "parameters": {"temperature": 0.5, "max_tokens": 2000}
    }


class TestAgentTemplateAPI:
    """Integration tests for AgentTemplate API endpoints."""

    def test_create_agent_template(self, client, sample_template_data):
        """Test creating a new agent template."""
        response = client.post("/api/v1/agent-templates/", json=sample_template_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == sample_template_data["name"]
        assert data["description"] == sample_template_data["description"]
        assert data["delegation_type"] == sample_template_data["delegation_type"]
        assert data["purpose_category"] == sample_template_data["purpose_category"]
        assert data["context_categories"] == sample_template_data["context_categories"]
        assert data["execution_engine"] == sample_template_data["execution_engine"]
        assert data["parameters"] == sample_template_data["parameters"]
        assert data["usage_count"] == 0
        assert "template_id" in data
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_agent_template_invalid_data(self, client):
        """Test creating agent template with invalid data."""
        invalid_data = {
            "name": "",  # Empty name
            "delegation_type": "invalid_type",
            "purpose_category": "analysis"
        }
        
        response = client.post("/api/v1/agent-templates/", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_list_agent_templates(self, client, sample_template_data):
        """Test listing agent templates."""
        # Create a template first
        client.post("/api/v1/agent-templates/", json=sample_template_data)
        
        response = client.get("/api/v1/agent-templates/")
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        template = data[0]
        assert "template_id" in template
        assert "name" in template
        assert "delegation_type" in template
        assert "purpose_category" in template

    def test_list_agent_templates_with_pagination(self, client, sample_template_data):
        """Test listing agent templates with pagination."""
        # Create multiple templates
        for i in range(5):
            template_data = sample_template_data.copy()
            template_data["name"] = f"Template {i}"
            client.post("/api/v1/agent-templates/", json=template_data)
        
        response = client.get("/api/v1/agent-templates/?skip=2&limit=2")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) <= 2

    def test_list_agent_templates_with_filters(self, client, sample_template_data):
        """Test listing agent templates with filters."""
        # Create template with specific category
        template_data = sample_template_data.copy()
        template_data["purpose_category"] = "specific_category"
        client.post("/api/v1/agent-templates/", json=template_data)
        
        response = client.get("/api/v1/agent-templates/?purpose_category=specific_category")
        assert response.status_code == 200
        
        data = response.json()
        for template in data:
            assert template["purpose_category"] == "specific_category"

    def test_get_agent_template(self, client, sample_template_data):
        """Test getting a specific agent template."""
        # Create template first
        create_response = client.post("/api/v1/agent-templates/", json=sample_template_data)
        created_template = create_response.json()
        template_id = created_template["template_id"]
        
        response = client.get(f"/api/v1/agent-templates/{template_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["template_id"] == template_id
        assert data["name"] == sample_template_data["name"]

    def test_get_agent_template_not_found(self, client):
        """Test getting non-existent agent template."""
        response = client.get("/api/v1/agent-templates/nonexistent-id")
        assert response.status_code == 404

    def test_update_agent_template(self, client, sample_template_data, sample_template_update):
        """Test updating an agent template."""
        # Create template first
        create_response = client.post("/api/v1/agent-templates/", json=sample_template_data)
        created_template = create_response.json()
        template_id = created_template["template_id"]
        
        response = client.put(f"/api/v1/agent-templates/{template_id}", json=sample_template_update)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == sample_template_update["name"]
        assert data["description"] == sample_template_update["description"]
        assert data["parameters"] == sample_template_update["parameters"]

    def test_update_agent_template_not_found(self, client, sample_template_update):
        """Test updating non-existent agent template."""
        response = client.put("/api/v1/agent-templates/nonexistent-id", json=sample_template_update)
        assert response.status_code == 404

    def test_delete_agent_template(self, client, sample_template_data):
        """Test deleting an agent template."""
        # Create template first
        create_response = client.post("/api/v1/agent-templates/", json=sample_template_data)
        created_template = create_response.json()
        template_id = created_template["template_id"]
        
        response = client.delete(f"/api/v1/agent-templates/{template_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "deleted successfully" in data["message"]
        
        # Verify template is deleted
        get_response = client.get(f"/api/v1/agent-templates/{template_id}")
        assert get_response.status_code == 404

    def test_delete_agent_template_not_found(self, client):
        """Test deleting non-existent agent template."""
        response = client.delete("/api/v1/agent-templates/nonexistent-id")
        assert response.status_code == 404

    def test_increment_template_usage(self, client, sample_template_data):
        """Test incrementing template usage count."""
        # Create template first
        create_response = client.post("/api/v1/agent-templates/", json=sample_template_data)
        created_template = create_response.json()
        template_id = created_template["template_id"]
        
        # Increment usage
        response = client.post(f"/api/v1/agent-templates/{template_id}/increment-usage")
        assert response.status_code == 200
        
        data = response.json()
        assert data["usage_count"] == 1
        
        # Increment again
        response = client.post(f"/api/v1/agent-templates/{template_id}/increment-usage")
        assert response.status_code == 200
        
        data = response.json()
        assert data["usage_count"] == 2

    def test_increment_template_usage_not_found(self, client):
        """Test incrementing usage for non-existent template."""
        response = client.post("/api/v1/agent-templates/nonexistent-id/increment-usage")
        assert response.status_code == 404

    def test_get_popular_templates(self, client, sample_template_data):
        """Test getting popular templates."""
        # Create multiple templates with different usage counts
        template_ids = []
        for i in range(3):
            template_data = sample_template_data.copy()
            template_data["name"] = f"Template {i}"
            create_response = client.post("/api/v1/agent-templates/", json=template_data)
            template_ids.append(create_response.json()["template_id"])
        
        # Increment usage for different templates
        for i, template_id in enumerate(template_ids):
            for _ in range(i + 1):  # Template 0: 1 use, Template 1: 2 uses, Template 2: 3 uses
                client.post(f"/api/v1/agent-templates/{template_id}/increment-usage")
        
        response = client.get("/api/v1/agent-templates/popular")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 3
        
        # Verify sorted by usage count (descending)
        usage_counts = [template["usage_count"] for template in data]
        assert usage_counts == sorted(usage_counts, reverse=True)

    def test_get_templates_by_category(self, client, sample_template_data):
        """Test getting templates by category."""
        # Create template with specific category
        template_data = sample_template_data.copy()
        template_data["purpose_category"] = "test_category"
        client.post("/api/v1/agent-templates/", json=template_data)
        
        response = client.get("/api/v1/agent-templates/category/test_category")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 1
        
        for template in data:
            assert template["purpose_category"] == "test_category"

    def test_get_templates_by_nonexistent_category(self, client):
        """Test getting templates by non-existent category."""
        response = client.get("/api/v1/agent-templates/category/nonexistent_category")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 0

    def test_agent_template_database_constraints(self, client, sample_template_data):
        """Test database constraints for agent templates."""
        # Create template
        create_response = client.post("/api/v1/agent-templates/", json=sample_template_data)
        assert create_response.status_code == 200
        
        # Try to create template with same name (should succeed - name not unique)
        response = client.post("/api/v1/agent-templates/", json=sample_template_data)
        assert response.status_code == 200

    def test_agent_template_execution_engine_validation(self, client, sample_template_data):
        """Test execution engine validation."""
        # Test with valid execution engine
        template_data = sample_template_data.copy()
        template_data["execution_engine"] = "claude-3.5-sonnet"
        response = client.post("/api/v1/agent-templates/", json=template_data)
        assert response.status_code == 200
        
        # Test with invalid execution engine
        template_data["execution_engine"] = "invalid-engine"
        response = client.post("/api/v1/agent-templates/", json=template_data)
        assert response.status_code == 422

    def test_agent_template_complex_parameters(self, client, sample_template_data):
        """Test agent template with complex parameters."""
        template_data = sample_template_data.copy()
        template_data["parameters"] = {
            "temperature": 0.8,
            "max_tokens": 2000,
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1,
            "stop_sequences": ["END", "STOP"],
            "system_instructions": "You are a helpful assistant",
            "custom_config": {
                "use_context": True,
                "context_window": 4000,
                "memory_enabled": False
            }
        }
        
        response = client.post("/api/v1/agent-templates/", json=template_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["parameters"] == template_data["parameters"]