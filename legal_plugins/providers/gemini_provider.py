"""Google Gemini SDK streaming adapter."""
from __future__ import annotations

import logging
from typing import AsyncIterator

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


async def stream_gemini(
    api_key: str,
    model: str,
    system_prompt: str,
    user_message: str,
) -> AsyncIterator[str]:
    """Yield text chunks from Gemini generate_content_stream."""
    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        max_output_tokens=4096,
    )
    async for chunk in await client.aio.models.generate_content_stream(
        model=model,
        contents=user_message,
        config=config,
    ):
        if chunk.text:
            yield chunk.text
