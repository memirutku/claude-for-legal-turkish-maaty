"""Anthropic SDK streaming adapter."""
from __future__ import annotations

import logging
from typing import AsyncIterator

from anthropic import AsyncAnthropic

logger = logging.getLogger(__name__)


async def stream_anthropic(
    api_key: str,
    model: str,
    system_prompt: str,
    user_message: str,
) -> AsyncIterator[str]:
    """Yield text chunks from Anthropic Messages API stream."""
    client = AsyncAnthropic(api_key=api_key)
    try:
        async with client.messages.stream(
            model=model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        ) as stream:
            async for text in stream.text_stream:
                yield text
    finally:
        await client.close()
