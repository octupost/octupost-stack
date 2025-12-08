# Audio Generation APIs

APIs for text-to-speech, voice cloning, music generation, and sound effects.

---

## Text-to-Speech (TTS)

### ElevenLabs

**Website:** https://elevenlabs.io  
**Docs:** https://docs.elevenlabs.io

**Authentication:** API key

**Pricing:**
- Free tier: 10,000 characters/month
- Starter: $5/month (30,000 chars)
- Creator: $22/month (100,000 chars)
- Pro: $99/month (500,000 chars)

**Key Capabilities:**
- Ultra-realistic voices
- Voice cloning (instant and professional)
- 29+ languages
- Emotion and style control
- Streaming audio
- Voice design (create new voices)

**Limitations:**
- Expensive for high volume
- Voice cloning has usage restrictions

**SDKs:** Python, JavaScript, REST

**Licensing:** Commercial use allowed; voice cloning has terms

**Sample Request:**
```python
from elevenlabs import generate, set_api_key

set_api_key("your-api-key")
audio = generate(
    text="Hello, this is a test.",
    voice="Rachel",
    model="eleven_monolingual_v1"
)
```

---

### OpenAI TTS

**Website:** https://openai.com  
**Docs:** https://platform.openai.com/docs/guides/text-to-speech

**Authentication:** API key (Bearer)

**Pricing:**
- TTS: $0.015/1K chars
- TTS-HD: $0.030/1K chars

**Key Capabilities:**
- 6 voices (alloy, echo, fable, onyx, nova, shimmer)
- Multiple output formats (mp3, opus, aac, flac)
- Streaming support
- Natural prosody

**Limitations:**
- No voice cloning
- Limited voice options
- No SSML support

**SDKs:** Python (`openai`), Node.js, REST

**Licensing:** Commercial use allowed

**Sample Request:**
```python
from openai import OpenAI
client = OpenAI()

response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="Hello, this is a test."
)
response.stream_to_file("output.mp3")
```

---

### Google Cloud Text-to-Speech

**Website:** https://cloud.google.com/text-to-speech  
**Docs:** https://cloud.google.com/text-to-speech/docs

**Authentication:** Service account / API key

**Pricing:**
- Standard: $4/1M characters
- WaveNet: $16/1M characters
- Neural2: $16/1M characters
- Free tier: 1M standard chars/month

**Key Capabilities:**
- 220+ voices, 40+ languages
- WaveNet and Neural2 high quality
- SSML support
- Custom Voice (enterprise)
- Audio profiles for devices

**Limitations:**
- Setup complexity (GCP project)
- No instant voice cloning

**SDKs:** Python, Node.js, Go, Java, REST

**Licensing:** Commercial use allowed

---

### Amazon Polly

**Website:** https://aws.amazon.com/polly  
**Docs:** https://docs.aws.amazon.com/polly

**Authentication:** AWS credentials

**Pricing:**
- Standard: $4/1M characters
- Neural: $16/1M characters
- Free tier: 5M chars/month (12 months)

**Key Capabilities:**
- 60+ voices, 30+ languages
- Neural TTS (NTTS) for realism
- SSML support
- Newscaster style
- Streaming and async synthesis

**Limitations:**
- AWS setup required
- Fewer cutting-edge voices than ElevenLabs

**SDKs:** Python (boto3), JavaScript, all AWS SDKs

**Licensing:** Commercial use allowed

---

### Microsoft Azure Speech

**Website:** https://azure.microsoft.com/services/cognitive-services/text-to-speech  
**Docs:** https://docs.microsoft.com/azure/cognitive-services/speech-service

**Authentication:** API key / Azure AD

**Pricing:**
- Neural: $16/1M characters
- Free tier: 500K chars/month

**Key Capabilities:**
- 400+ voices, 140+ languages
- Neural and Custom Neural Voice
- SSML with fine control
- Emotion and style (cheerful, sad, etc.)
- Real-time and batch synthesis

**Limitations:**
- Azure account required
- Custom voice expensive

**SDKs:** Python, JavaScript, C#, Java, REST

**Licensing:** Commercial use allowed

---

### PlayHT

**Website:** https://play.ht  
**Docs:** https://docs.play.ht

**Authentication:** API key

