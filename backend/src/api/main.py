from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
import json

from src.service.planner_agent import PlannerAgent
from src.service.sub_agents import AgentManager
from src.repository.kvs_repository import KVSRepository
from src.models.task_models import TaskData, TaskSchemas

app = FastAPI(title="Agentic Task Management System", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def decode_unicode_in_task_data(task_data):
    """TaskDataオブジェクト内のUnicode文字列をデコード"""
    def decode_unicode_string(text):
        if isinstance(text, str):
            try:
                return text.encode().decode('unicode_escape')
            except UnicodeDecodeError:
                return text
        return text
    
    def decode_task_list(tasks):
        if not tasks:
            return tasks
        
        decoded_tasks = []
        for task in tasks:
            decoded_task = task.model_copy()
            if hasattr(decoded_task, 'result') and decoded_task.result:
                decoded_task.result = decode_unicode_string(decoded_task.result)
            if hasattr(decoded_task, 'task') and decoded_task.task:
                decoded_task.task = decode_unicode_string(decoded_task.task)
            decoded_tasks.append(decoded_task)
        return decoded_tasks
    
    if task_data:
        task_data.daily_tasks = decode_task_list(task_data.daily_tasks)
        task_data.info_references = decode_task_list(task_data.info_references)
    
    return task_data

kvs_repo = KVSRepository()
planner_agent = PlannerAgent(kvs_repo)
agent_manager = AgentManager()


class TaskRequest(BaseModel):
    user_instruction: str
    session_id: Optional[str] = None


class HearingRequest(BaseModel):
    session_id: str
    hearing_result: str


class TaskStatusResponse(BaseModel):
    session_id: str
    task_data: Optional[TaskData]


@app.post("/api/sessions")
async def create_session() -> Dict[str, str]:
    session_id = str(uuid.uuid4())
    return {"session_id": session_id}


@app.post("/api/hearing")
async def save_hearing_result(request: HearingRequest) -> Dict[str, str]:
    kvs_repo.save_hearing_result(request.session_id, request.hearing_result)
    
    return {"message": "ヒアリング結果を保存しました", "session_id": request.session_id}


@app.get("/api/hearing/{session_id}")
async def get_hearing_result(session_id: str) -> Dict[str, Any]:
    hearing_result = kvs_repo.get_hearing_result(session_id)
    
    return {
        "session_id": session_id,
        "hearing_result": hearing_result
    }


@app.post("/api/tasks/create")
async def create_task_plan(request: TaskRequest) -> Dict[str, Any]:
    session_id = request.session_id or str(uuid.uuid4())
    
    plan = planner_agent.create_task_plan(session_id, request.user_instruction)
    
    return {
        "session_id": session_id,
        "plan": plan.model_dump(),
        "message": "タスクプランを作成しました"
    }


@app.post("/api/tasks/execute/{session_id}")
async def execute_task_plan(session_id: str) -> Dict[str, Any]:
    task_data = kvs_repo.get_task_data(session_id)
    
    from src.models.task_models import TaskPlan
    all_tasks = task_data.daily_tasks + task_data.info_references
    plan = TaskPlan(plan=all_tasks)
    
    results = planner_agent.execute_plan(session_id, plan)
    
    return {
        "session_id": session_id,
        "execution_results": results,
        "message": "タスクプランを実行しました"
    }


@app.get("/api/tasks/status/{session_id}")
async def get_task_status(session_id: str) -> TaskStatusResponse:
    task_data = kvs_repo.get_task_data(session_id)
    
    # Unicode文字列をデコード
    if task_data:
        task_data = decode_unicode_in_task_data(task_data)
    
    return TaskStatusResponse(
        session_id=session_id,
        task_data=task_data
    )


@app.put("/api/tasks/update/{session_id}/{task_id}")
async def update_task_status(session_id: str, task_id: str, status: str, result: Optional[str] = None) -> Dict[str, str]:
    kvs_repo.update_task_status(session_id, task_id, status, result)
    
    return {"message": "タスクステータスを更新しました"}


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str) -> Dict[str, str]:
    kvs_repo.delete_session_data(session_id)
    
    return {"message": "セッションデータを削除しました"}


@app.get("/api/agents")
async def get_available_agents() -> Dict[str, Any]:
    return {
        "agents": list(agent_manager.agents.keys()),
        "descriptions": {
            "web": "Web検索・情報収集エージェント",
            "coder": "プログラミング・データ処理エージェント",
            "casual": "自然言語処理・対話エージェント",
            "file": "ファイル操作エージェント"
        }
    }


@app.get("/")
async def root():
    return {"message": "Agentic Task Management System API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)