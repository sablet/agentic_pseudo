from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "未着手"
    IN_PROGRESS = "実行中"
    COMPLETED = "完了"
    FAILED = "失敗"


class AgentType(str, Enum):
    WEB = "web"
    CODER = "coder"
    CASUAL = "casual"
    FILE = "file"


class ReferenceType(str, Enum):
    KVS_DOCUMENT = "KVS_DOCUMENT"
    WEB_SEARCH = "WEB_SEARCH"
    FILE_READ = "FILE_READ"


class DailyTaskSchema(BaseModel):
    id: str = Field(..., description="タスクID")
    agent: AgentType = Field(..., description="実行エージェント")
    task: str = Field(..., description="タスク内容")
    need: List[str] = Field(default_factory=list, description="依存タスクID")
    schema_id: str = Field(default="daily_task_schema", description="スキーマID")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="タスク状態")
    tags: List[str] = Field(default_factory=list, description="タグ")
    created_at: datetime = Field(default_factory=datetime.now, description="作成日時")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新日時")
    result: Optional[str] = Field(None, description="実行結果")


class InfoReferenceSchema(BaseModel):
    id: str = Field(..., description="情報参照ID")
    agent: AgentType = Field(..., description="実行エージェント")
    task: str = Field(..., description="情報参照タスク")
    need: List[str] = Field(default_factory=list, description="依存タスクID")
    schema_id: str = Field(default="info_reference_schema", description="スキーマID")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="タスク状態")
    tags: List[str] = Field(default_factory=list, description="タグ")
    reference_type: ReferenceType = Field(..., description="参照タイプ")
    kvs_key: Optional[str] = Field(None, description="KVSキー")
    created_at: datetime = Field(default_factory=datetime.now, description="作成日時")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新日時")
    result: Optional[str] = Field(None, description="実行結果")


class TaskPlan(BaseModel):
    plan: List[DailyTaskSchema | InfoReferenceSchema] = Field(
        default_factory=list, description="実行計画"
    )
    created_at: datetime = Field(default_factory=datetime.now, description="作成日時")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新日時")


class TaskData(BaseModel):
    daily_tasks: List[DailyTaskSchema] = Field(
        default_factory=list, description="日次タスク"
    )
    info_references: List[InfoReferenceSchema] = Field(
        default_factory=list, description="情報参照タスク"
    )
    created_at: datetime = Field(default_factory=datetime.now, description="作成日時")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新日時")


class TaskSchemas(BaseModel):
    daily_task_schema: Dict[str, Any] = Field(
        default_factory=dict, description="日次タスクスキーマ"
    )
    info_reference_schema: Dict[str, Any] = Field(
        default_factory=dict, description="情報参照スキーマ"
    )
    created_at: datetime = Field(default_factory=datetime.now, description="作成日時")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新日時")


class UserSession(BaseModel):
    session_id: str = Field(..., description="セッションID")
    hearing_result: str = Field("", description="ヒアリング結果（Markdown形式）")
    created_at: datetime = Field(default_factory=datetime.now, description="作成日時")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新日時")


