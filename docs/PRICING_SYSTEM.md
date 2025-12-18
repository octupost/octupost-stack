# Pricing & Cost Calculation System

This document explains how generation costs are calculated and charged in Octupost.

## Overview

The pricing system calculates how many **credits** a generation will cost based on:
- **Base price** from FAL (the AI provider)
- **Parameter multipliers** configured per model (e.g., higher resolution = higher cost)
- **Markup** for profit margin

Users see the estimated cost before generating, and credits are deducted after generation completes.

## Key Concepts

| Term | Description |
|------|-------------|
| **Credits** | Internal currency. 100 credits = $1 USD |
| **Base Unit Price** | Cost per unit from FAL (e.g., $0.04 per second) |
| **Base Unit** | What the price is measured in (second, compute_second, generation, character) |
| **Base Price Selector** | Optional: Different base prices based on a parameter (e.g., voice type) |
| **Parameter Multiplier** | Cost modifier based on user selections (e.g., 4K = 4x cost) |
| **Markup Multiplier** | Profit margin (1.0 = pass-through, 1.5 = 50% profit) |
| **Unit Bucket Size** | Minimum billable unit. Usage is rounded up to nearest multiple. |

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ADMIN PANEL                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │  Sync from FAL  │  │ Set Multipliers │  │   Set Markup    │              │
│  │  (base price)   │  │ (per parameter) │  │   (profit %)    │              │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘              │
└───────────┼─────────────────────┼─────────────────────┼─────────────────────┘
            │                     │                     │
            ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATABASE (Supabase)                                  │
│                                                                              │
│   model_configs.pricing_config (JSONB)                                       │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │ {                                                                      │ │
│   │   "base_unit_price": 0.04,        ← From FAL API                      │ │
│   │   "base_unit": "second",          ← second/generation/character       │ │
│   │   "markup_multiplier": 1.2,       ← 20% profit                        │ │
│   │   "parameter_multipliers": {      ← Per-option cost modifiers         │ │
│   │     "resolution": { "1080p": 1, "2160p": 4 },                         │ │
│   │     "fps": { "25": 1, "50": 2 }                                       │ │
│   │   }                                                                    │ │
│   │ }                                                                      │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
            │                                           │
            ▼                                           ▼
┌───────────────────────────┐               ┌───────────────────────────┐
│     FRONTEND              │               │     BACKEND               │
│                           │               │                           │
│  cost-calculator.ts       │               │  cost_calculator.py       │
│  ┌─────────────────────┐  │               │  ┌─────────────────────┐  │
│  │ Calculate cost from │  │               │  │ Calculate cost from │  │
│  │ pricing_config +    │  │               │  │ pricing_config +    │  │
│  │ user selections     │  │               │  │ request params      │  │
│  └─────────┬───────────┘  │               │  └─────────┬───────────┘  │
│            │              │               │            │              │
│            ▼              │               │            ▼              │
│  ┌─────────────────────┐  │               │  ┌─────────────────────┐  │
│  │ Show "X credits"    │  │               │  │ Deduct credits from │  │
│  │ before generation   │  │               │  │ user balance        │  │
│  └─────────────────────┘  │               │  └─────────────────────┘  │
└───────────────────────────┘               └───────────────────────────┘
```

## The Formula

```
effective_base_price = base_price_selector[param_value] OR base_unit_price
billable_units = ceil(units / unit_bucket_size) × unit_bucket_size
Final Cost = effective_base_price × billable_units × parameter_multipliers × markup_multiplier

