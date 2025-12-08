# Utility APIs

APIs for transcoding, upscaling, background removal, captioning, and other processing tasks.

---

## Background Removal

### Remove.bg

**Website:** https://remove.bg  
**Docs:** https://www.remove.bg/api

**Authentication:** API key

**Pricing:**
- Free tier: 1 free preview/month (low-res)
- Pay-as-you-go: $0.90-1.99/image
- Subscription: From $9/month (40 credits)

**Key Capabilities:**
- Automatic background removal
- High-resolution output
- Transparent PNG
- Add new backgrounds
- Batch processing

**Limitations:**
- Expensive for volume
- Preview quality limited on free

**SDKs:** Python, JavaScript, PHP, Ruby, .NET, REST

**Licensing:** Commercial use allowed

**Sample Request:**
```python
import requests

response = requests.post(
    'https://api.remove.bg/v1.0/removebg',
    files={'image_file': open('input.jpg', 'rb')},
    data={'size': 'auto'},
    headers={'X-Api-Key': 'YOUR_API_KEY'},
)
with open('output.png', 'wb') as f:
    f.write(response.content)
```

---

### Photoroom API

**Website:** https://photoroom.com  
**Docs:** https://www.photoroom.com/api

**Authentication:** API key

**Pricing:**
- From $0.05/image (volume)
- Enterprise: Custom

**Key Capabilities:**
- Background removal
- Background replacement
- Object detection
- Batch processing
- E-commerce optimization

**Limitations:**
- Enterprise focus

**SDKs:** REST

**Licensing:** Commercial use allowed

---

### Clipdrop (Stability AI)

**Website:** https://clipdrop.co  
**Docs:** https://clipdrop.co/apis

**Authentication:** API key

**Pricing:**
- Free tier: 100 API calls/month
- Pro: From $9/month

**Key Capabilities:**
- Background removal
- Object removal (inpainting)
- Upscaling (4x)
- Relighting
- Text removal
- Sketch to image

**SDKs:** REST

**Licensing:** Commercial use allowed

**Sample Request:**
```bash
curl -X POST "https://clipdrop-api.co/remove-background/v1" \
  -H "x-api-key: YOUR_API_KEY" \
  -F "image_file=@input.jpg" \
  -o output.png
```

---

### Rembg (Open Source)

**Website:** https://github.com/danielgatis/rembg  
**Docs:** https://github.com/danielgatis/rembg#usage

**Authentication:** None (self-hosted)

**Pricing:** Free

**Key Capabilities:**
- Local background removal
- Multiple AI models
- CLI and Python library
- Docker support

**Limitations:**
- Self-hosted only
- Quality varies by model

**SDKs:** Python

**Licensing:** MIT

**Sample:**
```python
from rembg import remove
from PIL import Image

input = Image.open('input.jpg')
output = remove(input)
output.save('output.png')
```

---

## Image Upscaling

### Stability AI Upscaling

**Website:** https://platform.stability.ai  
**Docs:** https://platform.stability.ai/docs/api-reference#tag/Image-to-Image

**Authentication:** API key

**Pricing:**
- ~$0.01/upscale

**Key Capabilities:**
- 4x upscaling
- AI enhancement
- Conservative and creative modes

**SDKs:** Python, REST

**Licensing:** Commercial use allowed

---

### Replicate (Real-ESRGAN, etc.)

**Website:** https://replicate.com  
**Docs:** https://replicate.com/xinntao/realesrgan

**Authentication:** API key

**Pricing:**
- Pay per second (~$0.00115/sec)
- Real-ESRGAN: ~$0.02/image

**Key Capabilities:**
- Real-ESRGAN 4x upscaling
- Face enhancement (GFPGAN)
- Multiple models available

**SDKs:** Python, JavaScript, REST

**Licensing:** Model-dependent

**Sample:**
```python
import replicate

output = replicate.run(
    "xinntao/realesrgan:1b976a4d456ed9e4d1a846597b7614e79eadad3032e9124fa63c8e751fe95a",
    input={"image": open("input.jpg", "rb")}
)
```

---

### Topaz Labs (Gigapixel AI)

**Website:** https://topazlabs.com  
**Docs:** No public API

**Pricing:**
- $99 one-time purchase

**Key Capabilities:**
- Best-in-class upscaling
- Face recovery
- Noise reduction

