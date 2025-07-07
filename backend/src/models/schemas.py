"""Pydantic schemas for API request/response models."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


# Base schemas
class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


# Agent schemas
class AgentBase(BaseSchema):
    """Base agent schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: str = Field(..., min_length=1, max_length=50)
    status: str = Field(default="active", max_length=50)
    config: Optional[Dict[str, Any]] = None


class AgentCreate(AgentBase):
    """Schema for creating an agent."""

    pass


class AgentUpdate(BaseSchema):
    """Schema for updating an agent."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    type: Optional[str] = Field(None, min_length=1, max_length=50)
    status: Optional[str] = Field(None, max_length=50)
    config: Optional[Dict[str, Any]] = None


class Agent(AgentBase):
    """Agent response schema."""

    id: int
    created_at: datetime
    updated_at: datetime


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
    role: str = Field(..., regex=r"^(user|assistant|system)$")
    metadata: Optional[Dict[str, Any]] = None


class MessageCreate(MessageBase):
    """Schema for creating a message."""

    pass


class MessageUpdate(BaseSchema):
    """Schema for updating a message."""

    content: Optional[str] = Field(None, min_length=1)
    metadata: Optional[Dict[str, Any]] = None


class Message(MessageBase):
    """Message response schema."""

    id: int
    created_at: datetime


# Data Unit schemas
class DataUnitBase(BaseSchema):
    """Base data unit schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    data_type: str = Field(..., min_length=1, max_length=50)
    config: Optional[Dict[str, Any]] = None
    data_content: Optional[Dict[str, Any]] = None
    is_active: bool = True


class DataUnitCreate(DataUnitBase):
    """Schema for creating a data unit."""

    pass


class DataUnitUpdate(BaseSchema):
    """Schema for updating a data unit."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    data_type: Optional[str] = Field(None, min_length=1, max_length=50)
    config: Optional[Dict[str, Any]] = None
    data_content: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class DataUnit(DataUnitBase):
    """Data unit response schema."""

    id: int
    created_at: datetime
    updated_at: datetime


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
