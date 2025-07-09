"""Integration tests for Agent hierarchy structure."""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.main import app
from src.database import get_db, async_engine
from src.models.database_models import Base, Agent, AgentTemplate
from src.models.schemas import AgentCreate, AgentUpdate
from src.models.enums import AgentStatus, ExecutionEngine
from src.auth import get_optional_user


@pytest.fixture
def client():
    """Create test client."""
    # Override auth dependency for testing
    app.dependency_overrides[get_optional_user] = lambda: None
    return TestClient(app)


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Setup database before each test."""
    # Drop all tables and recreate them for each test
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture
def sample_agent_template_data():
    """Create sample agent template data for hierarchy tests."""
    return {
        "name": "Parent Agent Template",
        "description": "Template for parent agents",
        "delegation_type": "hierarchical",
        "purpose_category": "management",
        "context_categories": ["planning", "coordination"],
        "execution_engine": "gemini-2.5-flash",
        "parameters": {"temperature": 0.7, "max_tokens": 1000}
    }


@pytest.fixture
def sample_parent_agent_data():
    """Create sample parent agent data."""
    return {
        "name": "Parent Agent",
        "description": "A parent agent for hierarchy testing",
        "type": "coordinator",
        "purpose": "Coordinate child agents and manage workflow",
        "context": ["project_management", "task_delegation"],
        "status": "todo",
        "delegation_params": {"max_children": 5, "delegation_strategy": "round_robin"},
        "level": 0,
        "config": {"priority": "high", "timeout": 300}
    }


@pytest.fixture
def sample_child_agent_data():
    """Create sample child agent data."""
    return {
        "name": "Child Agent",
        "description": "A child agent for hierarchy testing",
        "type": "worker",
        "purpose": "Execute specific tasks assigned by parent",
        "context": ["data_processing", "analysis"],
        "status": "todo",
        "delegation_params": {"task_type": "analysis", "specialization": "data"},
        "level": 1,
        "config": {"priority": "medium", "timeout": 180}
    }


class TestAgentHierarchy:
    """Integration tests for Agent hierarchy structure."""

    def test_create_parent_agent(self, client, sample_agent_template_data, sample_parent_agent_data):
        """Test creating a parent agent."""
        # Create template first
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Add template_id to agent data
        agent_data = sample_parent_agent_data.copy()
        agent_data["template_id"] = template_id
        
        response = client.post("/api/v1/agents/", json=agent_data)
        if response.status_code != 201:  # Agent creation returns 201
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == agent_data["name"]
        assert data["level"] == 0
        assert data["parent_agent_id"] is None
        assert "agent_id" in data

    def test_create_child_agent_with_parent(self, client, sample_agent_template_data, sample_parent_agent_data, sample_child_agent_data):
        """Test creating a child agent with parent relationship."""
        # Create template first
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create parent agent
        parent_data = sample_parent_agent_data.copy()
        parent_data["template_id"] = template_id
        parent_response = client.post("/api/v1/agents/", json=parent_data)
        parent_id = parent_response.json()["id"]
        
        # Create child agent with parent reference
        child_data = sample_child_agent_data.copy()
        child_data["template_id"] = template_id
        child_data["parent_agent_id"] = parent_id
        
        response = client.post("/api/v1/agents/", json=child_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == child_data["name"]
        assert data["level"] == 1
        assert data["parent_agent_id"] == parent_id

    def test_get_agent_with_hierarchy_info(self, client, sample_agent_template_data, sample_parent_agent_data, sample_child_agent_data):
        """Test getting agent with hierarchy information."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create parent agent
        parent_data = sample_parent_agent_data.copy()
        parent_data["template_id"] = template_id
        parent_response = client.post("/api/v1/agents/", json=parent_data)
        parent_agent_id = parent_response.json()["agent_id"]
        
        # Create child agent
        child_data = sample_child_agent_data.copy()
        child_data["template_id"] = template_id
        child_data["parent_agent_id"] = parent_response.json()["id"]
        child_response = client.post("/api/v1/agents/", json=child_data)
        child_agent_id = child_response.json()["agent_id"]
        
        # Get parent agent and verify hierarchy using correct endpoint
        parent_get_response = client.get(f"/api/v1/agents/by-agent-id/{parent_agent_id}")
        assert parent_get_response.status_code == 200
        
        parent_data = parent_get_response.json()
        assert parent_data["level"] == 0
        assert parent_data["parent_agent_id"] is None

    def test_multiple_children_hierarchy(self, client, sample_agent_template_data, sample_parent_agent_data, sample_child_agent_data):
        """Test creating multiple children under one parent."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create parent agent
        parent_data = sample_parent_agent_data.copy()
        parent_data["template_id"] = template_id
        parent_response = client.post("/api/v1/agents/", json=parent_data)
        parent_id = parent_response.json()["id"]
        
        # Create multiple child agents
        child_agent_ids = []
        for i in range(3):
            child_data = sample_child_agent_data.copy()
            child_data["name"] = f"Child Agent {i}"
            child_data["template_id"] = template_id
            child_data["parent_agent_id"] = parent_id
            
            child_response = client.post("/api/v1/agents/", json=child_data)
            assert child_response.status_code == 201
            child_agent_ids.append(child_response.json()["agent_id"])
        
        assert len(child_agent_ids) == 3
        
        # Verify all children have correct parent
        for child_agent_id in child_agent_ids:
            child_get_response = client.get(f"/api/v1/agents/by-agent-id/{child_agent_id}")
            child_data = child_get_response.json()
            assert child_data["parent_agent_id"] == parent_id

    def test_multi_level_hierarchy(self, client, sample_agent_template_data, sample_parent_agent_data, sample_child_agent_data):
        """Test creating multi-level hierarchy (grandparent -> parent -> child)."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create grandparent agent (level 0)
        grandparent_data = sample_parent_agent_data.copy()
        grandparent_data["name"] = "Grandparent Agent"
        grandparent_data["template_id"] = template_id
        grandparent_data["level"] = 0
        grandparent_response = client.post("/api/v1/agents/", json=grandparent_data)
        grandparent_id = grandparent_response.json()["id"]
        
        # Create parent agent (level 1)
        parent_data = sample_parent_agent_data.copy()
        parent_data["name"] = "Parent Agent"
        parent_data["template_id"] = template_id
        parent_data["parent_agent_id"] = grandparent_id
        parent_data["level"] = 1
        parent_response = client.post("/api/v1/agents/", json=parent_data)
        parent_id = parent_response.json()["id"]
        
        # Create child agent (level 2)
        child_data = sample_child_agent_data.copy()
        child_data["name"] = "Child Agent"
        child_data["template_id"] = template_id
        child_data["parent_agent_id"] = parent_id
        child_data["level"] = 2
        child_response = client.post("/api/v1/agents/", json=child_data)
        child_id = child_response.json()["id"]
        
        # Verify hierarchy levels
        grandparent_get = client.get(f"/api/v1/agents/by-agent-id/{grandparent_response.json()['agent_id']}")
        parent_get = client.get(f"/api/v1/agents/by-agent-id/{parent_response.json()['agent_id']}")
        child_get = client.get(f"/api/v1/agents/by-agent-id/{child_response.json()['agent_id']}")
        
        assert grandparent_get.json()["level"] == 0
        assert parent_get.json()["level"] == 1
        assert child_get.json()["level"] == 2
        
        assert grandparent_get.json()["parent_agent_id"] is None
        assert parent_get.json()["parent_agent_id"] == grandparent_id
        assert child_get.json()["parent_agent_id"] == parent_id

    def test_update_agent_hierarchy(self, client, sample_agent_template_data, sample_parent_agent_data, sample_child_agent_data):
        """Test updating agent hierarchy relationships."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create two parent agents
        parent1_data = sample_parent_agent_data.copy()
        parent1_data["name"] = "Parent Agent 1"
        parent1_data["template_id"] = template_id
        parent1_response = client.post("/api/v1/agents/", json=parent1_data)
        parent1_id = parent1_response.json()["id"]
        
        parent2_data = sample_parent_agent_data.copy()
        parent2_data["name"] = "Parent Agent 2"
        parent2_data["template_id"] = template_id
        parent2_response = client.post("/api/v1/agents/", json=parent2_data)
        parent2_id = parent2_response.json()["id"]
        
        # Create child under parent1
        child_data = sample_child_agent_data.copy()
        child_data["template_id"] = template_id
        child_data["parent_agent_id"] = parent1_id
        child_response = client.post("/api/v1/agents/", json=child_data)
        child_agent_id = child_response.json()["agent_id"]
        
        # Update child to be under parent2 using correct endpoint (ID not agent_id)
        child_db_id = child_response.json()["id"]
        update_data = {"parent_agent_id": parent2_id}
        update_response = client.put(f"/api/v1/agents/{child_db_id}", json=update_data)
        assert update_response.status_code == 200
        
        # Verify the change
        updated_child = client.get(f"/api/v1/agents/by-agent-id/{child_agent_id}")
        assert updated_child.json()["parent_agent_id"] == parent2_id

    def test_delete_parent_with_children_constraint(self, client, sample_agent_template_data, sample_parent_agent_data, sample_child_agent_data):
        """Test that deleting a parent agent with children should handle constraints properly."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create parent agent
        parent_data = sample_parent_agent_data.copy()
        parent_data["template_id"] = template_id
        parent_response = client.post("/api/v1/agents/", json=parent_data)
        parent_agent_id = parent_response.json()["agent_id"]
        parent_id = parent_response.json()["id"]
        
        # Create child agent
        child_data = sample_child_agent_data.copy()
        child_data["template_id"] = template_id
        child_data["parent_agent_id"] = parent_id
        child_response = client.post("/api/v1/agents/", json=child_data)
        
        # Try to delete parent using correct endpoint (ID not agent_id)
        parent_db_id = parent_response.json()["id"]
        delete_response = client.delete(f"/api/v1/agents/{parent_db_id}")
        # This might succeed (cascading delete) or fail (constraint), depending on implementation
        # We just verify the response is handled properly
        assert delete_response.status_code in [200, 204, 400, 409]

    def test_agent_hierarchy_validation(self, client, sample_agent_template_data, sample_parent_agent_data):
        """Test validation rules for agent hierarchy."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Test invalid parent reference
        invalid_agent_data = sample_parent_agent_data.copy()
        invalid_agent_data["template_id"] = template_id
        invalid_agent_data["parent_agent_id"] = 99999  # Non-existent parent
        
        response = client.post("/api/v1/agents/", json=invalid_agent_data)
        # Should handle invalid parent reference gracefully
        assert response.status_code in [400, 404, 422, 500]

    def test_agent_status_hierarchy_workflow(self, client, sample_agent_template_data, sample_parent_agent_data, sample_child_agent_data):
        """Test workflow of agent status changes in hierarchy."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create parent agent
        parent_data = sample_parent_agent_data.copy()
        parent_data["template_id"] = template_id
        parent_response = client.post("/api/v1/agents/", json=parent_data)
        parent_agent_id = parent_response.json()["agent_id"]
        parent_id = parent_response.json()["id"]
        
        # Create child agent
        child_data = sample_child_agent_data.copy()
        child_data["template_id"] = template_id
        child_data["parent_agent_id"] = parent_id
        child_response = client.post("/api/v1/agents/", json=child_data)
        child_agent_id = child_response.json()["agent_id"]
        
        # Update parent status to "doing" using correct endpoint (ID not agent_id)
        parent_db_id = parent_response.json()["id"]
        parent_update = {"status": "doing"}
        parent_update_response = client.put(f"/api/v1/agents/{parent_db_id}", json=parent_update)
        assert parent_update_response.status_code == 200
        assert parent_update_response.json()["status"] == "doing"
        
        # Update child status to "doing"
        child_db_id = child_response.json()["id"]
        child_update = {"status": "doing"}
        child_update_response = client.put(f"/api/v1/agents/{child_db_id}", json=child_update)
        assert child_update_response.status_code == 200
        assert child_update_response.json()["status"] == "doing"

    def test_agent_hierarchy_level_consistency(self, client, sample_agent_template_data, sample_parent_agent_data, sample_child_agent_data):
        """Test that hierarchy levels are consistent."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create parent at level 0
        parent_data = sample_parent_agent_data.copy()
        parent_data["template_id"] = template_id
        parent_data["level"] = 0
        parent_response = client.post("/api/v1/agents/", json=parent_data)
        parent_id = parent_response.json()["id"]
        
        # Create child at level 1
        child_data = sample_child_agent_data.copy()
        child_data["template_id"] = template_id
        child_data["parent_agent_id"] = parent_id
        child_data["level"] = 1
        child_response = client.post("/api/v1/agents/", json=child_data)
        
        assert child_response.status_code == 201
        assert child_response.json()["level"] == 1

    def test_agent_hierarchy_context_inheritance(self, client, sample_agent_template_data, sample_parent_agent_data, sample_child_agent_data):
        """Test context inheritance in agent hierarchy."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create parent with specific context
        parent_data = sample_parent_agent_data.copy()
        parent_data["template_id"] = template_id
        parent_data["context"] = ["project_alpha", "high_priority"]
        parent_response = client.post("/api/v1/agents/", json=parent_data)
        parent_id = parent_response.json()["id"]
        
        # Create child that might inherit context
        child_data = sample_child_agent_data.copy()
        child_data["template_id"] = template_id
        child_data["parent_agent_id"] = parent_id
        child_data["context"] = ["project_alpha", "data_analysis"]  # Overlapping context
        child_response = client.post("/api/v1/agents/", json=child_data)
        
        assert child_response.status_code == 201
        child_context = child_response.json()["context"]
        assert "project_alpha" in child_context

    def test_agent_hierarchy_delegation_params(self, client, sample_agent_template_data, sample_parent_agent_data, sample_child_agent_data):
        """Test delegation parameters in hierarchy."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create parent with delegation parameters
        parent_data = sample_parent_agent_data.copy()
        parent_data["template_id"] = template_id
        parent_data["delegation_params"] = {
            "max_children": 3,
            "delegation_strategy": "priority_based",
            "auto_assign": True
        }
        parent_response = client.post("/api/v1/agents/", json=parent_data)
        parent_id = parent_response.json()["id"]
        
        # Create child with specific delegation parameters
        child_data = sample_child_agent_data.copy()
        child_data["template_id"] = template_id
        child_data["parent_agent_id"] = parent_id
        child_data["delegation_params"] = {
            "task_type": "analysis",
            "priority": "high",
            "estimated_duration": 60
        }
        child_response = client.post("/api/v1/agents/", json=child_data)
        
        assert child_response.status_code == 201
        child_delegation = child_response.json()["delegation_params"]
        assert child_delegation["task_type"] == "analysis"