"""AI Engine abstraction layer for multiple AI providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, AsyncGenerator
from enum import Enum


class AIProvider(Enum):
    """Supported AI providers."""

    GEMINI = "gemini"
    CLAUDE = "claude"
    OPENAI = "openai"


@dataclass
class AIMessage:
    """Represents a message in AI conversation."""

    role: str  # "user", "assistant", "system"
    content: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AIResponse:
    """Response from AI engine."""

    content: str
    provider: AIProvider
    model: str
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AIContext:
    """Context for AI conversation."""

    messages: List[AIMessage]
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class AIEngineInterface(ABC):
    """Abstract interface for AI engines."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    @property
    @abstractmethod
    def provider(self) -> AIProvider:
        """Return the AI provider type."""
        pass

    @abstractmethod
    async def generate_response(self, context: AIContext, **kwargs) -> AIResponse:
        """Generate AI response for given context."""
        pass

    @abstractmethod
    async def generate_streaming_response(
        self, context: AIContext, **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streaming AI response for given context."""
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        """Validate API connection and credentials."""
        pass


class AIEngineError(Exception):
    """Base exception for AI engine errors."""

    def __init__(
        self, message: str, provider: AIProvider, error_code: Optional[str] = None
    ):
        super().__init__(message)
        self.provider = provider
        self.error_code = error_code


class AIEngineConnectionError(AIEngineError):
    """AI engine connection error."""

    pass


class AIEngineQuotaError(AIEngineError):
    """AI engine quota/rate limit error."""

    pass


class AIEngineValidationError(AIEngineError):
    """AI engine input validation error."""

    pass
