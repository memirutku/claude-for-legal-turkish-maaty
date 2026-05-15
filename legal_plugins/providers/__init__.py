"""Provider registry — dispatches to per-provider stream function."""
from __future__ import annotations

from typing import AsyncIterator

from legal_plugins.providers.anthropic_provider import stream_anthropic
from legal_plugins.providers.gemini_provider import stream_gemini
from legal_plugins.providers.openai_provider import stream_openai


SUPPORTED_PROVIDERS = {"gemini", "openai", "anthropic"}


async def stream_skill(
    provider: str,
    api_key: str,
    model: str,
    system_prompt: str,
    user_message: str,
) -> AsyncIterator[str]:
    """Dispatch to the right provider and yield text chunks."""
    if provider == "gemini":
        async for chunk in stream_gemini(api_key, model, system_prompt, user_message):
            yield chunk
    elif provider == "openai":
        async for chunk in stream_openai(api_key, model, system_prompt, user_message):
            yield chunk
    elif provider == "anthropic":
        async for chunk in stream_anthropic(api_key, model, system_prompt, user_message):
            yield chunk
    else:
        raise ValueError(f"Unsupported provider: {provider}")
