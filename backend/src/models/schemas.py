"""Pydantic schemas for API request/response models."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


# Import enums from common module
from src.models.enums import AgentStatus, ExecutionEngine


# Base schemas
class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


# Agent Template schemas
class AgentTemplateBase(BaseSchema):
    """Base agent template schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    delegation_type: str = Field(..., min_length=1, max_length=100)
    purpose_category: str = Field(..., min_length=1, max_length=100)
    context_categories: List[str] = Field(default_factory=list)
    execution_engine: ExecutionEngine
    parameters: Optional[Dict[str, Any]] = None


class AgentTemplateCreate(AgentTemplateBase):
    """Schema for creating an agent template."""
    pass


class AgentTemplateUpdate(BaseSchema):
    """Schema for updating an agent template."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    delegation_type: Optional[str] = Field(None, min_length=1, max_length=100)
    purpose_category: Optional[str] = Field(None, min_length=1, max_length=100)
    context_categories: Optional[List[str]] = None
    execution_engine: Optional[ExecutionEngine] = None
    parameters: Optional[Dict[str, Any]] = None


class AgentTemplate(AgentTemplateBase):
    """Agent template response schema."""

    id: int
    template_id: str
    usage_count: int
    created_at: datetime
    updated_at: datetime


# Data Unit Category schemas
class DataUnitCategoryBase(BaseSchema):
    """Base data unit category schema."""

    name: str = Field(..., min_length=1, max_length=255)
    editable: bool = True


class DataUnitCategoryCreate(DataUnitCategoryBase):
    """Schema for creating a data unit category."""
    pass


class DataUnitCategoryUpdate(BaseSchema):
    """Schema for updating a data unit category."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    editable: Optional[bool] = None


class DataUnitCategory(DataUnitCategoryBase):
    """Data unit category response schema."""

    id: int
    category_id: str
    created_at: datetime
    updated_at: datetime


# Agent schemas
class AgentBase(BaseSchema):
    """Base agent schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: str = Field(..., min_length=1, max_length=50)
    purpose: Optional[str] = None
    context: Optional[List[Any]] = Field(default_factory=list)
    status: AgentStatus = AgentStatus.TODO
    delegation_params: Optional[Dict[str, Any]] = None
    level: int = 0
    config: Optional[Dict[str, Any]] = None
    template_id: Optional[int] = None
    parent_agent_id: Optional[int] = None


class AgentCreate(AgentBase):
    """Schema for creating an agent."""

    pass


class AgentUpdate(BaseSchema):
    """Schema for updating an agent."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    type: Optional[str] = Field(None, min_length=1, max_length=50)
    purpose: Optional[str] = None
    context: Optional[List[Any]] = None
    status: Optional[AgentStatus] = None
    delegation_params: Optional[Dict[str, Any]] = None
    level: Optional[int] = None
    config: Optional[Dict[str, Any]] = None
    template_id: Optional[int] = None
    parent_agent_id: Optional[int] = None


class Agent(AgentBase):
    """Agent response schema."""

    id: int
    agent_id: str
    created_at: datetime
    updated_at: datetime


# Agent Meta Info schemas
class ContextStatus(BaseSchema):
    """Context status schema."""

    id: str
    name: str
    type: str = Field(..., pattern=r"^(file|text|selection|approval)$")
    required: bool
    status: str = Field(..., pattern=r"^(sufficient|insufficient|pending)$")
    description: str
    current_value: Optional[Any] = None


class WaitingInfo(BaseSchema):
    """Waiting info schema."""

    type: str = Field(..., pattern=r"^(context|approval|dependency)$")
    description: str
    estimated_time: Optional[str] = None
    dependencies: Optional[List[str]] = Field(default_factory=list)


class ConversationMessage(BaseSchema):
    """Conversation message schema."""

    id: str
    role: str = Field(..., pattern=r"^(user|agent)$")
    content: str
    timestamp: datetime


class ParentAgentSummary(BaseSchema):
    """Parent agent summary schema."""

    agent_id: str
    name: str
    purpose: str
    level: int


class ChildAgentSummary(BaseSchema):
    """Child agent summary schema."""

    agent_id: str
    name: str
    purpose: str
    status: AgentStatus
    level: int


