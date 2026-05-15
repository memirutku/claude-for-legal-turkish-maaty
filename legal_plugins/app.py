"""Maaty Skill Template Service — FastAPI entrypoint."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from legal_plugins.config import settings
from legal_plugins.routes import catalog, health, invoke
from legal_plugins.skill_registry import registry


logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load skill registry on startup."""
    logger.info("Loading skills from %s", settings.PLUGINS_DIR)
    registry.load(settings.PLUGINS_DIR)
    logger.info("Service ready — %d skills available", registry.count())
    yield


app = FastAPI(
    title=settings.SERVICE_NAME,
    version=settings.VERSION,
    description="Skill Template Service for Maaty — runs claude-for-legal-turkish "
                "skills with user-provided LLM keys (BYOK).",
    lifespan=lifespan,
)

app.include_router(health.router, tags=["health"])
app.include_router(catalog.router, tags=["catalog"])
app.include_router(invoke.router, tags=["invoke"])
