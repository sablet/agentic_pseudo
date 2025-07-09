"""Integration tests for Agent execution functionality."""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.main import app
from src.database import get_db, async_engine
from src.models.database_models import Base, Agent, AgentTemplate
from src.models.schemas import AgentCreate
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
    """Create sample agent template data for execution tests."""
    return {
        "name": "Execution Test Template",
        "description": "Template for testing agent execution",
        "delegation_type": "direct",
        "purpose_category": "execution",
        "context_categories": ["task_execution", "workflow"],
        "execution_engine": "gemini-2.5-flash",
        "parameters": {"temperature": 0.3, "max_tokens": 1500}
    }


@pytest.fixture
def sample_agent_data():
    """Create sample agent data for execution tests."""
    return {
        "name": "Test Execution Agent",
        "description": "Agent for testing execution functionality",
        "type": "executor",
        "purpose": "Execute assigned tasks and workflows",
        "context": ["task_management", "execution_flow"],
        "status": "todo",
        "delegation_params": {"execution_mode": "sequential", "retry_count": 3},
        "level": 0,
        "config": {"timeout": 300, "priority": "normal"}
    }


class TestAgentExecution:
    """Integration tests for Agent execution functionality."""

    def test_execute_agent_basic(self, client, sample_agent_template_data, sample_agent_data):
        """Test basic agent execution."""
        # Create template first
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create agent
        agent_data = sample_agent_data.copy()
        agent_data["template_id"] = template_id
        agent_response = client.post("/api/v1/agents/", json=agent_data)
        agent_id = agent_response.json()["id"]
        
        # Execute agent
        execution_response = client.post(f"/api/v1/agents/{agent_id}/execute")
        assert execution_response.status_code == 200
        
        execution_result = execution_response.json()
        assert "message" in execution_result
        assert "status" in execution_result
        assert "execution_id" in execution_result
        assert execution_result["status"] == "doing"

    def test_execute_agent_with_parameters(self, client, sample_agent_template_data, sample_agent_data):
        """Test agent execution with custom parameters."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create agent
        agent_data = sample_agent_data.copy()
        agent_data["template_id"] = template_id
        agent_response = client.post("/api/v1/agents/", json=agent_data)
        agent_id = agent_response.json()["id"]
        
        # Execute agent with custom parameters
        execution_params = {
            "task_description": "Analyze market data",
            "priority": "high",
            "timeout": 600
        }
        execution_response = client.post(
            f"/api/v1/agents/{agent_id}/execute", 
            json=execution_params
        )
        assert execution_response.status_code == 200
        
        execution_result = execution_response.json()
        assert execution_result["status"] == "doing"

    def test_execute_nonexistent_agent(self, client):
        """Test execution of non-existent agent."""
        execution_response = client.post("/api/v1/agents/99999/execute")
        assert execution_response.status_code == 404

    def test_agent_status_after_execution(self, client, sample_agent_template_data, sample_agent_data):
        """Test that agent status changes to 'doing' after execution."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create agent
        agent_data = sample_agent_data.copy()
        agent_data["template_id"] = template_id
        agent_response = client.post("/api/v1/agents/", json=agent_data)
        agent_id = agent_response.json()["id"]
        agent_db_id = agent_response.json()["agent_id"]
        
        # Verify initial status
        initial_get_response = client.get(f"/api/v1/agents/by-agent-id/{agent_db_id}")
        assert initial_get_response.json()["status"] == "todo"
        
        # Execute agent
        execution_response = client.post(f"/api/v1/agents/{agent_id}/execute")
        assert execution_response.status_code == 200
        
        # Verify status changed to 'doing'
        updated_get_response = client.get(f"/api/v1/agents/by-agent-id/{agent_db_id}")
        assert updated_get_response.json()["status"] == "doing"

    def test_update_agent_status_manually(self, client, sample_agent_template_data, sample_agent_data):
        """Test manual agent status updates."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create agent
        agent_data = sample_agent_data.copy()
        agent_data["template_id"] = template_id
        agent_response = client.post("/api/v1/agents/", json=agent_data)
        agent_id = agent_response.json()["id"]
        
        # Test status updates
        statuses_to_test = ["doing", "waiting", "needs_input", "todo"]
        
        for status in statuses_to_test:
            status_update_response = client.put(
                f"/api/v1/agents/{agent_id}/status",
                json={"status": status}
            )
            assert status_update_response.status_code == 200
            assert status_update_response.json()["status"] == status

    def test_update_agent_status_invalid(self, client, sample_agent_template_data, sample_agent_data):
        """Test updating agent status with invalid values."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create agent
        agent_data = sample_agent_data.copy()
        agent_data["template_id"] = template_id
        agent_response = client.post("/api/v1/agents/", json=agent_data)
        agent_id = agent_response.json()["id"]
        
        # Test invalid status
        invalid_status_response = client.put(
            f"/api/v1/agents/{agent_id}/status",
            json={"status": "invalid_status"}
        )
        assert invalid_status_response.status_code == 400

    def test_update_agent_status_missing_field(self, client, sample_agent_template_data, sample_agent_data):
        """Test updating agent status without status field."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create agent
        agent_data = sample_agent_data.copy()
        agent_data["template_id"] = template_id
        agent_response = client.post("/api/v1/agents/", json=agent_data)
        agent_id = agent_response.json()["id"]
        
        # Test missing status field
        missing_field_response = client.put(
            f"/api/v1/agents/{agent_id}/status",
            json={"other_field": "value"}
        )
        assert missing_field_response.status_code == 400

    def test_update_agent_context(self, client, sample_agent_template_data, sample_agent_data):
        """Test updating agent context."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create agent
        agent_data = sample_agent_data.copy()
        agent_data["template_id"] = template_id
        agent_response = client.post("/api/v1/agents/", json=agent_data)
        agent_id = agent_response.json()["id"]
        
        # Update context
        new_context = {
            "new_context": ["additional_data", "updated_requirements"]
        }
        context_update_response = client.put(
            f"/api/v1/agents/{agent_id}/context",
            json=new_context
        )
        assert context_update_response.status_code == 200
        
        updated_agent = context_update_response.json()
        expected_context = agent_data["context"] + new_context["new_context"]
        assert updated_agent["context"] == expected_context

    def test_execute_agent_hierarchy_parent(self, client, sample_agent_template_data, sample_agent_data):
        """Test executing parent agent in hierarchy."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create parent agent
        parent_data = sample_agent_data.copy()
        parent_data["name"] = "Parent Execution Agent"
        parent_data["template_id"] = template_id
        parent_response = client.post("/api/v1/agents/", json=parent_data)
        parent_id = parent_response.json()["id"]
        
        # Create child agent
        child_data = sample_agent_data.copy()
        child_data["name"] = "Child Execution Agent"
        child_data["template_id"] = template_id
        child_data["parent_agent_id"] = parent_id
        child_data["level"] = 1
        child_response = client.post("/api/v1/agents/", json=child_data)
        
        # Execute parent agent
        execution_response = client.post(f"/api/v1/agents/{parent_id}/execute")
        assert execution_response.status_code == 200
        
        execution_result = execution_response.json()
        assert execution_result["status"] == "doing"

    def test_execute_agent_hierarchy_child(self, client, sample_agent_template_data, sample_agent_data):
        """Test executing child agent in hierarchy."""
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
        child_data["name"] = "Child Execution Agent"
        child_data["template_id"] = template_id
        child_data["parent_agent_id"] = parent_id
        child_data["level"] = 1
        child_response = client.post("/api/v1/agents/", json=child_data)
        child_id = child_response.json()["id"]
        
        # Execute child agent
        execution_response = client.post(f"/api/v1/agents/{child_id}/execute")
        assert execution_response.status_code == 200
        
        execution_result = execution_response.json()
        assert execution_result["status"] == "doing"

    def test_multiple_agent_executions(self, client, sample_agent_template_data, sample_agent_data):
        """Test executing multiple agents simultaneously."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create multiple agents
        agent_ids = []
        for i in range(3):
            agent_data = sample_agent_data.copy()
            agent_data["name"] = f"Execution Agent {i}"
            agent_data["template_id"] = template_id
            agent_response = client.post("/api/v1/agents/", json=agent_data)
            agent_ids.append(agent_response.json()["id"])
        
        # Execute all agents
        execution_ids = []
        for agent_id in agent_ids:
            execution_response = client.post(f"/api/v1/agents/{agent_id}/execute")
            assert execution_response.status_code == 200
            
            execution_result = execution_response.json()
            assert execution_result["status"] == "doing"
            execution_ids.append(execution_result["execution_id"])
        
        # Verify all execution IDs are unique
        assert len(set(execution_ids)) == len(execution_ids)

    def test_agent_execution_with_different_statuses(self, client, sample_agent_template_data, sample_agent_data):
        """Test agent execution from different initial statuses."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        initial_statuses = ["todo", "waiting", "needs_input"]
        
        for status in initial_statuses:
            # Create agent with specific status
            agent_data = sample_agent_data.copy()
            agent_data["name"] = f"Agent {status}"
            agent_data["template_id"] = template_id
            agent_data["status"] = status
            agent_response = client.post("/api/v1/agents/", json=agent_data)
            agent_id = agent_response.json()["id"]
            
            # Execute agent
            execution_response = client.post(f"/api/v1/agents/{agent_id}/execute")
            assert execution_response.status_code == 200
            
            execution_result = execution_response.json()
            assert execution_result["status"] == "doing"

    def test_agent_execution_empty_parameters(self, client, sample_agent_template_data, sample_agent_data):
        """Test agent execution with empty parameters."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create agent
        agent_data = sample_agent_data.copy()
        agent_data["template_id"] = template_id
        agent_response = client.post("/api/v1/agents/", json=agent_data)
        agent_id = agent_response.json()["id"]
        
        # Execute agent with empty parameters
        execution_response = client.post(f"/api/v1/agents/{agent_id}/execute", json={})
        assert execution_response.status_code == 200
        
        execution_result = execution_response.json()
        assert execution_result["status"] == "doing"

    def test_agent_execution_workflow_simulation(self, client, sample_agent_template_data, sample_agent_data):
        """Test simulated agent execution workflow."""
        # Create template
        template_response = client.post("/api/v1/agent-templates/", json=sample_agent_template_data)
        template_id = template_response.json()["id"]
        
        # Create agent
        agent_data = sample_agent_data.copy()
        agent_data["template_id"] = template_id
        agent_response = client.post("/api/v1/agents/", json=agent_data)
        agent_id = agent_response.json()["id"]
        agent_db_id = agent_response.json()["agent_id"]
        
        # Simulate workflow: todo -> doing -> waiting -> doing -> done (simulation only)
        
        # 1. Initial state should be 'todo'
        get_response = client.get(f"/api/v1/agents/by-agent-id/{agent_db_id}")
        assert get_response.json()["status"] == "todo"
        
        # 2. Execute agent (todo -> doing)
        execution_response = client.post(f"/api/v1/agents/{agent_id}/execute")
        assert execution_response.status_code == 200
        
        get_response = client.get(f"/api/v1/agents/by-agent-id/{agent_db_id}")
        assert get_response.json()["status"] == "doing"
        
        # 3. Simulate waiting for input (doing -> waiting)
        status_response = client.put(f"/api/v1/agents/{agent_id}/status", json={"status": "waiting"})
        assert status_response.status_code == 200
        assert status_response.json()["status"] == "waiting"
        
        # 4. Resume execution (waiting -> doing)
        execution_response = client.post(f"/api/v1/agents/{agent_id}/execute")
        assert execution_response.status_code == 200
        
        get_response = client.get(f"/api/v1/agents/by-agent-id/{agent_db_id}")
        assert get_response.json()["status"] == "doing"