Credits = Final Cost × 100 (rounded up, minimum 1)
```

### Unit Bucket Size

The `unit_bucket_size` defines the minimum billable unit. Usage is rounded UP to the nearest multiple of this value.

| Unit Type | Bucket Size | User Usage | Billed As |
|-----------|-------------|------------|-----------|
| character | 1000 | 500 chars | 1000 chars |
| character | 1000 | 1001 chars | 2000 chars |
| second | 5 | 3 seconds | 5 seconds |
| second | 5 | 7 seconds | 10 seconds |
| generation | 1 | 1 gen | 1 gen (default, no rounding) |

### Step by Step

1. **Determine effective base price**: 
   - If `base_price_selector` is configured, look up the price for the selected parameter value
   - Otherwise, use `base_unit_price`

2. **Get base cost**: `effective_base_price × units`
   - For video (`second` unit): units = duration in seconds
   - For images (`generation` unit): units = 1 (per generation)
   - For TTS (`character` unit): units = character count
   - For GPU-based (`compute_second` unit): units = GPU processing time (only known after generation!)

> ⚠️ **IMPORTANT: `second` vs `compute_second`**
> 
> - **`second`** = Video duration (e.g., 5-second video). Can estimate cost before generation.
> - **`compute_second`** = GPU processing time. A 5-second video might take 60 compute seconds. Cost is only known after generation completes.

3. **Apply parameter multipliers**: Multiply by each applicable multiplier
   - If user selects 2160p and multiplier is 4 → multiply by 4
   - If user enables 50fps and multiplier is 2 → multiply by 2
   - Multipliers stack (4 × 2 = 8x total)

4. **Apply markup**: Multiply by markup_multiplier

5. **Convert to credits**: Multiply by 100, round up

## Example Calculations

### Example 1: LTX Video (6 seconds, 2160p, 50fps)

**Pricing Config:**
```json
{
  "base_unit_price": 0.04,
  "base_unit": "second",
  "markup_multiplier": 1.2,
  "parameter_multipliers": {
    "resolution": { "1080p": 1, "1440p": 2, "2160p": 4 },
    "fps": { "25": 1, "50": 2 }
  }
}
```

**Calculation:**
```
Base cost     = $0.04 × 6 seconds = $0.24
Resolution    = × 4 (2160p)       = $0.96
FPS           = × 2 (50fps)       = $1.92
Markup        = × 1.2             = $2.304

Credits       = $2.304 × 100      = 231 credits
```

### Example 2: Image Generation (single image)

**Pricing Config:**
```json
{
  "base_unit_price": 0.10,
  "base_unit": "generation",
  "markup_multiplier": 1.0,
  "parameter_multipliers": {}
}
```

**Calculation:**
```
Base cost     = $0.10 × 1 generation = $0.10
No multipliers
No markup

Credits       = $0.10 × 100          = 10 credits
```

### Example 3: Text-to-Speech (500 characters)

**Pricing Config:**
```json
{
  "base_unit_price": 0.0001,
  "base_unit": "character",
  "markup_multiplier": 1.5,
  "parameter_multipliers": {}
}
```

**Calculation:**
```
Base cost     = $0.0001 × 500 chars = $0.05
Markup        = × 1.5               = $0.075

Credits       = $0.075 × 100        = 8 credits (rounded up from 7.5)
```

### Example 4: Text-to-Speech with Bucket Size (500 characters, bucket=1000)

**Pricing Config:**
```json
{
  "base_unit_price": 0.0001,
  "base_unit": "character",
  "markup_multiplier": 1.5,
  "unit_bucket_size": 1000,
  "parameter_multipliers": {}
}
```

**Calculation:**
```
Bucket round  = ceil(500 / 1000) × 1000 = 1000 billable chars
Base cost     = $0.0001 × 1000 chars = $0.10
Markup        = × 1.5                = $0.15

Credits       = $0.15 × 100          = 15 credits
```

### Example 5: Video with Bucket Size (3 seconds, bucket=5)

**Pricing Config:**
```json
{
  "base_unit_price": 0.04,
  "base_unit": "second",
  "markup_multiplier": 1.0,
  "unit_bucket_size": 5,
  "parameter_multipliers": {}
}
```

**Calculation:**
```
Bucket round  = ceil(3 / 5) × 5 = 5 billable seconds
Base cost     = $0.04 × 5 seconds = $0.20

