# Workflow Playbooks

Recommended API stacks for common video creation workflows.

---

## Playbook 1: Social Media Video from Text

**Goal:** Generate a short-form video (15-60s) from a text script with voiceover and background music.

### Recommended Stack

| Component | Primary Choice | Alternative |
|-----------|----------------|-------------|
| Script to TTS | ElevenLabs | OpenAI TTS |
| Background Music | Mubert API | Pixabay Audio |
| Stock Footage | Pexels API | Pixabay API |
| Video Composition | Shotstack | Creatomate |
| Captions | AssemblyAI | Deepgram |

### Workflow

```
1. Generate voiceover audio
   └─> ElevenLabs TTS (high quality) or OpenAI TTS (budget)

2. Get voiceover duration and generate captions
   └─> AssemblyAI transcribe (with word-level timestamps)

3. Generate/fetch background music
   └─> Mubert API (match duration, mood) or Pixabay (search by mood)

4. Fetch stock footage clips
   └─> Pexels API (search keywords from script)

5. Compose final video
   └─> Shotstack JSON timeline:
       - Video track: stock clips
       - Audio track 1: voiceover
       - Audio track 2: background music (ducked)
       - Text track: captions with timestamps

6. Export and deliver
   └─> Shotstack render → webhook → download
```

### Cost Estimate (60s video)
- TTS (1000 chars): ~$0.15-0.30
- Music: ~$0.05-0.10
- Stock footage: Free
- Captioning: ~$0.02
- Video composition: ~$0.05-0.10
- **Total: ~$0.30-0.60**

---

## Playbook 2: AI Avatar Explainer Video

**Goal:** Create a professional explainer video with an AI spokesperson avatar.

### Recommended Stack

| Component | Primary Choice | Alternative |
|-----------|----------------|-------------|
| Avatar Video | HeyGen API | Synthesia |
| Script Writing | GPT-4 | Claude |
| Background Graphics | Pexels / Custom | Unsplash |
| Captions | Built-in | AssemblyAI |
| Music | Epidemic Sound | Mubert |

### Workflow

```
1. Generate/refine script
   └─> OpenAI GPT-4 or Claude

2. Create avatar video
   └─> HeyGen API:
       - Select avatar (or upload custom)
       - Provide script text
       - Select language/voice
       - Add background template

3. Fetch background music
   └─> Epidemic Sound (manual) or Mubert API

4. Post-process (optional)
   └─> Shotstack: add logo, captions, music track

5. Export
   └─> Download from HeyGen or Shotstack
```

### Cost Estimate (2 min video)
- Avatar video: ~$1-2/minute = $2-4
- Background music: ~$0.20
- Post-processing: ~$0.10
- **Total: ~$2.50-4.50**

---

## Playbook 3: Product Showcase from Images

**Goal:** Create a dynamic video showcasing product images with motion effects.

### Recommended Stack

| Component | Primary Choice | Alternative |
|-----------|----------------|-------------|
| Image to Video | fal.ai Minimax I2V | Runway ML |
| Background Removal | Remove.bg | Rembg (self-host) |
| Image Enhancement | Stability AI Upscale | Replicate Real-ESRGAN |
| Video Composition | Shotstack | Creatomate |
| Music | Artlist | Pixabay Audio |

### Workflow

```
1. Prepare product images
   └─> Remove.bg: remove backgrounds
   └─> Stability AI: upscale to 4K

2. Generate motion clips
   └─> fal.ai Minimax I2V:
       - "Product rotating slowly with soft lighting"
       - "Zoom in on product details"

3. Fetch lifestyle B-roll
   └─> Pexels API (search product category)

4. Compose final video
   └─> Shotstack:
       - Ken Burns on static images
       - AI-generated motion clips
       - Transitions between shots
       - Add music and text overlays

5. Export in multiple formats
   └─> 16:9 for YouTube, 9:16 for TikTok/Reels
```

### Cost Estimate (5 product images, 30s video)
- Background removal (5x): ~$0.25-1.00
- Upscaling (5x): ~$0.05
- I2V generation (3 clips): ~$0.60-1.50
- Stock footage: Free
- Composition: ~$0.10
- **Total: ~$1.00-3.00**

---

## Playbook 4: Podcast/Interview Video with Waveforms

**Goal:** Create a video from audio podcast with visual waveforms and captions.

### Recommended Stack

| Component | Primary Choice | Alternative |
|-----------|----------------|-------------|
| Audio Source | User upload | - |
| Transcription | Deepgram | AssemblyAI |
| Speaker Diarization | Deepgram | AssemblyAI |
| Waveform Visualization | Custom / Shotstack | Audiogram.io |
| Video Composition | Shotstack | Creatomate |
| Thumbnail | Pexels + fal.ai | DALL-E 3 |

### Workflow

```
1. Upload and process audio
   └─> Deepgram: transcribe with speaker diarization

2. Generate speaker thumbnails/avatars
   └─> Option A: Use guest photos
   └─> Option B: DiceBear avatars from names

3. Create waveform video
   └─> Shotstack audio waveform asset
       - Synced to audio timeline

4. Add captions with speaker labels
   └─> Parse Deepgram output
   └─> Color-code by speaker

5. Compose final video
   └─> Layout: speaker photos, waveform, captions
   └─> Add intro/outro slides

6. Generate clips for social
   └─> Extract best moments (15-60s clips)
```

### Cost Estimate (30 min podcast)
- Transcription: ~$0.15
- Composition: ~$0.50
- Thumbnail: ~$0.02
- **Total: ~$0.70**

---

## Playbook 5: Lip-Synced Avatar from Photo

