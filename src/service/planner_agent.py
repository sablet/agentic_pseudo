import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.models.task_models import (
    TaskPlan, TaskData, TaskSchemas, DailyTaskSchema, InfoReferenceSchema,
    TaskStatus, AgentType, ReferenceType
)
from src.repository.kvs_repository import KVSRepository
from src.service.llm_agents import LLMAgentManager


class PlannerAgent:
    def __init__(self, kvs_repo: KVSRepository):
        self.kvs_repo = kvs_repo
        self.agents_work_result: Dict[str, Any] = {}
        self.llm_agent_manager = LLMAgentManager()
    
    def create_task_plan(self, session_id: str, user_instruction: str) -> TaskPlan:
        hearing_result = self.kvs_repo.get_hearing_result(session_id)
        schemas = self.kvs_repo.get_task_schemas(session_id)
        
        tasks = self._parse_user_instruction(user_instruction, hearing_result, schemas)
        plan = TaskPlan(plan=tasks)
        
        self._save_tasks_to_kvs(session_id, tasks)
        
        return plan
    
    def _parse_user_instruction(
        self, 
        instruction: str, 
        hearing_result: Optional[str], 
        schemas: Optional[TaskSchemas]
    ) -> List[DailyTaskSchema | InfoReferenceSchema]:
        tasks = []
        
        # レポート作成パターン
        if "レポート" in instruction:
            # 情報収集が必要かチェック
            needs_info = any(keyword in instruction for keyword in [
                "情報収集", "調査", "検索", "分析", "市場", "技術動向", "競合"
            ])
            
            if needs_info:
                info_task = InfoReferenceSchema(
                    id=f"info_{uuid.uuid4().hex[:8]}",
                    agent=AgentType.WEB,
                    task=f"「{instruction}」に必要な情報を検索",
                    reference_type=ReferenceType.WEB_SEARCH,
                    tags=["情報収集"]
                )
                tasks.append(info_task)
                
                daily_task = DailyTaskSchema(
                    id=f"task_{uuid.uuid4().hex[:8]}",
                    agent=AgentType.CASUAL,
                    task=f"レポートのドラフト作成",
                    need=[info_task.id],
                    tags=["レポート"]
                )
                tasks.append(daily_task)
            else:
                # 情報収集なしでレポート作成
                daily_task = DailyTaskSchema(
                    id=f"task_{uuid.uuid4().hex[:8]}",
                    agent=AgentType.CASUAL,
                    task=f"レポート作成: {instruction}",
                    tags=["レポート"]
                )
                tasks.append(daily_task)
        
        # データ分析パターン
        elif any(keyword in instruction for keyword in ["データ分析", "予測", "モデル", "Python", "コード"]):
            # データ処理タスク
            data_task = DailyTaskSchema(
                id=f"task_{uuid.uuid4().hex[:8]}",
                agent=AgentType.CODER,
                task=f"データ処理・分析: {instruction}",
                tags=["データ分析"]
            )
            tasks.append(data_task)
            
            # レポート作成タスク（データ分析結果のまとめ）
            report_task = DailyTaskSchema(
                id=f"task_{uuid.uuid4().hex[:8]}",
                agent=AgentType.CASUAL,
                task=f"分析結果レポート作成",
                need=[data_task.id],
                tags=["レポート", "分析"]
            )
            tasks.append(report_task)
        
        # プロジェクト管理・開発パターン
        elif any(keyword in instruction for keyword in ["プロジェクト", "開発", "Webサービス", "システム", "設計"]):
            # 調査・企画タスク
            research_task = InfoReferenceSchema(
                id=f"info_{uuid.uuid4().hex[:8]}",
                agent=AgentType.WEB,
                task=f"プロジェクト関連調査: {instruction}",
                reference_type=ReferenceType.WEB_SEARCH,
                tags=["調査", "企画"]
            )
            tasks.append(research_task)
            
            # 企画・設計タスク
            planning_task = DailyTaskSchema(
                id=f"task_{uuid.uuid4().hex[:8]}",
                agent=AgentType.CASUAL,
                task=f"企画・設計ドキュメント作成",
                need=[research_task.id],
                tags=["企画", "設計"]
            )
            tasks.append(planning_task)
        
        # 一般的なタスクパターン
        elif not tasks:
            # 基本的な作業タスクを生成
            base_task = DailyTaskSchema(
                id=f"task_{uuid.uuid4().hex[:8]}",
                agent=AgentType.CASUAL,
                task=instruction,
                tags=["一般"]
            )
            tasks.append(base_task)
        
        return tasks
    
    def _save_tasks_to_kvs(self, session_id: str, tasks: List[DailyTaskSchema | InfoReferenceSchema]):
        task_data = self.kvs_repo.get_task_data(session_id) or TaskData()
        
        for task in tasks:
            if isinstance(task, DailyTaskSchema):
                task_data.daily_tasks.append(task)
            elif isinstance(task, InfoReferenceSchema):
                task_data.info_references.append(task)
        
        self.kvs_repo.save_task_data(session_id, task_data)
    
    def execute_plan(self, session_id: str, plan: TaskPlan) -> Dict[str, Any]:
        results = {}
        
        for task in plan.plan:
            if self._can_execute_task(task):
                result = self._execute_task(session_id, task)
                results[task.id] = result
                self.agents_work_result[task.id] = result
        
        return results
    
    def _can_execute_task(self, task: DailyTaskSchema | InfoReferenceSchema) -> bool:
        if not task.need:
            return True
        
        for dependency_id in task.need:
            if dependency_id not in self.agents_work_result:
                return False
        
        return True
    
    def _execute_task(self, session_id: str, task: DailyTaskSchema | InfoReferenceSchema) -> Dict[str, Any]:
        self.kvs_repo.update_task_status(session_id, task.id, TaskStatus.IN_PROGRESS)
        
        # 依存関係のコンテキストを準備
        context = {}
        if task.need:
            dependencies_used = []
            for dep_id in task.need:
                if dep_id in self.agents_work_result:
                    dependencies_used.append(self.agents_work_result[dep_id])
            context["dependencies_used"] = dependencies_used
        
        result = self.llm_agent_manager.execute_task(task.agent.value, task.task, context)
        
        self.kvs_repo.update_task_status(
            session_id, task.id, TaskStatus.COMPLETED, json.dumps(result)
        )
        
        return result
    
    def get_task_status(self, session_id: str) -> Optional[TaskData]:
        return self.kvs_repo.get_task_data(session_id)
    
    def update_plan_dynamically(self, session_id: str, new_tasks: List[DailyTaskSchema | InfoReferenceSchema]):
        self._save_tasks_to_kvs(session_id, new_tasks)