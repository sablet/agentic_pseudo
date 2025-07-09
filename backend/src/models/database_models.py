"""Database models for the agentic pseudo system."""

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.database import Base
import enum
import uuid
from src.models.enums import AgentStatus, ExecutionEngine


class AgentTemplate(Base):
    """Agent template database model."""

    __tablename__ = "agent_templates"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(String(36), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    delegation_type = Column(String(100), nullable=False)
    purpose_category = Column(String(100), nullable=False)
    context_categories = Column(JSON)  # Array of strings
    execution_engine = Column(Enum(ExecutionEngine), nullable=False)
    parameters = Column(JSON)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    agents = relationship("Agent", back_populates="template")


class DataUnitCategory(Base):
    """Data unit category database model."""

    __tablename__ = "data_unit_categories"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(String(36), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    editable = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    data_units = relationship("DataUnit", back_populates="category")


class Agent(Base):
    """Agent database model."""

    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String(36), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))
    template_id = Column(Integer, ForeignKey("agent_templates.id"))
    parent_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    type = Column(String(50), nullable=False)
    purpose = Column(Text)  # Specific purpose acquired through conversation
    context = Column(JSON)  # Array of specific context values
    status = Column(Enum(AgentStatus), default=AgentStatus.TODO)
    delegation_params = Column(JSON)  # Flexible parameters
    level = Column(Integer, default=0)  # Hierarchy depth
    config = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    template = relationship("AgentTemplate", back_populates="agents")
    parent_agent = relationship("Agent", remote_side=[id], backref="child_agents")
    conversations = relationship("Conversation", back_populates="agent")
    templates = relationship("Template", back_populates="agent")


class Template(Base):
    """Template database model."""

    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    content = Column(Text, nullable=False)
    category = Column(String(100))
    is_public = Column(Boolean, default=False)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    agent = relationship("Agent", back_populates="templates")


class Conversation(Base):
    """Conversation database model."""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    agent_id = Column(Integer, ForeignKey("agents.id"))
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    agent = relationship("Agent", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")


class Message(Base):
    """Message database model."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    content = Column(Text, nullable=False)
    role = Column(String(50), nullable=False)  # user, assistant, system
    message_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class DataUnit(Base):
    """Data unit database model."""

    __tablename__ = "data_units"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String(255), nullable=False, unique=True, index=True)  # Primary identifier
    label = Column(String(255), nullable=False)  # Display name
    category_id = Column(Integer, ForeignKey("data_unit_categories.id"))
    editable = Column(Boolean, default=True)
    data_type = Column(String(50), nullable=False)
    config = Column(JSON)
    data_content = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("DataUnitCategory", back_populates="data_units")
