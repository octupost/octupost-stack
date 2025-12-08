---
title: Frontend Apps
summary: Technologies and responsibilities of Octupost web apps.
tags:
  - frontend
  - nextjs
  - supabase
---

## Apps

- `octupost`: Next.js 16 App Router, Supabase SSR client for auth/session, onboarding guard middleware, Sentry hooks. Primary surface for authentication, onboarding, dashboard.
- `octupost-studio`: Next.js editor experience (React 19), Tailwind, Radix UI, Remotion-ready video editor versions, Supabase client for shared auth cookies.
- `octupost-mixpost`: Laravel + Inertia-based social scheduling (standalone vendor app) living in the monorepo.
- `research/media-agent`: Next.js 14 playground for API exploration and now docs browsing.

## Auth & Sessions

- Supabase JS client in browser (`createBrowserClient`) and SSR (`createServerClient`) with cookies shared across subdomains when `NODE_ENV=production` (`.octupost.com`).
- Middleware (`octupost/lib/supabase/middleware.ts`) refreshes sessions and enforces onboarding redirects.

## Styling & UI

- Tailwind CSS + design tokens; Radix primitives for controls; classnames/clsx utilities.
- Media/editor UX components in `octupost-studio/components/editor` with per-version folders.

## Observability

- Sentry hooks in `octupost` and `octupost-studio` (edge/server/client configs). PostHog optional via env flags in studio.

