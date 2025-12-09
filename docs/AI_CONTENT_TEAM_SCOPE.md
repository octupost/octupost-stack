# 🎬 Octupost AI Content Team - Project Scope

> **Version:** 2.0  
> **Status:** Planning Phase  
> **Focus:** Workspace-Level (not User-Level)  
> **Schemas:** `octupost` (extended) + `agent` (sessions only)

---

## 📋 Executive Summary

Build an AI-powered content creation team that helps workplaces produce consistent, high-quality video content. The system uses multiple specialized AI agents coordinated through Agno framework, leveraging Octupost Studio for editing and Octupost API for generation.

**Key Principles:**
1. **Workspace-centric** - Everything belongs to a workspace, not a user
2. **Cost-conscious** - Track ALL costs (LLM, generation, API calls), support fully FREE tier
3. **Asset-first** - Always check existing/free assets before generating
4. **Perfect match** - Only use assets that match target aspect ratio exactly

---

## 🎯 Core Concepts

### Workspace-First Architecture

```
User (can own/be member of multiple workplaces)
    │
    ├── Workplace: "Facts Shorts Channel"
    │   ├── Preferences: 9:16, fast-paced, educational
    │   ├── Voice: Energetic, simple vocabulary
    │   ├── Brand: Blue theme, specific font
    │   ├── Avatar: AI presenter "Alex"
    │   ├── Persona: facts_shorts
    │   └── Projects → Assets
    │
    ├── Workplace: "Football News"
    │   ├── Preferences: 16:9, news style
    │   ├── Voice: Professional, authoritative
    │   ├── Brand: Green theme, sports font
    │   ├── Avatar: None (voiceover only)
    │   ├── Persona: news_creator
    │   └── Projects → Assets
    │
    └── Workplace: "E-commerce Brand X"
        ├── Preferences: 1:1/9:16, product-focused
        ├── Voice: Friendly, persuasive
        ├── Brand: Brand X colors
        ├── Avatar: Product showcase style
        ├── Persona: ecommerce
        └── Projects → Assets
```

### Aspect Ratio Strategy

> **Strict Matching:** Only use assets that **perfectly match** the target aspect ratio.

**Why no cropping:**
- Quality loss from cropping
- Important content might be cut
- Professional look requires proper framing
- Models are getting better at generating different ratios

**Supported Ratios:**
| Ratio | Use Case | Stock Search Filter |
|-------|----------|---------------------|
| `16:9` | YouTube, landscape | `orientation=landscape` |
| `9:16` | TikTok, Reels, Shorts | `orientation=portrait` |
| `1:1` | Instagram, Facebook | `orientation=square` |
| `4:5` | Instagram portrait | Custom filter |

**Asset Search with Ratio Filter:**
```python
async def search_assets_with_ratio(
    query: str,
    aspect_ratio: str,
    asset_type: str,  # video, image
) -> list[Asset]:
    # Calculate ratio tolerance (e.g., 16:9 = 1.77, allow ±0.05)
    target_ratio = ASPECT_RATIOS[aspect_ratio]["value"]
    tolerance = 0.05
    
    # Search with ratio filter
    return await db.query("""
        SELECT * FROM octupost.assets
        WHERE type = $1
        AND ABS((width::float / height::float) - $2) < $3
        AND to_tsvector('english', generation_params->>'prompt') @@ to_tsquery($4)
    """, asset_type, target_ratio, tolerance, query)
```

### Asset-First Strategy (Strictly Ordered)

> **Critical:** ALWAYS follow this order. Never skip steps!

**Priority Order:**
```
1. PROJECT ASSETS     → Already in current project (FREE, instant)
2. WORKPLACE ASSETS   → Shared across workspace (FREE, instant)
3. FREE STOCK         → Pexels, Pixabay (FREE API, must match ratio)
4. AI GENERATION      → Only if budget allows & free options exhausted
```

**Decision Flow:**
```python
async def find_asset_for_scene(scene: Scene, session: ContentSession) -> AssetResult:
    aspect_ratio = session.confirmed_settings["aspect_ratio"]
    
    # 1. FIRST: Check project's existing assets (FREE)
    project_assets = await db.search_project_assets(
        project_id=session.project_id,
        type=scene.visual_type,
        aspect_ratio=aspect_ratio,  # Must match exactly
        keywords=scene.keywords,    # Full-text search on prompt
    )
    if project_assets:
        return AssetResult(asset=project_assets[0], cost=0, source="project_existing")
    
    # 2. SECOND: Check workspace's assets (FREE)
    workspace_assets = await db.search_workspace_assets(
        workspace_id=session.workspace_id,
        type=scene.visual_type,
        aspect_ratio=aspect_ratio,  # Must match exactly
        keywords=scene.keywords,
        min_duration=scene.duration if scene.visual_type == "video" else None,
    )
    if workspace_assets:
        return AssetResult(asset=workspace_assets[0], cost=0, source="workspace_existing")
    
    # 3. THIRD: Search free stock (FREE API)
    # Director can suggest "free stock would work here" to prioritize this
    if scene.allow_stock or session.budget_mode == "free_only":
        stock = await stock_search.search(
            query=scene.search_query,
            type=scene.visual_type,
            aspect_ratio=aspect_ratio,  # Must match orientation
            min_duration=scene.duration - 2 if scene.visual_type == "video" else None,
            max_duration=scene.duration + 10 if scene.visual_type == "video" else None,
        )
        if stock:
            return AssetResult(asset=stock[0], cost=0, source="stock_free")
    
    # 4. FOURTH: Generate with AI (costs money)
    if session.budget_mode != "free_only":
        # Check if we have budget remaining
        remaining = await cost_tracker.get_remaining_budget(session.id)
        model = await model_selector.select(
            scene=scene,
            aspect_ratio=aspect_ratio,
            budget_remaining=remaining,
        )
        if model and model.estimated_cost <= remaining:
            return AssetResult(
                needs_generation=True,
                model=model,
                estimated_cost=model.estimated_cost,
                source="ai_generation"
            )
    
    # 5. No suitable asset found
    return AssetResult(
        needs_user_input=True,
        message=f"No {'free ' if session.budget_mode == 'free_only' else ''}asset found matching {aspect_ratio}. Options: provide asset, change ratio, or {'increase budget' if session.budget_mode != 'free_only' else 'try different scene'}."
    )
```

### Asset Search Strategy (100% FREE)

> **No embeddings, no vector search** - Use PostgreSQL full-text search on prompts.

Every asset has a prompt (in `generation_params->>'prompt'` or `description`). We search on that.

**Search Index (one-time setup):**
```sql
-- Add search index to assets (FREE - just SQL)
CREATE INDEX idx_assets_prompt_search ON octupost.assets 
USING gin(to_tsvector('english', COALESCE(generation_params->>'prompt', description, '')));

-- Add ratio calculation for filtering
CREATE INDEX idx_assets_aspect_ratio ON octupost.assets ((width::float / height::float));
```

