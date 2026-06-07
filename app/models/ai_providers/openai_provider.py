"""
OpenAI Provider
---------------
Uses LangChain + FAISS + OpenAI for RAG-backed NPC dialogue.
Requires: OPENAI_API_KEY environment variable.

The retrieval chain is cached at module level and invalidated
after CACHE_TTL_SECONDS to avoid re-embedding on every request
(important for laptop / low-resource environments).
"""

import os
import time

from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, OpenAI

from app.models.ai_providers.base import AIProvider

CACHE_TTL_SECONDS = 300  # Re-build the chain at most every 5 minutes

_chain_cache = None
_chain_built_at: float = 0.0


def _get_chain():
    """Return a cached RetrievalQA chain, rebuilding if stale or absent."""
    global _chain_cache, _chain_built_at

    now = time.monotonic()
    if _chain_cache is not None and (now - _chain_built_at) < CACHE_TTL_SECONDS:
        return _chain_cache

    # Lazy validation — only fail when actually needed
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY is not set. "
            "Add it to your .env file or switch to AI_PROVIDER=ollama."
        )

    # Import here to avoid circular imports with the campaign model
    from app.models.campaign import get_campaign_data

    campaign_data = get_campaign_data()
    if not campaign_data:
        raise ValueError(
            "No campaign data found. "
            "Seed the database via POST /debug/seed_campaign_logs first."
        )

    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    vectorstore = FAISS.from_texts(campaign_data, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    llm = OpenAI(openai_api_key=api_key)
    _chain_cache = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    _chain_built_at = now
    return _chain_cache


def _invoke(prompt: str) -> str:
    chain = _get_chain()
    result = chain.invoke({"query": prompt})
    if isinstance(result, dict) and "result" in result:
        return result["result"].strip()
    if isinstance(result, str):
        return result.strip()
    raise ValueError(f"Unexpected LangChain response format: {result}")


class OpenAIProvider(AIProvider):
    """LangChain RAG provider backed by OpenAI models."""

    def generate(self, query: str) -> str:
        return _invoke(query)

    def generate_with_context(
        self,
        query: str,
        npc_name: str,
        recent_interactions: list[str],
    ) -> str:
        history_block = "\n".join(recent_interactions)
        prompt = (
            f"You are {npc_name}, an NPC in a tabletop role-playing game. "
            f"Stay in character and respond naturally.\n\n"
            f"Recent interactions:\n{history_block}\n\n"
            f"Player: {query}\n"
            f"{npc_name}:"
        )
        return _invoke(prompt)