Credits       = $0.20 × 100       = 20 credits
```

## Configuring Pricing for a Model

### Via Admin Panel

1. Go to **Admin → Models → [Model Name]**
2. Find the **Pricing Configuration** section
3. Click **"Sync Base Price from FAL"** to fetch current FAL pricing
4. Set **Markup Multiplier** (1.0 = no markup, 1.5 = 50% profit)
5. Configure **Parameter Multipliers** for any enum parameters
6. Click **Save Changes**

### Pricing Config Structure

```typescript
interface PricingConfig {
  // Price per unit from FAL API (in USD)
  base_unit_price: number;       // e.g., 0.04
  
  // What the price is measured in
  // IMPORTANT: "second" (video duration) vs "compute_second" (GPU time)
  base_unit: string;             // "second" | "compute_second" | "generation" | "character"
  
  // Your profit margin
  markup_multiplier: number;     // 1.0 = 0%, 1.2 = 20%, 1.5 = 50%
  
  // Minimum billable unit size (rounds up to nearest multiple)
  // Default: 1 (no rounding)
  unit_bucket_size?: number;     // e.g., 1000 for character-based, 5 for second-based
  
  // Optional: Base price varies by parameter value
  // If not configured, uses base_unit_price for all
  base_price_selector?: {
    paramKey: string;            // e.g., "voice", "resolution"
    priceMap: {
      [optionValue: string]: number;  // e.g., { "standard": 0.001, "premium": 0.003 }
    };
  };
  
  // Cost modifiers per parameter value
  parameter_multipliers: {
    [paramName: string]: {
      [optionValue: string]: number;  // 1.0 = no change, 2.0 = 2x cost
    };
  };
}
```

### Understanding Base Units

| Unit | Description | Can Estimate Cost? |
|------|-------------|-------------------|
| `generation` | Fixed price per generation | ✅ Yes |
| `second` | Price per second of **video duration** | ✅ Yes (user specifies duration) |
| `compute_second` | Price per second of **GPU processing time** | ❌ No (only known after generation) |
| `character` | Price per character (for TTS) | ✅ Yes (based on text length) |
| `megapixel` | Price per megapixel (for images) | ✅ Yes (based on resolution) |

> ⚠️ For `compute_second` pricing (like Argil Avatars), the UI will show "Variable (based on GPU time)" instead of an estimated cost. The actual cost is calculated and charged after generation completes.

### Base Price Selector (Optional)

Sometimes, different parameter values have completely different base prices from the provider (not just multipliers). For example:
- **TTS with voice types**: "standard" voice costs $0.001/char, "premium" voice costs $0.003/char
- **Model variants**: "fast" mode has different pricing than "quality" mode

Instead of using multipliers (which multiply a single base price), you can use a **base price selector** to specify different base prices per parameter value.

**When to use Base Price Selector vs Multipliers:**

| Scenario | Use |
|----------|-----|
| Provider charges different rates for different options | Base Price Selector |
| You want to add a markup for premium features | Parameter Multiplier |
| FAL pricing page shows different $/unit for each option | Base Price Selector |
| Same base cost, but more expensive options | Parameter Multiplier |

**Configuration:**

In the Admin Panel, under Pricing Configuration:
1. Click "Add Base Price Selector"
2. Select which parameter controls the base price (must be an enum)
3. Enter the base price (in USD) for each option

The `base_unit_price` field becomes the fallback if no match is found.

**Example:**
```json
{
  "base_unit_price": 0.001,
  "base_unit": "character",
  "markup_multiplier": 1.2,
  "base_price_selector": {
    "paramKey": "voice",
    "priceMap": {
      "standard": 0.001,
      "professional": 0.002,
      "premium": 0.005
    }
  }
}
```

If user selects "premium" voice with 500 characters:
```
Base price   = $0.005 (from selector, not $0.001)
Base cost    = $0.005 × 500 = $2.50
Markup       = × 1.2         = $3.00
Credits      = 300 credits
```

### Setting Parameter Multipliers

For parameters with selectable options (enums), you can set a multiplier for each option:

| Resolution | Multiplier | Effect |
|------------|------------|--------|
| 1080p | 1.0 | Base price |
| 1440p | 2.0 | 2x the cost |
| 2160p | 4.0 | 4x the cost |

**Tip:** Leave multipliers at 1.0 (or empty) for options that shouldn't affect price.

## File Locations

| Component | Location |
|-----------|----------|
| Database Column | `octupost.model_configs.pricing_config` |
| TypeScript Types | `frontend/lib/types/pricing.ts` |
| Frontend Calculator | `frontend/lib/utils/cost-calculator.ts` |
| Backend Calculator | `api/app/services/cost_calculator.py` |
| Admin UI | `frontend/app/(app)/admin/models/[id]/page.tsx` |
| Sync API | `frontend/app/api/admin/model-configs/[id]/sync-pricing/route.ts` |

## User Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  User adjusts   │     │ Frontend shows  │     │  User clicks    │
│  parameters     │ ──▶ │ estimated cost  │ ──▶ │  Generate       │
│  (duration, etc)│     │ in real-time    │     │                 │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │ Credits deducted│     │ Backend checks  │
                        │ from balance    │ ◀── │ balance, starts │
                        │                 │     │ generation      │
                        └─────────────────┘     └─────────────────┘
```

