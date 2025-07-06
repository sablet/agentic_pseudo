import pytest
from fastapi.testclient import TestClient
import json

from src.api.main import app
from src.models.task_models import TaskData, TaskSchemas, UserSession


class TestAPIIntegration:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_create_session(self, client):
        # Act
        response = client.post("/api/sessions")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert len(data["session_id"]) > 0

    def test_save_hearing_result_success(self, client):
        # Arrange
        session_id = "test-session"
        hearing_result = "Test hearing result"

        # Act
        response = client.post(
            "/api/hearing",
            json={"session_id": session_id, "hearing_result": hearing_result},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "ヒアリング結果を保存しました"
        assert data["session_id"] == session_id

    def test_get_hearing_result_success(self, client):
        # Arrange
        session_id = "test-session"

        # Act
        response = client.get(f"/api/hearing/{session_id}")

        # Assert
        data = response.json()
        assert data["session_id"] == session_id

    def test_create_task_plan_success(self, client):
        # Arrange
        user_instruction = (
            "レポートを作成したい。その前に必要な情報収集をしておいてほしい"
        )
        session_id = "test-session"

        # Act
        response = client.post(
            "/api/tasks/create",
            json={"user_instruction": user_instruction, "session_id": session_id},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert "plan" in data
        assert data["message"] == "タスクプランを作成しました"

    def test_create_task_plan_without_session_id(self, client):
        # Arrange
        user_instruction = "レポートを作成したい"

        # Act
        response = client.post(
            "/api/tasks/create", json={"user_instruction": user_instruction}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert len(data["session_id"]) > 0

    def test_get_task_status_success(self, client):
        # Arrange
        session_id = "test-session"

        # Act
        response = client.get(f"/api/tasks/status/{session_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert "task_data" in data

    def test_update_task_status_success(self, client):
        # Arrange
        session_id = "test-session"
        task_id = "task1"
        status = "completed"
        result = "Task completed successfully"

        # Act
        response = client.put(
            f"/api/tasks/update/{session_id}/{task_id}",
            params={"status": status, "result": result},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "タスクステータスを更新しました"

    def test_delete_session_success(self, client):
        # Arrange
        session_id = "test-session"

        # Act
        response = client.delete(f"/api/sessions/{session_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "セッションデータを削除しました"

    def test_get_available_agents(self, client):
        # Act
        response = client.get("/api/agents")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert "descriptions" in data
        expected_agents = ["web", "coder", "casual", "file"]
        assert all(agent in data["agents"] for agent in expected_agents)

    def test_root_endpoint(self, client):
        # Act
        response = client.get("/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Agentic Task Management System API" in data["message"]
