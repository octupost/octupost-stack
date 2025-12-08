# cURL Examples

Quick copy-paste cURL commands for testing APIs.

## Image Generation

### DALL-E 3
```bash
curl https://api.openai.com/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "dall-e-3",
    "prompt": "A futuristic city at sunset, cyberpunk style",
    "n": 1,
    "size": "1024x1024"
  }'
```

### fal.ai Flux
```bash
curl -X POST "https://queue.fal.run/fal-ai/flux/dev" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A cute robot learning to paint"
  }'
```

### Stability AI SDXL
```bash
curl -X POST "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image" \
  -H "Authorization: Bearer $STABILITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text_prompts": [{"text": "A mountain landscape at dawn"}],
    "cfg_scale": 7,
    "height": 1024,
    "width": 1024,
    "steps": 30
  }'
```

---

## Text-to-Speech

### OpenAI TTS
```bash
curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "input": "Hello, this is a test of the text to speech API.",
    "voice": "alloy"
  }' \
  --output speech.mp3
```

### ElevenLabs
```bash
curl -X POST "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is Rachel from ElevenLabs.",
    "model_id": "eleven_monolingual_v1"
  }' \
  --output speech.mp3
```

### Google Cloud TTS
```bash
curl -X POST "https://texttospeech.googleapis.com/v1/text:synthesize" \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {"text": "Hello World"},
    "voice": {"languageCode": "en-US", "name": "en-US-Neural2-F"},
    "audioConfig": {"audioEncoding": "MP3"}
  }' | jq -r '.audioContent' | base64 -d > speech.mp3
```

---

## Stock Assets

### Pexels Images
```bash
curl "https://api.pexels.com/v1/search?query=nature&per_page=5" \
  -H "Authorization: $PEXELS_API_KEY"
```

### Pexels Videos
```bash
curl "https://api.pexels.com/videos/search?query=ocean&per_page=3" \
  -H "Authorization: $PEXELS_API_KEY"
```

### Unsplash
```bash
curl "https://api.unsplash.com/search/photos?query=mountains&per_page=5" \
  -H "Authorization: Client-ID $UNSPLASH_ACCESS_KEY"
```

### Giphy
```bash
curl "https://api.giphy.com/v1/gifs/search?api_key=$GIPHY_API_KEY&q=excited&limit=5"
```

### Tenor
```bash
curl "https://tenor.googleapis.com/v2/search?q=happy&key=$TENOR_API_KEY&limit=5"
```

### Pixabay
```bash
curl "https://pixabay.com/api/?key=$PIXABAY_API_KEY&q=yellow+flowers&image_type=photo"
```

---

## Video Generation

### fal.ai Minimax Image-to-Video
```bash
curl -X POST "https://queue.fal.run/fal-ai/minimax-video/image-to-video" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A woman walking through a neon-lit Tokyo street",
    "image_url": "https://example.com/image.jpg"
  }'
```

### D-ID Talking Head
```bash
curl -X POST "https://api.d-id.com/talks" \
  -H "Authorization: Basic $DID_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "source_url": "https://example.com/portrait.jpg",
    "script": {
      "type": "text",
      "input": "Hello, I am an AI avatar created from a photo.",
      "provider": {
        "type": "microsoft",
        "voice_id": "en-US-JennyNeural"
      }
    }
  }'
```

---

## Transcription

### OpenAI Whisper
```bash
curl https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F file="@audio.mp3" \
  -F model="whisper-1"
```

### AssemblyAI
```bash
# Step 1: Upload file
curl -X POST "https://api.assemblyai.com/v2/upload" \
  -H "authorization: $ASSEMBLYAI_API_KEY" \
  -T audio.mp3

# Step 2: Start transcription (use upload_url from step 1)
curl -X POST "https://api.assemblyai.com/v2/transcript" \
  -H "authorization: $ASSEMBLYAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "audio_url": "https://cdn.assemblyai.com/upload/..."
  }'

# Step 3: Get result (use id from step 2)
curl "https://api.assemblyai.com/v2/transcript/TRANSCRIPT_ID" \
  -H "authorization: $ASSEMBLYAI_API_KEY"
```

### fal.ai Whisper
```bash
curl -X POST "https://queue.fal.run/fal-ai/whisper" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "audio_url": "https://example.com/audio.mp3"
  }'
```

---

## Background Removal

### Remove.bg
```bash
curl -X POST "https://api.remove.bg/v1.0/removebg" \
  -H "X-Api-Key: $REMOVEBG_API_KEY" \
  -F "image_file=@input.jpg" \
  -F "size=auto" \
  -o output.png
```

### Clipdrop
```bash
curl -X POST "https://clipdrop-api.co/remove-background/v1" \
  -H "x-api-key: $CLIPDROP_API_KEY" \
  -F "image_file=@input.jpg" \
  -o output.png
```

---

## Video Editing

### Shotstack (Simple Merge)
```bash
curl -X POST "https://api.shotstack.io/stage/render" \
  -H "x-api-key: $SHOTSTACK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "timeline": {
      "tracks": [
        {
          "clips": [
            {
              "asset": {
                "type": "video",
                "src": "https://example.com/clip1.mp4"
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
  }'
```

---

## Avatars

### DiceBear
```bash
curl "https://api.dicebear.com/7.x/avataaars/svg?seed=John" -o avatar.svg
```

### Multiavatar
```bash
curl "https://api.multiavatar.com/John.svg" -o avatar.svg
```

---

## Music Generation

### Mubert
```bash
curl -X POST "https://api-b2b.mubert.com/v2/RecordTrackTTM" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "RecordTrackTTM",
    "params": {
      "pat": "$MUBERT_PAT",
      "duration": 30,
      "tags": ["chill", "ambient"],
      "mode": "track"
    }
  }'
```