**Search Query (FREE - just SQL):**
```sql
-- Search for "sunset beach" videos in 16:9
SELECT * FROM octupost.assets 
WHERE type = 'video'
AND ABS((width::float / height::float) - 1.777) < 0.05  -- 16:9 ratio
AND to_tsvector('english', COALESCE(generation_params->>'prompt', description, '')) 
    @@ to_tsquery('sunset & beach');
```

**Cost Summary:**
| Search Type | Cost | Notes |
|-------------|------|-------|
| Project assets (Supabase) | FREE | SQL query |
| Workspace assets (Supabase) | FREE | SQL query |
| Full-text search on prompts | FREE | PostgreSQL built-in |
| Pexels API | FREE | REST API, 200 req/hr |
| Pixabay API | FREE | REST API, 100 req/hr |

---

## 🗄️ Database Schema

### Schema Organization

```
┌─────────────────────────────────────────────────────────────────┐
│                        octupost schema                          │
│  (Extended with AI preferences - synced with existing tables)   │
│                                                                 │
│  • workplaces (existing + new ai_preferences JSONB column)      │
│  • projects (existing)                                          │
│  • assets (existing)                                            │
│  • workplace_assets (existing)                                  │
│  • project_assets (existing)                                    │
│  • workplace_personas (NEW)                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         agent schema                            │
│  (Session-specific data - ephemeral/per-project)                │
│                                                                 │
│  • content_sessions                                             │
│  • session_costs (includes LLM + generation costs)              │
│  • session_scenes                                               │
│  • session_qa_reviews                                           │
│  • model_knowledge (static reference)                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         agno schema                             │
│  (Auto-created by Agno framework - do not modify)               │
│                                                                 │
│  • sessions                                                     │
│  • memory                                                       │
└─────────────────────────────────────────────────────────────────┘
```

### Extended `octupost.workplaces` Table

Add JSONB columns to existing workplaces table:

```sql
ALTER TABLE octupost.workplaces ADD COLUMN IF NOT EXISTS ai_preferences JSONB DEFAULT '{}';
ALTER TABLE octupost.workplaces ADD COLUMN IF NOT EXISTS voice_profile JSONB DEFAULT '{}';
ALTER TABLE octupost.workplaces ADD COLUMN IF NOT EXISTS avatar_config JSONB DEFAULT NULL;
```

**`ai_preferences` JSONB Structure:**
```json
{
  "content_type": "facts_shorts",
  "default_duration_seconds": 60,
  "default_aspect_ratio": "9:16",
  "preferred_video_models": ["fal-ai/minimax-video", "fal-ai/kling-video"],
  "preferred_image_models": ["fal-ai/flux/schnell"],
  "preferred_voice_model": "elevenlabs",
  "preferred_voice_id": "21m00Tcm4TlvDq8ikWAM",
  "preferred_music_genre": "electronic",
  "budget_mode": "free_only",
  "max_budget_per_video": null,
  "auto_regenerate_on_qa_fail": false,
  "max_regeneration_attempts": 2,
  "subtitle_style": "bold",
  "text_overlay_font": "Inter",
  "updated_at": "2024-12-09T00:00:00Z"
}
```

> **Learning from History:** These preferences are updated based on user's previous video generations. When a user picks a different model or style, we update the defaults.

**`voice_profile` JSONB Structure:**
```json
{
  "style_description": "Energetic, fast-paced narrator for educational content",
  "vocabulary_level": "simple",
  "formality_level": 3,
  "energy_level": 8,
  "humor_level": 4,
  "good_phrases": ["Did you know?", "Here's the thing...", "Mind-blowing!"],
  "avoid_phrases": ["Actually...", "To be honest..."],
  "effective_hooks": ["question", "shocking_fact", "countdown"]
}
```

> **Per-Video Override:** Voice profile can be overridden per video generation. Workspace defaults are just starting points.

**`avatar_config` JSONB Structure:**
```json
{
  "name": "Alex",
  "type": "ai_generated",
  "source_asset_id": "uuid-here",
  "generation_config": {"style": "realistic", "age": "young_adult"},
  "style_description": "Friendly tech presenter",
  "is_active": true
}
```

> **Per-Video Override:** Avatar can be changed per video. Null means no avatar (voiceover only).

### NEW: `octupost.workplace_personas` Table

```sql
CREATE TABLE octupost.workplace_personas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workplace_id UUID NOT NULL REFERENCES octupost.workplaces(id) ON DELETE CASCADE,
    persona_type TEXT NOT NULL,  -- 'animator', 'news_creator', 'educator', 'ecommerce', 'facts_shorts'
    is_active BOOLEAN DEFAULT true,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(workplace_id, persona_type)
);
```

**Persona Types & Settings:**
```python
PERSONA_TEMPLATES = {
    "facts_shorts": {
        "fast_paced": True,
        "hook_style": "question",
        "max_duration": 60,
        "scene_change_rate": 3,  # seconds
        "text_emphasis": "high",
        "music_intensity": "high"
    },
    "news_creator": {
        "fact_check": "high",
        "source_citations": True,
        "tone": "professional",
        "max_duration": 180,
        "scene_change_rate": 8
    },
    "educator": {
        "pacing": "moderate",
        "visual_aids": True,
        "recap_sections": True,
        "vocabulary": "adaptive"
    },
    "ecommerce": {
        "product_focus": True,
        "urgency": "subtle",
        "cta_style": "soft_sell",
        "highlight_features": True
    },
    "animator": {
        "style": "dynamic",
        "transitions": "creative",
        "effects": "heavy",
        "music_sync": True
    }
}
```

### `agent.content_sessions` Table

> **Project-specific:** Each content session belongs to a project.

```sql
CREATE TABLE agent.content_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workplace_id UUID NOT NULL REFERENCES octupost.workplaces(id),
    project_id UUID NOT NULL REFERENCES octupost.projects(id),  -- Required!
    initiated_by UUID NOT NULL REFERENCES auth.users(id),
    
    -- Status tracking
    status TEXT NOT NULL DEFAULT 'planning',  -- planning, researching, scripting, producing, editing, qa, complete, cancelled
    
    -- Compressed data (to save context tokens)
    brief JSONB,              -- User's request, compressed
    research_summary JSONB,   -- Research output, max 500 tokens
    script_summary JSONB,     -- Scene breakdown, compressed
    
    -- User-confirmed settings (cannot change after confirmation)
    confirmed_settings JSONB, -- {aspect_ratio, duration, budget_mode, llm_tier}
    
    -- Budget tracking
    total_llm_cost_usd DECIMAL(10,6) DEFAULT 0,        -- LLM/agent costs
    total_generation_cost_usd DECIMAL(10,6) DEFAULT 0, -- Asset generation costs
    total_research_cost_usd DECIMAL(10,6) DEFAULT 0,   -- Research tool costs
    total_cost_usd DECIMAL(10,6) GENERATED ALWAYS AS (total_llm_cost_usd + total_generation_cost_usd + total_research_cost_usd) STORED,
    budget_limit_usd DECIMAL(10,4),
    free_only_mode BOOLEAN DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ
);
```

