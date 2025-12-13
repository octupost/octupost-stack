# 🎬 Octupost AI Content Team - Simplified Scope

> **Version:** 5.0 (Stock-First)  
> **Status:** Planning Phase  
> **Framework:** Agno  
> **Focus:** Script → Stock Footage → RVE Timeline

---

## 📋 Executive Summary

A streamlined AI content creation system that **finds and assembles stock footage** based on scripts. No generative AI for media—only LLMs for research, writing, and coordination.

**Core Flow:**
```
User Brief → Research → Script (with scenes) → Find 10 Videos → RVE Timeline
```

**What We Do:**
- Research topics using free tools (DuckDuckGo, YouTube, Wikipedia)
- Write scripts with scene descriptions
- Find matching stock videos from Pexels/Pixabay
- Output RVE-compatible timeline JSON

**What We DON'T Do:**
- ❌ AI video generation
- ❌ AI image generation  
- ❌ AI voice generation
- ❌ QA/visual analysis

---

## 🎯 Architecture Overview

### Team Structure (4 Agents)

```
┌─────────────────────────────────────────────────────────────┐
│                    CONTENT TEAM (Agno Team)                 │
│                     mode="coordinate"                        │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Researcher │→ │   Writer    │→ │  Producer   │         │
│  │   Agent     │  │   Agent     │  │   Agent     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                           │                  │
│                                           ▼                  │
│                                    ┌─────────────┐          │
│                                    │   Editor    │          │
│                                    │   Agent     │          │
│                                    └─────────────┘          │
│                                           │                  │
│                                           ▼                  │
│                                    [RVE Timeline]           │
└─────────────────────────────────────────────────────────────┘
```

**Why 4 agents?**
- Researcher: Gathers information
- Writer: Creates script with ~10 scenes
- Producer: Finds 10 stock videos (1 per scene)
- Editor: Assembles into RVE timeline

---

## 🤖 Agent Definitions

### 1. Researcher Agent

**Purpose:** Gather information for content creation.

```python
from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.youtube import YouTubeTools
from agno.tools.wikipedia import WikipediaTools
from agno.tools.newspaper4k import Newspaper4kTools

researcher = Agent(
    name="Researcher",
    role="Research and gather information for video content",
    model=OpenRouterChat(id="amazon/nova-2-lite-v1:free"),  # FREE
    tools=[
        DuckDuckGoTools(),      # FREE web search
        YouTubeTools(),         # FREE YouTube search
        WikipediaTools(),       # FREE Wikipedia
        Newspaper4kTools(),     # FREE article extraction
    ],
    instructions=[
        "Search for relevant, recent information on the topic",
        "Extract 5-10 key facts",
        "Identify trending angles",
        "Suggest 3 hook ideas",
        "Note visual concepts that could be found in stock footage",
        "Keep output under 500 tokens"
    ],
    markdown=True,
)
```

**Tools (All FREE):**
| Tool | Purpose |
|------|---------|
| DuckDuckGo | Web search for facts |
| YouTube | Find trending video angles |
| Wikipedia | Background information |
| Newspaper4k | Extract article content |

---

### 2. Writer Agent

**Purpose:** Create scripts with scene descriptions optimized for stock footage search.

```python
writer = Agent(
    name="Writer",
    role="Write video scripts with stock-footage-friendly scenes",
    model=OpenRouterChat(id="amazon/nova-2-lite-v1:free"),  # FREE
    instructions=[
        "Create exactly 10 scenes for the video",
        "Each scene should be 3-6 seconds",
        "Write scene descriptions that match common stock footage",
        "Use generic, searchable visual concepts",
        "Avoid overly specific scenes that won't match stock",
        "Include voice-over text for each scene",
        "Target total duration: {target_duration}s",
        
        # Stock-friendly scene guidelines
        "GOOD scenes: 'person working at laptop', 'city skyline at sunset'",
        "BAD scenes: 'specific celebrity', 'branded product close-up'",
    ],
    markdown=True,
)
```

**Output Format:**
```json
{
  "title": "Video Title",
  "hook": "Opening hook text",
  "scenes": [
    {
      "scene_number": 1,
      "duration": 5,
      "visual_description": "Person typing on laptop in modern office",
      "search_keywords": ["person laptop", "office work", "typing computer"],
      "voice_over": "In today's digital world..."
    },
    // ... 9 more scenes
  ],
  "total_duration": 50
}
```

---

### 3. Producer Agent

**Purpose:** Find stock videos for each scene. **No AI generation.**

