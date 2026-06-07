"""
AI Facade
---------
Public interface for AI generation. Routes requests to the active
provider (OpenAI or Ollama) configured via AI_PROVIDER env var.

Usage:
    from app.models.ai import generate_suggestion, generate_quest, generate_loot
"""

from dotenv import load_dotenv

load_dotenv()

from app.models.ai_providers import get_provider  # noqa: E402


def generate_suggestion(query: str) -> str:
    """Generate a general narrative suggestion from the AI provider."""
    return get_provider().generate(query)


def generate_suggestion_with_context(
    query: str,
    npc_name: str,
    recent_interactions: list[str],
) -> str:
    """
    Generate an in-character NPC response using recent chat history.

    Args:
        query: The player's latest message.
        npc_name: Name of the NPC for persona framing.
        recent_interactions: Recent chat turns (plain strings, oldest first).
    """
    return get_provider().generate_with_context(query, npc_name, recent_interactions)


def generate_quest(npc_name: str, location: str) -> str:
    """Generate an AI-written quest request from a named NPC at a location."""
    prompt = (
        f"{npc_name}, a knowledgeable NPC located in {location}, "
        "wants to assign a task to adventurers. "
        "Generate a detailed, immersive quest they might request."
    )
    return generate_suggestion(prompt)


def generate_loot(quest_name: str) -> str:
    """Generate themed loot rewards for a completed quest."""
    prompt = (
        f"Based on the completion of the quest '{quest_name}', "
        "generate a suitable and thematic loot reward for the adventuring party."
    )
    return generate_suggestion(prompt)