## Credit Balance

Users have two types of credits:
- **Monthly Credits**: Reset each billing cycle (used first)
- **Extra Credits**: Purchased credits that never expire (used after monthly depleted)

See `docs/BILLING_SYSTEM.md` for more details on credit management.

## Fallback Behavior

If a model doesn't have `pricing_config` set (or `base_unit_price` is 0):
1. Backend falls back to the legacy registry-based pricing from `provider.json`
2. Frontend won't show estimated cost (no price displayed)

This ensures backward compatibility with models that haven't been configured yet.

## Common Scenarios

### Scenario: Model charges per second, higher quality costs more

```json
{
  "base_unit_price": 0.05,
  "base_unit": "second",
  "markup_multiplier": 1.0,
  "parameter_multipliers": {
    "quality": { "standard": 1, "high": 1.5, "ultra": 2.5 }
  }
}
```

### Scenario: Fixed price per generation with markup

```json
{
  "base_unit_price": 0.25,
  "base_unit": "generation",
  "markup_multiplier": 1.4,
  "parameter_multipliers": {}
}
```
Result: Each generation costs $0.35 (35 credits)

### Scenario: Audio generation with feature toggles

```json
{
  "base_unit_price": 0.10,
  "base_unit": "generation",
  "markup_multiplier": 1.2,
  "parameter_multipliers": {
    "enable_vocals": { "true": 1.5, "false": 1 },
    "duration": { "30": 1, "60": 1.8, "120": 3 }
  }
}
```

### Scenario: TTS with different voice tiers (Base Price Selector)

When the provider charges completely different rates per voice:

```json
{
  "base_unit_price": 0.0001,
  "base_unit": "character",
  "markup_multiplier": 1.5,
  "unit_source_param": "text",
  "base_price_selector": {
    "paramKey": "voice",
    "priceMap": {
      "basic": 0.0001,
      "standard": 0.0003,
      "professional": 0.0008,
      "celebrity": 0.002
    }
  },
  "parameter_multipliers": {}
}
```

User selects "professional" voice with 1000 characters:
- Base price: $0.0008/char (from selector)
- Base cost: $0.0008 × 1000 = $0.80
- Markup: × 1.5 = $1.20
- Credits: 120 credits

### Scenario: Video model with resolution-based pricing

When different resolutions have different base costs from the provider:

```json
{
  "base_unit_price": 0.02,
  "base_unit": "second",
  "markup_multiplier": 1.2,
  "unit_source_param": "duration",
  "base_price_selector": {
    "paramKey": "resolution",
    "priceMap": {
      "720p": 0.02,
      "1080p": 0.05,
      "2160p": 0.15
    }
  },
  "parameter_multipliers": {}
}
```

Note: Use base_price_selector when the provider charges different rates.
Use parameter_multipliers when you want to add your own markup on top of a single base rate.