**Limitations:**
- No API (desktop only)
- Not automatable

**SDKs:** None

**Licensing:** Commercial use with license

---

### imgix

**Website:** https://imgix.com  
**Docs:** https://docs.imgix.com

**Authentication:** API key + domain

**Pricing:**
- Free tier: 1000 images
- Starter: $10/month

**Key Capabilities:**
- On-the-fly image processing
- Resize, crop, format conversion
- Filters and effects
- CDN delivery

**SDKs:** JavaScript, Python, REST

**Licensing:** Commercial use allowed

---

## Transcription & Captioning

### AssemblyAI

**Website:** https://assemblyai.com  
**Docs:** https://www.assemblyai.com/docs

**Authentication:** API key

**Pricing:**
- $0.00025/second ($0.90/hour)
- Free tier: 100 hours

**Key Capabilities:**
- Speech-to-text
- Speaker diarization
- Sentiment analysis
- Topic detection
- PII redaction
- Real-time transcription

**SDKs:** Python, JavaScript, REST

**Licensing:** Commercial use allowed

**Sample Request:**
```python
import assemblyai as aai

aai.settings.api_key = "YOUR_API_KEY"
transcriber = aai.Transcriber()

transcript = transcriber.transcribe("https://example.com/audio.mp3")
print(transcript.text)
```

---

### Deepgram

**Website:** https://deepgram.com  
**Docs:** https://developers.deepgram.com

**Authentication:** API key

**Pricing:**
- Nova-2: $0.0043/minute
- Free tier: $200 credit

**Key Capabilities:**
- Fast transcription (real-time)
- Speaker diarization
- Smart formatting
- Topic detection
- Custom vocabulary

**SDKs:** Python, JavaScript, Go, .NET, REST

**Licensing:** Commercial use allowed

---

### OpenAI Whisper API

**Website:** https://openai.com  
**Docs:** https://platform.openai.com/docs/guides/speech-to-text

**Authentication:** API key

**Pricing:**
- $0.006/minute

**Key Capabilities:**
- Multi-language transcription
- Translation to English
- Timestamps

**SDKs:** Python, JavaScript, REST

**Licensing:** Commercial use allowed

**Sample:**
```python
from openai import OpenAI
client = OpenAI()

audio_file = open("speech.mp3", "rb")
transcript = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file
)
```

---

### Rev.ai

**Website:** https://rev.ai  
**Docs:** https://docs.rev.ai

**Authentication:** API key

**Pricing:**
- Async: $0.02/minute
- Streaming: $0.035/minute

**Key Capabilities:**
- High accuracy
- Speaker diarization
- Custom vocabulary
- Human review option

**SDKs:** Python, Node.js, REST

**Licensing:** Commercial use allowed

---

### fal.ai Whisper

**Website:** https://fal.ai  
**Docs:** https://docs.fal.ai/model-apis/guides/convert-speech-to-text

**Authentication:** API key

**Pricing:**
- Pay per second

**Key Capabilities:**
- Whisper model hosting
- Fast inference
- Multiple languages

**SDKs:** JavaScript, Python, REST

**Licensing:** Commercial use allowed

**Sample:**
```typescript
import { fal } from "@fal-ai/client";

const result = await fal.subscribe("fal-ai/whisper", {
  input: {
    audio_url: "https://example.com/audio.mp3"
  },
});
```

---

## Video Transcoding

### Coconut.co

**Website:** https://coconut.co  
**Docs:** https://docs.coconut.co

**Authentication:** API key

**Pricing:**
- From $0.015/minute

**Key Capabilities:**
- Video encoding (all formats)
- HLS/DASH streaming
- Thumbnails
- Watermarks
- S3/GCS integration

**SDKs:** Ruby, Node.js, Python, REST

**Licensing:** Commercial use allowed

---

### Transloadit

**Website:** https://transloadit.com  
**Docs:** https://transloadit.com/docs

**Authentication:** API key

**Pricing:**
- Free tier: 1GB/month
- Startup: $49/month

**Key Capabilities:**
- Video/audio encoding
- Image processing
- File importing
- Assembly-based workflows

**SDKs:** JavaScript, Python, Ruby, Go, REST

**Licensing:** Commercial use allowed

---

### Mux

