"""AI processor service for handling conversation processing with AI engines."""

import logging
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.schemas import AIProcessResponse, MessageCreate
from .ai_engine import AIContext, AIMessage, AIProvider
from .ai_retry import QUOTA_AWARE_RETRY, AIRetryHandler
from .conversation_service import ConversationService, MessageService
from .gemini_engine import GeminiEngine

logger = logging.getLogger(__name__)


class AIProcessor:
    """AI processor service for conversation handling."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.conversation_service = ConversationService(db)
        self.message_service = MessageService(db)

        # Initialize AI engines
        self.engines = {AIProvider.GEMINI: GeminiEngine()}
        self.default_engine = self.engines[AIProvider.GEMINI]

        # Initialize retry handler
        self.retry_handler = AIRetryHandler(QUOTA_AWARE_RETRY)

    async def process_conversation(
        self,
        conversation_id: int,
        user_message: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        engine_type: AIProvider = AIProvider.GEMINI,
    ) -> AIProcessResponse:
        """Process conversation with AI engine and store messages."""

        # Verify conversation exists
        conversation = await self.conversation_service.get_conversation(conversation_id)

        # Get conversation history
        messages = await self.message_service.get_messages(
            conversation_id=conversation_id
        )

        # Convert to AI context
        ai_messages = []
        for msg in messages:
            ai_messages.append(
                AIMessage(role=msg.role, content=msg.content, metadata=msg.message_metadata)
            )

        # Add current user message
        ai_messages.append(AIMessage(role="user", content=user_message))

        # Create AI context
        context = AIContext(
            messages=ai_messages,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Get AI engine
        engine = self.engines.get(engine_type, self.default_engine)

        # Generate AI response with retry logic
        async def ai_operation():
            return await engine.generate_response(context)

        ai_response = await self.retry_handler.execute_with_retry(
            ai_operation,
            operation_name=f"AI response generation ({engine.provider.value})",
        )

        # Store user message
        user_msg_data = MessageCreate(
            conversation_id=conversation_id,
            content=user_message,
            role="user",
            metadata={"timestamp": "auto"},
        )
        await self.message_service.create_message(user_msg_data)

        # Store AI response message
        ai_msg_data = MessageCreate(
            conversation_id=conversation_id,
            content=ai_response.content,
            role="assistant",
            metadata={
                "provider": ai_response.provider.value,
                "model": ai_response.model,
                "usage": ai_response.usage,
                "ai_metadata": ai_response.metadata,
                "timestamp": "auto",
            },
        )
        await self.message_service.create_message(ai_msg_data)

        # Return response
        return AIProcessResponse(
            content=ai_response.content,
            provider=ai_response.provider.value,
            model=ai_response.model,
            usage=ai_response.usage,
            metadata=ai_response.metadata,
        )

    async def stream_conversation(
        self,
        conversation_id: int,
        user_message: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        engine_type: AIProvider = AIProvider.GEMINI,
    ) -> AsyncGenerator[str, None]:
        """Stream AI response for conversation processing."""

        # Verify conversation exists
        conversation = await self.conversation_service.get_conversation(conversation_id)

        # Get conversation history
        messages = await self.message_service.get_messages(
            conversation_id=conversation_id
        )

        # Convert to AI context
        ai_messages = []
        for msg in messages:
            ai_messages.append(
                AIMessage(role=msg.role, content=msg.content, metadata=msg.message_metadata)
            )

        # Add current user message
        ai_messages.append(AIMessage(role="user", content=user_message))

        # Create AI context
        context = AIContext(
            messages=ai_messages,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Get AI engine
        engine = self.engines.get(engine_type, self.default_engine)

        # Store user message
        user_msg_data = MessageCreate(
            conversation_id=conversation_id,
            content=user_message,
            role="user",
            metadata={"timestamp": "auto"},
        )
        await self.message_service.create_message(user_msg_data)

        # Stream AI response and collect full content
        full_content = ""
        async for chunk in engine.generate_streaming_response(context):
            full_content += chunk
            yield chunk

        # Store complete AI response message
        ai_msg_data = MessageCreate(
            conversation_id=conversation_id,
            content=full_content,
            role="assistant",
            metadata={
                "provider": engine.provider.value,
                "model": engine.model,
                "streaming": True,
                "timestamp": "auto",
            },
        )
        await self.message_service.create_message(ai_msg_data)

    async def get_context_summary(
        self, conversation_id: int, max_messages: int = 10
    ) -> str:
        """Get conversation context summary."""

        # Get recent messages
        messages = await self.message_service.get_messages(
            conversation_id=conversation_id, limit=max_messages
        )

        if not messages:
            return "Empty conversation"

        # Build context summary
        summary_parts = []
        for msg in messages[-max_messages:]:  # Get last N messages
            summary_parts.append(f"{msg.role.title()}: {msg.content[:100]}...")

        return "\n".join(summary_parts)

    async def validate_engine_connection(
        self, engine_type: AIProvider = AIProvider.GEMINI
    ) -> bool:
        """Validate AI engine connection."""

        engine = self.engines.get(engine_type, self.default_engine)
        return await engine.validate_connection()
