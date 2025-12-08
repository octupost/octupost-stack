---
title: Backend Services
summary: FastAPI service for AI generation, job orchestration, and supporting pieces.
tags:
  - backend
  - fastapi
  - inngest
  - fal-ai
---

## FastAPI (`octupost-api`)

- Framework: FastAPI, served via Uvicorn.
- Configuration: `app/config.py` (pydantic-settings) loads env from shared `.env` files.
- Auth/Config: uses Supabase service role key; CORS defaults include local ports 3000/3001.
- Optional Redis for job state.
- Sentry SDK (FastAPI integration) available via env vars.

## Job Orchestration (Inngest)

- Inngest dev server recommended in local (`npx inngest-cli dev`).
- Event keys + signing keys configured via env.
- Pattern: API enqueues generation jobs -> Inngest worker executes -> updates job status (Redis or in-memory) -> results returned via polling endpoint.

## AI Providers (Fal AI)

- Models specified in README: Flux/SDXL for TTI, Wan/Minimax/Luma for TTV/ITV, Kokoro/F5 for TTS.
- `FAL_KEY` env required.

## API Surface

- Generation endpoints: `/api/generate/image`, `/video`, `/video-from-image`, `/speech`.
- Job endpoints: `/api/jobs/{job_id}` for status/result, `/api/jobs/{job_id}/cancel`.

## Data Flow (backend)

- Request validated in FastAPI -> job created (ULID) -> Inngest event dispatched -> Fal AI call -> status stored -> client polls status endpoint.

