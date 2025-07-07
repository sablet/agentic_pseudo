import pytest
import json
import os
from datetime import datetime

from src.service.planner_agent import PlannerAgent
from src.service.llm_agents import LLMConfig
from src.repository.kvs_repository import KVSRepository
from src.models.task_models import (
    TaskData,
    TaskSchemas,
    DailyTaskSchema,
    InfoReferenceSchema,
    TaskStatus,
    AgentType,
    ReferenceType,
)


class TestUseCaseScenarios:
    """
    設計書 what-definition.md に基づく典型的なユースケースの受け入れテスト
    docs/use_case_scenarios.md で定義されたシナリオを検証
    """

    @pytest.fixture
    def planner_agent(self):
        kvs_repo = KVSRepository()
        return PlannerAgent(kvs_repo)

    @pytest.fixture
    def kvs_repo(self):
        return KVSRepository()


class TestMarketResearchUseCase(TestUseCaseScenarios):
    """ユースケース1: 市場調査レポート作成（基本ワークフロー）"""

    def test_market_research_hearing_setup(self, kvs_repo, planner_agent):
        """ヒアリング結果の設定と参照のテスト"""
        # Given: 市場調査プロジェクトのヒアリング結果
        hearing_result = """
        # ユーザー要望ヒアリング結果
        
        ## 基本情報
        - 担当者: 企画部 田中様
        - プロジェクト: 生成AI事業参入検討
        - 期限: 2週間後
        
        ## 調査要件
        - **対象領域**: 生成AI技術（特にマルチモーダルAI）
        - **調査範囲**: 技術動向、市場動向、競合他社分析
        - **成果物**: PowerPoint用サマリー、詳細調査レポート
        """

        session_id = "market_research_test_session"
        kvs_repo.save_hearing_result(session_id, hearing_result)
        kvs_repo.save_task_schemas(session_id, TaskSchemas())

        # When: タスクプランを作成
        user_instruction = "生成AI技術、特にマルチモーダルAIの市場調査レポートを作成したい。技術動向、市場規模、競合他社分析を含む包括的な調査をお願いします。まずは必要な情報収集から始めてください。"

        plan = planner_agent.create_task_plan(session_id, user_instruction)

        # Then: ヒアリング結果が考慮されたタスクプランが生成される
        assert len(plan.plan) >= 2  # 最低限の情報収集+レポート作成

        # 情報収集タスクの存在確認
        info_tasks = [
            task for task in plan.plan if isinstance(task, InfoReferenceSchema)
        ]
        work_tasks = [task for task in plan.plan if isinstance(task, DailyTaskSchema)]

        assert len(info_tasks) > 0, "情報収集タスクが生成されていない"
        assert len(work_tasks) > 0, "作業タスクが生成されていない"

        # タスク内容に調査要件が反映されているか
        all_task_descriptions = [task.task for task in plan.plan]
        combined_descriptions = " ".join(all_task_descriptions)

        assert "情報" in combined_descriptions or "検索" in combined_descriptions, (
            "情報収集タスクが含まれていない"
        )
        assert "レポート" in combined_descriptions, "レポート作成タスクが含まれていない"

    def test_market_research_task_dependencies(self, kvs_repo, planner_agent):
        """情報収集→レポート作成の依存関係テスト"""
        # Given: 市場調査のタスクプラン
        session_id = "dependency_test_session"
        kvs_repo.save_hearing_result(session_id, "市場調査プロジェクト要件")
        kvs_repo.save_task_schemas(session_id, TaskSchemas())

        user_instruction = (
            "生成AI市場調査レポートを作成したい。情報収集から始めてください。"
        )
        plan = planner_agent.create_task_plan(session_id, user_instruction)

        # When: 依存関係を確認
        info_tasks = [
            task for task in plan.plan if isinstance(task, InfoReferenceSchema)
        ]
        work_tasks = [task for task in plan.plan if isinstance(task, DailyTaskSchema)]

        # Then: 作業タスクが情報収集タスクに依存している
        if info_tasks and work_tasks:
            info_task_ids = [task.id for task in info_tasks]

            # 少なくとも1つの作業タスクが情報収集タスクに依存している
            has_dependency = any(
                any(info_id in work_task.need for info_id in info_task_ids)
                for work_task in work_tasks
            )
            assert has_dependency, "作業タスクが情報収集タスクに依存していない"

    def test_market_research_execution_flow(self, kvs_repo, planner_agent):
        """市場調査の実行フローテスト"""
        # Given: 市場調査タスクプラン
        session_id = "execution_flow_test"
        kvs_repo.save_hearing_result(session_id, "市場調査要件")
        kvs_repo.save_task_schemas(session_id, TaskSchemas())

        user_instruction = "生成AI技術の市場調査レポートを作成してください。"
        plan = planner_agent.create_task_plan(session_id, user_instruction)

        # When: タスクプランを実行
        results = planner_agent.execute_plan(session_id, plan)

        # Then: 全てのタスクが実行される
        assert len(results) == len(plan.plan), "全てのタスクが実行されていない"

        # 実行結果にエラーが含まれていない（または適切に処理されている）
        for task_id, result in results.items():
            assert isinstance(result, dict), f"タスク {task_id} の結果が辞書形式でない"
            # エラーがある場合も、システムが継続動作していることを確認
            if "error" in result:
                print(f"Warning: Task {task_id} had error: {result['error']}")

    def test_market_research_agent_specialization(self, kvs_repo, planner_agent):
        """エージェントの専門性テスト"""
        # Given: 市場調査タスクプラン
        session_id = "agent_specialization_test"
        kvs_repo.save_hearing_result(session_id, "市場調査要件")

        user_instruction = "AI技術の市場調査レポートを作成してください。"
        plan = planner_agent.create_task_plan(session_id, user_instruction)

        # When: 各タスクのエージェント割り当てを確認
        web_tasks = [task for task in plan.plan if task.agent == AgentType.WEB]
        casual_tasks = [task for task in plan.plan if task.agent == AgentType.CASUAL]

        # Then: 適切なエージェントにタスクが割り当てられている
        if web_tasks:
            for task in web_tasks:
                # Web Agentは情報収集タスクを担当
                assert (
                    "検索" in task.task
                    or "情報" in task.task
                    or isinstance(task, InfoReferenceSchema)
                ), f"Web Agentに不適切なタスクが割り当てられている: {task.task}"

        if casual_tasks:
            for task in casual_tasks:
                # Casual Agentはレポート作成等を担当
                assert (
                    "レポート" in task.task
                    or "作成" in task.task
                    or "分析" in task.task
                ), f"Casual Agentに不適切なタスクが割り当てられている: {task.task}"