### `agent.session_costs` Table (Comprehensive Cost Tracking)

> **Track EVERYTHING:** LLM calls, generation, research, QA - all costs.

```sql
CREATE TABLE agent.session_costs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES agent.content_sessions(id) ON DELETE CASCADE,
    
    -- Cost category
    cost_category TEXT NOT NULL,  -- 'llm', 'generation', 'research', 'qa', 'stock'
    
    -- What was this for?
    team_name TEXT NOT NULL,      -- 'front_desk', 'research', 'content', 'production', 'editing', 'qa', 'translation'
    agent_name TEXT,              -- Specific agent within team
    operation TEXT NOT NULL,      -- What operation was performed
    
    -- Model/Service details
    model_id TEXT,                -- LLM model or generation model used
    provider TEXT,                -- 'openrouter', 'anthropic', 'fal', 'elevenlabs', 'pexels', etc.
    
    -- Cost details
    is_free BOOLEAN DEFAULT false,
    cost_usd DECIMAL(10,6) DEFAULT 0,
    
    -- Usage metrics
    input_tokens INT,             -- For LLM calls
    output_tokens INT,            -- For LLM calls
    duration_seconds DECIMAL(8,2),-- For video/audio generation
    
    -- Results
    asset_id UUID REFERENCES octupost.assets(id),
    source_asset_id UUID REFERENCES octupost.assets(id),  -- If reused existing
    status TEXT DEFAULT 'pending',  -- pending, completed, failed
    error_message TEXT,
    
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Index for quick cost summaries
CREATE INDEX idx_session_costs_session ON agent.session_costs(session_id);
CREATE INDEX idx_session_costs_category ON agent.session_costs(cost_category);
CREATE INDEX idx_session_costs_team ON agent.session_costs(team_name);
```

### `agent.session_scenes` Table

```sql
CREATE TABLE agent.session_scenes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES agent.content_sessions(id) ON DELETE CASCADE,
    scene_index INT NOT NULL,
    duration_seconds DECIMAL(6,2) NOT NULL,
    scene_type TEXT NOT NULL,  -- 'intro', 'content', 'transition', 'outro', 'b_roll'
    has_voiceover BOOLEAN DEFAULT false,
    visual_type TEXT NOT NULL, -- 'ai_video', 'stock_video', 'ai_image', 'stock_image', 'text_only'
    allow_stock BOOLEAN DEFAULT true,  -- Director can mark scenes where stock is acceptable
    prompt_summary TEXT,       -- Compressed prompt, <200 chars
    aspect_ratio TEXT NOT NULL,
    
    -- Asset assignment
    asset_id UUID REFERENCES octupost.assets(id),
    existing_asset_id UUID REFERENCES octupost.assets(id),  -- If reused
    asset_source TEXT,         -- 'project_existing', 'workspace_existing', 'stock_free', 'ai_generation'
    
    status TEXT DEFAULT 'planned',  -- planned, searching, generating, complete, failed
    created_at TIMESTAMPTZ DEFAULT now()
);
```

### `agent.session_qa_reviews` Table

```sql
CREATE TABLE agent.session_qa_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES agent.content_sessions(id) ON DELETE CASCADE,
    scene_id UUID REFERENCES agent.session_scenes(id),
    asset_id UUID NOT NULL REFERENCES octupost.assets(id),
    
    -- QA results
    passed BOOLEAN NOT NULL,
    confidence_score DECIMAL(4,3),  -- 0.000 to 1.000
    issues JSONB,  -- [{type, severity, description, timestamp}]
    
    -- What was checked
    checks_performed JSONB,  -- ['visual_quality', 'audio_sync', 'model_consistency', 'brand_match']
    
    -- Regeneration tracking
    attempt_number INT DEFAULT 1,
    model_used TEXT,
    suggested_alternative TEXT,
    
    -- User interaction
    user_notified BOOLEAN DEFAULT false,
    user_approved BOOLEAN,
    user_feedback TEXT,
    
    -- Cost tracking (QA itself can cost money)
    qa_model_used TEXT,        -- LLM used for QA
    qa_cost_usd DECIMAL(10,6) DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT now()
);
```

### `agent.model_knowledge` Table (Static Reference)

```sql
CREATE TABLE agent.model_knowledge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id TEXT NOT NULL UNIQUE,
    model_type TEXT NOT NULL,  -- 'llm', 'video', 'image', 'audio', 'voice', 'music'
    provider TEXT NOT NULL,    -- 'openrouter', 'anthropic', 'openai', 'fal', 'elevenlabs', 'google'
    
    -- Capabilities
    generation_type TEXT,      -- 'text-to-video', 'image-to-video', 'text-to-image', etc.
    supported_ratios TEXT[],   -- ['16:9', '9:16', '1:1']
    min_duration INT,          -- For video/audio
    max_duration INT,
    has_audio BOOLEAN,
    
    -- Pricing
    is_free BOOLEAN DEFAULT false,
    cost_per_1k_tokens DECIMAL(10,6),  -- For LLMs
    cost_per_second DECIMAL(10,6),     -- For video/audio
    cost_per_image DECIMAL(10,6),      -- For images
    
    -- Quality & Use cases
    quality_tier TEXT,         -- 'free', 'budget', 'standard', 'premium'
    best_for TEXT[],           -- ['qa', 'research', 'scripting', 'generation']
    limitations TEXT,
    
    is_enabled BOOLEAN DEFAULT true,
    updated_at TIMESTAMPTZ DEFAULT now()
);
```

---

## 💰 Comprehensive Cost Tracking

### Cost Categories

```python
COST_CATEGORIES = {
    "llm": "Language model API calls (GPT, Claude, Gemini, etc.)",
    "generation": "AI asset generation (video, image, audio, voice)",
    "research": "Research API calls (Tavily, SerpAPI if used)",
    "qa": "QA-specific LLM calls",
    "stock": "Stock API calls (always $0, but tracked for analytics)"
}
```

### Cost Tracking Per Team

| Team | Cost Types | Models Used | Free Option |
|------|-----------|-------------|-------------|
| **Front Desk** | LLM | Gemma 2 9B (free) / Claude 3.5 | ✅ Gemma 2 9B |
| **Research** | LLM + API | Gemma 2 9B + DuckDuckGo | ✅ Both free |
| **Content** | LLM | Gemma 2 9B / GPT-4o / Claude | ✅ Gemma 2 9B |
| **Consistency** | LLM | Gemma 2 9B / Claude 3.5 | ✅ Gemma 2 9B |
| **Production** | LLM + Generation | Various (see below) | ⚠️ Limited |
| **Editing** | LLM | Gemma 2 9B / Claude 3.5 | ✅ Gemma 2 9B |
| **QA** | LLM (vision) | Gemini 1.5 Flash (free) / GPT-4o Vision | ✅ Gemini Flash |
| **Translation** | LLM | Gemma 2 9B / GPT-4o | ✅ Gemma 2 9B |

### Free Tier LLM Models

