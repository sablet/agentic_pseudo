"""Integration tests for AI engine functionality."""

import asyncio
import os

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.ai_engine import AIContext, AIMessage, AIProvider
from src.service.ai_retry import AIRetryHandler, RetryConfig
from src.service.gemini_engine import GeminiEngine


class TestGeminiEngineIntegration:
    """Integration tests for Gemini engine."""

    @pytest.fixture
    def gemini_engine(self):
        """Create Gemini engine with test API key."""
        api_key = os.getenv("GEMINI_API_KEY", "test_key")
        return GeminiEngine(api_key=api_key, model="gemini-1.5-flash")

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
        assert gemini_engine.api_key is not None

    def test_convert_messages_to_gemini_format(self, gemini_engine, ai_context):
        """Test message format conversion."""
        prompt = gemini_engine._convert_messages_to_gemini_format(ai_context)

        assert "System: You are a helpful assistant." in prompt
        assert "Human: Hello, how are you?" in prompt

    @pytest.mark.asyncio
    async def test_gemini_engine_with_rate_limiting(self, gemini_engine, ai_context):
        """Test Gemini engine with rate limiting handling."""
        # Skip test if no real API key
        if gemini_engine.api_key == "test_key":
            pytest.skip("No real API key available")

        # Test with rate limiting consideration
        try:
            response = await gemini_engine.generate_response(ai_context)
            assert response.content is not None
            assert response.provider == AIProvider.GEMINI
            assert response.model == "gemini-1.5-flash"
            
            # Wait to respect rate limits (free tier: 10 requests/minute)
            await asyncio.sleep(6)  # 60s / 10 requests = 6s per request
            
        except Exception as e:
            if "quota" in str(e).lower() or "rate" in str(e).lower():
                pytest.skip(f"Rate limit exceeded: {e}")
            else:
                raise

    @pytest.mark.asyncio
    async def test_gemini_engine_connection_validation(self, gemini_engine):
        """Test connection validation with rate limiting."""
        # Skip test if no real API key
        if gemini_engine.api_key == "test_key":
            pytest.skip("No real API key available")

        try:
            is_valid = await gemini_engine.validate_connection()
            assert isinstance(is_valid, bool)
            
            # Wait to respect rate limits
            await asyncio.sleep(6)
            
        except Exception as e:
            if "quota" in str(e).lower() or "rate" in str(e).lower():
                pytest.skip(f"Rate limit exceeded: {e}")
            else:
                raise


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
