from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import httpx
import json
from datetime import datetime


class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def execute(
        self, task: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        pass


class WebAgent(BaseAgent):
    def __init__(self):
        super().__init__("WebAgent")
        self.client = httpx.Client(timeout=30.0)

    def execute(
        self, task: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        search_results = self._search_web(task)
        return {
            "agent": self.name,
            "task": task,
            "type": "web_search",
            "results": search_results,
            "timestamp": datetime.now().isoformat(),
        }

    def _search_web(self, query: str) -> List[Dict[str, Any]]:
        return [
            {
                "title": f"検索結果1: {query}",
                "url": "https://example.com/search1",
                "snippet": "検索結果の概要1",
            },
            {
                "title": f"検索結果2: {query}",
                "url": "https://example.com/search2",
                "snippet": "検索結果の概要2",
            },
        ]


class CoderAgent(BaseAgent):
    def __init__(self):
        super().__init__("CoderAgent")

    def execute(
        self, task: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        result = self._execute_code_task(task, context)
        return {
            "agent": self.name,
            "task": task,
            "type": "code_execution",
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }

    def _execute_code_task(
        self, task: str, context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        if "データ処理" in task:
            return {
                "code": "# データ処理のサンプルコード\ndata = [1, 2, 3, 4, 5]\nresult = sum(data)\nprint(f'合計: {result}')",
                "output": "合計: 15",
                "status": "completed",
            }
        elif "分析" in task:
            return {
                "code": "# 分析のサンプルコード\nimport statistics\ndata = [1, 2, 3, 4, 5]\naverage = statistics.mean(data)\nprint(f'平均: {average}')",
                "output": "平均: 3.0",
                "status": "completed",
            }
        else:
            return {
                "code": f"# {task}のサンプルコード\nprint('タスク完了')",
                "output": "タスク完了",
                "status": "completed",
            }


class CasualAgent(BaseAgent):
    def __init__(self):
        super().__init__("CasualAgent")

    def execute(
        self, task: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        result = self._process_casual_task(task, context)
        return {
            "agent": self.name,
            "task": task,
            "type": "casual_work",
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }

    def _process_casual_task(
        self, task: str, context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        if "レポート" in task:
            return {
                "content": f"# {task}\n\n## 概要\n{task}に関するレポートを作成しました。\n\n## 詳細\n- 項目1: 詳細内容1\n- 項目2: 詳細内容2\n\n## 結論\n{task}を完了しました。",
                "format": "markdown",
                "status": "completed",
            }
        elif "要約" in task:
            return {
                "content": f"{task}の要約:\n\n主要なポイント:\n1. ポイント1\n2. ポイント2\n3. ポイント3",
                "format": "text",
                "status": "completed",
            }
        else:
            return {
                "content": f"{task}を処理しました。",
                "format": "text",
                "status": "completed",
            }


class FileAgent(BaseAgent):
    def __init__(self):
        super().__init__("FileAgent")

    def execute(
        self, task: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        result = self._process_file_task(task, context)
        return {
            "agent": self.name,
            "task": task,
            "type": "file_operation",
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }

    def _process_file_task(
        self, task: str, context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        if "読み込み" in task or "読み取り" in task:
            return {
                "operation": "read",
                "files": ["sample.txt", "data.json"],
                "content": "ファイルの内容をここに表示",
                "status": "completed",
            }
        elif "作成" in task or "書き込み" in task:
            return {
                "operation": "write",
                "files": ["output.txt"],
                "content": f"{task}の結果をファイルに書き込みました",
                "status": "completed",
            }
        elif "変換" in task:
            return {
                "operation": "convert",
                "input_files": ["input.csv"],
                "output_files": ["output.json"],
                "status": "completed",
            }
        else:
            return {
                "operation": "generic",
                "message": f"{task}を処理しました",
                "status": "completed",
            }


class AgentManager:
    def __init__(self):
        self.agents = {
            "web": WebAgent(),
            "coder": CoderAgent(),
            "casual": CasualAgent(),
            "file": FileAgent(),
        }

    def get_agent(self, agent_type: str) -> Optional[BaseAgent]:
        return self.agents.get(agent_type)

    def execute_task(
        self, agent_type: str, task: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        agent = self.get_agent(agent_type)
        if agent is None:
            raise ValueError(f"Unknown agent type: {agent_type}")
        return agent.execute(task, context)