```python
FREE_LLM_MODELS = {
    # Via OpenRouter (verified free)
    "google/gemma-2-9b-it:free": {
        "provider": "openrouter",
        "cost_per_1k_tokens": 0,
        "best_for": ["routing", "simple_tasks", "classification"],
        "context_limit": 8192,
        "quality": "good_for_simple_tasks"
    },
    "meta-llama/llama-3.2-3b-instruct:free": {
        "provider": "openrouter",
        "cost_per_1k_tokens": 0,
        "best_for": ["fast_responses", "simple_qa"],
        "context_limit": 8192,
        "quality": "basic"
    },
    
    # Via Google AI Studio (free tier)
    "gemini-1.5-flash": {
        "provider": "google",
        "cost_per_1k_tokens": 0,  # Free tier: 15 RPM, 1M TPM
        "best_for": ["qa", "vision", "analysis"],
        "context_limit": 1000000,
        "has_vision": True,
        "quality": "good"
    },
    "gemini-1.5-flash-8b": {
        "provider": "google",
        "cost_per_1k_tokens": 0,  # Free tier
        "best_for": ["fast_qa", "simple_vision"],
        "context_limit": 1000000,
        "has_vision": True,
        "quality": "basic"
    }
}
```

### Team Technology Stack

#### Research Team
```python
RESEARCH_TEAM_TECH = {
    "llm": {
        "free": "google/gemma-2-9b-it:free",
        "paid": "anthropic/claude-3.5-sonnet",
        "cost": "Free option available"
    },
    "tools": {
        "DuckDuckGoTools": {"cost": "FREE", "rate_limit": "None"},
        "WikipediaTools": {"cost": "FREE", "rate_limit": "None"},
        "YouTubeTools": {"cost": "FREE", "rate_limit": "YouTube API quotas"},
        "RedditTools": {"cost": "FREE", "rate_limit": "Reddit API quotas"},
        "HackerNewsTools": {"cost": "FREE", "rate_limit": "None"},
        "Newspaper4kTools": {"cost": "FREE", "rate_limit": "None"},
        # Paid options (not needed for MVP)
        "TavilyTools": {"cost": "$0.01/search", "quality": "Better for AI"},
        "SerpApiTools": {"cost": "$50/5000 searches", "quality": "Google results"}
    },
    "total_for_free_tier": "100% FREE"
}
```

#### QA Team
```python
QA_TEAM_TECH = {
    "visual_qa": {
        "free": "gemini-1.5-flash",  # FREE via Google AI Studio
        "paid": "gpt-4o",
        "why": "Vision models needed to analyze generated content"
    },
    "audio_qa": {
        "free": "gemini-1.5-flash",  # Can analyze audio
        "paid": "gpt-4o"
    },
    "checks": [
        "visual_artifacts",      # Blurriness, glitches
        "model_consistency",     # Same model throughout video
        "text_overlay_style",    # Consistent fonts/colors
        "subtitle_style",        # Match workspace settings
        "audio_sync",            # Voice matches visuals
        "brand_compliance"       # Colors, logo placement
    ],
    "cost_per_qa_review": {
        "free": "$0 (Gemini Flash)",
        "paid": "~$0.02 (GPT-4o Vision)"
    }
}
```

#### Production Team
```python
PRODUCTION_TEAM_TECH = {
    "llm": {
        "free": "google/gemma-2-9b-it:free",
        "paid": "anthropic/claude-3.5-sonnet"
    },
    "asset_search": {
        "project_assets": {"cost": "FREE", "method": "SQL"},
        "workspace_assets": {"cost": "FREE", "method": "SQL"},
        "pexels": {"cost": "FREE", "rate_limit": "200/hour"},
        "pixabay": {"cost": "FREE", "rate_limit": "100/hour"}
    },
    "generation": {
        # Video models (via Octupost API → fal.ai)
        "video_free": None,  # No free video generation
        "video_budget": {
            "fal-ai/hunyuan-video": "$0.035/sec",
            "fal-ai/longcat-video/distilled": "$0.005/sec"
        },
        "video_standard": {
            "fal-ai/minimax-video": "$0.08/sec",
            "fal-ai/kling-video/v2.6/pro": "$0.15/sec"
        },
        "video_premium": {
            "fal-ai/veo3": "$0.50/sec",
            "fal-ai/sora-2": "$0.45/sec"
        },
        
        # Image models
        "image_free": None,
        "image_budget": {
            "fal-ai/flux/schnell": "$0.003/image"
        },
        "image_standard": {
            "fal-ai/flux/dev": "$0.025/image"
        },
        "image_premium": {
            "fal-ai/flux/pro": "$0.05/image"
        },
        
        # Voice/TTS
        "voice_budget": {
            "fal-ai/f5-tts": "$0.005/sec"
        },
        "voice_standard": {
            "elevenlabs": "$0.018/sec (multilingual)"
        },
        
        # Music
        "music_free": {
            "pixabay": "FREE stock music"
        },
        "music_paid": {
            "fal-ai/stable-audio": "$0.015/sec"
        }
    }
}
```

### Cost Tracker Implementation

