"""Integration tests for AI engine functionality."""

import pytest
import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.ai_engine import AIContext, AIMessage, AIProvider
from src.service.gemini_engine import GeminiEngine
from src.service.ai_processor import AIProcessor
from src.service.ai_retry import AIRetryHandler, RetryConfig
from src.models.schemas import AIProcessRequest


# Mock database configuration for tests
@pytest.fixture(autouse=True)
def mock_database():
    """Mock database configuration to avoid connection issues in tests."""
    with patch.dict(os.environ, {"DATABASE_URL": "sqlite+aiosqlite:///:memory:"}):
        yield


class TestGeminiEngineIntegration:
    """Integration tests for Gemini engine."""

    @pytest.fixture
    def gemini_engine(self):
        """Create Gemini engine with mock API key."""
        return GeminiEngine(api_key="test_key", model="gemini-1.5-flash")

    @pytest.fixture
    def ai_context(self):
        """Create test AI context."""
        return AIContext(
            messages=[AIMessage(role="user", content="Hello, how are you?")],
            system_prompt="You are a helpful assistant.",
            temperature=0.7,
            max_tokens=100,
        )

    def test_gemini_engine_initialization(self, gemini_engine):
        """Test Gemini engine initialization."""
        assert gemini_engine.provider == AIProvider.GEMINI
        assert gemini_engine.model == "gemini-1.5-flash"
        assert gemini_engine.api_key == "test_key"

    def test_convert_messages_to_gemini_format(self, gemini_engine, ai_context):
        """Test message format conversion."""
        prompt = gemini_engine._convert_messages_to_gemini_format(ai_context)

        assert "System: You are a helpful assistant." in prompt
        assert "Human: Hello, how are you?" in prompt

    @pytest.mark.asyncio
    async def test_gemini_engine_mock_response(self, gemini_engine, ai_context):
        """Test Gemini engine with mocked response."""
        # Mock the Gemini client
        mock_response = MagicMock()
        mock_response.text = "Hello! I'm doing well, thank you for asking."
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].finish_reason = "STOP"
        mock_response.candidates[0].safety_ratings = []

        # Mock usage metadata
        mock_usage = MagicMock()
        mock_usage.prompt_token_count = 10
        mock_usage.candidates_token_count = 15
        mock_usage.total_token_count = 25
        mock_response.usage_metadata = mock_usage

        gemini_engine.client.generate_content = AsyncMock(return_value=mock_response)

        response = await gemini_engine.generate_response(ai_context)

        assert response.content == "Hello! I'm doing well, thank you for asking."
        assert response.provider == AIProvider.GEMINI
        assert response.model == "gemini-1.5-flash"
        assert response.usage["total_tokens"] == 25


class TestAIRetryHandler:
    """Tests for AI retry handler."""

    @pytest.fixture
    def retry_config(self):
        """Create test retry configuration."""
        return RetryConfig(
            max_attempts=3, base_delay=0.1, max_delay=1.0, exponential_base=2.0
        )

    @pytest.fixture
    def retry_handler(self, retry_config):
        """Create retry handler."""
        return AIRetryHandler(retry_config)

    @pytest.mark.asyncio
    async def test_successful_operation(self, retry_handler):
        """Test successful operation without retries."""

        async def successful_operation():
            return "success"

        result = await retry_handler.execute_with_retry(
            successful_operation, "test operation"
        )

        assert result == "success"

    @pytest.mark.asyncio
    async def test_retry_on_failure(self, retry_handler):
        """Test retry logic on failures."""
        call_count = 0

        async def failing_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success after retries"

        result = await retry_handler.execute_with_retry(
            failing_operation, "test operation"
        )

        assert result == "success after retries"
        assert call_count == 3

    def test_delay_calculation(self, retry_handler):
        """Test delay calculation for retries."""
        assert retry_handler.calculate_delay(1) == 0.1
        assert retry_handler.calculate_delay(2) == 0.2
        assert retry_handler.calculate_delay(3) == 0.4
        assert retry_handler.calculate_delay(10) == 1.0  # Max delay