**Pricing:**
- Free tier: 12,500 chars/month
- Creator: $39/month (400K chars)
- Pro: $99/month (1M chars)

**Key Capabilities:**
- Ultra-realistic voices
- Instant voice cloning
- 800+ voices, 140+ languages
- Emotion control
- Podcast-quality output

**Limitations:**
- Expensive for volume
- Some voices behind higher tiers

**SDKs:** Python, JavaScript, REST

**Licensing:** Commercial use allowed

---

### Murf.ai

**Website:** https://murf.ai  
**Docs:** https://murf.ai/api

**Authentication:** API key

**Pricing:**
- Free trial available
- Pro: $29/month
- API access on enterprise plans

**Key Capabilities:**
- Studio-quality voices
- Voice cloning
- 120+ voices, 20+ languages
- Emphasis and pitch control

**Limitations:**
- API on enterprise only
- Limited free tier

**SDKs:** REST

**Licensing:** Commercial use allowed

---

### Typecast

**Website:** https://typecast.ai  
**Docs:** https://typecast.ai/developers

**Authentication:** API key

**Pricing:**
- Subscription-based
- API on business plans

**Key Capabilities:**
- Emotionally expressive voices
- AI avatars with voice
- 300+ voice actors
- Multiple emotions per voice

**Limitations:**
- Limited API access
- Korean company (some voices)

**SDKs:** REST

**Licensing:** Commercial use allowed

---

## Voice Cloning & Dubbing

### ElevenLabs (Voice Cloning)

See above for general info.

**Voice Cloning Specifics:**
- Instant Clone: ~1 min audio sample
- Professional Clone: 30+ min samples (higher quality)
- Voice Design: Create from description

---

### Resemble.ai

**Website:** https://resemble.ai  
**Docs:** https://docs.resemble.ai

**Authentication:** API key

**Pricing:**
- $0.006/second of audio
- Enterprise custom pricing

**Key Capabilities:**
- Real-time voice cloning
- Emotion injection
- Localization (dubbing)
- Speech-to-speech

**Limitations:**
- Requires quality training data

**SDKs:** Python, REST

**Licensing:** Commercial use with terms

---

### Rask AI (Dubbing)

**Website:** https://rask.ai  
**Docs:** Contact for API

**Authentication:** API key

**Pricing:**
- Subscription-based
- Pay-per-minute dubbing

**Key Capabilities:**
- Video dubbing in 130+ languages
- Lip sync
- Voice cloning
- Subtitle generation

**Limitations:**
- API access limited
- Primarily web platform

**SDKs:** REST (limited)

**Licensing:** Commercial use allowed

---

## Music Generation

### Suno AI

**Website:** https://suno.ai  
**Docs:** API in development

**Authentication:** Limited API access

**Pricing:**
- Free tier: 50 credits/day
- Pro: $10/month (2500 credits)

**Key Capabilities:**
- Full song generation from text
- Lyrics and melody
- Multiple genres
- High quality audio

**Limitations:**
- No public API yet
- Web interface only

**SDKs:** Not available

**Licensing:** Check terms for commercial

---

### Udio

**Website:** https://udio.com  
**Docs:** API planned

**Authentication:** Not available

**Pricing:**
- Free tier available
- Subscription plans

**Key Capabilities:**
- High-quality music generation
- Text-to-music
- Style control

**Limitations:**
- No API access
- Web only

**SDKs:** Not available

**Licensing:** Check terms

---

### Mubert

**Website:** https://mubert.com  
**Docs:** https://mubert.com/render/api

**Authentication:** API key

**Pricing:**
- Free tier: Limited
- Pro: From $14/month
- API: Custom pricing

**Key Capabilities:**
- AI-generated royalty-free music
- By mood, genre, duration
- Instant generation
- Loopable tracks

**Limitations:**
- AI-generated (not human artist)
- Some limitations on style

**SDKs:** REST

**Licensing:** Royalty-free for commercial

---

### Beatoven.ai

**Website:** https://beatoven.ai  
**Docs:** https://docs.beatoven.ai

**Authentication:** API key

**Pricing:**
- Free tier: 15 min/month
- Pro: $20/month

**Key Capabilities:**
- Mood-based music generation
- Multiple genres
- Customizable length
- Video sync (cut detection)