```python
class CostTracker:
    """Track ALL costs - LLM, generation, research, QA."""
    
    async def record_llm_call(
        self,
        session_id: str,
        team_name: str,
        agent_name: str,
        model_id: str,
        input_tokens: int,
        output_tokens: int,
    ) -> CostRecord:
        """Record an LLM API call cost."""
        model_info = await self.get_model_info(model_id)
        total_tokens = input_tokens + output_tokens
        cost = (total_tokens / 1000) * model_info.cost_per_1k_tokens
        
        return await db.insert("agent.session_costs", {
            "session_id": session_id,
            "cost_category": "llm",
            "team_name": team_name,
            "agent_name": agent_name,
            "operation": "llm_call",
            "model_id": model_id,
            "provider": model_info.provider,
            "is_free": model_info.is_free,
            "cost_usd": cost,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "status": "completed"
        })
    
    async def record_generation(
        self,
        session_id: str,
        team_name: str,
        model_id: str,
        duration_seconds: float = None,
        is_image: bool = False,
        asset_id: str = None,
    ) -> CostRecord:
        """Record an AI generation cost."""
        model_info = await self.get_model_info(model_id)
        
        if is_image:
            cost = model_info.cost_per_image
        else:
            cost = duration_seconds * model_info.cost_per_second
        
        return await db.insert("agent.session_costs", {
            "session_id": session_id,
            "cost_category": "generation",
            "team_name": team_name,
            "operation": "ai_generation",
            "model_id": model_id,
            "provider": model_info.provider,
            "is_free": False,
            "cost_usd": cost,
            "duration_seconds": duration_seconds,
            "asset_id": asset_id,
            "status": "completed"
        })
    
    async def record_stock_search(
        self,
        session_id: str,
        provider: str,  # 'pexels', 'pixabay'
        asset_id: str = None,
    ) -> CostRecord:
        """Record a stock search (always free, but tracked)."""
        return await db.insert("agent.session_costs", {
            "session_id": session_id,
            "cost_category": "stock",
            "team_name": "production",
            "operation": "stock_search",
            "provider": provider,
            "is_free": True,
            "cost_usd": 0,
            "asset_id": asset_id,
            "status": "completed"
        })
    
    async def record_qa_review(
        self,
        session_id: str,
        model_id: str,
        input_tokens: int,
        output_tokens: int,
    ) -> CostRecord:
        """Record a QA review cost (vision model call)."""
        model_info = await self.get_model_info(model_id)
        total_tokens = input_tokens + output_tokens
        cost = (total_tokens / 1000) * model_info.cost_per_1k_tokens
        
        return await db.insert("agent.session_costs", {
            "session_id": session_id,
            "cost_category": "qa",
            "team_name": "qa",
            "operation": "qa_review",
            "model_id": model_id,
            "provider": model_info.provider,
            "is_free": model_info.is_free,
            "cost_usd": cost,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "status": "completed"
        })
    
    async def get_session_summary(self, session_id: str) -> CostSummary:
        """Get cost breakdown for a session."""
        costs = await db.query("""
            SELECT 
                cost_category,
                team_name,
                SUM(cost_usd) as total_cost,
                COUNT(*) as operation_count,
                SUM(CASE WHEN is_free THEN 1 ELSE 0 END) as free_count
            FROM agent.session_costs
            WHERE session_id = $1
            GROUP BY cost_category, team_name
        """, session_id)
        
        return CostSummary(
            by_category={c["cost_category"]: c["total_cost"] for c in costs},
            by_team={c["team_name"]: c["total_cost"] for c in costs},
            total=sum(c["total_cost"] for c in costs),
            free_operations=sum(c["free_count"] for c in costs),
            paid_operations=sum(c["operation_count"] - c["free_count"] for c in costs)
        )
    
    async def can_afford(self, session_id: str, estimated_cost: float) -> bool:
        """Check if session has budget for an operation."""
        session = await db.get_session(session_id)
        if session.free_only_mode:
            return estimated_cost == 0
        if session.budget_limit_usd is None:
            return True
        return session.total_cost_usd + estimated_cost <= session.budget_limit_usd
```

---

## 🤖 Teams & Agents Architecture

### Team Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONT DESK                               │
│  • Router Agent (orchestrates)                                  │
│  • Workspace Preference Loader                                  │
│  • Confirmation Handler (always confirms key settings)          │
│  LLM: Gemma 2 9B (FREE) / Claude 3.5 (paid)                    │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ RESEARCH TEAM │    │ CONTENT TEAM  │    │  COST TRACKER │
│               │    │               │    │   (Utility)   │
│ • Web Search  │    │ • Planner     │◄──►│ • Estimator   │
│ • YouTube     │    │ • Hook Gen    │    │ • Recorder    │
│ • News        │    │ • Script      │    │ • Budget Gate │
│ • Trends      │    │               │    │               │
│               │    │               │    │ Tracks ALL:   │
│ LLM: Gemma 2  │    │ LLM: Gemma 2  │    │ - LLM costs   │
│ Tools: FREE   │    │ or Claude     │    │ - Gen costs   │
│ Cost: $0      │    │               │    │ - Research    │
└───────────────┘    └───────┬───────┘    │ - QA costs    │
                             │            └───────────────┘
                    ┌────────┴────────┐
                    ▼                 ▼
           ┌───────────────┐  ┌───────────────┐
           │  CONSISTENCY  │  │  PRODUCTION   │
           │     TEAM      │  │     TEAM      │
           │               │  │               │
           │ • Voice/Tone  │◄─┤ • Scene Plan  │
           │ • Brand       │  │ • Asset Find  │
           │ • Avatar      │  │ • Model Select│
           │ • Model Style │  │ • AI Gen Dir  │
           │ • Text/Subs   │  │               │
           │               │  │ Priority:     │
           │ LLM: Gemma 2  │  │ 1. Project ✓  │
           │ Cost: $0      │  │ 2. Workspace ✓│
           └───────────────┘  │ 3. Stock FREE │
                              │ 4. Generate $ │
                              └───────┬───────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
           ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
           │ EDITING TEAM  │  │   QA TEAM     │  │  TRANSLATION  │
           │               │  │               │  │     TEAM      │
           │ • Studio Spec │  │ • Visual QA   │  │               │
           │ • Captions    │  │ • Audio QA    │  │ • Translator  │
           │ • Audio Mix   │  │ • Model Check │  │ • Subtitler   │
           │ • Transitions │  │ • Style Check │  │               │
           │               │  │               │  │ LLM: Gemma 2  │
           │ LLM: Gemma 2  │  │ LLM: Gemini   │  │ Cost: $0      │
           │ Cost: $0      │  │ Flash (FREE)  │  │               │
           └───────────────┘  │ Cost: $0      │  └───────────────┘
                              └───────────────┘
```

---

## 📦 Detailed Team Specifications

### 1. Front Desk Team

**Purpose:** Entry point, orchestration, confirmation handler.

**Technology:**
| Component | Free Option | Paid Option |
|-----------|-------------|-------------|
| LLM | `google/gemma-2-9b-it:free` | `anthropic/claude-3.5-sonnet` |
| Cost | $0 | ~$0.003/1K tokens |

**Agents:**
- **Router Agent**: Classifies intent, routes to teams
- **Workspace Loader**: Loads workspace preferences, brand, voice profile
- **Confirmation Handler**: Always confirms key settings with user

**Key Behaviors:**
```python
# ALWAYS confirm these even if defaults exist:
MUST_CONFIRM = [
    "aspect_ratio",     # 16:9, 9:16, 1:1
    "target_duration",  # Seconds
    "budget_mode",      # free_only, budget, standard, premium
]

# Load from workspace but can use defaults:
CAN_USE_DEFAULTS = [
    "voice_profile",    # From octupost.workplaces.voice_profile
    "avatar_config",    # From octupost.workplaces.avatar_config
    "subtitle_style",   # From ai_preferences
    "text_overlay_font" # From ai_preferences
]
```

---

### 2. Research Team

**Purpose:** Gather information for content creation.

**Technology:**
| Component | Option | Cost |
|-----------|--------|------|
| LLM | `google/gemma-2-9b-it:free` | $0 |
| Web Search | `DuckDuckGoTools` | $0 |
| Wikipedia | `WikipediaTools` | $0 |
| YouTube | `YouTubeTools` | $0 |
| Reddit | `RedditTools` | $0 |
| Hacker News | `HackerNewsTools` | $0 |
| Article Extraction | `Newspaper4kTools` | $0 |
| **Total** | | **$0** |

**Agents:**
- **Web Searcher**: General web search (DuckDuckGo)
- **YouTube Researcher**: Trends, competitor analysis
- **News Researcher**: Current events
- **Trend Finder**: Viral content, trending sounds
- **Research Combiner**: Compresses all research

**Tools (All FREE):**
```python
# Research & Search (FREE)
from agno.tools.duckduckgo import DuckDuckGoTools    # General web search - FREE
from agno.tools.youtube import YouTubeTools          # YouTube search - FREE
from agno.tools.reddit import RedditTools            # Reddit content - FREE
from agno.tools.hackernews import HackerNewsTools    # Tech trends - FREE
from agno.tools.newspaper4k import Newspaper4kTools  # Article extraction - FREE
from agno.tools.wikipedia import WikipediaTools      # Wikipedia - FREE
from agno.tools.website import WebsiteTools          # Website scraping - FREE