class TestAIProcessorIntegration:
    """Integration tests for AI processor."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def ai_processor(self, mock_db):
        """Create AI processor with mocked dependencies."""
        processor = AIProcessor(mock_db)

        # Mock services
        processor.conversation_service.get_conversation = AsyncMock()
        processor.conversation_service.get_conversation.return_value = MagicMock(id=1)

        processor.message_service.get_messages = AsyncMock(return_value=[])
        processor.message_service.create_message = AsyncMock()

        return processor

    @pytest.mark.asyncio
    async def test_process_conversation_flow(self, ai_processor):
        """Test complete conversation processing flow."""
        # Mock AI engine response
        mock_response = MagicMock()
        mock_response.content = "AI response content"
        mock_response.provider = AIProvider.GEMINI
        mock_response.model = "gemini-1.5-flash"
        mock_response.usage = {"total_tokens": 50}
        mock_response.metadata = {"finish_reason": "STOP"}

        ai_processor.default_engine.generate_response = AsyncMock(
            return_value=mock_response
        )

        # Process conversation
        response = await ai_processor.process_conversation(
            conversation_id=1,
            user_message="Hello AI",
            system_prompt="You are helpful",
            temperature=0.8,
        )

        # Verify response
        assert response.content == "AI response content"
        assert response.provider == "gemini"
        assert response.model == "gemini-1.5-flash"

        # Verify service calls
        ai_processor.conversation_service.get_conversation.assert_called_once_with(1)
        ai_processor.message_service.get_messages.assert_called_once_with(
            conversation_id=1
        )
        assert (
            ai_processor.message_service.create_message.call_count == 2
        )  # User + AI messages

    @pytest.mark.asyncio
    async def test_context_summary(self, ai_processor):
        """Test conversation context summary."""
        # Mock messages
        mock_messages = [
            MagicMock(role="user", content="Hello"),
            MagicMock(role="assistant", content="Hi there!"),
            MagicMock(role="user", content="How are you?"),
        ]
        ai_processor.message_service.get_messages = AsyncMock(
            return_value=mock_messages
        )

        summary = await ai_processor.get_context_summary(
            conversation_id=1, max_messages=5
        )

        assert "User: Hello" in summary
        assert "Assistant: Hi there!" in summary
        assert "User: How are you?" in summary

    @pytest.mark.asyncio
    async def test_validate_engine_connection(self, ai_processor):
        """Test engine connection validation."""
        ai_processor.default_engine.validate_connection = AsyncMock(return_value=True)

        result = await ai_processor.validate_engine_connection()

        assert result is True
        ai_processor.default_engine.validate_connection.assert_called_once()


class TestAIEngineEndToEnd:
    """End-to-end tests for AI engine functionality."""

    @pytest.mark.asyncio
    async def test_complete_ai_flow_mock(self):
        """Test complete AI processing flow with mocks."""
        # This test would ideally use real API calls in a staging environment
        # For now, we'll use mocks to verify the complete flow

        # Create mock database
        mock_db = AsyncMock(spec=AsyncSession)

        # Create AI processor
        ai_processor = AIProcessor(mock_db)

        # Mock all dependencies
        ai_processor.conversation_service.get_conversation = AsyncMock()
        ai_processor.conversation_service.get_conversation.return_value = MagicMock(
            id=1
        )

        ai_processor.message_service.get_messages = AsyncMock(return_value=[])
        ai_processor.message_service.create_message = AsyncMock()

        # Mock AI response
        mock_response = MagicMock()
        mock_response.content = "This is a test AI response."
        mock_response.provider = AIProvider.GEMINI
        mock_response.model = "gemini-1.5-flash"
        mock_response.usage = {"total_tokens": 75}
        mock_response.metadata = {"finish_reason": "STOP"}

        ai_processor.default_engine.generate_response = AsyncMock(
            return_value=mock_response
        )

        # Process conversation
        response = await ai_processor.process_conversation(
            conversation_id=1,
            user_message="Test message",
            system_prompt="Be helpful and concise",
            temperature=0.5,
            max_tokens=100,
        )

        # Verify complete flow
        assert response.content == "This is a test AI response."
        assert response.provider == "gemini"
        assert response.usage["total_tokens"] == 75

        # Verify all services were called appropriately
        ai_processor.conversation_service.get_conversation.assert_called_once()
        ai_processor.message_service.get_messages.assert_called_once()
        ai_processor.default_engine.generate_response.assert_called_once()

        # Verify messages were stored
        assert ai_processor.message_service.create_message.call_count == 2
