# Video Generation & Editing APIs

APIs for text-to-video, image-to-video, and programmatic video editing.

> Last verified: 2025-12-06. Pricing, durations, and aspect ratios change often—confirm with vendor docs before purchase.

---

## Text-to-Video

### Runway ML (Gen-3 Alpha)

**Website:** https://runwayml.com  
**Docs:** https://docs.runwayml.com

**Authentication:** API key

**Pricing:**
- Gen-3 Alpha: ~$0.50/second of video
- Subscription plans start at $15/month (limited credits)

**Key Capabilities:**
- State-of-the-art video generation
- Text-to-video and image-to-video
- Camera motion controls
- 10-second clips (16:9, 1:1, 9:16)
- Realistic motion and physics

**Limitations:**
- Expensive for long videos
- 10-second max per generation
- Queue times during peak

**SDKs:** REST API, Python

**Licensing:** Commercial use allowed with subscription

---

### Pika Labs

**Website:** https://pika.art  
**Docs:** API in development

**Authentication:** API access limited

**Pricing:**
- Free tier: 250 credits/month
- Pro: $10/month

**Key Capabilities:**
- Text-to-video, image-to-video
- Video-to-video modification
- Lip sync
- Extend video length (typically 3–4s clips; 16:9, 1:1, 9:16)

**Limitations:**
- API not publicly available yet
- Web/Discord interface only

**SDKs:** Not available

**Licensing:** TBD

---

### Kling AI

**Website:** https://klingai.com  
**Docs:** Contact for API

**Authentication:** API key (enterprise)

**Pricing:**
- Consumer: ~$0.14/video (5 sec)
- Enterprise: Custom

**Key Capabilities:**
- High-quality 1080p video
- Text-to-video, image-to-video
- Long video generation (up to ~3 min; 16:9 and portrait support)
- Chinese language optimized

**Limitations:**
- API access restricted
- Some content restrictions

**SDKs:** REST API

**Licensing:** Commercial use allowed

---

### Luma Labs (Dream Machine)

**Website:** https://lumalabs.ai  
**Docs:** https://docs.lumalabs.ai

**Authentication:** API key

**Pricing:**
- Free tier: 30 generations/month
- Standard: $29.99/month (150 gen)
- Pay-per-generation available

**Key Capabilities:**
- Text-to-video, image-to-video
- Camera motion presets
- Realistic physics
- 5-second clips, extendable (16:9, 1:1, 9:16)

**Limitations:**
- Limited resolution options
- Queue times

**SDKs:** REST API

**Licensing:** Commercial use allowed

---

### Minimax (Hailuo)

**Website:** https://hailuoai.video  
**Docs:** Available via fal.ai

**Authentication:** Via fal.ai or direct API

**Pricing:**
- Via fal.ai: ~$0.20-0.50/video (5-6s clips)

**Key Capabilities:**
- High-quality video generation
- Strong motion coherence
- Text-to-video, image-to-video (16:9 or 9:16 presets)

**Limitations:**
- Direct API access limited
- Content moderation

**SDKs:** Via fal.ai

**Licensing:** Commercial use with terms

**Sample Request (via fal.ai):**
```typescript
import { fal } from "@fal-ai/client";

const result = await fal.subscribe("fal-ai/minimax-video/image-to-video", {
  input: {
    prompt: "A woman walks down a Tokyo street with neon lights",
    image_url: "https://example.com/image.jpg"
  },
});
```

---

### HeyGen (Text-to-Video with Avatar)

**Website:** https://heygen.com  
**Docs:** https://docs.heygen.com

**Authentication:** API key

**Pricing:**
- Creator: $29/month (15 min video)
- Business: $89/month (60 min video)
- API: Per-minute pricing (~$0.50/min; volume discounts)

**Key Capabilities:**
- AI avatar videos from text
- 100+ stock avatars
- 40+ languages with translation
- Custom avatar creation
- Template library
- Aspect ratios: 16:9, 1:1, 9:16

**Limitations:**
- Avatar-focused (not general video)
- Expensive for volume
- 4K not yet available on lower tiers

**SDKs:** REST API

**Licensing:** Commercial use allowed

---

### Synthesia

**Website:** https://synthesia.io  
**Docs:** https://docs.synthesia.io

**Authentication:** API key

**Pricing:**
- Starter: $22/month (10 min)
- Creator: $67/month (30 min)
- Enterprise: Custom

**Key Capabilities:**
- AI avatar videos
- 150+ avatars
- 130+ languages
- Custom avatars
- Screen recording integration

**Limitations:**
- API on higher tiers only
- Avatar-focused
- Aspect ratios: 16:9 and 1:1 primary; no vertical output on basic plans

**SDKs:** REST API

**Licensing:** Commercial use allowed

---

## Image-to-Video

### fal.ai (Multiple Models)

**Website:** https://fal.ai  
**Docs:** https://docs.fal.ai/model-apis/guides/generate-videos-from-image

**Authentication:** API key