# NOTE: We do NOT use paid tools like TavilyTools or SerpApiTools
# DuckDuckGo is sufficient for our research needs and it's FREE
```

**Output Contract (Compressed):**
```python
@dataclass
class ResearchOutput:
    """Max 800 tokens total."""
    topic: str                      # 50 chars
    key_facts: list[str]            # Max 5 items, 80 chars each
    trending_angles: list[str]      # Max 3 items, 50 chars each
    suggested_hooks: list[str]      # Max 3 items, 100 chars each
    keywords: list[str]             # Max 8 items
    competitor_notes: str           # 100 chars
    trending_sounds: list[str]      # Max 2 references
```

---

### 3. Consistency Team

**Purpose:** Ensure all content matches **workspace** identity across ALL dimensions.

**Technology:**
| Component | Free Option | Paid Option |
|-----------|-------------|-------------|
| LLM | `google/gemma-2-9b-it:free` | `anthropic/claude-3.5-sonnet` |
| Cost | $0 | ~$0.003/1K tokens |

**Agents:**
- **Voice Keeper**: Ensures writing matches workspace voice profile
- **Brand Guardian**: Ensures visuals match workspace brand
- **Avatar Manager**: Handles workspace avatar selection/consistency
- **Style Guardian**: Ensures visual consistency (NEW)

**Style Guardian Responsibilities (NEW):**
```python
STYLE_CONSISTENCY_CHECKS = {
    "video_model_consistency": {
        "description": "All AI-generated videos should use same model within a project",
        "check": "Compare model_id across all session scenes",
        "exception": "Stock videos are exempt"
    },
    "text_overlay_consistency": {
        "description": "All text overlays use same font, size scale, positioning",
        "check": "Validate against workspace ai_preferences.text_overlay_font",
        "elements": ["font_family", "font_weight", "shadow_style", "animation"]
    },
    "subtitle_style_consistency": {
        "description": "All subtitles use same style throughout video",
        "check": "Validate against workspace ai_preferences.subtitle_style",
        "elements": ["font", "size", "color", "background", "position", "animation"]
    },
    "color_palette_consistency": {
        "description": "Brand colors used consistently",
        "check": "Validate against workspace brand_color",
        "elements": ["primary_color", "accent_color", "text_color"]
    },
    "transition_consistency": {
        "description": "Same transition style between scenes",
        "check": "Validate transition type and duration",
        "exception": "Intro/outro can have special transitions"
    }
}
```

**Consistency Validation Flow:**
```python
async def validate_consistency(session: ContentSession) -> ConsistencyResult:
    workspace = await db.get_workspace(session.workspace_id)
    scenes = await db.get_session_scenes(session.id)
    
    issues = []
    
    # 1. Check video model consistency
    video_scenes = [s for s in scenes if s.visual_type == "ai_video"]
    if video_scenes:
        models_used = set(s.model_id for s in video_scenes if s.model_id)
        if len(models_used) > 1:
            issues.append(ConsistencyIssue(
                type="video_model_mismatch",
                severity="warning",
                message=f"Multiple video models used: {models_used}. Consider using same model for consistency.",
                suggestion=f"Recommended: {workspace.ai_preferences.get('preferred_video_models', [None])[0]}"
            ))
    
    # 2. Check text overlay style
    expected_font = workspace.ai_preferences.get("text_overlay_font", "Inter")
    # ... validate against project overlays
    
    # 3. Check subtitle style
    expected_subtitle = workspace.ai_preferences.get("subtitle_style", "default")
    # ... validate against caption settings
    
    # 4. Check color palette
    brand_color = workspace.brand_color
    # ... validate text/overlay colors match brand
    
    return ConsistencyResult(
        passed=len(issues) == 0,
        issues=issues,
        auto_fixable=[i for i in issues if i.can_auto_fix]
    )
```

---

### 4. Content Team

**Purpose:** Plan and script content.

**Technology:**
| Component | Free Option | Paid Option |
|-----------|-------------|-------------|
| LLM | `google/gemma-2-9b-it:free` | `anthropic/claude-3.5-sonnet` |
| Cost | $0 | ~$0.003/1K tokens |

**Agents:**
- **Content Planner**: Creates content structure from research
- **Hook Generator**: Creates attention-grabbing openings
- **Script Writer**: Writes full script with scene breakdown

**Key Behavior:** ALWAYS connected with Consistency Team throughout.

---

### 5. Production Team

**Purpose:** Find/create all assets for the video.

**Technology:**
| Component | Free Option | Paid Options |
|-----------|-------------|--------------|
| LLM | `google/gemma-2-9b-it:free` | `claude-3.5-sonnet` |
| Asset Search | SQL queries, Pexels, Pixabay | N/A |
| Video Gen | N/A | fal models ($0.005-$0.50/sec) |
| Image Gen | N/A | fal models ($0.003-$0.05/img) |
| Voice Gen | N/A | f5-tts ($0.005/sec), ElevenLabs ($0.018/sec) |
| Music | Pixabay (FREE) | Stable Audio ($0.015/sec) |

**Agents:**
- **Scene Planner**: Breaks script into scenes, decides asset type per scene
- **Asset Curator**: Finds existing assets first, then stock, then generates
- **Model Selector**: Chooses optimal AI model based on constraints
- **AI Generation Director**: Crafts prompts, handles generation
- **Avatar Selector**: Picks/generates avatar for consistency

**Asset Priority (STRICT ORDER):**
```python
ASSET_PRIORITY = [
    "project_existing",     # 1. Check project assets (FREE, instant, perfect match)
    "workspace_existing",   # 2. Check workspace assets (FREE, instant)
    "stock_free",           # 3. Pexels/Pixabay (FREE API, must match ratio)
    "ai_generation",        # 4. Generate only if no free option works
]