**Limitations:**
- Limited instruments
- Queue times

**SDKs:** REST

**Licensing:** Royalty-free

---

## Sound Effects

### Freesound

**Website:** https://freesound.org  
**Docs:** https://freesound.org/docs/api

**Authentication:** OAuth2 / API key

**Pricing:** Free (Creative Commons)

**Key Capabilities:**
- 500,000+ sounds
- Search by tags, duration, format
- Download in multiple formats
- Community contributed

**Limitations:**
- Varying quality
- Attribution required (CC-BY)

**SDKs:** Python (`freesound-python`), REST

**Licensing:** Creative Commons (various)

**Sample Request:**
```python
import freesound

client = freesound.FreesoundClient()
client.set_token("your-api-key")

results = client.text_search(query="thunder", fields="id,name,previews")
for sound in results:
    print(sound.name)
```

---

### Epidemic Sound

**Website:** https://epidemicsound.com  
**Docs:** Enterprise API

**Authentication:** API key (enterprise)

**Pricing:**
- Personal: $9/month
- Commercial: $49/month
- Enterprise API: Custom

**Key Capabilities:**
- 40,000+ tracks
- 90,000+ sound effects
- Cleared for all platforms
- Search by mood, genre

**Limitations:**
- API for enterprise only
- Subscription required

**SDKs:** REST (enterprise)

**Licensing:** Royalty-free with subscription

---

### Artlist

**Website:** https://artlist.io  
**Docs:** No public API

**Authentication:** N/A

**Pricing:**
- Music: $9.99/month
- Music + SFX: $16.99/month

**Key Capabilities:**
- High-quality curated music
- Sound effects library
- Unlimited downloads

**Limitations:**
- No API
- Manual download only

**SDKs:** None

**Licensing:** Universal license (all platforms)

---

### Pixabay Audio

**Website:** https://pixabay.com/music  
**Docs:** https://pixabay.com/api/docs (images API, audio included)

**Authentication:** API key

**Pricing:** Free

**Key Capabilities:**
- Royalty-free music and SFX
- No attribution required
- Multiple genres

**Limitations:**
- Smaller catalog
- Audio API less featured

**SDKs:** REST

**Licensing:** Pixabay License (free commercial)

---

## fal.ai Audio Models

fal.ai provides a comprehensive suite of audio models accessible via a unified API. All models support JavaScript, Python, REST, and cURL.

**Website:** https://fal.ai  
**Docs:** https://docs.fal.ai/model-apis

**Authentication:** API key

**General Pricing:** Pay-per-use (per second of audio generated/processed)

---

### fal.ai Maya TTS

**Endpoint:** `fal-ai/maya`

**Key Capabilities:**
- State-of-the-art expressive voice generation
- Real human emotion capture
- Precise voice design control
- High-quality audio output

**Sample Request:**
```typescript
import { fal } from "@fal-ai/client";

const result = await fal.subscribe("fal-ai/maya", {
  input: {
    text: "Hello, this is a test.",
    voice: "default"
  }
});
```

---

### fal.ai MiniMax Speech 2.6 HD

**Endpoint:** `fal-ai/minimax/speech-2.6-hd`

**Key Capabilities:**
- High-quality text-to-speech synthesis
- Multiple voice options
- Natural prosody
- Advanced AI techniques

**Sample Request:**
```typescript
import { fal } from "@fal-ai/client";

const result = await fal.subscribe("fal-ai/minimax/speech-2.6-hd", {
  input: { text: "Hello world" }
});
```

---

### fal.ai MiniMax Speech 2.6 Turbo

**Endpoint:** `fal-ai/minimax/speech-2.6-turbo`

**Key Capabilities:**
- Fast text-to-speech generation
- Optimized for speed
- Multiple voice options
- Good quality-speed balance

---

### fal.ai PlayAI TTS Dialog

**Endpoint:** `fal-ai/playai/tts/dialog`

**Key Capabilities:**
- Multi-speaker dialogue generation
- Natural-sounding conversations
- Expressive outputs
- Perfect for storytelling, games, animation

---

### fal.ai Whisper (Speech-to-Text)

**Endpoint:** `fal-ai/whisper`

