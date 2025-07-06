"""Conversation service layer."""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from src.models.database_models import Conversation, Message
from src.models.schemas import (
    ConversationCreate,
    ConversationUpdate,
    MessageCreate,
    MessageUpdate,
)
from src.exceptions import not_found_exception


class ConversationService:
    """Service for managing conversations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_conversation(
        self, conversation_data: ConversationCreate
    ) -> Conversation:
        """Create a new conversation."""
        db_conversation = Conversation(**conversation_data.model_dump())
        self.db.add(db_conversation)
        await self.db.commit()
        await self.db.refresh(db_conversation)
        return db_conversation

    async def get_conversation(self, conversation_id: int) -> Conversation:
        """Get a conversation by ID."""
        query = select(Conversation).where(Conversation.id == conversation_id)
        result = await self.db.execute(query)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise not_found_exception("Conversation", conversation_id)

        return conversation

    async def get_conversations(
        self,
        skip: int = 0,
        limit: int = 100,
        agent_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[Conversation]:
        """Get list of conversations with optional filtering."""
        query = select(Conversation)

        if agent_id:
            query = query.where(Conversation.agent_id == agent_id)
        if status:
            query = query.where(Conversation.status == status)

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_conversation(
        self, conversation_id: int, conversation_data: ConversationUpdate
    ) -> Conversation:
        """Update a conversation."""
        # Check if conversation exists
        await self.get_conversation(conversation_id)

        # Update conversation
        update_data = conversation_data.model_dump(exclude_unset=True)
        if update_data:
            query = (
                update(Conversation)
                .where(Conversation.id == conversation_id)
                .values(**update_data)
            )
            await self.db.execute(query)
            await self.db.commit()

        # Return updated conversation
        return await self.get_conversation(conversation_id)

    async def delete_conversation(self, conversation_id: int) -> bool:
        """Delete a conversation."""
        # Check if conversation exists
        await self.get_conversation(conversation_id)

        # Delete conversation
        query = delete(Conversation).where(Conversation.id == conversation_id)
        await self.db.execute(query)
        await self.db.commit()

        return True

    async def get_conversation_with_messages(
        self, conversation_id: int
    ) -> Conversation:
        """Get a conversation with its messages."""
        query = (
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.id == conversation_id)
        )

        result = await self.db.execute(query)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise not_found_exception("Conversation", conversation_id)

        return conversation

    async def count_conversations(
        self, agent_id: Optional[int] = None, status: Optional[str] = None
    ) -> int:
        """Count conversations with optional filtering."""
        query = select(Conversation.id)

        if agent_id:
            query = query.where(Conversation.agent_id == agent_id)
        if status:
            query = query.where(Conversation.status == status)

        result = await self.db.execute(query)
        return len(result.scalars().all())


class MessageService:
    """Service for managing messages."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_message(self, message_data: MessageCreate) -> Message:
        """Create a new message."""
        db_message = Message(**message_data.model_dump())
        self.db.add(db_message)
        await self.db.commit()
        await self.db.refresh(db_message)
        return db_message

    async def get_message(self, message_id: int) -> Message:
        """Get a message by ID."""
        query = select(Message).where(Message.id == message_id)
        result = await self.db.execute(query)
        message = result.scalar_one_or_none()

        if not message:
            raise not_found_exception("Message", message_id)

        return message

    async def get_messages(
        self,
        conversation_id: int,
        skip: int = 0,
        limit: int = 100,
        role: Optional[str] = None,
    ) -> List[Message]:
        """Get messages for a conversation."""
        query = select(Message).where(Message.conversation_id == conversation_id)

        if role:
            query = query.where(Message.role == role)

        query = query.offset(skip).limit(limit).order_by(Message.created_at)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_message(
        self, message_id: int, message_data: MessageUpdate
    ) -> Message:
        """Update a message."""
        # Check if message exists
        await self.get_message(message_id)

        # Update message
        update_data = message_data.model_dump(exclude_unset=True)
        if update_data:
            query = (
                update(Message).where(Message.id == message_id).values(**update_data)
            )
            await self.db.execute(query)
            await self.db.commit()

        # Return updated message
        return await self.get_message(message_id)

    async def delete_message(self, message_id: int) -> bool:
        """Delete a message."""
        # Check if message exists
        await self.get_message(message_id)

        # Delete message
        query = delete(Message).where(Message.id == message_id)
        await self.db.execute(query)
        await self.db.commit()

        return True

    async def count_messages(
        self, conversation_id: int, role: Optional[str] = None
    ) -> int:
        """Count messages for a conversation."""
        query = select(Message.id).where(Message.conversation_id == conversation_id)

        if role:
            query = query.where(Message.role == role)

        result = await self.db.execute(query)
        return len(result.scalars().all())