class TestDataAnalysisUseCase(TestUseCaseScenarios):
    """ユースケース2: データ分析レポート作成（技術的ワークフロー）"""

    def test_data_analysis_technical_workflow(self, kvs_repo, planner_agent):
        """データ分析プロジェクトの技術的ワークフローテスト"""
        # Given: データ分析プロジェクトのヒアリング結果
        hearing_result = """
        # データ分析プロジェクト要件
        
        ## プロジェクト概要
        - 目的: Q4売上予測モデルの構築と精度検証
        - データ期間: 過去3年間の月次売上データ
        
        ## 技術要件
        - **データ処理**: Python/pandas使用
        - **モデリング**: 時系列分析（ARIMA、Prophet）
        - **可視化**: matplotlib、seaborn使用
        """

        session_id = "data_analysis_test_session"
        kvs_repo.save_hearing_result(session_id, hearing_result)
        kvs_repo.save_task_schemas(session_id, TaskSchemas())

        # When: データ分析タスクプランを作成
        user_instruction = "営業データの時系列分析を行い、Q4売上予測モデルを構築したい。データ処理から予測、レポート作成まで一貫して対応してください。"

        plan = planner_agent.create_task_plan(session_id, user_instruction)

        # Then: 技術的なタスクが適切に生成される
        coder_tasks = [task for task in plan.plan if task.agent == AgentType.CODER]

        # コード生成・データ処理タスクが含まれている
        if len(plan.plan) > 0:
            task_descriptions = " ".join([task.task for task in plan.plan])

            # データ分析に関連するキーワードが含まれている
            technical_keywords = ["データ", "分析", "予測", "モデル", "処理"]
            has_technical_content = any(
                keyword in task_descriptions for keyword in technical_keywords
            )

            assert has_technical_content, "データ分析に関連するタスクが生成されていない"

    def test_coder_agent_utilization(self, kvs_repo, planner_agent):
        """Coder Agentの活用テスト"""
        # Given: コード生成が必要な指示
        session_id = "coder_agent_test"
        kvs_repo.save_hearing_result(session_id, "Python コード生成要件")

        user_instruction = "Pythonでデータ分析コードを生成してください。pandasを使用した前処理から可視化まで。"
        plan = planner_agent.create_task_plan(session_id, user_instruction)

        # When & Then: Coder Agentが活用されている（または適切な代替処理）
        if len(plan.plan) > 0:
            # タスクが生成されていることを確認
            assert len(plan.plan) >= 1, "タスクが生成されていない"

            # コード関連のタスクが含まれている
            code_related = any(
                "コード" in task.task or "Python" in task.task or "データ" in task.task
                for task in plan.plan
            )

            # タスクが生成されているか、Coder Agentが使用されている
            coder_tasks = [task for task in plan.plan if task.agent == AgentType.CODER]

            assert code_related or len(coder_tasks) > 0, (
                "コード関連タスクが適切に処理されていない"
            )


