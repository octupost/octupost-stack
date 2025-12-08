# API Comparison Matrix

Quick reference tables for comparing APIs across domains.

> Last verified: 2025-12-06. Pricing/durations change frequently—confirm on vendor docs.

---

## Image Generation

| API | Free Tier | Price/Image | Quality | Speed | Voice/Avatar | Best For |
|-----|-----------|-------------|---------|-------|--------------|----------|
| **OpenAI DALL-E 3** | None | $0.04-0.12 | ★★★★★ | 10-20s | No | High-quality creative images |
| **fal.ai Flux** | Pay-as-you-go | ~$0.025 | ★★★★★ | 5-10s | No | Fast, high-quality generation |
| **fal.ai Fast-SDXL** | Pay-as-you-go | ~$0.0025 | ★★★★ | 2-3s | No | Budget-friendly, fast |
| **Stability AI SDXL** | 25 credits | $0.002-0.006 | ★★★★ | 5-15s | No | Flexibility, fine-tuning |
| **Replicate** | Limited | ~$0.02 | ★★★★ | Varies | No | Open-source model access |
| **DeepAI** | 5/month | $0.05 | ★★★ | 3-5s | No | Quick prototypes |

### Recommendation
- **Best Quality:** DALL-E 3 or Flux
- **Best Value:** fal.ai Fast-SDXL
- **Most Flexible:** Replicate (access to any model)

---

## Text-to-Speech

| API | Free Tier | Price/1K Chars | Voice Quality | Languages | Cloning | Streaming |
|-----|-----------|----------------|---------------|-----------|---------|-----------|
| **ElevenLabs** | 10K chars/mo | $0.18-0.30 | ★★★★★ | 29 | Yes | Yes |
| **OpenAI TTS** | None | $0.015-0.030 | ★★★★ | 50+ | No | Yes |
| **Google Cloud TTS** | 1M chars/mo | $0.004-0.016 | ★★★★ | 40+ | Enterprise | Yes |
| **Amazon Polly** | 5M chars/mo | $0.004-0.016 | ★★★★ | 30+ | No | Yes |
| **Azure Speech** | 500K chars/mo | $0.016 | ★★★★ | 140+ | Enterprise | Yes |
| **PlayHT** | 12.5K chars/mo | ~$0.10 | ★★★★★ | 140+ | Yes | Yes |

### Recommendation
- **Best Quality:** ElevenLabs
- **Best Free Tier:** Amazon Polly or Google Cloud
- **Best for Cloning:** ElevenLabs
- **Most Languages:** Azure Speech

---

## Video Generation (Text/Image to Video)

| API | Free Tier | Price/Video | Duration | Quality | I2V | T2V |
|-----|-----------|-------------|----------|---------|-----|-----|
| **Runway Gen-3** | Limited | ~$0.50/sec | 10s (16:9/1:1/9:16) | ★★★★★ | Yes | Yes |
| **Luma Dream Machine** | 30/month | ~$0.15-0.30 | 5–10s (16:9/1:1/9:16) | ★★★★★ | Yes | Yes |
| **Minimax (via fal)** | Pay-as-you-go | ~$0.20-0.50 | 5-6s (16:9/9:16) | ★★★★ | Yes | Yes |
| **Stable Video** | Limited | ~$0.20 | 4s (16:9 or 9:16) | ★★★★ | Yes | No |
| **HeyGen** | Trial | ~$0.50/min | Minutes+ (16:9/1:1/9:16) | ★★★★ | No | Yes (avatar) |
| **Synthesia** | Trial | ~$0.50-1/min | Minutes+ (16:9/1:1) | ★★★★ | No | Yes (avatar) |
| **D-ID** | 5 min | ~$0.15/min | Minutes+ (16:9/9:16/1:1) | ★★★ | Yes | Yes (avatar) |

### Recommendation
- **Best Quality:** Runway Gen-3 or Luma
- **Best Value:** Minimax via fal.ai
- **Avatar Videos:** HeyGen or Synthesia
- **Talking Head from Photo:** D-ID

---

## Stock Assets

| API | Free | Images | Videos | GIFs | Music/SFX | Rate Limit |
|-----|------|--------|--------|------|-----------|------------|
| **Pexels** | ✅ | ✅ | ✅ | ❌ | ❌ | 200/hr |
| **Unsplash** | ✅ | ✅ | ❌ | ❌ | ❌ | 50/hr (demo) |
| **Pixabay** | ✅ | ✅ | ✅ | ❌ | ✅ | 100/min |
| **Giphy** | ✅ | ❌ | ❌ | ✅ | ❌ | 100/hr |
| **Tenor** | ✅ | ❌ | ❌ | ✅ | ❌ | Varies |
| **Freesound** | ✅ | ❌ | ❌ | ❌ | ✅ | Rate limited |

### Recommendation
- **Images:** Pexels + Unsplash (combine for variety)
- **Videos:** Pexels or Pixabay
- **GIFs:** Giphy (largest library)
- **Sound Effects:** Freesound (free) or Epidemic Sound (premium)

---

