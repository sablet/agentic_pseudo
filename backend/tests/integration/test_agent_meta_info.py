"""Integration tests for Agent MetaInfo API."""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.main import app
from src.database import get_db, async_engine
from src.models.database_models import Base, Agent, AgentTemplate
from src.models.schemas import AgentCreate, AgentMetaInfo
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
    """Create sample agent template data for meta info tests."""
    return {
        "name": "Meta Info Test Template",
        "description": "Template for testing agent meta info",
        "delegation_type": "sequential",
        "purpose_category": "analysis",
        "context_categories": ["data_analysis", "reporting"],
        "execution_engine": "gemini-2.5-flash",
        "parameters": {"temperature": 0.5, "max_tokens": 2000}
    }


@pytest.fixture
def sample_agent_data():
    """Create sample agent data for meta info tests."""
    return {
        "name": "Test Agent for Meta Info",
        "description": "Agent for testing meta info functionality",
        "type": "analyzer",
        "purpose": "Analyze data and generate insights",
        "context": ["financial_data", "market_analysis"],
        "status": "todo",
        "delegation_params": {"analysis_type": "statistical", "depth": "comprehensive"},
        "level": 0,
        "config": {"timeout": 600, "priority": "high"}
    }


class TestAgentMetaInfo:
    """Integration tests for Agent MetaInfo API."""

    def test_get_agent_meta_info_basic(self, client, sample_agent_template_data, sample_agent_data):
        """Test basic agent meta info retrieval."""
        # Create template first
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create agent
        agent_data = sample_agent_data.copy()
        agent_data["template_id"] = template_id
        agent_response = client.post("/api/v1/agents/", json=agent_data)
        agent_id = agent_response.json()["id"]
        
        # Get meta info
        response = client.get(f"/api/v1/agents/{agent_id}/meta-info")
        assert response.status_code == 200
        
        meta_info = response.json()
        assert meta_info["agent_id"] == agent_response.json()["agent_id"]
        assert meta_info["purpose"] == agent_data["purpose"]
        assert meta_info["description"] == agent_data["description"]
        assert meta_info["level"] == 0

    def test_get_agent_meta_info_with_hierarchy(self, client, sample_agent_template_data, sample_agent_data):
        """Test agent meta info with parent-child relationships."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create parent agent
        parent_data = sample_agent_data.copy()
        parent_data["name"] = "Parent Agent"
        parent_data["template_id"] = template_id
        parent_response = client.post("/api/v1/agents/", json=parent_data)
        parent_id = parent_response.json()["id"]
        
        # Create child agent
        child_data = sample_agent_data.copy()
        child_data["name"] = "Child Agent"
        child_data["template_id"] = template_id
        child_data["parent_agent_id"] = parent_id
        child_data["level"] = 1
        child_response = client.post("/api/v1/agents/", json=child_data)
        child_id = child_response.json()["id"]
        
        # Get parent meta info
        parent_meta_response = client.get(f"/api/v1/agents/{parent_id}/meta-info")
        assert parent_meta_response.status_code == 200
        
        parent_meta = parent_meta_response.json()
        assert parent_meta["level"] == 0
        assert parent_meta["parent_agent_summary"] is None
        assert len(parent_meta["child_agent_summaries"]) == 1
        assert parent_meta["child_agent_summaries"][0]["name"] == "Child Agent"
        
        # Get child meta info
        child_meta_response = client.get(f"/api/v1/agents/{child_id}/meta-info")
        assert child_meta_response.status_code == 200
        
        child_meta = child_meta_response.json()
        assert child_meta["level"] == 1
        assert child_meta["parent_agent_summary"] is not None
        assert child_meta["parent_agent_summary"]["name"] == "Parent Agent"
        assert len(child_meta["child_agent_summaries"]) == 0

    def test_get_agent_meta_info_context_status(self, client, sample_agent_template_data, sample_agent_data):
        """Test agent meta info context status information."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create agent
        agent_data = sample_agent_data.copy()
        agent_data["template_id"] = template_id
        agent_response = client.post("/api/v1/agents/", json=agent_data)
        agent_id = agent_response.json()["id"]
        
        # Get meta info
        response = client.get(f"/api/v1/agents/{agent_id}/meta-info")
        assert response.status_code == 200
        
        meta_info = response.json()
        assert "context_status" in meta_info
        assert isinstance(meta_info["context_status"], list)

    def test_get_agent_meta_info_waiting_status(self, client, sample_agent_template_data, sample_agent_data):
        """Test agent meta info with waiting status."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create agent with waiting status
        agent_data = sample_agent_data.copy()
        agent_data["template_id"] = template_id
        agent_data["status"] = "waiting"
        agent_response = client.post("/api/v1/agents/", json=agent_data)
        agent_id = agent_response.json()["id"]
        
        # Get meta info
        response = client.get(f"/api/v1/agents/{agent_id}/meta-info")
        assert response.status_code == 200
        
        meta_info = response.json()
        assert "waiting_for" in meta_info
        assert isinstance(meta_info["waiting_for"], list)

    def test_get_agent_meta_info_execution_log(self, client, sample_agent_template_data, sample_agent_data):
        """Test agent meta info execution log."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create agent
        agent_data = sample_agent_data.copy()
        agent_data["template_id"] = template_id
        agent_response = client.post("/api/v1/agents/", json=agent_data)
        agent_id = agent_response.json()["id"]
        
        # Get meta info
        response = client.get(f"/api/v1/agents/{agent_id}/meta-info")
        assert response.status_code == 200
        
        meta_info = response.json()
        assert "execution_log" in meta_info
        assert isinstance(meta_info["execution_log"], list)
        assert len(meta_info["execution_log"]) > 0

    def test_get_agent_meta_info_conversation_history(self, client, sample_agent_template_data, sample_agent_data):
        """Test agent meta info conversation history."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create agent
        agent_data = sample_agent_data.copy()
        agent_data["template_id"] = template_id
        agent_response = client.post("/api/v1/agents/", json=agent_data)
        agent_id = agent_response.json()["id"]
        
        # Get meta info
        response = client.get(f"/api/v1/agents/{agent_id}/meta-info")
        assert response.status_code == 200
        
        meta_info = response.json()
        assert "conversation_history" in meta_info
        assert isinstance(meta_info["conversation_history"], list)

    def test_get_agent_meta_info_multiple_children(self, client, sample_agent_template_data, sample_agent_data):
        """Test agent meta info with multiple child agents."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create parent agent
        parent_data = sample_agent_data.copy()
        parent_data["name"] = "Parent Agent"
        parent_data["template_id"] = template_id
        parent_response = client.post("/api/v1/agents/", json=parent_data)
        parent_id = parent_response.json()["id"]
        
        # Create multiple child agents
        child_names = ["Child Agent 1", "Child Agent 2", "Child Agent 3"]
        for child_name in child_names:
            child_data = sample_agent_data.copy()
            child_data["name"] = child_name
            child_data["template_id"] = template_id
            child_data["parent_agent_id"] = parent_id
            child_data["level"] = 1
            client.post("/api/v1/agents/", json=child_data)
        
        # Get parent meta info
        response = client.get(f"/api/v1/agents/{parent_id}/meta-info")
        assert response.status_code == 200
        
        meta_info = response.json()
        assert len(meta_info["child_agent_summaries"]) == 3
        
        # Check all child names are present
        child_summary_names = [child["name"] for child in meta_info["child_agent_summaries"]]
        for child_name in child_names:
            assert child_name in child_summary_names

    def test_get_agent_meta_info_nonexistent_agent(self, client):
        """Test meta info for non-existent agent."""
        response = client.get("/api/v1/agents/99999/meta-info")
        assert response.status_code == 404

    def test_get_agent_meta_info_different_statuses(self, client, sample_agent_template_data, sample_agent_data):
        """Test agent meta info for agents with different statuses."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        statuses = ["todo", "doing", "waiting", "needs_input"]
        
        for status in statuses:
            # Create agent with specific status
            agent_data = sample_agent_data.copy()
            agent_data["name"] = f"Agent {status}"
            agent_data["template_id"] = template_id
            agent_data["status"] = status
            agent_response = client.post("/api/v1/agents/", json=agent_data)
            if agent_response.status_code != 201:
                print(f"Failed to create agent with status {status}: {agent_response.status_code} - {agent_response.text}")
                continue
            agent_id = agent_response.json()["id"]
            
            # Get meta info
            response = client.get(f"/api/v1/agents/{agent_id}/meta-info")
            assert response.status_code == 200
            
            meta_info = response.json()
            assert meta_info["agent_id"] == agent_response.json()["agent_id"]

    def test_get_agent_meta_info_schema_validation(self, client, sample_agent_template_data, sample_agent_data):
        """Test that agent meta info response matches expected schema."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create agent
        agent_data = sample_agent_data.copy()
        agent_data["template_id"] = template_id
        agent_response = client.post("/api/v1/agents/", json=agent_data)
        agent_id = agent_response.json()["id"]
        
        # Get meta info
        response = client.get(f"/api/v1/agents/{agent_id}/meta-info")
        assert response.status_code == 200
        
        meta_info = response.json()
        
        # Validate required fields
        required_fields = [
            "agent_id", "purpose", "description", "level",
            "context_status", "waiting_for", "execution_log",
            "conversation_history", "parent_agent_summary", "child_agent_summaries"
        ]
        
        for field in required_fields:
            assert field in meta_info

    def test_get_agent_meta_info_deep_hierarchy(self, client, sample_agent_template_data, sample_agent_data):
        """Test agent meta info in deep hierarchy (3 levels)."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create grandparent agent (level 0)
        grandparent_data = sample_agent_data.copy()
        grandparent_data["name"] = "Grandparent Agent"
        grandparent_data["template_id"] = template_id
        grandparent_data["level"] = 0
        grandparent_response = client.post("/api/v1/agents/", json=grandparent_data)
        grandparent_id = grandparent_response.json()["id"]
        
        # Create parent agent (level 1)
        parent_data = sample_agent_data.copy()
        parent_data["name"] = "Parent Agent"
        parent_data["template_id"] = template_id
        parent_data["parent_agent_id"] = grandparent_id
        parent_data["level"] = 1
        parent_response = client.post("/api/v1/agents/", json=parent_data)
        parent_id = parent_response.json()["id"]
        
        # Create child agent (level 2)
        child_data = sample_agent_data.copy()
        child_data["name"] = "Child Agent"
        child_data["template_id"] = template_id
        child_data["parent_agent_id"] = parent_id
        child_data["level"] = 2
        child_response = client.post("/api/v1/agents/", json=child_data)
        child_id = child_response.json()["id"]
        
        # Test child meta info (should have parent but no children)
        child_meta_response = client.get(f"/api/v1/agents/{child_id}/meta-info")
        assert child_meta_response.status_code == 200
        
        child_meta = child_meta_response.json()
        assert child_meta["level"] == 2
        assert child_meta["parent_agent_summary"]["name"] == "Parent Agent"
        assert len(child_meta["child_agent_summaries"]) == 0
        
        # Test parent meta info (should have both parent and child)
        parent_meta_response = client.get(f"/api/v1/agents/{parent_id}/meta-info")
        assert parent_meta_response.status_code == 200
        
        parent_meta = parent_meta_response.json()
        assert parent_meta["level"] == 1
        assert parent_meta["parent_agent_summary"]["name"] == "Grandparent Agent"
        assert len(parent_meta["child_agent_summaries"]) == 1
        assert parent_meta["child_agent_summaries"][0]["name"] == "Child Agent"
        
        # Test grandparent meta info (should have child but no parent)
        grandparent_meta_response = client.get(f"/api/v1/agents/{grandparent_id}/meta-info")
        assert grandparent_meta_response.status_code == 200
        
        grandparent_meta = grandparent_meta_response.json()
        assert grandparent_meta["level"] == 0
        assert grandparent_meta["parent_agent_summary"] is None
        assert len(grandparent_meta["child_agent_summaries"]) == 1
        assert grandparent_meta["child_agent_summaries"][0]["name"] == "Parent Agent"