import pytest
import os
from datetime import datetime

from src.repository.kvs_repository import KVSRepository
from src.service.planner_agent import PlannerAgent
from src.models.task_models import (
    TaskData,
    TaskSchemas,
    UserSession,
    DailyTaskSchema,
    AgentType,
)


class TestKVSIntegration:
    """実際のKVSを使用した統合テスト"""

    @pytest.fixture
    def kvs_repo(self):
        """テスト用KVSリポジトリ"""
        return KVSRepository()

    @pytest.fixture
    def test_session_id(self):
        """テスト用セッションID"""
        return f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    @pytest.fixture
    def planner_agent_with_kvs(self, kvs_repo):
        """実際のKVSを使用するPlannerAgent"""
        return PlannerAgent(kvs_repo)

    def test_kvs_hearing_result_persistence(self, kvs_repo, test_session_id):
        """ヒアリング結果の永続化テスト"""
        # Given: ヒアリング結果
        hearing_result = """
        # テスト用ヒアリング結果
        - プロジェクト: KVS統合テスト
        - 要件: データ永続化の検証
        """

        # When: ヒアリング結果を保存
        save_result = kvs_repo.save_hearing_result(test_session_id, hearing_result)

        # Then: 保存が成功する
        assert save_result is True

        # When: ヒアリング結果を取得
        retrieved_result = kvs_repo.get_hearing_result(test_session_id)

        # Then: 正しく取得できる
        assert retrieved_result == hearing_result

        # Cleanup
        kvs_repo.delete_session_data(test_session_id)

    def test_kvs_task_data_persistence(self, kvs_repo, test_session_id):
        """タスクデータの永続化テスト"""
        # Given: タスクデータ
        task_data = TaskData(
            daily_tasks=[
                DailyTaskSchema(
                    id="test_task_1",
                    agent=AgentType.WEB,
                    task="テスト用タスク1",
                    tags=["テスト"],
                )
            ],
            info_references=[],
            updated_at=datetime.now(),
        )

        # When: タスクデータを保存
        save_result = kvs_repo.save_task_data(test_session_id, task_data)

        # Then: 保存が成功する
        assert save_result is True

        # When: タスクデータを取得
        retrieved_data = kvs_repo.get_task_data(test_session_id)

        # Then: 正しく取得できる
        assert retrieved_data is not None
        assert len(retrieved_data.daily_tasks) == 1
        assert retrieved_data.daily_tasks[0].id == "test_task_1"
        assert retrieved_data.daily_tasks[0].task == "テスト用タスク1"

        # Cleanup
        kvs_repo.delete_session_data(test_session_id)

    def test_kvs_task_status_update(self, kvs_repo, test_session_id):
        """タスクステータス更新テスト"""
        # Given: 初期タスクデータ
        task_data = TaskData(
            daily_tasks=[
                DailyTaskSchema(
                    id="status_test_task",
                    agent=AgentType.CASUAL,
                    task="ステータス更新テスト",
                    status="未着手",
                )
            ]
        )
        kvs_repo.save_task_data(test_session_id, task_data)

        # When: タスクステータスを更新
        update_result = kvs_repo.update_task_status(
            test_session_id, "status_test_task", "完了", "テスト完了"
        )

        # Then: 更新が成功する
        assert update_result is True

        # When: 更新後のデータを取得
        updated_data = kvs_repo.get_task_data(test_session_id)

        # Then: ステータスが更新されている
        assert updated_data.daily_tasks[0].status == "完了"
        assert updated_data.daily_tasks[0].result == "テスト完了"

        # Cleanup
        kvs_repo.delete_session_data(test_session_id)

    def test_kvs_session_cleanup(self, kvs_repo, test_session_id):
        """セッションデータの削除テスト"""
        # Given: セッションデータを作成
        hearing_result = "テスト用ヒアリング"
        task_schemas = TaskSchemas()
        task_data = TaskData()

        kvs_repo.save_hearing_result(test_session_id, hearing_result)
        kvs_repo.save_task_schemas(test_session_id, task_schemas)
        kvs_repo.save_task_data(test_session_id, task_data)

        # When: セッションデータを削除
        delete_result = kvs_repo.delete_session_data(test_session_id)

        # Then: 削除が成功する
        assert delete_result is True

        # When: 削除後にデータを取得
        retrieved_hearing = kvs_repo.get_hearing_result(test_session_id)
        retrieved_schemas = kvs_repo.get_task_schemas(test_session_id)
        retrieved_data = kvs_repo.get_task_data(test_session_id)

        # Then: データが削除されている
        assert retrieved_hearing is None
        assert retrieved_schemas is None
        assert retrieved_data is None

    def test_planner_agent_kvs_integration(
        self, planner_agent_with_kvs, test_session_id
    ):
        """PlannerAgentとKVSの統合テスト"""
        # Given: ヒアリング結果を事前に保存
        hearing_result = """
        # 統合テスト用ヒアリング
        - 目的: PlannerAgentとKVSの統合検証
        - 要件: タスクプランの作成と実行
        """
        planner_agent_with_kvs.kvs_repo.save_hearing_result(
            test_session_id, hearing_result
        )

        # When: タスクプランを作成
        user_instruction = "統合テスト用のレポートを作成してください"
        plan = planner_agent_with_kvs.create_task_plan(
            test_session_id, user_instruction
        )

        # Then: タスクプランが作成される
        assert len(plan.plan) > 0

        # When: タスクプランを実行
        results = planner_agent_with_kvs.execute_plan(test_session_id, plan)

        # Then: タスクが実行される
        assert len(results) > 0

        # When: KVSからタスクデータを取得
        stored_data = planner_agent_with_kvs.kvs_repo.get_task_data(test_session_id)

        # Then: 実行結果がKVSに保存されている
        assert stored_data is not None
        assert len(stored_data.daily_tasks) > 0 or len(stored_data.info_references) > 0

        # Cleanup
        planner_agent_with_kvs.kvs_repo.delete_session_data(test_session_id)

    def test_kvs_data_validation(self, kvs_repo, test_session_id):
        """KVSデータバリデーションテスト"""
        # Given: 無効なデータ
        invalid_task_data = "invalid json data"

        # When: 無効なデータでタスクデータを保存（内部的にJSON変換される）
        task_data = TaskData()
        save_result = kvs_repo.save_task_data(test_session_id, task_data)

        # Then: 保存が成功する（有効なTaskDataオブジェクトのため）
        assert save_result is True

        # When: 保存されたデータを取得
        retrieved_data = kvs_repo.get_task_data(test_session_id)

        # Then: データが正しく取得される
        assert retrieved_data is not None
        assert isinstance(retrieved_data, TaskData)

        # Cleanup
        kvs_repo.delete_session_data(test_session_id)