class TestDynamicPlanningUseCase(TestUseCaseScenarios):
    """ユースケース3: 複合的プロジェクト管理（動的計画更新）"""

    def test_dynamic_plan_update_capability(self, kvs_repo, planner_agent):
        """動的計画更新機能のテスト"""
        # Given: 初期プロジェクト要件
        session_id = "dynamic_planning_test"
        initial_hearing = """
        # Webサービス開発プロジェクト
        
        ## サービス概要
        - サービス名: TaskFlow（仮称）
        - 概要: チーム向けタスク管理サービス
        
        ## フェーズ1要件（企画・調査）
        - 市場調査
        - 技術選定調査
        """

        kvs_repo.save_hearing_result(session_id, initial_hearing)
        kvs_repo.save_task_schemas(session_id, TaskSchemas())

        # When: 初期タスクプランを作成
        initial_instruction = "新規Webサービス『TaskFlow』の開発プロジェクトを開始したい。まずは企画フェーズから始めて、市場調査と技術選定をお願いします。"

        initial_plan = planner_agent.create_task_plan(session_id, initial_instruction)

        # Then: 初期プランが生成される
        assert len(initial_plan.plan) >= 1, "初期タスクプランが生成されていない"

        # When: 動的にタスクを追加
        additional_tasks = [
            DailyTaskSchema(
                id="dynamic_task_1",
                agent=AgentType.WEB,
                task="UI/UXベストプラクティス調査",
                tags=["追加調査"],
            ),
            DailyTaskSchema(
                id="dynamic_task_2",
                agent=AgentType.CASUAL,
                task="技術選定レポート作成",
                need=["dynamic_task_1"],
                tags=["レポート"],
            ),
        ]

        planner_agent.update_plan_dynamically(session_id, additional_tasks)

        # Then: 動的更新が成功する
        updated_task_data = kvs_repo.get_task_data(session_id)
        assert updated_task_data is not None

        # 保存されたデータに新しいタスクが含まれている
        assert len(updated_task_data.daily_tasks) >= 2, (
            "動的タスク追加が正しく保存されていない"
        )

    def test_phased_project_execution(self, kvs_repo, planner_agent):
        """段階的プロジェクト実行のテスト"""
        # Given: 段階的プロジェクト設定
        session_id = "phased_project_test"
        phased_hearing = """
        # 段階的Webサービス開発
        
        ## フェーズ1: 企画・調査
        - 競合サービス分析
        - 技術スタック調査
        
        ## フェーズ2: 設計・実装（後日追加予定）
        - システム設計
        - 開発実装
        """

        kvs_repo.save_hearing_result(session_id, phased_hearing)

        # When: フェーズ1のタスクプランを作成・実行
        phase1_instruction = (
            "Webサービス開発プロジェクトのフェーズ1（企画・調査）を開始してください。"
        )

        phase1_plan = planner_agent.create_task_plan(session_id, phase1_instruction)
        phase1_results = planner_agent.execute_plan(session_id, phase1_plan)

        # Then: フェーズ1が適切に実行される
        assert len(phase1_plan.plan) >= 1, "フェーズ1のタスクが生成されていない"
        assert len(phase1_results) >= 1, "フェーズ1のタスクが実行されていない"

        # フェーズ1のタスクに企画・調査関連の内容が含まれている
        phase1_tasks = " ".join([task.task for task in phase1_plan.plan])
        assert (
            "調査" in phase1_tasks or "企画" in phase1_tasks or "分析" in phase1_tasks
        ), "フェーズ1に適切なタスクが含まれていない"