```python
producer = Agent(
    name="Producer",
    role="Find stock footage for each scene",
    model=OpenRouterChat(id="amazon/nova-2-lite-v1:free"),  # FREE
    tools=[
        PexelsSearchTool(),          # FREE stock video
        PixabaySearchTool(),         # FREE stock video
    ],
    instructions=[
        "For each scene, search stock footage using the keywords",
        "Find exactly 1 video per scene (10 total)",
        "Match aspect_ratio: {aspect_ratio}",
        "Prefer videos 5-15 seconds long",
        "Verify video quality (min 720p)",
        "Return video URLs, durations, and attribution",
        
        # Search strategy
        "Try primary keyword first",
        "If no results, try alternative keywords",
        "If still no results, broaden the search",
        "NEVER skip a scene - always find something",
    ],
    markdown=True,
)
```

**Output Format:**
```json
{
  "assets": [
    {
      "scene_number": 1,
      "source": "pexels",
      "video_url": "https://videos.pexels.com/...",
      "video_id": "12345",
      "duration": 8,
      "width": 1920,
      "height": 1080,
      "attribution": "Video by John Doe from Pexels",
      "search_query_used": "person laptop office"
    },
    // ... 9 more assets
  ]
}
```

**Stock APIs (All FREE):**

| API | Rate Limit | Quality | License |
|-----|------------|---------|---------|
| Pexels | 200 req/hr | High | Free for commercial |
| Pixabay | 100 req/min | Good | Free for commercial |

---

### 4. Editor Agent

**Purpose:** Assemble assets into RVE Timeline format.

```python
editor = Agent(
    name="Editor",
    role="Assemble stock footage into RVE Timeline",
    model=OpenRouterChat(id="amazon/nova-2-lite-v1:free"),  # FREE
    instructions=[
        "Create RVE Timeline JSON from script and assets",
        "Place each video clip on the timeline",
        "Set correct start times and durations",
        "Trim clips to match scene duration",
        "Add text overlays for voice-over (optional)",
        "Apply default transitions between clips",
        "Output valid RVE Timeline JSON"
    ],
    markdown=True,
)
```

**RVE Timeline Output Format:**
```json
{
  "id": "timeline-uuid",
  "duration": 50,
  "tracks": [
    {
      "id": "video-track",
      "type": "video",
      "clips": [
        {
          "id": "clip-1",
          "type": "video",
          "src": "https://videos.pexels.com/...",
          "start": 0,
          "duration": 5,
          "trim": { "start": 0, "end": 5 },
          "position": { "x": 0, "y": 0 },
          "size": { "width": 1920, "height": 1080 }
        },
        // ... more clips
      ]
    },
    {
      "id": "text-track",
      "type": "text",
      "clips": [
        {
          "id": "text-1",
          "type": "text",
          "content": "In today's digital world...",
          "start": 0,
          "duration": 5,
          "style": {
            "fontSize": 48,
            "fontFamily": "Inter",
            "color": "#ffffff",
            "position": "bottom-center"
          }
        }
      ]
    }
  ],
  "settings": {
    "width": 1920,
    "height": 1080,
    "fps": 30,
    "aspectRatio": "16:9"
  }
}
```

---

## 👥 Content Team (Agno Team)

```python
from agno.team import Team
from agno.storage.postgres import PostgresStorage

content_team = Team(
    name="Stock Footage Content Team",
    mode="coordinate",  # Sequential: research → write → produce → edit
    leader=Agent(
        name="Director",
        role="Coordinate content creation workflow",
        model=OpenRouterChat(id="amazon/nova-2-lite-v1:free"),
    ),
    members=[researcher, writer, producer, editor],
    storage=PostgresStorage(
        db_url=DATABASE_URL,
        table_name="content_sessions",
    ),
    instructions=[
        "1. Research the topic thoroughly",
        "2. Write a 10-scene script with stock-friendly descriptions",
        "3. Find stock videos for all 10 scenes",
        "4. Assemble into RVE Timeline",
        "5. Return timeline JSON"
    ],
    enable_agentic_context=True,
    share_member_interactions=True,
)
```

---

## 🔧 Tools Implementation

### Pexels Search Tool

