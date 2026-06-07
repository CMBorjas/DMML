"""
AI Provider Registry
--------------------
Returns the active AIProvider based on the AI_PROVIDER environment variable.

    AI_PROVIDER=openai   → OpenAIProvider  (default)
    AI_PROVIDER=ollama   → OllamaProvider
"""

import os

from app.models.ai_providers.base import AIProvider

_provider_instance: AIProvider | None = None


def get_provider() -> AIProvider:
    """Return the singleton AI provider, instantiating it on first call."""
    global _provider_instance

    if _provider_instance is not None:
        return _provider_instance

    choice = os.getenv("AI_PROVIDER", "openai").lower().strip()

    if choice == "ollama":
        from app.models.ai_providers.ollama_provider import OllamaProvider
        _provider_instance = OllamaProvider()
    else:
        from app.models.ai_providers.openai_provider import OpenAIProvider
        _provider_instance = OpenAIProvider()

    return _provider_instance
