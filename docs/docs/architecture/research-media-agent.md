---
title: Research Media Agent App
summary: Playground Next.js app for exploring media APIs and hosting internal docs.
tags:
  - research
  - explorer
  - docs
---

## Purpose

- Interactive catalog of media APIs (audio/video/data sources) with filters and modal details.
- Now also hosts architecture documentation with tag-based browsing.

## Stack

- Next.js 14 App Router, React 18.
- Tailwind for styling, `classnames` helper.
- Filtering/search built with `Fuse.js` (`filtering.ts`) supporting category, pricing, features, price caps, and sorting.
- Data source: `data/apis.json` for API catalog; markdown docs under `docs/architecture/` for internal docs.

## UX Components

- `app/page.tsx`: main explorer with search bar, filter sidebar, grid/list toggle, and detail modal.
- Docs page (added) renders markdown content with tag filtering and navigation.