**Key Capabilities:**
- Speech transcription
- Translation support
- Multiple language support
- High accuracy

**Sample Request:**
```typescript
import { fal } from "@fal-ai/client";

const result = await fal.subscribe("fal-ai/whisper", {
  input: {
    audio_url: "https://example.com/audio.mp3"
  }
});
```

---

### fal.ai Wizper (Optimized Speech-to-Text)

**Endpoint:** `fal-ai/wizper`

**Key Capabilities:**
- Whisper v3 Large optimized
- Same WER (Word Error Rate)
- 2x performance improvement
- Multi-language transcription

---

### fal.ai MiniMax Music 2.0

**Endpoint:** `fal-ai/minimax-music/v2`

**Key Capabilities:**
- Text-to-music generation
- Diverse musical genres
- High-quality compositions
- AI-powered arrangement

**Sample Request:**
```typescript
import { fal } from "@fal-ai/client";

const result = await fal.subscribe("fal-ai/minimax-music/v2", {
  input: { prompt: "upbeat electronic dance music" }
});
```

---

### fal.ai Beatoven Music Generation

**Endpoint:** `fal-ai/beatoven/music-generation`

**Key Capabilities:**
- Royalty-free instrumental music
- Multiple genres (electronic, hip hop, cinematic, classical)
- Perfect for games, films, social content

---

### fal.ai Beatoven Sound Effects

**Endpoint:** `fal-ai/beatoven/sound-effect-generation`

**Key Capabilities:**
- Professional-grade sound effects
- Diverse categories (animals, vehicles, nature, sci-fi)
- Perfect for films, games, digital content

**Sample Request:**
```typescript
import { fal } from "@fal-ai/client";

const result = await fal.subscribe("fal-ai/beatoven/sound-effect-generation", {
  input: { prompt: "thunderstorm with heavy rain" }
});
```

---

### fal.ai Mirelo SFX (Video-to-Audio)

**Endpoint:** `fal-ai/mirelo-ai/sfx-v1/video-to-audio`

**Key Capabilities:**
- Generate synced sounds for video
- Automatic sound effect creation
- MMAudio-style processing
- Returns audio track only

---

### fal.ai Mirelo SFX (Video-to-Video)

**Endpoint:** `fal-ai/mirelo-ai/sfx-v1/video-to-video`

**Key Capabilities:**
- Generate synced sounds for video
- Returns video with new soundtrack
- Automatic audio replacement

---

### fal.ai Dia TTS Voice Clone

**Endpoint:** `fal-ai/dia-tts/voice-clone`

**Key Capabilities:**
- Voice cloning from sample audio
- Dialog generation
- High-quality text-to-speech
- Sample-based synthesis

**Sample Request:**
```typescript
import { fal } from "@fal-ai/client";

const result = await fal.subscribe("fal-ai/dia-tts/voice-clone", {
  input: {
    text: "Hello world",
    voice_sample_url: "https://example.com/voice.mp3"
  }
});
```

---

### fal.ai Sync Lipsync v2

**Endpoint:** `fal-ai/sync-lipsync/v2`

**Key Capabilities:**
- Realistic lip sync animations
- Audio-to-video synchronization
- High-quality output
- Advanced algorithms

**Sample Request:**
```typescript
import { fal } from "@fal-ai/client";

const result = await fal.subscribe("fal-ai/sync-lipsync/v2", {
  input: {
    video_url: "https://example.com/video.mp4",
    audio_url: "https://example.com/audio.mp3"
  }
});
```

---

### fal.ai PixVerse Lipsync

**Endpoint:** `fal-ai/pixverse/lipsync`

**Key Capabilities:**
- Lip sync animations
- Audio-video synchronization
- PixVerse integration

---

### fal.ai ByteDance OmniHuman v1.5

**Endpoint:** `fal-ai/bytedance/omnihuman/v1.5`

**Key Capabilities:**
- Audio-to-video generation
- Image + audio to animated video
- Human figure animation
- Vivid, high-quality output

**Sample Request:**
```typescript
import { fal } from "@fal-ai/client";

const result = await fal.subscribe("fal-ai/bytedance/omnihuman/v1.5", {
  input: {
    image_url: "https://example.com/person.jpg",
    audio_url: "https://example.com/speech.mp3"
  }
});
```

