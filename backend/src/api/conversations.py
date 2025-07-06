"""Conversation API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.service.conversation_service import ConversationService, MessageService
from src.models.schemas import (
    Conversation,
    ConversationCreate,
    ConversationUpdate,
    Message,
    MessageCreate,
    MessageUpdate,
    ListResponse,
)
from src.auth import get_optional_user, TokenData

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/", response_model=Conversation, status_code=201)
async def create_conversation(
    conversation_data: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Create a new conversation."""
    service = ConversationService(db)
    return await service.create_conversation(conversation_data)


@router.get("/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Get a conversation by ID."""
    service = ConversationService(db)
    return await service.get_conversation(conversation_id)


@router.get("/", response_model=ListResponse)
async def get_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    agent_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Get list of conversations with optional filtering."""
    service = ConversationService(db)

    conversations = await service.get_conversations(
        skip=skip, limit=limit, agent_id=agent_id, status=status
    )

    total = await service.count_conversations(agent_id=agent_id, status=status)

    return ListResponse(
        items=conversations, total=total, page=skip // limit + 1, per_page=limit
    )


@router.put("/{conversation_id}", response_model=Conversation)
async def update_conversation(
    conversation_id: int,
    conversation_data: ConversationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Update a conversation."""
    service = ConversationService(db)
    return await service.update_conversation(conversation_id, conversation_data)


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Delete a conversation."""
    service = ConversationService(db)
    await service.delete_conversation(conversation_id)


@router.get("/{conversation_id}/messages", response_model=ListResponse)
async def get_conversation_messages(
    conversation_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    role: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Get messages for a conversation."""
    service = MessageService(db)

    messages = await service.get_messages(
        conversation_id=conversation_id, skip=skip, limit=limit, role=role
    )

    total = await service.count_messages(conversation_id=conversation_id, role=role)

    return ListResponse(
        items=messages, total=total, page=skip // limit + 1, per_page=limit
    )


@router.post("/{conversation_id}/messages", response_model=Message, status_code=201)
async def create_message(
    conversation_id: int,
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Create a new message in a conversation."""
    # Ensure the conversation_id matches
    message_data.conversation_id = conversation_id

    service = MessageService(db)
    return await service.create_message(message_data)


@router.get("/messages/{message_id}", response_model=Message)
async def get_message(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Get a message by ID."""
    service = MessageService(db)
    return await service.get_message(message_id)


@router.put("/messages/{message_id}", response_model=Message)
async def update_message(
    message_id: int,
    message_data: MessageUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Update a message."""
    service = MessageService(db)
    return await service.update_message(message_id, message_data)


@router.delete("/messages/{message_id}", status_code=204)
async def delete_message(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_optional_user),
):
    """Delete a message."""
    service = MessageService(db)
    await service.delete_message(message_id)
