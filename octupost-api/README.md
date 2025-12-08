# Octupost API - AI Generation Backend

FastAPI backend service for AI-powered media generation using Fal AI and Inngest for job processing.

## Features

- **Text-to-Image (TTI)**: Generate images from text prompts
- **Text-to-Video (TTV)**: Generate videos from text prompts
- **Image-to-Video (ITV)**: Generate videos from images
- **Text-to-Speech (TTS)**: Generate speech from text

## Supported Models

| Type | Model 1 (Fast) | Model 2 (Quality) |
|------|----------------|-------------------|
| TTI | `fal-ai/flux/schnell` | `fal-ai/fast-sdxl` |
| TTV | `fal-ai/wan/v2.2-a14b/text-to-video` | `fal-ai/minimax-video` |
| ITV | `fal-ai/minimax-video/image-to-video` | `fal-ai/luma-dream-machine` |
| TTS | `fal-ai/kokoro` | `fal-ai/f5-tts` |

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy environment file and configure:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Run the development server:
```bash
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

### Generation Endpoints

- `POST /api/generate/image` - Start image generation job
- `POST /api/generate/video` - Start video generation job  
- `POST /api/generate/video-from-image` - Start image-to-video job
- `POST /api/generate/speech` - Start text-to-speech job

### Job Management

- `GET /api/jobs/{job_id}` - Get job status and result
- `GET /api/jobs/{job_id}/cancel` - Cancel a pending job

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `FAL_KEY` | Fal AI API key | Yes |
| `INNGEST_EVENT_KEY` | Inngest event key | Yes |
| `INNGEST_SIGNING_KEY` | Inngest signing key | Yes |
| `REDIS_URL` | Redis connection URL | No |

## Architecture

```
Frontend --> FastAPI Server --> Inngest Queue --> Fal AI APIs
                  |
                  v
            Redis (job state)
```

## Development

Run Inngest Dev Server alongside the API:
```bash
npx inngest-cli@latest dev
```

## License

Private - All rights reserved