```python
from agno.tools import Toolkit
import httpx

class PexelsSearchTool(Toolkit):
    """Search Pexels for stock videos."""
    
    def __init__(self, api_key: str):
        super().__init__(name="pexels_search")
        self.api_key = api_key
        self.base_url = "https://api.pexels.com/videos"
        self.register(self.search_videos)
    
    def search_videos(
        self, 
        query: str, 
        orientation: str = "landscape",  # landscape, portrait, square
        per_page: int = 5
    ) -> list:
        """
        Search Pexels for videos matching query.
        
        Args:
            query: Search keywords
            orientation: Video orientation (landscape=16:9, portrait=9:16, square=1:1)
            per_page: Number of results (max 80)
        
        Returns:
            List of video results with URLs and metadata
        """
        response = httpx.get(
            f"{self.base_url}/search",
            params={
                "query": query,
                "orientation": orientation,
                "per_page": per_page,
            },
            headers={"Authorization": self.api_key}
        )
        
        data = response.json()
        
        return [
            {
                "id": video["id"],
                "url": video["url"],
                "duration": video["duration"],
                "width": video["width"],
                "height": video["height"],
                "video_files": [
                    {
                        "quality": f["quality"],
                        "link": f["link"],
                        "width": f["width"],
                        "height": f["height"],
                    }
                    for f in video["video_files"]
                    if f["quality"] in ["hd", "sd"]
                ],
                "user": video["user"]["name"],
            }
            for video in data.get("videos", [])
        ]
```

### Pixabay Search Tool

```python
class PixabaySearchTool(Toolkit):
    """Search Pixabay for stock videos."""
    
    def __init__(self, api_key: str):
        super().__init__(name="pixabay_search")
        self.api_key = api_key
        self.base_url = "https://pixabay.com/api/videos"
        self.register(self.search_videos)
    
    def search_videos(
        self, 
        query: str,
        video_type: str = "all",  # all, film, animation
        per_page: int = 5
    ) -> list:
        """
        Search Pixabay for videos matching query.
        
        Args:
            query: Search keywords
            video_type: Type of video
            per_page: Number of results (max 200)
        
        Returns:
            List of video results with URLs and metadata
        """
        response = httpx.get(
            self.base_url,
            params={
                "key": self.api_key,
                "q": query,
                "video_type": video_type,
                "per_page": per_page,
            }
        )
        
        data = response.json()
        
        return [
            {
                "id": video["id"],
                "duration": video["duration"],
                "width": video["videos"]["medium"]["width"],
                "height": video["videos"]["medium"]["height"],
                "video_files": {
                    "large": video["videos"]["large"]["url"],
                    "medium": video["videos"]["medium"]["url"],
                    "small": video["videos"]["small"]["url"],
                },
                "user": video["user"],
                "tags": video["tags"],
            }
            for video in data.get("hits", [])
        ]
```

---

## 🔄 Workflow

### Simple Flow (All FREE)

```
User Request: "Create a video about productivity tips"
    │
    ▼
┌─────────────────────────────────────────┐
│ 1. RESEARCH (FREE)                       │
│    Researcher: DuckDuckGo, YouTube       │
│    Output: Key facts, trending angles    │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ 2. WRITE SCRIPT (FREE)                   │
│    Writer: Create 10 scenes              │
│    Output: Script with stock keywords    │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ 3. FIND STOCK FOOTAGE (FREE)             │
│    Producer: Pexels + Pixabay search     │
│    Output: 10 video URLs                 │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ 4. ASSEMBLE TIMELINE (FREE)              │
│    Editor: Create RVE Timeline JSON      │
│    Output: Timeline ready for player     │
└─────────────────────────────────────────┘
    │
    ▼
[RVE Video Player renders the timeline]
```

### Implementation

```python
async def create_stock_video(brief: str, aspect_ratio: str = "16:9", duration: int = 60):
    """Create a video using only stock footage."""
    
    # Map aspect ratio to orientation
    orientation_map = {
        "16:9": "landscape",
        "9:16": "portrait",
        "1:1": "square"
    }
    
    # Run the content team
    result = await content_team.run(
        message=f"""
        Create a video about: {brief}
        
        Requirements:
        - Aspect ratio: {aspect_ratio}
        - Target duration: {duration} seconds
        - Create exactly 10 scenes
        - Find stock footage for each scene
        - Output RVE Timeline JSON
        """,
        session_id=f"stock-video-{uuid4()}",
    )
    
    return result  # RVE Timeline JSON
```

---

## 🗄️ Database Schema (Minimal)

### Only What We Need