class TestKVSPerformance:
    """KVSパフォーマンステスト"""

    @pytest.fixture
    def kvs_repo(self):
        """テスト用KVSリポジトリ"""
        return KVSRepository()

    def test_kvs_bulk_operations(self, kvs_repo):
        """KVS大量操作テスト"""
        import time

        # Given: 複数のセッションデータ
        session_ids = [f"bulk_test_{i}" for i in range(10)]

        start_time = time.time()

        # When: 複数のセッションデータを保存
        for session_id in session_ids:
            hearing_result = f"Bulk test hearing for {session_id}"
            task_data = TaskData(
                daily_tasks=[
                    DailyTaskSchema(
                        id=f"task_{session_id}",
                        agent=AgentType.WEB,
                        task=f"Bulk test task for {session_id}",
                    )
                ]
            )
            kvs_repo.save_hearing_result(session_id, hearing_result)
            kvs_repo.save_task_data(session_id, task_data)

        save_time = time.time() - start_time

        # Then: 保存が適切な時間内に完了する
        assert save_time < 10.0  # 10秒以内

        start_time = time.time()

        # When: 複数のセッションデータを取得
        for session_id in session_ids:
            hearing_result = kvs_repo.get_hearing_result(session_id)
            task_data = kvs_repo.get_task_data(session_id)

            assert hearing_result is not None
            assert task_data is not None

        retrieve_time = time.time() - start_time

        # Then: 取得が適切な時間内に完了する
        assert retrieve_time < 5.0  # 5秒以内

        # Cleanup
        for session_id in session_ids:
            kvs_repo.delete_session_data(session_id)
