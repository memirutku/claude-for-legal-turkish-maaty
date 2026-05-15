# Maaty Skill Template Service (`legal_plugins/`)

This directory contains the **FastAPI service** that lets Maaty production
run the skill manifests from this repository over Maaty's own BYOK LLM
stack (Gemini / OpenAI / Anthropic). Claude Code CLI is **not** required
at runtime.

## How it works

```
Maaty backend (api container)
    │
    │ POST /skills/{skill_id}/invoke
    │ Headers: X-AI-Provider, X-AI-Model, X-AI-Key, X-User-Id, X-Session-Id
    │ Body: { "input": "<user text>" }
    ▼
legal_plugins service (this directory, in its own container)
    │
    │ 1. Look up skill in registry (skill_loader parses SKILL.md frontmatter)
    │ 2. Use skill.instructions as system prompt
    │ 3. Use request.input as user message
    │ 4. Call provider SDK with X-AI-Key
    │ 5. Stream tokens back as SSE
    ▼
Maaty backend → ChatPanel → user UI
```

API keys are **never** stored in the container — every invoke request
carries its own `X-AI-Key` header, decrypted by Maaty backend just before
the call. No env-var secrets.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness + skill count |
| `GET` | `/skills` | Catalog (all skills + grouped by category) |
| `GET` | `/skills/{id}` | One skill's metadata |
| `POST` | `/skills/{id}/invoke` | Run a skill, stream output as SSE |

## Pilot Skills (Faz 6)

8 skills shipped in `Dockerfile` COPY (see Maaty plan):

- `pia-generation` — KVKK / Privacy
- `review`, `nda-review` — Sözleşme
- `diligence-issue-extraction` — Corporate / M&A
- `policy-drafting` — Employment
- `reg-feed-watcher` — Regulatory
- `cease-desist` — IP
- `demand-intake` — Litigation

To add more skills later, edit `Dockerfile` `COPY` lines.

## Run locally

```bash
# From repo root
docker build -t legal_plugins-test .
docker run --rm -p 8003:8000 legal_plugins-test

# In another shell
curl http://localhost:8003/health
curl http://localhost:8003/skills | jq

# Invoke (Gemini example)
curl -N -X POST http://localhost:8003/skills/pia-generation/invoke \
  -H "Content-Type: application/json" \
  -H "X-AI-Provider: gemini" \
  -H "X-AI-Model: gemini-2.5-pro" \
  -H "X-AI-Key: $GEMINI_KEY" \
  -d '{"input":"Şirket içi finansal yazılım PIA — kullanıcı: muhasebe ekibi (35 kişi), veri: maaş + IBAN + TC kimlik"}'
```

## Configuration

| Env var | Default | Purpose |
|---|---|---|
| `PLUGINS_DIR` | `/app/plugins` | Where skill_loader scans for `*/skills/*/SKILL.md` |
| `LOG_LEVEL` | `info` | Standard Python log level |
| `PORT` | `8000` | Uvicorn bind port (also used in healthcheck) |

## License

This service is part of the `memirutku/claude-for-legal-turkish-maaty`
fork. Apache 2.0 — see top-level `LICENSE` and `NOTICE`.
