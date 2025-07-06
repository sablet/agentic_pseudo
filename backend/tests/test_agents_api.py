"""Tests for agent API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.main import app
from src.database import Base, get_db

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def setup_database():
    """Setup test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestAgentAPI:
    """Test agent API endpoints."""

    def test_create_agent(self, setup_database):
        """Test creating an agent."""
        agent_data = {
            "name": "Test Agent",
            "description": "A test agent",
            "type": "assistant",
            "status": "active",
            "config": {"temperature": 0.7},
        }

        response = client.post("/api/v1/agents/", json=agent_data)
        assert response.status_code == 201

        data = response.json()
        assert data["name"] == "Test Agent"
        assert data["type"] == "assistant"
        assert data["status"] == "active"
        assert "id" in data
        assert "created_at" in data

    def test_get_agent(self, setup_database):
        """Test getting an agent by ID."""
        # Create agent first
        agent_data = {
            "name": "Test Agent",
            "description": "A test agent",
            "type": "assistant",
        }

        create_response = client.post("/api/v1/agents/", json=agent_data)
        agent_id = create_response.json()["id"]

        # Get agent
        response = client.get(f"/api/v1/agents/{agent_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Test Agent"
        assert data["id"] == agent_id

    def test_get_agent_not_found(self, setup_database):
        """Test getting non-existent agent."""
        response = client.get("/api/v1/agents/999")
        assert response.status_code == 404

    def test_get_agents_list(self, setup_database):
        """Test getting list of agents."""
        # Create multiple agents
        for i in range(3):
            agent_data = {"name": f"Agent {i}", "type": "assistant"}
            client.post("/api/v1/agents/", json=agent_data)

        response = client.get("/api/v1/agents/")
        assert response.status_code == 200

        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 3

    def test_update_agent(self, setup_database):
        """Test updating an agent."""
        # Create agent first
        agent_data = {"name": "Original Name", "type": "assistant"}

        create_response = client.post("/api/v1/agents/", json=agent_data)
        agent_id = create_response.json()["id"]

        # Update agent
        update_data = {"name": "Updated Name", "status": "inactive"}

        response = client.put(f"/api/v1/agents/{agent_id}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["status"] == "inactive"

    def test_delete_agent(self, setup_database):
        """Test deleting an agent."""
        # Create agent first
        agent_data = {"name": "Test Agent", "type": "assistant"}

        create_response = client.post("/api/v1/agents/", json=agent_data)
        agent_id = create_response.json()["id"]

        # Delete agent
        response = client.delete(f"/api/v1/agents/{agent_id}")
        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(f"/api/v1/agents/{agent_id}")
        assert get_response.status_code == 404

    def test_agent_filtering(self, setup_database):
        """Test filtering agents by type and status."""
        # Create agents with different types and statuses
        agents = [
            {"name": "Agent 1", "type": "assistant", "status": "active"},
            {"name": "Agent 2", "type": "assistant", "status": "inactive"},
            {"name": "Agent 3", "type": "planner", "status": "active"},
        ]

        for agent in agents:
            client.post("/api/v1/agents/", json=agent)

        # Filter by type
        response = client.get("/api/v1/agents/?type=assistant")
        assert response.status_code == 200
        assert len(response.json()["items"]) == 2

        # Filter by status
        response = client.get("/api/v1/agents/?status=active")
        assert response.status_code == 200
        assert len(response.json()["items"]) == 2
