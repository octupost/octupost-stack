# Billing System Documentation

This document explains how the billing system calculates and displays costs for AI generation requests (video, audio, image, speech, etc.).

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Pricing Strategies](#pricing-strategies)
4. [Provider Configuration Schema](#provider-configuration-schema)
5. [Credit Reservation System](#credit-reservation-system)
6. [Failure & Refund Handling](#failure--refund-handling)
7. [Frontend Price Calculation](#frontend-price-calculation)
8. [Backend Cost Calculation](#backend-cost-calculation)
9. [Price Display](#price-display)
10. [Examples](#examples)
11. [Key Files](#key-files)

---

## System Overview

The billing system uses a **centralized price configuration** stored in `provider.json`. Each AI model/provider has its own pricing configuration that supports multiple pricing strategies. The system calculates costs in real-time on both frontend (for display) and backend (for validation/billing).

### Core Principles

- **Pay-per-use**: Users are charged based on actual usage (duration, characters, or per request)
- **Transparent pricing**: Costs are shown before generation starts
- **Dynamic calculation**: Prices adjust based on user-selected parameters (resolution, audio, etc.)
- **Tiered pricing**: Some models have different prices based on quality/resolution

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SHARED PACKAGE                                  │
│                     packages/shared/src/registry/                           │
│                                                                              │
│   provider.json ──► Pricing configuration for all models                    │
│   pricing.ts    ──► Price calculation functions (frontend)                  │
│   types.ts      ──► TypeScript types for pricing                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
┌─────────────────────────────┐     ┌─────────────────────────────┐
│         FRONTEND            │     │          BACKEND            │
│                             │     │                             │
│  video-generator.tsx        │     │  api/app/registry/          │
│  image-generator.tsx        │     │  ├── reader.py              │
│  speech-generator.tsx       │     │  └── types.py               │
│  etc.                       │     │                             │
│                             │     │  calculate_cost() function  │
│  Uses: calculatePrice()     │     │  for backend validation     │
│        formatPrice()        │     │                             │
│        getDisplayPrice()    │     │                             │
└─────────────────────────────┘     └─────────────────────────────┘
```

---

## Pricing Strategies

The system supports **3 pricing strategies** that can be combined with multipliers:

### 1. Per Second (`per_second`)

Price is calculated based on the duration of the generated content.

```
Total Price = price_per_unit × duration
```

**Example**: Video generation at $0.04/second
- 5 second video = $0.04 × 5 = **$0.20**

### 2. Per Request (`per_request`)

Fixed price per generation request, regardless of output length.

```
Total Price = price_per_unit (flat fee)
```

**Example**: Image generation at $0.02/request
- Any image = **$0.02**

### 3. Per Character (`per_char`)

Price based on text length, typically used for text-to-speech.

```
Total Price = (character_count / billing_unit_size) × price_per_unit
```

**Example**: TTS at $0.10 per 1000 characters
- 500 characters = (500 / 1000) × $0.10 = **$0.05**

---

## Provider Configuration Schema

Each provider in `provider.json` has a `price` object:

```typescript
interface ProviderPrice {
  /** Unit of pricing: "per_second" | "per_request" | "per_char" */
  unit: PriceUnit
  
  /** Base price per unit (used when no tier pricing) */
  price_per_unit?: number
  
  /** For per_char: how many characters = 1 unit (e.g., 1000) */
  billing_unit_size?: number
  
  /** Tier-based pricing lookup (e.g., by resolution) */
  tier?: Record<string, number>
  
  /** Field key to look up in tier (e.g., "resolution" or "duration") */
  tier_field_key?: string
  
  /** Field(s) that trigger a price multiplier when true */
  multiplier_field_key?: string | string[]
  
  /** Multiplier value (e.g., 1.5 for +50%) */
  multiplier_value?: number
}
```

---

## Credit Reservation System

Some models (like avatar and text-to-speech) have **unknown output duration** before generation. The output duration depends on the input text/script length, not a user-specified parameter. This creates a problem: a user with 10 credits could submit a long script that generates content costing 500+ credits.

### The Problem

```
User Balance: 10 credits
Script: "Hello world!" (short) → ~1 second → 2 credits ✓
Script: "Once upon a time..." (long) → ~5 minutes → 500 credits ✗
```

Without safeguards, users could abuse the system by submitting expensive requests with insufficient credits.

### The Solution: Reserve → Generate → Settle

For models with unknown duration, we use a **two-phase credit system**:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   ESTIMATE  │ ──► │   RESERVE   │ ──► │  GENERATE   │ ──► │   SETTLE    │
│   Duration  │     │   Credits   │     │   Content   │     │   Credits   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
     │                    │                   │                    │
     │                    │                   │                    │
  From text         With 30%            AI Provider          Refund excess
  (~14 char/sec)    buffer              returns actual       OR charge
                                        duration             difference
```

### Duration Estimation

Output duration is estimated from input text using average speaking rates:

```
Estimated Duration = Character Count / 14 (chars per second)
```

This is based on ~140 words per minute speaking rate.

| Text Length | Estimated Duration |
|-------------|-------------------|
| 140 chars   | ~10 seconds       |
| 420 chars   | ~30 seconds       |
| 840 chars   | ~60 seconds       |

### Reservation with Buffer

Credits are reserved with a **30% safety buffer** to account for:
- Speech pace variations
- Pauses in generated content
- Model-specific timing differences

```
Reserved Credits = Estimated Credits × 1.3
```

### Settlement After Generation

After generation completes, the reservation is **settled** with the actual cost:

| Scenario | Action |
|----------|--------|
| Actual < Reserved | Refund the difference to user |
| Actual > Reserved | Charge the difference from user balance |
| Actual = Reserved | No adjustment needed |

### Database Schema

The `stripe.credit_reservations` table tracks pending reservations:

```sql
create table stripe.credit_reservations (
  id uuid primary key,
  user_id uuid not null,
  job_id text not null unique,
  reserved_amount integer not null,  -- Credits held (with buffer)
  estimated_amount integer not null, -- Original estimate (without buffer)
  actual_amount integer,             -- Filled after generation
  status text not null,              -- 'pending', 'settled', 'released'
  model_id text,
  created_at timestamptz,
  settled_at timestamptz
);
```

### Billing Strategy Configuration

Each model specifies its billing strategy in `provider.json`:

```json
{
  "endpoint": "argil/avatar",
  "billing_strategy": "reservation",
  ...
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `billing_strategy` | `"direct"` \| `"reservation"` | `"direct"` | Billing method to use |

**When to use each:**

| Strategy | Use When | Examples |
|----------|----------|----------|
| `"direct"` | Cost is known upfront (user specifies duration, fixed per-request, or duration from input media) | Video generation, image generation, audio-input avatars (Kling) |
| `"reservation"` | Output duration depends on text input and is unknown before generation | Text-to-speech, text-based avatars (Argil) |

Models with `per_char` pricing don't need reservations because the cost is calculated from input text length.

---

## Failure & Refund Handling

The billing system ensures users are never permanently charged for failed generations.

### Direct Deduction Models (Known Duration)

For models where duration is specified by the user:

1. Credits are **deducted** before generation starts
2. On failure, credits are **refunded** to user's balance
3. Refunds go to `extra_balance` (never expire)

```python
# In Inngest generation function
except Exception as e:
    if user_id and credits_used > 0:
        await credit_service.refund_credits(
            user_id=user_id,
            amount=credits_used,
            job_id=job_id,
            description=f"Generation failed: {str(e)[:100]}",
        )
```

### Reservation Models (Unknown Duration)

For models using the reservation system:

1. Credits are **reserved** before generation starts
2. On failure, reservation is **released** (full amount returned)
3. On success, reservation is **settled** with actual cost

```python
# In Inngest generation function
except Exception as e:
    if reservation_id:
        await credit_service.release_reservation(
            reservation_id=reservation_id,
            reason=f"Generation failed: {str(e)[:100]}",
        )
```

### Edge Cases

| Scenario | Handling |
|----------|----------|
| Job fails to enqueue | Immediate refund/release |
| Generation times out | Refund/release on error |
| Actual > Reserved | Charge difference from balance |
| Insufficient balance for extra | Charge what's available, log deficit |

### Transaction Types

All credit changes are logged in `stripe.credit_transactions`:

| Type | Description |
|------|-------------|
| `usage` | Credits deducted/reserved for generation |
| `refund` | Credits returned (failure or settlement) |
| `subscription_grant` | Monthly credits from subscription |
| `purchase` | One-time credit purchase |

---

## Frontend Price Calculation

Located in `packages/shared/src/registry/pricing.ts`:

### `calculatePrice(provider, formValues)`

Main function that calculates the total price based on provider config and user selections.

```typescript
import { calculatePrice, formatPrice } from "@octupost/shared/registry"

// Example usage in video generator
const videoPrice = formatPrice(
  calculatePrice(currentProvider, { 
    duration: videoDuration, 
    resolution: videoResolution, 
    enable_audio: videoEnableAudio 
  })
)
// Returns: "$0.60"
```

### Calculation Steps:

1. **Determine base price**:
   - Use `price_per_unit` if defined
   - OR look up tier price using `tier_field_key` (e.g., resolution → price)

2. **Calculate total based on unit**:
   - `per_second`: `basePrice × duration`
   - `per_request`: `basePrice` (flat)
   - `per_char`: `basePrice` (actual calc needs text length)

3. **Apply multiplier** (if applicable):
   - Check if `multiplier_field_key` is true in form values
   - If yes: `totalPrice × multiplier_value`

### `calculateCharPrice(provider, textLength)`

Specialized function for text-to-speech providers:

```typescript
const speechPrice = calculateCharPrice(provider, text.length)
// 500 chars at $0.10/1000 = $0.05
```

---

## Backend Cost Calculation

Located in `api/app/registry/reader.py`:

### `calculate_cost(model_id, quantity, params)`

```python
from app.registry import calculate_cost

# Calculate cost for a 5-second video
cost = calculate_cost(
    model_id="fal-ai/longcat-video/text-to-video/720p",
    quantity=5.0,  # 5 seconds
    params={"resolution": "720p", "enable_audio": True}
)
# Returns: 0.30 (USD)
```

The backend uses the same logic as frontend:
1. Load pricing config from `provider.json`
2. Apply tier pricing if configured
3. Multiply by quantity
4. Apply multipliers for optional features

---

## Price Display

### `formatPrice(price)`

Formats price for UI display with appropriate precision:

```typescript
formatPrice(0.30)   // "$0.30"
formatPrice(0.005)  // "$0.0050"  (4 decimals for small amounts)
```

### `getDisplayPrice(provider)`

Shows price range in model selector:

```typescript
getDisplayPrice(provider)
// Simple pricing: "$0.04/sec"
// Tiered pricing: "$0.06 - $0.24/sec"
// Per request: "$0.02"
// Character pricing: "$0.10/char"
```

### `getEstimatedPriceRange(provider)`

Returns min/max prices based on duration limits:

```typescript
const range = getEstimatedPriceRange(provider)
// { min: 0.08, max: 0.64 } for 2-16 sec at $0.04/sec
```

---

## Examples

### Example 1: Simple Per-Second Pricing

**Provider**: Long Cat (Video)

```json
{
  "price": {
    "unit": "per_second",
    "price_per_unit": 0.04
  }
}
```

| Duration | Calculation | Price |
|----------|-------------|-------|
| 4 sec    | 0.04 × 4    | $0.16 |
| 8 sec    | 0.04 × 8    | $0.32 |
| 16 sec   | 0.04 × 16   | $0.64 |

---

### Example 2: Tiered Pricing by Resolution

**Provider**: LTX 2 (Video)

```json
{
  "price": {
    "tier": {
      "1080p": 0.06,
      "1440p": 0.12,
      "2160p": 0.24
    },
    "unit": "per_second",
    "tier_field_key": "resolution"
  }
}
```

| Resolution | Duration | Calculation | Price |
|------------|----------|-------------|-------|
| 1080p      | 5 sec    | 0.06 × 5    | $0.30 |
| 1440p      | 5 sec    | 0.12 × 5    | $0.60 |
| 2160p      | 5 sec    | 0.24 × 5    | $1.20 |

---

### Example 3: Tiered Pricing by Duration

**Provider**: Kling (Video)

```json
{
  "price": {
    "tier": {
      "6": 0.28,
      "10": 0.56
    },
    "unit": "per_request",
    "tier_field_key": "duration"
  }
}
```

| Duration Selection | Price |
|--------------------|-------|
| 6 seconds          | $0.28 |
| 10 seconds         | $0.56 |

---

### Example 4: Audio Multiplier

**Provider**: Wan 2.1 (Video with optional audio)

```json
{
  "price": {
    "unit": "per_second",
    "price_per_unit": 0.1,
    "multiplier_field_key": "enable_audio",
    "multiplier_value": 1.5
  }
}
```

| Duration | Audio | Calculation       | Price |
|----------|-------|-------------------|-------|
| 4 sec    | Off   | 0.1 × 4           | $0.40 |
| 4 sec    | On    | 0.1 × 4 × 1.5     | $0.60 |
| 8 sec    | Off   | 0.1 × 8           | $0.80 |
| 8 sec    | On    | 0.1 × 8 × 1.5     | $1.20 |

UI shows: "Generate audio/sound effects with your video (+50% cost)"

---

### Example 5: Per-Character TTS Pricing

**Provider**: Minimax (Text-to-Speech)

```json
{
  "price": {
    "unit": "per_char",
    "price_per_unit": 0.1,
    "billing_unit_size": 1000
  }
}
```

| Text Length | Calculation          | Price |
|-------------|----------------------|-------|
| 100 chars   | (100/1000) × 0.1     | $0.01 |
| 500 chars   | (500/1000) × 0.1     | $0.05 |
| 2000 chars  | (2000/1000) × 0.1    | $0.20 |

---

### Example 6: Multiple Multiplier Fields

**Provider**: Avatar provider with transparent background

```json
{
  "price": {
    "unit": "per_second",
    "price_per_unit": 0.0225,
    "multiplier_field_key": ["transparent_background"],
    "multiplier_value": 1.5
  }
}
```

Multiplier applies if ANY of the listed fields is true.

---

### Example 7: Avatar with Credit Reservation

**Provider**: Argil Avatar (unknown output duration)

```json
{
  "type": "avatar",
  "price": {
    "unit": "per_second",
    "price_per_unit": 0.0225
  }
}
```

**Credit Calculation Flow**:

1. User submits script: "Hello, welcome to our product demo. Today we'll show you..."
   - 280 characters
   - Estimated duration: 280 / 14 = **20 seconds**
   - Estimated credits: 20 × 0.0225 × 100 = **45 credits**

2. System reserves with 30% buffer:
   - Reserved credits: 45 × 1.3 = **59 credits**
   - User must have ≥59 credits to proceed

3. Generation completes:
   - Actual duration from API: **18 seconds**
   - Actual credits: 18 × 0.0225 × 100 = **41 credits**

4. Settlement:
   - Reserved: 59 credits
   - Actual: 41 credits
   - **Refunded: 18 credits** returned to user

| Step | Action | Credits |
|------|--------|---------|
| Before | User balance | 100 |
| Reserve | Deduct 59 | 41 |
| Generate | (AI processing) | 41 |
| Settle | Refund 18 | **59** |

Final cost: 41 credits for 18 seconds of avatar video.

---

## Key Files

### Pricing Configuration

| File | Purpose |
|------|---------|
| `packages/shared/src/registry/provider.json` | Central pricing configuration for all providers |
| `packages/shared/src/registry/pricing.ts` | Frontend price/credit calculation & duration estimation |
| `packages/shared/src/registry/types.ts` | TypeScript types for pricing |

### Backend

| File | Purpose |
|------|---------|
| `api/app/registry/reader.py` | Backend cost calculation (`calculate_cost()`) |
| `api/app/registry/types.py` | Python types for pricing |
| `api/app/services/credit_service.py` | Credit operations (deduct, refund, reserve, settle) |
| `api/app/routes/generate.py` | Generation API with credit checking |
| `api/app/inngest/functions/generate.py` | Async generation with settlement/refund |

### Database

| File | Purpose |
|------|---------|
| `supabase/migrations/20251214_add_billing_credits.sql` | Credit balances & transactions tables |
| `supabase/migrations/20251214_dual_credit_balance.sql` | Monthly/extra balance separation |
| `supabase/migrations/20251214_credit_reservations.sql` | Credit reservation system |

### Frontend Examples

| File | Purpose |
|------|---------|
| `frontend/components/playground/video-generator.tsx` | Example usage in UI |
| `frontend/components/playground/speech-generator.tsx` | TTS pricing example |

---

## Adding a New Provider

When adding a new provider to `provider.json`, include the `price` object:

```json
{
  "endpoint": "provider/model-name",
  "provider": "Display Name",
  "type": "text-to-video",
  "is_active": true,
  "price": {
    "unit": "per_second",      // or "per_request" or "per_char"
    "price_per_unit": 0.05     // base price
    // Optional fields:
    // "tier": { "720p": 0.05, "1080p": 0.10 },
    // "tier_field_key": "resolution",
    // "multiplier_field_key": "enable_audio",
    // "multiplier_value": 1.5,
    // "billing_unit_size": 1000  // for per_char
  },
  "parameters": [...]
}
```

The frontend will automatically:
- Calculate and display the estimated cost
- Show the price range in the model selector
- Apply multipliers when relevant options are toggled

