"""Common enums used across the application."""

from enum import Enum


class AgentStatus(str, Enum):
    """Agent status enum."""
    TODO = "todo"
    DOING = "doing"
    WAITING = "waiting"
    NEEDS_INPUT = "needs_input"


class ExecutionEngine(str, Enum):
    """Execution engine enum."""
    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    CLAUDE_CODE = "claude-code"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    CLAUDE_3_5_SONNET = "claude-3.5-sonnet"
    GEMINI_1_5_PRO = "gemini-1.5-pro"