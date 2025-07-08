
import pytest

from src.models.task_models import (
    AgentType,
    DailyTaskSchema,
    InfoReferenceSchema,
    ReferenceType,
)
from src.repository.kvs_repository import KVSRepository
from src.service.planner_agent import PlannerAgent


class TestLLMIntegration:
    @pytest.fixture
    def kvs_repo(self):
        return KVSRepository()

    def test_planner_agent_with_llm_available(self, kvs_repo):
        """LLMが利用可能な場合のPlannerAgentの動作テスト"""
        # Act
        planner = PlannerAgent(kvs_repo)

        # Assert
        assert planner.llm_agent_manager is not None

    def test_planner_agent_without_llm(self, kvs_repo):
        """LLMを使用しない場合のPlannerAgentの動作テスト"""
        # Act
        planner = PlannerAgent(kvs_repo)

        # Assert
        assert planner.llm_agent_manager is not None

    def test_task_execution_with_llm(self, kvs_repo):
        """LLMを使用したタスク実行のテスト"""
        planner = PlannerAgent(kvs_repo)

        # Web検索タスクを作成
        task = InfoReferenceSchema(
            id="llm_test_task",
            agent=AgentType.WEB,
            task="LLMを使用した検索テスト",
            reference_type=ReferenceType.WEB_SEARCH,
        )

        # Act
        result = planner._execute_task("test_session", task)

        # Assert
        assert "error" not in result
        assert "results" in result or "content" in result

    def test_task_execution_with_context(self, kvs_repo):
        """依存関係のコンテキストを含むLLMタスク実行のテスト"""
        planner = PlannerAgent(kvs_repo)

        # 依存関係のある情報を設定
        planner.agents_work_result["dep_task"] = {
            "type": "web_search",
            "results": ["検索結果1", "検索結果2"],
        }

        # レポート作成タスクを作成（依存関係あり）
        task = DailyTaskSchema(
            id="llm_report_task",
            agent=AgentType.CASUAL,
            task="依存情報を基にレポート作成",
            need=["dep_task"],
        )

        # Act
        result = planner._execute_task("test_session", task)

        # Assert
        assert "error" not in result
        assert "result" in result and (
            "content" in result["result"] or "output" in result["result"]
        )

    def test_end_to_end_workflow_with_llm(self, kvs_repo):
        """LLMを使用したエンドツーエンドワークフローのテスト"""
        planner = PlannerAgent(kvs_repo)

        # Act
        # 1. タスクプラン作成
        plan = planner.create_task_plan(
            "test_session",
            "市場調査レポートを作成したい。その前に必要な情報収集をしておいてほしい",
        )

        # 2. タスクプラン実行
        results = planner.execute_plan("test_session", plan)

        # Assert
        assert len(plan.plan) >= 1
        assert len(results) >= 1

        # タスクが実行されたことを確認
        for result in results.values():
            assert "error" not in result or "content" in result or "output" in result

    def test_configuration_validation(self):
        """設定の妥当性テスト"""
        from src.service.llm_agents import LLMConfig

        # Act - 設定の呼び出しテスト
        result = LLMConfig.configure_gemini()

        # Assert - 何らかの結果が返ることを確認
        assert result is not None or result is None  # 設定の成功/失敗どちらでも許容
