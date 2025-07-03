import os
import json
from typing import Optional, Dict, Any
from datetime import datetime
from upstash_redis import Redis
from dotenv import load_dotenv

from src.models.task_models import TaskData, TaskSchemas, UserSession

load_dotenv()


class KVSRepository:
    def __init__(self):
        self.redis = Redis(
            url=os.environ.get("UPSTASH_URL"),
            token=os.environ.get("UPSTASH_TOKEN")
        )
    
    def save_hearing_result(self, session_id: str, hearing_result: str) -> bool:
        user_session = UserSession(
            session_id=session_id,
            hearing_result=hearing_result,
            updated_at=datetime.now()
        )
        self.redis.set(session_id, user_session.model_dump_json())
        return True
    
    def get_hearing_result(self, session_id: str) -> Optional[str]:
        data = self.redis.get(session_id)
        if data:
            user_session = UserSession.model_validate_json(data)
            return user_session.hearing_result
        return None
    
    def save_task_schemas(self, session_id: str, schemas: TaskSchemas) -> bool:
        key = f"task_schemas:{session_id}"
        schemas.updated_at = datetime.now()
        self.redis.set(key, schemas.model_dump_json())
        return True
    
    def get_task_schemas(self, session_id: str) -> Optional[TaskSchemas]:
        key = f"task_schemas:{session_id}"
        data = self.redis.get(key)
        if data:
            return TaskSchemas.model_validate_json(data)
        return None
    
    def save_task_data(self, session_id: str, task_data: TaskData) -> bool:
        key = f"tasks:{session_id}"
        task_data.updated_at = datetime.now()
        self.redis.set(key, task_data.model_dump_json())
        return True
    
    def get_task_data(self, session_id: str) -> Optional[TaskData]:
        key = f"tasks:{session_id}"
        data = self.redis.get(key)
        if data:
            return TaskData.model_validate_json(data)
        return None
    
    def update_task_status(self, session_id: str, task_id: str, status: str, result: Optional[str] = None) -> bool:
        task_data = self.get_task_data(session_id)
        
        if task_data is None:
            return False
        
        updated = False
        for task in task_data.daily_tasks:
            if task.id == task_id:
                task.status = status
                task.updated_at = datetime.now()
                if result:
                    task.result = result
                updated = True
                break
        
        if not updated:
            for task in task_data.info_references:
                if task.id == task_id:
                    task.status = status
                    task.updated_at = datetime.now()
                    if result:
                        task.result = result
                    updated = True
                    break
        
        return self.save_task_data(session_id, task_data)
    
    def delete_session_data(self, session_id: str) -> bool:
        keys = [
            session_id,
            f"task_schemas:{session_id}",
            f"tasks:{session_id}"
        ]
        for key in keys:
            self.redis.delete(key)
        return True