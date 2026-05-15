"""Skill invoke route — streams LLM output as SSE."""
from __future__ import annotations

import json
import logging
from typing import AsyncIterator

from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from legal_plugins.config import settings
from legal_plugins.providers import SUPPORTED_PROVIDERS, stream_skill
from legal_plugins.skill_registry import registry

logger = logging.getLogger(__name__)

router = APIRouter()


class InvokeRequest(BaseModel):
    input: str
    context: dict | None = None  # Reserved for future use (chat history, attachments)


def _sse(event: dict) -> str:
    """Format a dict as one SSE data line."""
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


@router.post("/skills/{skill_id}/invoke")
async def invoke_skill(
    skill_id: str,
    request: InvokeRequest,
    raw_request: Request,
    x_ai_provider: str = Header(..., alias="X-AI-Provider"),
    x_ai_key: str = Header(..., alias="X-AI-Key"),
    x_ai_model: str | None = Header(default=None, alias="X-AI-Model"),
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    x_session_id: str | None = Header(default=None, alias="X-Session-Id"),
) -> StreamingResponse:
    """Run a skill against the user-provided LLM provider/key and stream output."""
    skill = registry.get(skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail=f"Skill {skill_id!r} not found")

    provider = x_ai_provider.lower().strip()
    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider!r}")

    model = (x_ai_model or settings.DEFAULT_MODELS.get(provider) or "").strip()
    if not model:
        raise HTTPException(status_code=400, detail="Missing X-AI-Model header and no default")

    logger.info(
        "Invoke skill=%s provider=%s model=%s user=%s session=%s",
        skill_id, provider, model, x_user_id, x_session_id,
    )

    async def event_stream() -> AsyncIterator[str]:
        yield _sse({"type": "status", "content": f"{skill.name} başlatılıyor..."})
        try:
            async for chunk in stream_skill(
                provider=provider,
                api_key=x_ai_key,
                model=model,
                system_prompt=skill.system_prompt(),
                user_message=request.input,
            ):
                # Client disconnect kontrol
                if await raw_request.is_disconnected():
                    logger.info("Client disconnected — aborting skill stream")
                    return
                yield _sse({"type": "token", "content": chunk})
            yield _sse({"type": "done"})
        except Exception as exc:
            logger.exception("Skill invocation failed: %s", exc)
            yield _sse({"type": "error", "content": str(exc)})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
