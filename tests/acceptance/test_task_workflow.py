import pytest
import asyncio
import os

from src.service.planner_agent import PlannerAgent
from src.repository.kvs_repository import KVSRepository
from src.models.task_models import TaskData, TaskSchemas, TaskStatus, AgentType


class TestTaskWorkflow:
    @pytest.fixture
    def kvs_repo(self):
        return KVSRepository()
    
    @pytest.fixture
    def planner_agent(self, kvs_repo):
        return PlannerAgent(kvs_repo)
    
    def test_complete_task_workflow_report_creation(self, planner_agent, kvs_repo):
        """受け入れテスト: レポート作成タスクの完全なワークフロー"""
        # Given: ユーザーがレポート作成を依頼
        session_id = "workflow-test-session"
        user_instruction = "競合他社の市場調査レポートを作成したい。その前に必要な情報収集をしておいてほしい"
        
        # セットアップ: KVSに実際のヒアリング結果を保存
        hearing_result = """
        # ユーザー要望
        - 市場調査レポートの作成が必要
        - 競合他社の分析を含める
        - 週次での進捗報告を希望
        """
        kvs_repo.save_hearing_result(session_id, hearing_result)
        kvs_repo.save_task_schemas(session_id, TaskSchemas())
        kvs_repo.save_task_data(session_id, TaskData())
        
        # When: タスクプランを作成
        plan = planner_agent.create_task_plan(session_id, user_instruction)
        
        # Then: 適切なタスクが生成される
        assert len(plan.plan) == 2
        
        # 情報収集タスクが先に作成される
        info_task = plan.plan[0]
        assert info_task.agent == AgentType.WEB
        assert "情報" in info_task.task or "検索" in info_task.task
        assert "情報収集" in info_task.tags
        
        # レポート作成タスクが依存関係を持って作成される
        report_task = plan.plan[1]
        assert report_task.agent == AgentType.CASUAL
        assert "レポート" in report_task.task
        assert info_task.id in report_task.need
        assert "レポート" in report_task.tags
        
        # When: タスクプランを実行
        results = planner_agent.execute_plan(session_id, plan)
        
        # Then: 両方のタスクが実行される
        assert len(results) == 2
        assert info_task.id in results
        assert report_task.id in results
        
        # 情報収集の結果が適切に設定される
        info_result = results[info_task.id]
        assert info_result["type"] in ["web_search", "llm_web_search"]  # LLM使用時は異なるtype
        assert "results" in info_result or "content" in info_result
        
        # レポート作成の結果が適切に設定される
        report_result = results[report_task.id]
        assert report_result["type"] in ["casual_work", "llm_casual"]  # LLM使用時は異なるtype
        
        # KVSへの適切な保存が行われる（実際のデータ確認）
        saved_task_data = kvs_repo.get_task_data(session_id)
        assert saved_task_data is not None
        assert len(saved_task_data.daily_tasks) > 0 or len(saved_task_data.info_references) > 0
    
    def test_task_dependency_resolution(self, planner_agent):
        """受け入れテスト: タスクの依存関係解決"""
        # Given: 依存関係のあるタスク
        from src.models.task_models import DailyTaskSchema, InfoReferenceSchema, ReferenceType
        
        info_task = InfoReferenceSchema(
            id="info_dep_test",
            agent=AgentType.WEB,
            task="依存情報の取得",
            reference_type=ReferenceType.WEB_SEARCH
        )
        
        main_task = DailyTaskSchema(
            id="main_dep_test",
            agent=AgentType.CASUAL,
            task="メインタスクの実行",
            need=["info_dep_test"]
        )
        
        # When: 依存関係なしのタスクの実行可能性をチェック
        can_execute_info = planner_agent._can_execute_task(info_task)
        can_execute_main_before = planner_agent._can_execute_task(main_task)
        
        # Then: 情報タスクは実行可能、メインタスクは実行不可
        assert can_execute_info is True
        assert can_execute_main_before is False
        
        # When: 情報タスクを実行してから再チェック
        planner_agent.agents_work_result["info_dep_test"] = {"status": "completed"}
        can_execute_main_after = planner_agent._can_execute_task(main_task)
        
        # Then: メインタスクも実行可能になる
        assert can_execute_main_after is True
    
    
    def test_error_handling_workflow(self, planner_agent, kvs_repo):
        """受け入れテスト: エラーハンドリング"""
        # Given: エラーが発生する可能性のある状況
        session_id = "error-test-session"
        
        # When: タスクを実行
        from src.models.task_models import DailyTaskSchema
        task = DailyTaskSchema(
            id="error_task",
            agent=AgentType.WEB,
            task="エラーテストタスク"
        )
        
        # Then: タスク実行が成功する
        result = planner_agent._execute_task(session_id, task)
        
        assert "error" not in result
        assert result["type"] in ["web_search", "llm_web_search"]
    
    def test_dynamic_plan_update(self, planner_agent, kvs_repo):
        """受け入れテスト: 動的なプラン更新"""
        # Given: 既存のタスクデータ
        session_id = "dynamic-test-session"
        existing_task_data = TaskData()
        kvs_repo.save_task_data(session_id, existing_task_data)
        
        # When: 新しいタスクを動的に追加
        from src.models.task_models import DailyTaskSchema
        new_tasks = [
            DailyTaskSchema(
                id="dynamic_task_1",
                agent=AgentType.WEB,
                task="動的追加タスク1"
            ),
            DailyTaskSchema(
                id="dynamic_task_2",
                agent=AgentType.CASUAL,
                task="動的追加タスク2"
            )
        ]
        
        planner_agent.update_plan_dynamically(session_id, new_tasks)
        
        # Then: タスクが適切に保存される
        saved_task_data = kvs_repo.get_task_data(session_id)
        assert saved_task_data is not None
        assert len(saved_task_data.daily_tasks) == 2
        assert saved_task_data.daily_tasks[0].id == "dynamic_task_1"
        assert saved_task_data.daily_tasks[1].id == "dynamic_task_2"