**Goal:** Make a photo talk with custom audio.

### Recommended Stack

| Component | Primary Choice | Alternative |
|-----------|----------------|-------------|
| Photo Source | User upload | Stock (Pexels) |
| Audio Generation | ElevenLabs | OpenAI TTS |
| Lip Sync | D-ID | Sync Labs |
| Post-Processing | FFmpeg | Shotstack |

### Workflow

```
1. Prepare the portrait photo
   └─> Ensure face is visible, good lighting
   └─> Remove.bg if needed for clean background

2. Generate voice audio
   └─> ElevenLabs: select voice, generate from text
   └─> Or: use uploaded audio

3. Create talking head video
   └─> D-ID API:
       - Input: photo + audio URL
       - Output: lip-synced video

4. Post-process
   └─> Add background, lower third, logo
   └─> Merge into larger video if needed
```

### Cost Estimate (30s clip)
- TTS (500 chars): ~$0.10
- D-ID (30s): ~$0.10-0.15
- **Total: ~$0.20-0.25**

---

## Playbook 6: Text-to-Video with AI Generation

**Goal:** Generate a cinematic video purely from a text prompt.

### Recommended Stack

| Component | Primary Choice | Alternative |
|-----------|----------------|-------------|
| Video Generation | Runway Gen-3 | Luma Dream Machine |
| Extend/Loop | Same platform | Manual editing |
| Audio | OpenAI TTS / Mubert | ElevenLabs |
| Post-Processing | Shotstack | FFmpeg |

### Workflow

```
1. Write detailed video prompt
   └─> "A drone shot flying over a misty forest at sunrise..."

2. Generate initial clip
   └─> Runway Gen-3: 10s clip
   └─> Cost: ~$5

3. Extend if needed
   └─> Use last frame as input for next clip
   └─> Repeat to desired length

4. Add audio
   └─> Option A: Voiceover (ElevenLabs)
   └─> Option B: Background music (Mubert)
   └─> Option C: Both

5. Final composition
   └─> Shotstack: merge clips, add music, titles
```

### Cost Estimate (30s video)
- Video generation (30s): ~$15
- Audio: ~$0.20
- Composition: ~$0.10
- **Total: ~$15-20** (expensive, use for hero content)

---

## Playbook 7: Batch Social Content Generation

**Goal:** Generate multiple video variations for A/B testing or multi-platform distribution.

### Recommended Stack

| Component | Primary Choice | Alternative |
|-----------|----------------|-------------|
| Template System | Creatomate | Shotstack |
| Data Source | JSON / Spreadsheet | - |
| Assets | Pexels + DiceBear | Custom |
| TTS | OpenAI (bulk) | ElevenLabs |

### Workflow

```
1. Create master template
   └─> Creatomate: design with dynamic placeholders
       - {{headline}}, {{product_image}}, {{cta}}

2. Prepare data source
   └─> JSON array of variations:
       [
         { headline: "Sale Today!", cta: "Shop Now" },
         { headline: "50% Off!", cta: "Buy Now" },
         ...
       ]

3. Generate TTS for each variation
   └─> OpenAI TTS: batch process all CTA texts

4. Batch render
   └─> Creatomate: POST each data row
   └─> Receive webhook per completion

5. Distribute
   └─> Auto-upload to CDN/platform
```

### Cost Estimate (10 variations, 15s each)
- Renders: ~$0.50-1.00
- TTS: ~$0.05
- **Total: ~$0.60-1.10 for 10 videos**

---

## Playbook 8: User-Generated Content Enhancement

**Goal:** Take user-uploaded video and enhance with captions, music, and effects.

### Recommended Stack

| Component | Primary Choice | Alternative |
|-----------|----------------|-------------|
| Upload Handling | Mux | Cloudinary |
| Transcription | AssemblyAI | Deepgram |
| Enhancement | Shotstack | Creatomate |
| Music Matching | Mubert | Pixabay |

### Workflow

```
1. Accept user upload
   └─> Mux: ingest and process
   └─> Get duration, resolution, thumbnail

2. Transcribe audio
   └─> AssemblyAI: extract speech
   └─> Generate word-level timestamps

3. Auto-select music
   └─> Mubert: generate based on video duration
   └─> Match mood (detect from transcript sentiment)

4. Apply enhancements
   └─> Shotstack:
       - Overlay captions
       - Add background music (ducked)
       - Apply color filter
       - Add logo watermark

5. Deliver processed video
   └─> Webhook → user notification
```

### Cost Estimate (60s user video)
- Processing: ~$0.05
- Transcription: ~$0.02
- Music: ~$0.05
- Enhancement: ~$0.10
- **Total: ~$0.25**

---

## Quick Reference: API Selection by Use Case

| Use Case | Best Free Option | Best Paid Option |
|----------|------------------|------------------|
| Generate image | fal.ai Fast-SDXL | DALL-E 3 |
| Generate video | N/A | Runway Gen-3 |
| Image to video | Stable Video (limited) | Minimax via fal.ai |
| Voiceover | OpenAI TTS | ElevenLabs |
| Transcription | Whisper (self-host) | AssemblyAI |
| Background removal | Rembg | Remove.bg |
| Stock images | Pexels/Unsplash | Shutterstock |
| Stock videos | Pexels | Shutterstock |
| GIFs | Giphy | Giphy |
| Stock music | Pixabay Audio | Epidemic Sound |
| SFX | Freesound | Epidemic Sound |
| Video editing | FFmpeg | Shotstack |
| Avatars (static) | DiceBear | - |
| Avatars (video) | D-ID trial | HeyGen |
| Lip sync | Self-host Wav2Lip | D-ID |