# Director can mark scenes where stock is acceptable
# This prioritizes free stock even when generation is possible
SCENE_STOCK_ALLOWANCE = {
    "b_roll": True,         # B-roll is perfect for stock
    "transition": True,     # Transitions work well with stock
    "content": "director_decision",  # Director decides
    "intro": False,         # Custom intros preferred
    "outro": False          # Custom outros preferred
}
```

**Model Selection with Aspect Ratio:**
```python
class ModelSelector:
    """Select model that supports exact aspect ratio."""
    
    MODELS_BY_RATIO = {
        "16:9": [
            "fal-ai/minimax-video",
            "fal-ai/kling-video/v2.6/pro",
            "fal-ai/veo3",
            "fal-ai/sora-2"
        ],
        "9:16": [
            "fal-ai/minimax-video",  # Supports portrait
            "fal-ai/kling-video/v2.6/pro",
            "fal-ai/veo3"
        ],
        "1:1": [
            "fal-ai/minimax-video",
            "fal-ai/kling-video/v2.6/pro"
        ]
    }
    
    async def select(
        self,
        scene: Scene,
        aspect_ratio: str,
        budget_remaining: float,
        budget_mode: str,
    ) -> ModelDecision:
        # 1. If free_only mode, no AI generation
        if budget_mode == "free_only":
            return ModelDecision(
                strategy="stock_only",
                recommendation="Use Pexels/Pixabay stock video"
            )
        
        # 2. Get models that support this aspect ratio
        compatible_models = self.MODELS_BY_RATIO.get(aspect_ratio, [])
        if not compatible_models:
            return ModelDecision(
                strategy="unsupported_ratio",
                recommendation=f"No AI models support {aspect_ratio}. Use stock or change ratio."
            )
        
        # 3. Filter by budget tier
        allowed_tiers = self._get_allowed_tiers(budget_mode)
        candidates = [m for m in compatible_models 
                      if self.MODEL_INFO[m]["tier"] in allowed_tiers]
        
        # 4. Select cheapest that fits duration and budget
        for model in sorted(candidates, key=lambda m: self.MODEL_INFO[m]["cost/s"]):
            model_info = self.MODEL_INFO[model]
            if model_info["min_dur"] <= scene.duration <= model_info["max_dur"]:
                cost = scene.duration * model_info["cost/s"]
                if cost <= budget_remaining:
                    return ModelDecision(
                        model_id=model,
                        estimated_cost=cost,
                        aspect_ratio=aspect_ratio,
                        strategy="single_generation"
                    )
        
        return ModelDecision(
            strategy="over_budget",
            recommendation="Consider stock video or increase budget"
        )
```

---

### 6. Editing Team

**Purpose:** Assemble and polish the video in Octupost Studio.

**Technology:**
| Component | Free Option | Paid Option |
|-----------|-------------|-------------|
| LLM | `google/gemma-2-9b-it:free` | `anthropic/claude-3.5-sonnet` |
| Cost | $0 | ~$0.003/1K tokens |

**Agents:**
- **Octupost Studio Specialist**: Main editor
- **Caption Specialist**: Auto-captions with styling
- **Audio Mixer**: Music levels, voice clarity
- **Transition Specialist**: Scene-to-scene transitions

**Studio Specialist Knowledge Base:**
```python
STUDIO_KNOWLEDGE = {
    "overlay_types": ["text", "image", "video", "sound", "caption", "sticker"],
    "animation_presets": {
        "enter": ["fade-in", "slide-up", "zoom-in", "bounce"],
        "exit": ["fade-out", "slide-down", "zoom-out"]
    },
    "caption_templates": ["default", "bold", "karaoke", "highlight", "minimal"],
    "filter_presets": ["vintage", "cinematic", "vivid", "bw"],
    "best_practices": {
        "text_readability": "Min 32px font, high contrast",
        "safe_zones": "Keep important content 10% from edges",
        "pacing": "Scene changes every 3-5 seconds for shorts"
    }
}
```

---

### 7. QA Team

**Purpose:** Quality check all generated content with focus on consistency.

**Technology:**
| Component | Free Option | Paid Option |
|-----------|-------------|-------------|
| Vision LLM | `gemini-1.5-flash` (FREE tier) | `gpt-4o` |
| Cost | $0 (15 RPM free) | ~$0.02/review |

**Agents:**
- **Visual QA**: Checks for artifacts, quality
- **Audio QA**: Checks audio clarity, sync
- **Consistency QA**: Checks style consistency (NEW)
- **QA Coordinator**: Decides regenerate or approve

**QA Checks (Extended):**
```python
QA_CHECKS = {
    "visual_quality": {
        "artifacts": "Check for AI generation artifacts, glitches",
        "resolution": "Ensure matches target resolution",
        "aspect_ratio": "Verify correct aspect ratio"
    },
    "audio_quality": {
        "clarity": "Voice is clear and understandable",
        "sync": "Audio syncs with visuals",
        "levels": "Audio levels are balanced"
    },
    "consistency": {  # NEW
        "model_consistency": "Same video model used throughout",
        "text_overlay_style": "Same font/style for all text overlays",
        "subtitle_style": "Same caption template throughout",
        "color_palette": "Brand colors used consistently",
        "transition_style": "Same transitions between scenes"
    },
    "brand_compliance": {
        "logo_placement": "Logo in correct position if required",
        "colors": "Brand colors used correctly",
        "voice_tone": "Voice matches workspace profile"
    }
}
```

**QA Flow with Consistency:**
```python
async def qa_review(
    asset: Asset,
    session: ContentSession,
    scene: Scene = None,
) -> QADecision:
    # Use FREE Gemini Flash for QA
    qa_model = "gemini-1.5-flash"  # FREE via Google AI Studio
    
    # 1. Run visual QA
    visual_result = await visual_qa.check(asset, model=qa_model)
    
    # 2. Run audio QA (if applicable)
    audio_result = await audio_qa.check(asset, model=qa_model) if asset.has_audio else None
    
    # 3. Run consistency QA (NEW)
    consistency_result = await consistency_qa.check(
        asset=asset,
        session=session,
        scene=scene,
        model=qa_model
    )
    
    # 4. Record QA cost
    await cost_tracker.record_qa_review(
        session_id=session.id,
        model_id=qa_model,
        input_tokens=visual_result.tokens + (audio_result.tokens if audio_result else 0) + consistency_result.tokens,
        output_tokens=100  # Approximate
    )
    
    # 5. Calculate confidence
    all_issues = visual_result.issues + (audio_result.issues if audio_result else []) + consistency_result.issues
    confidence = 1.0 - (len(all_issues) * 0.1)
    
    # 6. Decision logic
    if confidence >= 0.8 and not any(i.severity == "critical" for i in all_issues):
        return QADecision(action="approve", confidence=confidence)
    
    if session.free_only_mode:
        # Can't regenerate, warn user about issues
        return QADecision(
            action="warn_user",
            issues=all_issues,
            message="Issues found but in free-only mode. Accept or provide alternative asset."
        )
    
    # Check if we can afford regeneration
    if await cost_tracker.can_afford(session.id, estimate_regeneration_cost(scene)):
        if session.current_attempt < session.max_regeneration_attempts:
            return QADecision(action="regenerate", with_model=select_alternative_model())
    
    return QADecision(
        action="ask_user",
        issues=all_issues,
        options=["approve_anyway", "regenerate_manually", "provide_asset", "cancel"]
    )