**Website:** https://mux.com  
**Docs:** https://docs.mux.com

**Authentication:** API key

**Pricing:**
- Encoding: $0.015/minute
- Delivery: $0.00057/minute streamed
- Free tier: 10 hours

**Key Capabilities:**
- Video hosting and streaming
- Adaptive bitrate (HLS)
- Thumbnails
- Subtitles
- Analytics

**SDKs:** Node.js, Ruby, Python, Go, REST

**Licensing:** Commercial use allowed

---

### Cloudinary

**Website:** https://cloudinary.com  
**Docs:** https://cloudinary.com/documentation

**Authentication:** API key

**Pricing:**
- Free tier: 25 credits
- Plus: $89/month

**Key Capabilities:**
- Image/video storage
- On-the-fly transformations
- Video transcoding
- CDN delivery
- AI features

**SDKs:** All major languages

**Licensing:** Commercial use allowed

---

## Lip Sync

### Wav2Lip

**Website:** https://github.com/Rudrabha/Wav2Lip  
**Docs:** https://github.com/Rudrabha/Wav2Lip#readme

**Authentication:** None (self-hosted)

**Pricing:** Free

**Key Capabilities:**
- Lip sync to any audio
- Works with any face
- Open source

**Limitations:**
- Self-hosted only
- Requires GPU
- Quality varies

**SDKs:** Python

**Licensing:** Research license (check for commercial)

---

### SadTalker

**Website:** https://github.com/OpenTalker/SadTalker  
**Docs:** https://github.com/OpenTalker/SadTalker#readme

**Authentication:** None (self-hosted)

**Pricing:** Free

**Key Capabilities:**
- Single image to talking head
- Expression control
- Head motion

**Limitations:**
- Self-hosted
- GPU required

**SDKs:** Python

**Licensing:** Research/non-commercial

---

### D-ID Lip Sync

**Website:** https://d-id.com  
**Docs:** https://docs.d-id.com

**Authentication:** API key

**Pricing:**
- See D-ID pricing in visuals.md

**Key Capabilities:**
- Photo to talking head
- Voice or text input
- Real-time streaming

**SDKs:** REST, JavaScript

**Licensing:** Commercial use allowed

---

### Sync Labs

**Website:** https://synclabs.so  
**Docs:** https://docs.synclabs.so

**Authentication:** API key

**Pricing:**
- Pay per second
- Enterprise plans available

**Key Capabilities:**
- Video lip sync
- High quality
- Any language

**SDKs:** REST

**Licensing:** Commercial use allowed

---

## Object Detection & Segmentation

### Roboflow

**Website:** https://roboflow.com  
**Docs:** https://docs.roboflow.com

**Authentication:** API key

**Pricing:**
- Free tier: 1000 inferences/month
- Starter: $249/month

**Key Capabilities:**
- Object detection
- Image segmentation
- Model training
- Dataset management

**SDKs:** Python, JavaScript, REST

**Licensing:** Commercial use allowed

---

### Segment Anything (via Replicate)

**Website:** https://replicate.com/meta/sam-2  
**Docs:** https://replicate.com/meta/sam-2/api

**Authentication:** Replicate API key

**Pricing:**
- Pay per second

**Key Capabilities:**
- Universal image segmentation
- Point/box prompts
- Zero-shot segmentation

**SDKs:** Python, REST

**Licensing:** Apache 2.0

---

## Text Detection & OCR

### Google Cloud Vision

**Website:** https://cloud.google.com/vision  
**Docs:** https://cloud.google.com/vision/docs

**Authentication:** Service account

**Pricing:**
- 1000 images/month free
- $1.50/1000 images

**Key Capabilities:**
- OCR (text detection)
- Object detection
- Face detection
- Label detection
- Logo detection

**SDKs:** Python, Node.js, Go, Java, REST

**Licensing:** Commercial use allowed

---

### Tesseract OCR

**Website:** https://github.com/tesseract-ocr/tesseract  
**Docs:** https://tesseract-ocr.github.io

**Authentication:** None (self-hosted)

**Pricing:** Free

**Key Capabilities:**
- Open source OCR
- 100+ languages
- CLI and libraries

**Limitations:**
- Accuracy varies
- Self-hosted

**SDKs:** Python (`pytesseract`), C++

**Licensing:** Apache 2.0

