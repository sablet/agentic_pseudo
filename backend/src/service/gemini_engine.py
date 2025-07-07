"""Gemini AI engine implementation."""

import os
import asyncio
from typing import AsyncGenerator, Optional, Dict, Any
import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse

from .ai_engine import (
    AIEngineInterface,
    AIProvider,
    AIContext,
    AIResponse,
    AIMessage,
    AIEngineError,
    AIEngineConnectionError,
    AIEngineQuotaError,
    AIEngineValidationError,
)


class GeminiEngine(AIEngineInterface):
    """Gemini AI engine implementation."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        # Get API key from environment if not provided
        if api_key is None:
            api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise AIEngineValidationError(
                "Gemini API key is required", AIProvider.GEMINI, "missing_api_key"
            )

        super().__init__(api_key, model)

        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(model_name=self.model)

    @property
    def provider(self) -> AIProvider:
        """Return the AI provider type."""
        return AIProvider.GEMINI

    def _convert_messages_to_gemini_format(self, context: AIContext) -> str:
        """Convert AIContext messages to Gemini prompt format."""
        prompt_parts = []

        # Add system prompt if provided
        if context.system_prompt:
            prompt_parts.append(f"System: {context.system_prompt}")

        # Add conversation messages
        for message in context.messages:
            if message.role == "user":
                prompt_parts.append(f"Human: {message.content}")
            elif message.role == "assistant":
                prompt_parts.append(f"Assistant: {message.content}")
            # Skip system messages as they're handled separately

        return "\n\n".join(prompt_parts)

    async def generate_response(self, context: AIContext, **kwargs) -> AIResponse:
        """Generate AI response for given context."""
        try:
            # Convert context to Gemini format
            prompt = self._convert_messages_to_gemini_format(context)

            # Configure generation parameters
            generation_config = {
                "temperature": context.temperature,
            }

            if context.max_tokens:
                generation_config["max_output_tokens"] = context.max_tokens

            # Generate response
            response: GenerateContentResponse = await asyncio.to_thread(
                self.client.generate_content,
                prompt,
                generation_config=generation_config,
            )

            # Extract content
            if not response.text:
                raise AIEngineError(
                    "Empty response from Gemini", AIProvider.GEMINI, "empty_response"
                )

            # Extract usage information if available
            usage = None
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                usage = {
                    "prompt_tokens": getattr(
                        response.usage_metadata, "prompt_token_count", 0
                    ),
                    "completion_tokens": getattr(
                        response.usage_metadata, "candidates_token_count", 0
                    ),
                    "total_tokens": getattr(
                        response.usage_metadata, "total_token_count", 0
                    ),
                }

            return AIResponse(
                content=response.text,
                provider=self.provider,
                model=self.model,
                usage=usage,
                metadata={
                    "finish_reason": getattr(
                        response.candidates[0], "finish_reason", None
                    )
                    if response.candidates
                    else None,
                    "safety_ratings": getattr(
                        response.candidates[0], "safety_ratings", None
                    )
                    if response.candidates
                    else None,
                },
            )

        except Exception as e:
            # Handle specific Gemini errors
            error_message = str(e).lower()

            if "quota" in error_message or "rate" in error_message:
                raise AIEngineQuotaError(
                    f"Gemini quota/rate limit exceeded: {str(e)}",
                    AIProvider.GEMINI,
                    "quota_exceeded",
                )
            elif "unauthorized" in error_message or "api key" in error_message:
                raise AIEngineConnectionError(
                    f"Gemini authentication failed: {str(e)}",
                    AIProvider.GEMINI,
                    "auth_failed",
                )
            else:
                raise AIEngineError(
                    f"Gemini generation failed: {str(e)}",
                    AIProvider.GEMINI,
                    "generation_failed",
                )

    async def generate_streaming_response(
        self, context: AIContext, **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streaming AI response for given context."""
        try:
            # Convert context to Gemini format
            prompt = self._convert_messages_to_gemini_format(context)

            # Configure generation parameters
            generation_config = {
                "temperature": context.temperature,
            }

            if context.max_tokens:
                generation_config["max_output_tokens"] = context.max_tokens

            # Generate streaming response
            response_stream = await asyncio.to_thread(
                self.client.generate_content,
                prompt,
                generation_config=generation_config,
                stream=True,
            )

            # Yield content chunks
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            # Handle specific Gemini errors
            error_message = str(e).lower()

            if "quota" in error_message or "rate" in error_message:
                raise AIEngineQuotaError(
                    f"Gemini quota/rate limit exceeded: {str(e)}",
                    AIProvider.GEMINI,
                    "quota_exceeded",
                )
            elif "unauthorized" in error_message or "api key" in error_message:
                raise AIEngineConnectionError(
                    f"Gemini authentication failed: {str(e)}",
                    AIProvider.GEMINI,
                    "auth_failed",
                )
            else:
                raise AIEngineError(
                    f"Gemini streaming failed: {str(e)}",
                    AIProvider.GEMINI,
                    "streaming_failed",
                )

    async def validate_connection(self) -> bool:
        """Validate API connection and credentials."""
        try:
            # Simple test generation to validate connection
            test_context = AIContext(
                messages=[AIMessage(role="user", content="Hello")],
                temperature=0.1,
                max_tokens=10,
            )

            response = await self.generate_response(test_context)
            return bool(response.content)

        except AIEngineConnectionError:
            return False
        except Exception:
            return False
