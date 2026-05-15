# Maaty Skill Template Service container — runs claude-for-legal-turkish
# skill manifests via Maaty BYOK LLM stack.
#
# Build context: this repository root (fork repo).
# Skill manifests are copied selectively into /app/plugins (only pilot 8).

FROM python:3.12-slim

WORKDIR /app

# System deps — kept minimal; only gcc/g++ for any source-only wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install service dependencies first (layer cache)
COPY legal_plugins/pyproject.toml /app/legal_plugins/pyproject.toml
WORKDIR /app/legal_plugins
RUN pip install --no-cache-dir -e .

# Copy service code
WORKDIR /app
COPY legal_plugins /app/legal_plugins

# Copy pilot skill manifests (8 skills across 7 plugins)
# Each pilot skill ships with its own SKILL.md (and optional references/)
COPY privacy-legal/skills/pia-generation /app/plugins/privacy-legal/skills/pia-generation
COPY commercial-legal/skills/review /app/plugins/commercial-legal/skills/review
COPY commercial-legal/skills/nda-review /app/plugins/commercial-legal/skills/nda-review
COPY corporate-legal/skills/diligence-issue-extraction /app/plugins/corporate-legal/skills/diligence-issue-extraction
COPY employment-legal/skills/policy-drafting /app/plugins/employment-legal/skills/policy-drafting
COPY regulatory-legal/skills/reg-feed-watcher /app/plugins/regulatory-legal/skills/reg-feed-watcher
COPY ip-legal/skills/cease-desist /app/plugins/ip-legal/skills/cease-desist
COPY litigation-legal/skills/demand-intake /app/plugins/litigation-legal/skills/demand-intake

ENV PLUGINS_DIR=/app/plugins
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health', timeout=5).raise_for_status()" || exit 1

# Run via uvicorn — single worker is fine for I/O-bound LLM streaming
CMD ["uvicorn", "legal_plugins.app:app", "--host", "0.0.0.0", "--port", "8000"]
