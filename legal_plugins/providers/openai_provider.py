"""OpenAI SDK streaming adapter."""
from __future__ import annotations

import logging
from typing import AsyncIterator

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


async def stream_openai(
    api_key: str,
    model: str,
    system_prompt: str,
    user_message: str,
) -> AsyncIterator[str]:
    """Yield text chunks from OpenAI Responses/Chat stream."""
    client = AsyncOpenAI(api_key=api_key)
    try:
        stream = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            stream=True,
        )
        async for event in stream:
            if not event.choices:
                continue
            delta = event.choices[0].delta
            if delta and delta.content:
                yield delta.content
    finally:
        await client.close()