class AgentMetaInfo(BaseSchema):
    """Agent meta info schema."""

    agent_id: str
    purpose: str
    description: str
    level: int
    context_status: List[ContextStatus] = Field(default_factory=list)
    waiting_for: List[WaitingInfo] = Field(default_factory=list)
    execution_log: List[str] = Field(default_factory=list)
    conversation_history: List[ConversationMessage] = Field(default_factory=list)
    parent_agent_summary: Optional[ParentAgentSummary] = None
    child_agent_summaries: List[ChildAgentSummary] = Field(default_factory=list)


# Chat Message schemas
class AgentProposal(BaseSchema):
    """Agent proposal schema."""

    purpose: str
    delegation_type: str
    context: str
    delegation_params: Optional[Dict[str, Any]] = None


class ChatMessage(BaseSchema):
    """Chat message schema."""

    id: str
    role: str = Field(..., pattern=r"^(user|agent|assistant|system|system_notification)$")
    content: str
    timestamp: datetime
    agent_id: Optional[str] = None
    agent_proposal: Optional[AgentProposal] = None


# Template schemas
class TemplateBase(BaseSchema):
    """Base template schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    content: str = Field(..., min_length=1)
    category: Optional[str] = Field(None, max_length=100)
    is_public: bool = False
    agent_id: Optional[int] = None


class TemplateCreate(TemplateBase):
    """Schema for creating a template."""

    pass


class TemplateUpdate(BaseSchema):
    """Schema for updating a template."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    content: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, max_length=100)
    is_public: Optional[bool] = None
    agent_id: Optional[int] = None


class Template(TemplateBase):
    """Template response schema."""

    id: int
    created_at: datetime
    updated_at: datetime


# Conversation schemas
class ConversationBase(BaseSchema):
    """Base conversation schema."""

    title: Optional[str] = Field(None, max_length=255)
    agent_id: int
    status: str = Field(default="active", max_length=50)


class ConversationCreate(ConversationBase):
    """Schema for creating a conversation."""

    pass


class ConversationUpdate(BaseSchema):
    """Schema for updating a conversation."""

    title: Optional[str] = Field(None, max_length=255)
    status: Optional[str] = Field(None, max_length=50)


class Conversation(ConversationBase):
    """Conversation response schema."""

    id: int
    created_at: datetime
    updated_at: datetime


# Message schemas
class MessageBase(BaseSchema):
    """Base message schema."""

    conversation_id: int
    content: str = Field(..., min_length=1)
    role: str = Field(..., pattern=r"^(user|assistant|system)$")
    message_metadata: Optional[Dict[str, Any]] = None


class MessageCreate(MessageBase):
    """Schema for creating a message."""

    pass


class MessageUpdate(BaseSchema):
    """Schema for updating a message."""

    content: Optional[str] = Field(None, min_length=1)
    message_metadata: Optional[Dict[str, Any]] = None


class Message(MessageBase):
    """Message response schema."""

    id: int
    created_at: datetime


# Data Unit schemas
class DataUnitBase(BaseSchema):
    """Base data unit schema."""

    value: str = Field(..., min_length=1, max_length=255)  # Primary identifier
    label: str = Field(..., min_length=1, max_length=255)  # Display name
    category_id: Optional[int] = None
    editable: bool = True
    data_type: str = Field(..., min_length=1, max_length=50)
    config: Optional[Dict[str, Any]] = None
    data_content: Optional[Dict[str, Any]] = None
    is_active: bool = True


class DataUnitCreate(DataUnitBase):
    """Schema for creating a data unit."""

    pass


class DataUnitUpdate(BaseSchema):
    """Schema for updating a data unit."""

    value: Optional[str] = Field(None, min_length=1, max_length=255)
    label: Optional[str] = Field(None, min_length=1, max_length=255)
    category_id: Optional[int] = None
    editable: Optional[bool] = None
    data_type: Optional[str] = Field(None, min_length=1, max_length=50)
    config: Optional[Dict[str, Any]] = None
    data_content: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class DataUnit(DataUnitBase):
    """Data unit response schema."""

    id: int
    created_at: datetime
    updated_at: datetime


# AI Processing schemas
class AIProcessRequest(BaseSchema):
    """Schema for AI processing request."""

    message: str = Field(..., min_length=1)
    system_prompt: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, gt=0, le=4096)
    stream: bool = False


class AIProcessResponse(BaseSchema):
    """Schema for AI processing response."""

    content: str
    provider: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    message_metadata: Optional[Dict[str, Any]] = None


# Response schemas
class ListResponse(BaseSchema):
    """Generic list response schema."""

    items: List[Any]
    total: int
    page: int = 1
    per_page: int = 10


class ErrorResponse(BaseSchema):
    """Error response schema."""

    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
