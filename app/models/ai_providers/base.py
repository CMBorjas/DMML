"""
AI Provider Interface
---------------------
Defines the abstract base class all AI providers must implement.
Select a provider at runtime via the AI_PROVIDER environment variable:
    AI_PROVIDER=openai   (default) - requires OPENAI_API_KEY
    AI_PROVIDER=ollama             - requires OLLAMA_BASE_URL (default: http://localhost:11434)
"""

from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Abstract interface for an LLM-backed suggestion provider."""

    @abstractmethod
    def generate(self, query: str) -> str:
        """Generate a narrative response for the given query string."""
        ...

    @abstractmethod
    def generate_with_context(
        self,
        query: str,
        npc_name: str,
        recent_interactions: list[str],
    ) -> str:
        """
        Generate a response with NPC persona and recent chat context.

        Args:
            query: The player's current message.
            npc_name: Name of the NPC being portrayed.
            recent_interactions: Last N chat turns as plain strings.
        """
        ...

    @abstractmethod
    def generate_stream_with_context(
        self,
        query: str,
        npc_name: str,
        recent_interactions: list[str],
    ):
        """
        Generate a streamed response (yields chunks).
        """
        ...