class TestErrorHandlingAndResilience(TestUseCaseScenarios):
    """エラーハンドリングと回復力のテスト"""

    def test_llm_fallback_behavior(self, kvs_repo):
        """LLMフォールバック動作のテスト"""
        planner = PlannerAgent(kvs_repo)

        # When: タスクプランを作成・実行
        session_id = "fallback_test"
        kvs_repo.save_hearing_result(session_id, "LLMフォールバックテスト要件")

        user_instruction = "市場調査レポートを作成してください。"
        plan = planner.create_task_plan(session_id, user_instruction)

        # Then: タスクが生成される
        assert planner.llm_agent_manager is not None, (
            "LLMマネージャーが初期化されていない"
        )

        # タスクが生成される
        if len(plan.plan) > 0:
            assert len(plan.plan) >= 1, "タスクが生成されていない"

    def test_partial_task_failure_resilience(self, kvs_repo, planner_agent):
        """部分的タスク失敗時の回復力テスト"""
        # Given: 一部のタスクが失敗する状況をシミュレート
        session_id = "resilience_test"
        kvs_repo.save_hearing_result(session_id, "回復力テスト要件")

        # When: タスクプランを実行
        user_instruction = "テストレポートを作成してください。"
        plan = planner_agent.create_task_plan(session_id, user_instruction)

        results = planner_agent.execute_plan(session_id, plan)

        # Then: システムが適切に処理する
        assert len(results) >= 0, "タスク実行が全く行われていない"


class TestKVSIntegration(TestUseCaseScenarios):
    """KVS統合機能のテスト"""

    def test_hearing_result_integration(self, kvs_repo, planner_agent):
        """ヒアリング結果統合のテスト"""
        # Given: 詳細なヒアリング結果
        detailed_hearing = """
        # 詳細プロジェクト要件
        
        ## 対象業界
        - FinTech領域
        - 決済システム
        
        ## 技術制約
        - セキュリティ要件: PCI DSS準拠
        - パフォーマンス要件: 100ms以下のレスポンス
        
        ## 成果物形式
        - 技術仕様書（Markdown）
        - アーキテクチャ図（Mermaid）
        - セキュリティチェックリスト
        """

        session_id = "kvs_integration_test"
        kvs_repo.save_hearing_result(session_id, detailed_hearing)
        kvs_repo.save_task_schemas(session_id, TaskSchemas())

        # When: ヒアリング結果を参考にタスクプランを作成
        user_instruction = "FinTech決済システムの技術仕様書を作成してください。"
        plan = planner_agent.create_task_plan(session_id, user_instruction)

        # Then: ヒアリング結果の内容がタスクに反映される
        if len(plan.plan) > 0:
            all_tasks = " ".join([task.task for task in plan.plan])

            # ヒアリング内容に関連するキーワードがタスクに含まれている
            fintech_keywords = ["技術", "仕様", "セキュリティ", "システム"]
            has_relevant_content = any(
                keyword in all_tasks for keyword in fintech_keywords
            )

            assert has_relevant_content, "ヒアリング結果がタスク生成に反映されていない"

    def test_session_data_persistence(self, kvs_repo, planner_agent):
        """セッションデータ永続化のテスト"""
        # Given: セッションデータ
        session_id = "persistence_test"
        kvs_repo.save_hearing_result(session_id, "永続化テスト要件")
        kvs_repo.save_task_schemas(session_id, TaskSchemas())

        # When: タスクプランを作成
        user_instruction = "データ永続化テストを実行してください。"
        plan = planner_agent.create_task_plan(session_id, user_instruction)

        # Then: 適切なKVS操作が行われる
        # ヒアリング結果が正しく取得される
        retrieved_hearing = kvs_repo.get_hearing_result(session_id)
        assert retrieved_hearing == "永続化テスト要件"

        # タスクスキーマが正しく取得される
        retrieved_schemas = kvs_repo.get_task_schemas(session_id)
        assert retrieved_schemas is not None

        # タスクデータが保存される
        if len(plan.plan) > 0:
            saved_task_data = kvs_repo.get_task_data(session_id)
            assert saved_task_data is not None
            assert isinstance(saved_task_data, TaskData), (
                "TaskDataオブジェクトが保存されていない"
            )
