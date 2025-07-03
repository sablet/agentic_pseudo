import asyncio
import httpx
from typing import Dict, Any, Optional
import json


class FrontendInterface:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id: Optional[str] = None
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def create_session(self) -> str:
        response = await self.client.post(f"{self.base_url}/api/sessions")
        response.raise_for_status()
        data = response.json()
        self.session_id = data["session_id"]
        return self.session_id
    
    async def save_hearing_result(self, hearing_result: str) -> Dict[str, Any]:
        if not self.session_id:
            await self.create_session()
        
        response = await self.client.post(
            f"{self.base_url}/api/hearing",
            json={
                "session_id": self.session_id,
                "hearing_result": hearing_result
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def create_task_plan(self, user_instruction: str) -> Dict[str, Any]:
        if not self.session_id:
            await self.create_session()
        
        response = await self.client.post(
            f"{self.base_url}/api/tasks/create",
            json={
                "user_instruction": user_instruction,
                "session_id": self.session_id
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def execute_task_plan(self) -> Dict[str, Any]:
        response = await self.client.post(
            f"{self.base_url}/api/tasks/execute/{self.session_id}"
        )
        response.raise_for_status()
        return response.json()
    
    async def get_task_status(self) -> Dict[str, Any]:
        response = await self.client.get(
            f"{self.base_url}/api/tasks/status/{self.session_id}"
        )
        response.raise_for_status()
        return response.json()
    
    async def get_available_agents(self) -> Dict[str, Any]:
        response = await self.client.get(f"{self.base_url}/api/agents")
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        await self.client.aclose()
    
    def print_task_status(self, status_data: Dict[str, Any]):
        print(f"\n=== タスクステータス (セッション: {status_data['session_id']}) ===")
        
        task_data = status_data.get('task_data')
        if not task_data:
            print("タスクデータがありません")
            return
        
        print("\n--- 日次タスク ---")
        for task in task_data.get('daily_tasks', []):
            print(f"ID: {task['id']}")
            print(f"  タスク: {task['task']}")
            print(f"  エージェント: {task['agent']}")
            print(f"  ステータス: {task['status']}")
            print(f"  タグ: {', '.join(task['tags'])}")
            if task.get('result'):
                print(f"  結果: {task['result']}")
            print()
        
        print("\n--- 情報参照タスク ---")
        for task in task_data.get('info_references', []):
            print(f"ID: {task['id']}")
            print(f"  タスク: {task['task']}")
            print(f"  エージェント: {task['agent']}")
            print(f"  ステータス: {task['status']}")
            print(f"  参照タイプ: {task['reference_type']}")
            print(f"  タグ: {', '.join(task['tags'])}")
            if task.get('result'):
                print(f"  結果: {task['result']}")
            print()


async def main():
    frontend = FrontendInterface()
    
    print("=== Agentic Task Management System ===")
    
    # セッション作成
    session_id = await frontend.create_session()
    print(f"セッションを作成しました: {session_id}")
    
    # ヒアリング結果を保存
    hearing_result = """
    # ユーザー要望
    - 市場調査レポートの作成が必要
    - 競合他社の分析を含める
    - 週次での進捗報告を希望
    """
    await frontend.save_hearing_result(hearing_result)
    print("ヒアリング結果を保存しました")
    
    # タスクプランの作成
    user_instruction = "競合他社の市場調査レポートを作成したい。その前に必要な情報収集をしておいてほしい"
    plan_result = await frontend.create_task_plan(user_instruction)
    print(f"タスクプランを作成しました: {plan_result['message']}")
    
    # タスクステータスの確認
    status = await frontend.get_task_status()
    frontend.print_task_status(status)
    
    # タスクプランの実行
    execution_result = await frontend.execute_task_plan()
    print(f"タスクプランを実行しました: {execution_result['message']}")
    
    # 実行後のステータス確認
    status = await frontend.get_task_status()
    frontend.print_task_status(status)
    
    # 利用可能なエージェントの確認
    agents = await frontend.get_available_agents()
    print(f"\n利用可能なエージェント: {agents['agents']}")
    
    await frontend.close()


if __name__ == "__main__":
    asyncio.run(main())