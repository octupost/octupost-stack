# Media Agent Research Pack

A comprehensive collection of APIs, tools, and resources for building a video editing and image generation agent.

## Purpose

This research pack consolidates information about external services that can power an AI media agent capable of:

- Generating and editing images
- Creating videos from text, images, or templates
- Synthesizing speech and audio
- Sourcing stock assets (images, videos, GIFs, music)
- Applying visual effects, captions, and enhancements

## Directory Structure

```
research/media-agent/
├── README.md              # This file
├── plan.md                # Research phases and checklist
├── apis/
│   ├── visuals.md         # Image generation, avatars, graphics
│   ├── video.md           # Text-to-video, image-to-video, editing
│   ├── audio.md           # TTS, voice cloning, dubbing, music
│   ├── data-sources.md    # Stock assets (Pexels, Pixabay, Giphy, etc.)
│   └── utils.md           # Transcoding, upscaling, bg removal, captions
├── comparison/
│   ├── matrix.md          # Side-by-side capability/pricing table
│   └── playbooks.md       # Recommended stacks for common workflows
└── examples/
    ├── curl/              # Sample cURL requests
    ├── typescript/        # TypeScript/Node.js examples
    └── python/            # Python examples
```

## Quick Navigation

| Need | Document |
|------|----------|
| Generate images | [apis/visuals.md](apis/visuals.md) |
| Create videos | [apis/video.md](apis/video.md) |
| Add voiceover/music | [apis/audio.md](apis/audio.md) |
| Find stock footage | [apis/data-sources.md](apis/data-sources.md) |
| Caption/upscale/transcode | [apis/utils.md](apis/utils.md) |
| Compare options | [comparison/matrix.md](comparison/matrix.md) |
| End-to-end workflows | [comparison/playbooks.md](comparison/playbooks.md) |

## Using the explorer (simplified)

- Open the docs app (`npm run dev` inside `docs/`) and use the single search bar for names, features, or categories.
- Tap category chips to narrow results; switch pricing with the compact dropdown (free, free tier, freemium, paid).
- Jump via category anchors just like fal.ai’s lightweight docs—no bulky sidebar.
- Sort by relevance, quality, or name; clear everything with Reset.
- Open a card to view a lightweight detail sheet with links and examples.

## Evaluation Criteria

When selecting an API, consider:

1. **Pricing tier** - Free tier limits, pay-as-you-go rates
2. **Rate limits** - Requests per minute/day, concurrent jobs
3. **Quality** - Output resolution, model capabilities
4. **Latency** - Generation time, cold start penalties
5. **Licensing** - Commercial use rights, attribution requirements
6. **SDK support** - Official libraries for Python, JS/TS, etc.
7. **Region/compliance** - Data residency, GDPR, SOC 2

## Getting Started

1. Review [plan.md](plan.md) for the research approach
2. Browse individual API docs in `apis/`
3. Check [comparison/matrix.md](comparison/matrix.md) to shortlist options
4. Use [comparison/playbooks.md](comparison/playbooks.md) for workflow guidance
5. Copy examples from `examples/` to bootstrap integration

## Contributing

When adding new APIs:

1. Add entry to the relevant `apis/*.md` file following the template
2. Update [comparison/matrix.md](comparison/matrix.md)
3. Add example requests if available
4. Note any licensing or attribution requirements

