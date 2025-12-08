---
title: fal.ai Model Explorer
summary: Design for a filterable fal.ai model catalog that pulls live metadata and pricing via MCP.
tags:
  - fal.ai
  - models
  - pricing
  - mcp
---

## Goal

- Build a separate research app page that surfaces fal.ai model documentation in a filterable catalog (not touching Mixpost or other apps).
- Include up-to-date pricing (per second/per output) and link back to fal docs and OpenAPI details.
- Leverage the fal MCP to keep data fresh without hardcoding large tables.

## Data Source (MCP-first)

- Primary: fal MCP `getModels` (endpoint ids like `fal-ai/flux/dev`, `fal-ai/minimax/video-01/image-to-video`).
- Fields to capture: `endpoint_id`, `name`, `description`, `category` (text-to-image, image-to-video, music, 3d, editing), `status`, `pricing` (unit + rate), `latency`, `tags` (lora/controlnet/sdxl/flux), `input_schema` basics (context length, resolution hints).
- Pricing: use returned pricing block when present; otherwise scrape from `openapi` expansion or docs fallback (see `docs.fal.ai/model-apis`).
- Auth: read API key from env (`FAL_KEY`), never commit it. MCP handles transport; script only calls the MCP tool.

## Data Ingestion Flow

1) Script: `scripts/fal/fetch-models.ts`
   - Calls MCP `fal-ai getModels` with `expand=openapi-3.0` to capture pricing and request schema.
   - Normalizes into `FalModelRecord` (see schema below).
   - Writes `research/media-agent/data/fal-models.json`.
2) Optional enrichment: map categories from endpoint id (e.g., `flux` -> visuals/image-gen, `wan` -> video, `minimax` -> video, `hunyuan` -> 3d).
3) Validation: ensure `price.amount` exists; flag models missing pricing in a report so we can fill from docs manually.

## Schema (proposed)

```ts
type FalPricingModel = "per-second" | "per-image" | "per-video" | "per-audio" | "subscription";

interface FalModelRecord {
  id: string; // endpoint_id
  name: string;
  category: "visuals" | "video" | "audio" | "3d" | "utils";
  subcategory: string; // e.g., "text-to-image", "image-to-video"
  pricingModel: FalPricingModel;
  pricePerUnit?: number;
  priceUnit?: string; // "second", "image", "video-minute", etc.
  freeTier?: { limit: string; value: number; unit: string } | null;
  features: string[]; // lora, controlnet, img2img, upscaling, motion-lora, depth, etc.
  quality: 1 | 2 | 3 | 4 | 5;
  speed: "instant" | "fast" | "medium" | "slow";
  status: "active" | "deprecated";
  website: string; // model page
  docs: string; // direct docs link
  examples: { typescript?: string; python?: string; curl?: string };
}
```

## UI/UX Plan

- New route: `app/fal/page.tsx` (client) that reuses the existing explorer layout but scoped to fal models only.
- Filters:
  - Category (visuals/video/audio/3d/utils)
  - Pricing model (per-second/per-output/subscription) + free tier toggle
  - Features (lora, controlnet, img2img, inpainting, upscaling, video-length, fps)
  - Price slider (cap by `pricePerUnit`)
  - Status (active vs deprecated)
- Sorting: relevance (Fuse), price asc/desc, quality, latency (if present), name.
- Detail modal: show OpenAPI link, pricing block, latency notes, and ready-to-run code snippets using `@fal-ai/client`.
- Docs links: add quick links to `docs.fal.ai/model-apis` and the specific `endpoint_id` doc section.

## Implementation Steps

1) Add `scripts/fal/fetch-models.ts` to call the MCP and produce `data/fal-models.json`.
2) Add `lib/fal/types.ts` (or extend existing `lib/types.ts` with fal-specific enums) plus `lib/fal/normalize.ts` to map MCP responses into the schema.
3) Create `app/fal/page.tsx` that loads `fal-models.json`, derives filters via `deriveFilters`, and renders cards/modals adapted to fal fields (include latency/pricing badges).
4) Add docs entry in `_sidebar.md` pointing to this file for architecture reference.
5) Keep isolated: no changes to Mixpost or other production apps; all under `research/media-agent`.

## Open Questions / TODO

- Exact pricing keys per endpoint vary; confirm MCP `pricing` shape vs docs for consistency.
- Some endpoints have usage-based discounts; decide whether to show base rate only or tiered table.
- If MCP returns truncated lists without auth, ensure we fail loudly and surface a “connect API key” banner.

## Testing

- Unit test normalization for 2-3 known endpoints (Flux, minimax image-to-video, wan text-to-image) to ensure price parsing is stable.
- Snapshot test the filter derivation to confirm categories/features resolve as expected.

