"""Unit tests for AI engine functionality."""

import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch

from src.service.ai_engine import AIContext, AIMessage, AIProvider
from src.service.gemini_engine import GeminiEngine
from src.service.ai_retry import AIRetryHandler, RetryConfig


class TestGeminiEngine:
    """Unit tests for Gemini engine."""
    
    @pytest.fixture
    def gemini_engine(self):
        """Create Gemini engine with mock API key."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}):
            return GeminiEngine(model="gemini-1.5-flash")
    
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
        
        # Mock generate_content as AsyncMock since we use asyncio.to_thread
        with patch('asyncio.to_thread', new_callable=AsyncMock) as mock_to_thread:
            mock_to_thread.return_value = mock_response
            
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


class TestAIEngineIntegration:
    """Integration tests for AI engine interfaces."""
    
    def test_ai_message_creation(self):
        """Test AI message creation."""
        message = AIMessage(
            role="user",
            content="Test message",
            metadata={"timestamp": "2025-01-01"}
        )
        
        assert message.role == "user"
        assert message.content == "Test message"
        assert message.metadata["timestamp"] == "2025-01-01"
    
    def test_ai_context_creation(self):
        """Test AI context creation."""
        messages = [
            AIMessage(role="user", content="Hello"),
            AIMessage(role="assistant", content="Hi there!")
        ]
        
        context = AIContext(
            messages=messages,
            system_prompt="Be helpful",
            temperature=0.8,
            max_tokens=200
        )
        
        assert len(context.messages) == 2
        assert context.system_prompt == "Be helpful"
        assert context.temperature == 0.8
        assert context.max_tokens == 200
    
    def test_ai_provider_enum(self):
        """Test AI provider enumeration."""
        assert AIProvider.GEMINI.value == "gemini"
        assert AIProvider.CLAUDE.value == "claude"
        assert AIProvider.OPENAI.value == "openai"