**Pricing:**
- Minimax I2V: ~$0.20-0.50/video
- Wan I2V: Similar pricing
- Pay-per-second GPU

**Key Capabilities:**
- Multiple model options
- Fast inference
- Prompt-guided animation
- Various styles

**Limitations:**
- Quality varies by model

**SDKs:** JavaScript, Python, REST

**Licensing:** Commercial use allowed

---

### Stable Video Diffusion (via Stability AI)

**Website:** https://stability.ai  
**Docs:** https://platform.stability.ai

**Authentication:** API key

**Pricing:**
- ~$0.20/video generation (4s clip)

**Key Capabilities:**
- Image-to-video animation
- Motion control
- 4-second clips (landscape or portrait; 16:9/9:16)

**Limitations:**
- Short duration
- Limited motion control
- Fixed aspect options (16:9, 9:16)

**SDKs:** Python, REST

**Licensing:** Commercial use with API

---

### deAPI

**Website:** https://deapi.ai  
**Docs:** https://docs.deapi.ai

**Authentication:** API key

**Pricing:**
- Pay-per-generation
- Competitive rates

**Key Capabilities:**
- Unified API for multiple AI video models
- Image-to-video
- Scalable infrastructure

**Limitations:**
- Aggregator (depends on underlying models)

**SDKs:** REST

**Licensing:** Depends on model

---

## Programmatic Video Editing

### Shotstack

**Website:** https://shotstack.io  
**Docs:** https://shotstack.io/docs/api

**Authentication:** API key

**Pricing:**
- Free tier: 500 renders/month (watermarked)
- Starter: $25/month (500 renders)
- Business: $99/month (2000 renders)

**Key Capabilities:**
- JSON-based video editing
- Merge clips, images, audio
- Text overlays, transitions
- Templates
- Webhook delivery

**Limitations:**
- Learning curve for JSON schema
- Limited effects compared to desktop editors

**SDKs:** Node.js, PHP, Ruby, Python, REST

**Licensing:** Commercial use allowed

**Sample Request:**
```json
{
  "timeline": {
    "tracks": [
      {
        "clips": [
          {
            "asset": {
              "type": "video",
              "src": "https://example.com/video.mp4"
            },
            "start": 0,
            "length": 5
          }
        ]
      }
    ]
  },
  "output": {
    "format": "mp4",
    "resolution": "hd"
  }
}
```

---

### Creatomate

**Website:** https://creatomate.com  
**Docs:** https://creatomate.com/docs

**Authentication:** API key

**Pricing:**
- Free tier: 5 renders/month
- Pro: $59/month (200 renders)
- Business: $149/month (500 renders)

**Key Capabilities:**
- Template-based rendering
- Dynamic content insertion
- Animations and effects
- Batch rendering
- Social media formats

**Limitations:**
- Template-focused workflow
- Limited free tier

**SDKs:** Node.js, Python, REST

**Licensing:** Commercial use allowed

---

### JSON2Video

**Website:** https://json2video.com  
**Docs:** https://json2video.com/docs

**Authentication:** API key

**Pricing:**
- Pay-per-minute of video
- ~$0.10/minute

**Key Capabilities:**
- JSON to video conversion
- Text, images, video clips
- TTS integration
- Subtitles

**Limitations:**
- Basic effects
- Simpler than Shotstack

**SDKs:** REST

**Licensing:** Commercial use allowed

---

### Editframe

**Website:** https://editframe.com  
**Docs:** https://docs.editframe.com

**Authentication:** API key

**Pricing:**
- Free tier available
- Usage-based pricing

**Key Capabilities:**
- Programmatic video editing
- Filters, transitions
- Audio mixing
- Template system

**Limitations:**
- Newer platform

**SDKs:** Node.js, Python, REST

**Licensing:** Commercial use allowed

---

## Video Processing Libraries

### FFmpeg

**Website:** https://ffmpeg.org  
**Docs:** https://ffmpeg.org/documentation.html

**Authentication:** None (self-hosted)

**Pricing:** Free (open source)

**Key Capabilities:**
- Transcode any format
- Trim, merge, concatenate
- Add audio, subtitles
- Filters and effects
- Hardware acceleration

**Limitations:**
- Command-line complexity
- Self-hosted only

**SDKs:** C library, CLI, wrappers in all languages

**Licensing:** LGPL/GPL

---

### MoviePy (Python)

**Website:** https://zulko.github.io/moviepy  
**Docs:** https://zulko.github.io/moviepy/getting_started

**Authentication:** None (library)

**Pricing:** Free (open source)

**Key Capabilities:**
- Python-based video editing
- Cut, concatenate, composite
- Text overlays
- Effects and transitions
- GIF export

**Limitations:**
- Slower than FFmpeg
- Memory-intensive

**SDKs:** Python

**Licensing:** MIT

**Sample:**
```python
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

video = VideoFileClip("input.mp4").subclip(0, 10)
text = TextClip("Hello World", fontsize=50, color='white')
text = text.set_position('center').set_duration(5)
final = CompositeVideoClip([video, text])
final.write_videofile("output.mp4")
```

