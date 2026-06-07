"""
Ollama Provider
---------------
Uses a locally-running Ollama server for NPC dialogue.
Great for offline / laptop use — no API key or internet required.

Requires:
    OLLAMA_BASE_URL  (default: http://localhost:11434)
    OLLAMA_MODEL     (default: llama3)

Campaign context is injected directly into the system prompt
instead of using FAISS, keeping memory usage minimal on a laptop.
"""

import os

import requests

from app.models.ai_providers.base import AIProvider

_DEFAULT_BASE_URL = "http://localhost:11434"
_DEFAULT_MODEL = "llama3"


def _get_campaign_context() -> str:
    """Fetch a brief campaign summary to inject into the system prompt."""
    try:
        from app.models.campaign import get_campaign_data

        data = get_campaign_data()
        # Keep it short to fit within context windows on small local models
        snippet = "\n".join(data[:6])  # At most 6 log entries
        return f"Campaign context:\n{snippet}\n" if snippet else ""
    except Exception:
        return ""


class OllamaProvider(AIProvider):
    """LLM provider that calls a local Ollama server."""

    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", _DEFAULT_BASE_URL).rstrip("/")
        self.model = os.getenv("OLLAMA_MODEL", _DEFAULT_MODEL)

    def _chat(self, system: str, user: str) -> str:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()["message"]["content"].strip()
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Could not connect to Ollama at {self.base_url}. "
                "Is Ollama running? Start it with: ollama serve"
            )

    def generate(self, query: str) -> str:
        campaign_ctx = _get_campaign_context()
        system = (
            "You are an AI Dungeon Master assistant. "
            "Generate creative, immersive tabletop RPG content.\n"
            + campaign_ctx
        )
        return self._chat(system, query)

    def generate_with_context(
        self,
        query: str,
        npc_name: str,
        recent_interactions: list[str],
    ) -> str:
        campaign_ctx = _get_campaign_context()
        history_block = "\n".join(recent_interactions)
        system = (
            f"You are {npc_name}, an NPC in a tabletop role-playing game. "
            f"Stay in character at all times and respond naturally.\n"
            f"{campaign_ctx}"
        )
        user = (
            f"Recent interactions:\n{history_block}\n\n"
            f"Player: {query}\n"
            f"{npc_name}:"
        )
        return self._chat(system, user)