```

---

### 8. Translation Team

**Purpose:** Post-production translation and subtitling.

**Technology:**
| Component | Free Option | Paid Option |
|-----------|-------------|-------------|
| LLM | `google/gemma-2-9b-it:free` | `gpt-4o` |
| Cost | $0 | ~$0.005/1K tokens |

**Agents:**
- **Translate Agent**: Decides if/what needs translation
- **Multi-language Subtitler**: Generates subtitles in target languages

---

## 🆓 Fully Free Mode

### How Free Mode Works

```python
FREE_MODE_CAPABILITIES = {
    # What you CAN do for free
    "can_do": [
        "All LLM operations (Gemma 2 9B, Gemini Flash)",
        "Research (DuckDuckGo, Wikipedia, YouTube, etc.)",
        "Script writing and planning",
        "QA reviews",
        "Search project assets",
        "Search workspace assets",
        "Search Pexels (videos, images)",
        "Search Pixabay (videos, images, music, SFX)",
        "Assemble video in Octupost Studio",
        "Add captions/subtitles",
        "Apply filters and transitions"
    ],
    
    # What you CANNOT do for free
    "cannot_do": [
        "Generate AI videos",
        "Generate AI images",
        "Generate AI voice (TTS)",
        "Generate AI music",
        "Use premium LLMs (Claude, GPT-4o)"
    ],
    
    # Workarounds
    "alternatives": {
        "ai_video": "Use Pexels stock video or existing assets",
        "ai_image": "Use Pexels stock images or existing assets",
        "ai_voice": "User provides voiceover or uses stock narration",
        "ai_music": "Use Pixabay royalty-free music"
    }
}
```

### Free Mode Flow

```
User Request → Front Desk
    ↓
Confirm Settings (aspect_ratio, duration, budget_mode=free_only)
    ↓
Research Team (FREE - Gemma 2 + DuckDuckGo)
    ↓
Content Team (FREE - Gemma 2)
    ↓
Production Team:
    1. Search project assets (FREE)
    2. Search workspace assets (FREE)
    3. Search Pexels/Pixabay (FREE)
    4. If no match → Ask user to provide asset
    ↓
Editing Team (FREE - Gemma 2 + Studio)
    ↓
QA Team (FREE - Gemini Flash)
    ↓
Render (Using Studio)
```

### Free Mode Limitations & Messaging

```python
FREE_MODE_MESSAGES = {
    "no_asset_found": """
        No free asset found for this scene ({scene_type}, {duration}s, {aspect_ratio}).
        
        Options:
        1. Provide your own asset (upload)
        2. Change scene description (might find better stock match)
        3. Change aspect ratio (more stock options in 16:9)
        4. Switch to budget mode ($X estimated for this scene)
    """,
    
    "stock_quality_warning": """
        Found stock video but it may not perfectly match your scene.
        
        Stock: "{stock_description}"
        Scene: "{scene_description}"
        
        Options:
        1. Use this stock video anyway
        2. Search for alternatives
        3. Provide your own asset
        4. Switch to paid generation
    """,
    
    "voice_not_available": """
        AI voice generation requires a paid tier.
        
        Options:
        1. Record and upload your own voiceover
        2. Use text-on-screen only
        3. Switch to budget mode ($X for voice)
    """
}
```

---

## 📊 Phase Plan

### Phase 1: Foundation (MVP) ⭐ START HERE
**Goal:** Basic end-to-end flow with comprehensive cost tracking

**Database:**
- [ ] Extend `octupost.workplaces` with ai_preferences, voice_profile, avatar_config columns
- [ ] Create `octupost.workplace_personas` table
- [ ] Create `agent` schema
- [ ] Create `agent.content_sessions` table
- [ ] Create `agent.session_costs` table (with LLM + generation + research tracking)
- [ ] Create `agent.model_knowledge` table with cost data
- [ ] Add full-text search index to `octupost.assets`

**Cost Tracking:**
- [ ] Implement CostTracker class
- [ ] Track LLM costs per team
- [ ] Track generation costs
- [ ] Track research costs (all $0 for MVP)
- [ ] Session cost summary API

**LLM Selection:**
- [ ] OpenRouter integration for free models
- [ ] Google AI Studio integration for free Gemini
- [ ] Model selector with tier support

**Agents (Minimal):**
- [ ] Front Desk Router (Gemma 2 - FREE)
- [ ] Cost Tracker utility (CRITICAL)
- [ ] Basic asset search (project → workspace → stock)
- [ ] Basic QA (Gemini Flash - FREE)

**Tools:**
- [ ] Pexels search tool (FREE)
- [ ] Pixabay search tool (FREE)
- [ ] Asset search tool (SQL - FREE)
- [ ] Octupost API generation tool (paid)

### Phase 2: Content Intelligence
**Goal:** Research and script capabilities

**Database:**
- [ ] Create `agent.session_scenes` table

**Agents:**
- [ ] Research Team (all FREE tools)
- [ ] Content Team (Gemma 2 - FREE)
- [ ] Consistency Team (Gemma 2 - FREE)

### Phase 3: Smart Production & QA
**Goal:** Intelligent asset selection and comprehensive QA

**Database:**
- [ ] Create `agent.session_qa_reviews` table

**Agents:**
- [ ] Model Selector (aspect ratio + cost aware)
- [ ] Asset Curator (strict priority order)
- [ ] Full QA Team with consistency checks
- [ ] Style Guardian for consistency

### Phase 4: Polish & Advanced Features
**Goal:** Advanced editing and personalization

**Features:**
- [ ] Translation Team
- [ ] Advanced editing capabilities
- [ ] Persona-specific workflows
- [ ] Learning from user feedback (update workspace preferences)

---

## 🎯 Success Metrics

1. **Cost Accuracy**: Estimated vs actual within 10%
2. **Free Mode Viability**: Complete videos possible with $0 spend
3. **Cost Tracking Coverage**: 100% of operations tracked
4. **QA Pass Rate**: >80% first-attempt pass
5. **Asset Reuse Rate**: >30% scenes use existing/stock assets
6. **Consistency Score**: >90% style consistency within projects

---

## 📝 Design Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Schema split | `octupost` + `agent` | Keep workspace data synced, sessions ephemeral |
| Aspect ratio | Exact match only | Quality > convenience |
| Asset search | Full-text on prompts | 100% free, good enough |
| Free LLMs | Gemma 2 + Gemini Flash | Both actually free, good quality |
| QA model | Gemini Flash | Free tier with vision support |
| Research tools | DuckDuckGo + free tools | All free, sufficient for MVP |
| Cost tracking | Per-operation | Granular for debugging and optimization |

---

## 🔗 References

**Schemas:**
- `octupost.*` - App data (extended with AI columns)
- `agent.*` - Session-specific data (costs, scenes, QA)
- `agno.*` - Agno framework data (auto-created)

**Free APIs:**
- OpenRouter free models: https://openrouter.ai/models?q=free
- Google AI Studio (Gemini): https://ai.google.dev/pricing
- Pexels API: https://www.pexels.com/api/documentation/
- Pixabay API: https://pixabay.com/api/docs/
- DuckDuckGo: No API key needed

**Code:**
- Model registry: `packages/shared/src/registry/models.json`
- Studio types: `octupost-studio/app/reactvideoeditor/pro/types/`
- Octupost API: `octupost-api/app/services/generation_service.py`
