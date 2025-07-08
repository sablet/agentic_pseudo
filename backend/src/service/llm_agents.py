import json
import os
import re
from datetime import datetime
from typing import Any, Dict, Optional

import dspy
from dotenv import load_dotenv

from .gemini_constants import GeminiConfig
from .sub_agents import BaseAgent


def parse_llm_json_response(response_text: str) -> dict:
    """LLMからのJSON応答を解析する共通関数"""
    # JSONブロック（```json ... ```）を抽出
    json_match = re.search(r"```json\s*(.*?)\s*```", response_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        json_str = response_text

    # 末尾の不要なテキストを除去
    json_str = re.sub(r"\[\[.*?\]\].*$", "", json_str, flags=re.DOTALL).strip()

    return json.loads(json_str)


class LLMConfig:
    @staticmethod
    def configure_gemini():
        load_dotenv(os.path.expanduser(".env"))
        gemini = dspy.LM(
            model=GeminiConfig.get_dspy_model_name(),
            temperature=GeminiConfig.DEFAULT_TEMPERATURE,
            max_tokens=10000,
            num_retries=3,
            cache=True,
        )
        dspy.settings.configure(lm=gemini)
        return gemini


class WebSearchSignature(dspy.Signature):
    """Web検索を実行し、関連する情報を収集する"""

    query: str = dspy.InputField(desc="検索クエリ")
    search_results: str = dspy.OutputField(desc="検索結果の要約（JSON形式）")


class ReportGenerationSignature(dspy.Signature):
    """情報に基づいてレポートを生成する"""

    task_description: str = dspy.InputField(desc="タスクの説明")
    reference_info: str = dspy.InputField(desc="参考情報")
    report: str = dspy.OutputField(desc="生成されたレポート（Markdown形式）")


class CodeGenerationSignature(dspy.Signature):
    """コード生成とデータ処理を実行する"""

    task_description: str = dspy.InputField(desc="タスクの説明")
    code_and_result: str = dspy.OutputField(
        desc="生成されたコードと実行結果（JSON形式）"
    )


class FileOperationSignature(dspy.Signature):
    """ファイル操作のプランニングと実行指示を生成する"""

    task_description: str = dspy.InputField(desc="ファイル操作のタスク説明")
    operation_plan: str = dspy.OutputField(desc="ファイル操作の計画と手順（JSON形式）")


class LLMWebAgent(BaseAgent):
    def __init__(self):
        super().__init__("LLMWebAgent")
        self.llm = LLMConfig.configure_gemini()
        self.search_module = dspy.Predict(WebSearchSignature)

    def execute(
        self, task: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        result = self.search_module(query=task)

        # JSON形式の結果をパースして構造化
        search_data = parse_llm_json_response(result.search_results)

        return {
            "agent": self.name,
            "task": task,
            "type": "llm_web_search",
            "results": search_data,
            "timestamp": datetime.now().isoformat(),
            "llm_used": True,
        }


class LLMCasualAgent(BaseAgent):
    def __init__(self):
        super().__init__("LLMCasualAgent")
        self.llm = LLMConfig.configure_gemini()
        self.report_module = dspy.Predict(ReportGenerationSignature)

    def execute(
        self, task: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        # コンテキストから参考情報を取得
        reference_info = ""
        if context and "dependencies_used" in context:
            reference_info = str(context["dependencies_used"])
        elif context:
            reference_info = str(context)

        result = self.report_module(
            task_description=task, reference_info=reference_info
        )

        return {
            "agent": self.name,
            "task": task,
            "type": "llm_casual",
            "result": {
                "content": result.report,
                "format": "markdown",
                "status": "completed",
            },
            "timestamp": datetime.now().isoformat(),
            "llm_used": True,
        }


class LLMCoderAgent(BaseAgent):
    def __init__(self):
        super().__init__("LLMCoderAgent")
        self.llm = LLMConfig.configure_gemini()
        self.code_module = dspy.Predict(CodeGenerationSignature)

    def execute(
        self, task: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        result = self.code_module(task_description=task)

        # JSON形式の結果をパースして構造化
        code_data = parse_llm_json_response(result.code_and_result)

        return {
            "agent": self.name,
            "task": task,
            "type": "llm_code_execution",
            "result": code_data,
            "timestamp": datetime.now().isoformat(),
            "llm_used": True,
        }


class LLMFileAgent(BaseAgent):
    def __init__(self):
        super().__init__("LLMFileAgent")
        self.llm = LLMConfig.configure_gemini()
        self.file_module = dspy.Predict(FileOperationSignature)

    def execute(
        self, task: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        result = self.file_module(task_description=task)

        # JSON形式の結果をパースして構造化
        file_data = parse_llm_json_response(result.operation_plan)

        return {
            "agent": self.name,
            "task": task,
            "type": "llm_file_operation",
            "result": file_data,
            "timestamp": datetime.now().isoformat(),
            "llm_used": True,
        }


class LLMAgentManager:
    def __init__(self):
        LLMConfig.configure_gemini()
        self.agents = {
            "web": LLMWebAgent(),
            "coder": LLMCoderAgent(),
            "casual": LLMCasualAgent(),
            "file": LLMFileAgent(),
        }

    def get_agent(self, agent_type: str) -> Optional[BaseAgent]:
        return self.agents.get(agent_type)

    def execute_task(
        self, agent_type: str, task: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        agent = self.get_agent(agent_type)
        return agent.execute(task, context)
