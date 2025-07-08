"""Gemini AI engine constants."""


class GeminiModels:
    """Gemini model constants."""

    # Primary model for general use
    GEMINI_2_5_FLASH = "gemini-2.5-flash"

    # Default model
    DEFAULT_MODEL = GEMINI_2_5_FLASH


class GeminiConfig:
    """Gemini configuration constants."""

    # Default temperature (0 for deterministic responses)
    DEFAULT_TEMPERATURE = 0.0

    # DSPy model format
    DSPY_MODEL_FORMAT = "gemini/{model}"

    @classmethod
    def get_dspy_model_name(cls, model: str = None) -> str:
        """Get DSPy format model name."""
        if model is None:
            model = GeminiModels.DEFAULT_MODEL
        return cls.DSPY_MODEL_FORMAT.format(model=model)