```sql
-- Agno manages sessions automatically
-- We only need minimal tracking

CREATE SCHEMA IF NOT EXISTS agent;

-- Track sessions for debugging
CREATE TABLE agent.stock_video_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    project_id UUID,
    
    -- Request
    brief TEXT NOT NULL,
    aspect_ratio TEXT DEFAULT '16:9',
    target_duration INT DEFAULT 60,
    
    -- Results
    script_json JSONB,
    assets_json JSONB,
    timeline_json JSONB,
    
    -- Status
    status TEXT DEFAULT 'pending',  -- pending, researching, writing, producing, editing, complete, error
    error_message TEXT,
    
    created_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_sessions_workspace ON agent.stock_video_sessions(workspace_id);
CREATE INDEX idx_sessions_status ON agent.stock_video_sessions(status);
```

**That's it! Just 1 table.** Agno handles the rest.

---

## 💰 Cost Analysis

### Everything is FREE

| Component | Cost | Notes |
|-----------|------|-------|
| LLM (Gemma 2) | $0 | OpenRouter free tier |
| DuckDuckGo | $0 | No API key needed |
| YouTube Search | $0 | Public API |
| Wikipedia | $0 | Public API |
| Pexels | $0 | Free API, 200 req/hr |
| Pixabay | $0 | Free API, 100 req/min |
| **Total per video** | **$0** | ✅ |

### Costs We Removed

| Removed Feature | Was Costing |
|-----------------|-------------|
| AI video generation | $0.035-$0.50/second |
| AI image generation | $0.003-$0.05/image |
| AI voice generation | $0.005-$0.018/second |
| QA visual analysis | Gemini API costs |
| Premium LLMs | $0.003-$0.005/1K tokens |

---

## 🎯 Supported Configurations

### Aspect Ratios

| Ratio | Use Case | Pexels Param | RVE Setting |
|-------|----------|--------------|-------------|
| 16:9 | YouTube, Desktop | `landscape` | 1920x1080 |
| 9:16 | TikTok, Reels, Shorts | `portrait` | 1080x1920 |
| 1:1 | Instagram, Feed | `square` | 1080x1080 |

### Duration Targets

| Type | Duration | Scenes |
|------|----------|--------|
| Short | 15-30s | 5-6 scenes |
| Standard | 45-60s | 10 scenes |
| Long | 90-120s | 15-20 scenes |

---

## 📊 Phase Plan

### Phase 1: MVP ⭐ NOW

**Goal:** End-to-end stock video creation

- [ ] Set up Agno Team with 4 agents
- [ ] Implement PexelsSearchTool
- [ ] Implement PixabaySearchTool  
- [ ] Create RVE Timeline output format
- [ ] Test with simple brief
- [ ] Integrate with RVE player

**Deliverable:** Create 60s video from brief using stock footage

### Phase 2: Improvements

**Goal:** Better matching and variety

- [ ] Add project/workspace asset search (reuse existing)
- [ ] Improve search keyword generation
- [ ] Add fallback search strategies
- [ ] Support music/audio tracks from Pixabay
- [ ] Add subtitle/caption support

**Deliverable:** Higher quality matches, audio support

### Phase 3: Polish

**Goal:** User experience

- [ ] Preview before finalizing
- [ ] Swap individual clips
- [ ] Manual search override
- [ ] Save favorite clips to workspace

---

## 🎯 Success Metrics

| Metric | Target |
|--------|--------|
| Videos created at $0 | 100% |
| Stock footage found | 10/10 scenes |
| Average creation time | < 2 minutes |
| User satisfaction | > 80% keep result |

---

## 📝 Design Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| No AI generation | Stock only | Zero cost, instant results |
| 4 agents (not 5) | Remove QA | Simpler, user can review |
| 10 scenes | Fixed count | Predictable, good length |
| Pexels + Pixabay | Two sources | More variety, both free |
| RVE Timeline | JSON output | Direct player integration |
| Single table | Minimal DB | Agno handles sessions |

---

## 🔗 API References

**Stock Video APIs:**
- Pexels: https://www.pexels.com/api/documentation/#videos
- Pixabay: https://pixabay.com/api/docs/#videos

**Agno Framework:**
- Teams: https://docs.agno.com/teams
- Tools: https://docs.agno.com/tools

**RVE (React Video Editor):**
- Timeline format: Based on RVE Default Sidebar schema
- Player integration: RVE General documentation

---

## 📄 Changelog

### Version 5.0 (Stock-First)
- **Removed** QA Agent (user reviews instead)
- **Removed** ALL AI generation (video, image, voice)
- **Removed** cost tracking (everything is free)
- **Removed** budget modes (only free mode)
- **Removed** generation tools
- **Simplified** to 4 agents from 5
- **Simplified** database to 1 table
- **Added** RVE Timeline output format
- **Focus** on stock footage discovery and assembly

### Previous Version
- v4.0: 5 agents, AI generation support, cost tracking

