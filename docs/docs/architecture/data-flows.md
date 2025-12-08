---
title: Key Data Flows
summary: How frontend apps talk to backend services, auth, and generation pipelines.
tags:
  - flows
  - auth
  - generation
---

## Auth Flow

- User signs in via Supabase auth in `octupost`; cookies set for `.octupost.com` (production).
- Middleware refreshes tokens on requests and redirects to onboarding/dashboard depending on profile state.
- `octupost-studio` and other subdomains reuse the same Supabase session via shared cookies.

## Media Generation Flow

1) Frontend (studio/app) sends generation request to FastAPI (`octupost-api`).
2) FastAPI creates job (ULID), dispatches Inngest event with payload and model selection.
3) Inngest worker calls Fal AI model; optional Redis stores job status/result.
4) Client polls `/api/jobs/{job_id}` for status and result URLs/blobs.
5) Cancellation: `/api/jobs/{job_id}/cancel` if still pending.

## Content & Assets

- Media assets managed per app context; editor components (Remotion-ready) live in `octupost-studio`.
- Supabase storage not referenced directly in code here; backend can integrate via Supabase service role if needed.

