---
title: Octupost Architecture Overview
summary: High-level view of the Octupost stack across web apps, backend services, and shared services.
tags:
  - architecture
  - overview
  - stack
---

## Scope

Octupost spans multiple apps and services:

- User-facing web apps: `octupost` (auth + onboarding + dashboard), `octupost-studio` (rich editor), `octupost-mixpost` (social scheduling).
- Backend: `octupost-api` (FastAPI + Inngest + Fal AI).
- Shared services: Supabase (auth/session + DB), Redis (optional job state), Sentry (monitoring), PostHog (optional analytics).
- Research: `research/media-agent` (API explorer and docs browser).

## Principles

- Keep auth centralized via Supabase; share session cookies across subdomains (`.octupost.com` in prod).
- Asynchronous media generation through Inngest + Fal AI with optional Redis for job state.
- Next.js App Router for all web apps; client/server split per route; edge-friendly middleware for auth/session refresh.

## Environments

- Local: Next.js apps on 3000/3001, FastAPI on 8000, Supabase env via shared `.env` files.
- Production: Supabase auth/domain cookies, Sentry optional in all apps, PostHog optional.