## Transcription & Captioning

| API | Free Tier | Price/Hour | Accuracy | Real-time | Diarization | Languages |
|-----|-----------|------------|----------|-----------|-------------|-----------|
| **AssemblyAI** | 100 hrs | $0.90 | ★★★★★ | Yes | Yes | 100+ |
| **Deepgram** | $200 credit | $0.26 | ★★★★★ | Yes | Yes | 30+ |
| **OpenAI Whisper** | None | $0.36 | ★★★★ | No | No | 50+ |
| **Rev.ai** | None | $1.20 | ★★★★★ | Yes | Yes | 30+ |
| **fal.ai Whisper** | Pay-as-you-go | ~$0.30 | ★★★★ | No | No | 50+ |

### Recommendation
- **Best Accuracy:** AssemblyAI or Deepgram
- **Best Value:** Deepgram
- **Simplest:** OpenAI Whisper

---

## Background Removal

| API | Free Tier | Price/Image | Quality | Speed | Batch |
|-----|-----------|-------------|---------|-------|-------|
| **Remove.bg** | 1/month (low-res) | $0.90-1.99 | ★★★★★ | 1-2s | Yes |
| **Photoroom** | Limited | ~$0.05 | ★★★★★ | 1-2s | Yes |
| **Clipdrop** | 100/month | ~$0.09 | ★★★★ | 1-2s | Yes |
| **Rembg** | Unlimited | Free (self-host) | ★★★★ | 2-5s | Yes |

### Recommendation
- **Best Quality:** Remove.bg or Photoroom
- **Best Value:** Rembg (free, self-hosted)
- **Multi-purpose:** Clipdrop (includes upscaling, inpainting)

---

## Upscaling

| API | Free Tier | Price/Image | Quality | Max Scale | Speed |
|-----|-----------|-------------|---------|-----------|-------|
| **Stability AI** | 25 credits | ~$0.01 | ★★★★ | 4x | Fast |
| **Replicate Real-ESRGAN** | Limited | ~$0.02 | ★★★★★ | 4x | 5-10s |
| **Clipdrop** | 100/month | ~$0.09 | ★★★★ | 4x | 2-5s |
| **imgix** | 1000 images | Varies | ★★★ | 2x | Real-time |

### Recommendation
- **Best Quality:** Replicate Real-ESRGAN
- **Best Integration:** Clipdrop (part of suite)
- **CDN + Processing:** imgix

---

## Programmatic Video Editing

| API | Free Tier | Pricing | Ease of Use | Templates | Webhooks |
|-----|-----------|---------|-------------|-----------|----------|
| **Shotstack** | 500/mo (watermarked) | $25-99/mo | ★★★★ | Yes | Yes |
| **Creatomate** | 5/month | $59-149/mo | ★★★★★ | Yes | Yes |
| **JSON2Video** | Limited | $0.10/min | ★★★★ | Yes | Yes |
| **Editframe** | Available | Usage-based | ★★★★ | Yes | Yes |
| **FFmpeg** | Unlimited | Free | ★★ | No | N/A |
| **MoviePy** | Unlimited | Free | ★★★ | No | N/A |

### Recommendation
- **Best for Templates:** Creatomate
- **Best Flexibility:** Shotstack
- **Self-hosted:** FFmpeg with MoviePy wrapper

---

## Avatar Platforms

| API | Free Tier | Pricing | Stock Avatars | Custom Avatar | Languages | Lip Sync |
|-----|-----------|---------|---------------|---------------|-----------|----------|
| **HeyGen** | Trial | $29-89/mo | 100+ | Yes | 40+ | Yes |
| **Synthesia** | Trial | $22-67/mo | 150+ | Yes (video) | 130+ | Yes |
| **D-ID** | 5 min | $6-49/mo | Limited | Photo | 30+ | Yes |
| **DiceBear** | Unlimited | Free | 20+ styles | No | N/A | No |
| **Multiavatar** | Limited | $9 | 12B+ | No | N/A | No |

### Recommendation
- **Best Enterprise:** Synthesia
- **Best Value:** HeyGen
- **Talking Head from Photo:** D-ID
- **Static Avatars:** DiceBear (free)

---

## Music & Sound

| API | Free | Catalog Size | Commercial Use | API | Quality |
|-----|------|--------------|----------------|-----|---------|
| **Freesound** | ✅ | 500K+ | CC licenses | ✅ | ★★★ |
| **Epidemic Sound** | ❌ | 40K+ tracks | ✅ (subscription) | Enterprise | ★★★★★ |
| **Artlist** | ❌ | Large | ✅ (subscription) | ❌ | ★★★★★ |
| **Pixabay Audio** | ✅ | Medium | ✅ | ✅ | ★★★ |
| **Mubert** | Limited | AI-generated | ✅ | ✅ | ★★★★ |
| **Beatoven.ai** | 15 min/mo | AI-generated | ✅ | ✅ | ★★★★ |

### Recommendation
- **Free SFX:** Freesound
- **Premium Music:** Epidemic Sound
- **AI-Generated:** Mubert or Beatoven.ai

