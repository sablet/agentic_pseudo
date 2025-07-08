"""Enhanced pytest tests for Gemini engine with comprehensive verification."""

import asyncio
import os

import pytest
from dotenv import load_dotenv

from src.service.ai_engine import (
    AIContext,
    AIEngineConnectionError,
    AIEngineError,
    AIEngineQuotaError,
    AIEngineValidationError,
    AIMessage,
    AIProvider,
)
from src.service.gemini_constants import GeminiConfig, GeminiModels
from src.service.gemini_engine import GeminiEngine

# Load environment variables
load_dotenv('../.env')


class TestGeminiEngineEnhanced:
    """Enhanced test suite for Gemini engine."""

    def test_gemini_constants_consistency(self):
        """Test that constants are properly defined and consistent."""
        # Verify model constants
        assert GeminiModels.DEFAULT_MODEL == GeminiModels.GEMINI_2_5_FLASH
        assert GeminiModels.GEMINI_2_5_FLASH == "gemini-2.5-flash"
        assert GeminiConfig.DEFAULT_TEMPERATURE == 0.0
        assert GeminiConfig.get_dspy_model_name() == "gemini/gemini-2.5-flash"

    def test_gemini_engine_initialization(self):
        """Test Gemini engine initialization with constants."""
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "test_key")
        
        engine = GeminiEngine(api_key=api_key)
        assert engine.model == GeminiModels.DEFAULT_MODEL
        assert engine.api_key == api_key

    def test_gemini_engine_initialization_with_custom_model(self):
        """Test Gemini engine initialization with custom model."""
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "test_key")
        custom_model = "gemini-1.5-flash"
        
        engine = GeminiEngine(api_key=api_key, model=custom_model)
        assert engine.model == custom_model

    def test_gemini_engine_missing_api_key(self):
        """Test error handling when API key is missing."""
        # Clear environment variables and pass None explicitly
        old_gemini_key = os.environ.pop("GEMINI_API_KEY", None)
        old_google_key = os.environ.pop("GOOGLE_API_KEY", None)
        
        try:
            with pytest.raises(AIEngineValidationError) as excinfo:
                GeminiEngine(api_key=None)
            assert "Gemini API key is required" in str(excinfo.value)
        finally:
            # Restore environment variables
            if old_gemini_key:
                os.environ["GEMINI_API_KEY"] = old_gemini_key
            if old_google_key:
                os.environ["GOOGLE_API_KEY"] = old_google_key

    @pytest.mark.asyncio
    async def test_context_to_gemini_format_conversion(self):
        """Test message format conversion to Gemini format."""
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "test_key")
        engine = GeminiEngine(api_key=api_key)

        context = AIContext(
            messages=[
                AIMessage(role="user", content="Hello"),
                AIMessage(role="assistant", content="Hi there!"),
                AIMessage(role="user", content="How are you?")
            ],
            system_prompt="You are a helpful assistant."
        )

        prompt = engine._convert_messages_to_gemini_format(context)

        expected_parts = [
            "System: You are a helpful assistant.",
            "Human: Hello",
            "Assistant: Hi there!",
            "Human: How are you?"
        ]

        for part in expected_parts:
            assert part in prompt

    @pytest.mark.asyncio
    async def test_gemini_engine_real_api_call(self):
        """Test actual API call to Gemini if API key is available."""
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            pytest.skip("No Gemini API key available")
            
        engine = GeminiEngine(api_key=api_key)
        
        context = AIContext(
            messages=[AIMessage(role="user", content="Say hello in one word")],
            temperature=0.0,
            max_tokens=10
        )
        
        try:
            response = await engine.generate_response(context)
            assert response.content is not None
            assert len(response.content) > 0
            assert response.provider == AIProvider.GEMINI
            
            # Respect rate limits (free tier: 10 requests/minute)
            await asyncio.sleep(6)
            
        except Exception as e:
            if "quota" in str(e).lower() or "rate" in str(e).lower():
                pytest.skip(f"Rate limit exceeded: {e}")
            else:
                raise

    @pytest.mark.asyncio
    async def test_gemini_engine_connection_validation(self):
        """Test connection validation."""
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            pytest.skip("No Gemini API key available")
            
        engine = GeminiEngine(api_key=api_key)
        
        try:
            is_valid = await engine.validate_connection()
            assert isinstance(is_valid, bool)
            
            # Respect rate limits
            await asyncio.sleep(6)
            
        except Exception as e:
            if "quota" in str(e).lower() or "rate" in str(e).lower():
                pytest.skip(f"Rate limit exceeded: {e}")
            else:
                raise

    @pytest.mark.asyncio
    async def test_gemini_engine_error_handling(self):
        """Test error handling with invalid API key."""
        engine = GeminiEngine(api_key="invalid_key")
        
        context = AIContext(
            messages=[AIMessage(role="user", content="Test")],
            temperature=0.0
        )
        
        with pytest.raises(AIEngineError):
            await engine.generate_response(context)

    @pytest.mark.asyncio
    async def test_gemini_engine_streaming_response(self):
        """Test streaming response functionality."""
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            pytest.skip("No Gemini API key available")
            
        engine = GeminiEngine(api_key=api_key)
        
        context = AIContext(
            messages=[AIMessage(role="user", content="Count from 1 to 3")],
            temperature=0.0,
            max_tokens=20
        )
        
        try:
            chunks = []
            async for chunk in engine.generate_stream(context):
                chunks.append(chunk)
                
            assert len(chunks) > 0
            full_response = ''.join(chunk.content for chunk in chunks)
            assert len(full_response) > 0
            
            # Respect rate limits
            await asyncio.sleep(6)
            
        except Exception as e:
            if "quota" in str(e).lower() or "rate" in str(e).lower():
                pytest.skip(f"Rate limit exceeded: {e}")
            else:
                raise

    def test_gemini_config_default_values(self):
        """Test default configuration values."""
        assert GeminiConfig.DEFAULT_TEMPERATURE == 0.0
        assert GeminiConfig.DSPY_MODEL_FORMAT == "gemini/{model}"
        assert GeminiConfig.get_dspy_model_name() == "gemini/gemini-2.5-flash"