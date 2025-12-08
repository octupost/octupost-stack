---
title: Infrastructure & Operations
summary: Shared services, environments, and monitoring for Octupost.
tags:
  - infra
  - operations
  - monitoring
---

## Environments

- Local: Next.js apps on 3000/3001, FastAPI on 8000. Supabase creds pulled from shared `.env` files at repo root (`.env.local`, `.env.development`).
- Production: shared auth cookies on `.octupost.com` domain; environment-specific Supabase keys and Sentry DSNs.

## Auth & Data

- Supabase as auth/session and primary data store; clients use anon key, backend uses service role key.
- Cookies configured for cross-subdomain sharing in production.

## Observability

- Sentry client/server/edge configs in both `octupost` and `octupost-studio`.
- PostHog optional in studio (env-gated).

## Background Processing

- Inngest for orchestration; Fal AI for generation work; optional Redis for job state caching.

## Deployment Notes

- Next.js apps can run in standard Node targets; middleware handles auth refresh.
- FastAPI served by `uvicorn app.main:app --port 8000`; ensure envs for Fal/Inngest/Supabase are present.

