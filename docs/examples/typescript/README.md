# TypeScript Examples

Copy-paste TypeScript/Node.js examples for integrating APIs.

## Setup

```bash
npm install openai @fal-ai/client axios
```

---

## Image Generation

### DALL-E 3

```typescript
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

async function generateImage(prompt: string) {
  const response = await openai.images.generate({
    model: "dall-e-3",
    prompt,
    n: 1,
    size: "1024x1024",
  });

  return response.data[0].url;
}

// Usage
const imageUrl = await generateImage("A robot painting a sunset");
console.log(imageUrl);
```

### fal.ai Flux

```typescript
import { fal } from "@fal-ai/client";

fal.config({
  credentials: process.env.FAL_KEY,
});

async function generateImage(prompt: string) {
  const result = await fal.subscribe("fal-ai/flux/dev", {
    input: { prompt },
  });

  return result.data.images[0].url;
}

// Usage
const imageUrl = await generateImage("A cyberpunk city at night");
console.log(imageUrl);
```

---

## Text-to-Speech

### OpenAI TTS

```typescript
import OpenAI from 'openai';
import fs from 'fs';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

async function textToSpeech(text: string, outputPath: string) {
  const response = await openai.audio.speech.create({
    model: "tts-1",
    voice: "alloy",
    input: text,
  });

  const buffer = Buffer.from(await response.arrayBuffer());
  await fs.promises.writeFile(outputPath, buffer);
  
  return outputPath;
}

// Usage
await textToSpeech("Hello, world!", "output.mp3");
```

### ElevenLabs

```typescript
import axios from 'axios';
import fs from 'fs';

const VOICE_ID = "21m00Tcm4TlvDq8ikWAM"; // Rachel

async function textToSpeech(text: string, outputPath: string) {
  const response = await axios.post(
    `https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}`,
    {
      text,
      model_id: "eleven_monolingual_v1",
    },
    {
      headers: {
        "xi-api-key": process.env.ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
      },
      responseType: "arraybuffer",
    }
  );

  await fs.promises.writeFile(outputPath, response.data);
  return outputPath;
}

// Usage
await textToSpeech("Hello from ElevenLabs!", "output.mp3");
```

---

## Stock Assets

### Pexels

```typescript
import axios from 'axios';

interface PexelsPhoto {
  id: number;
  src: {
    original: string;
    large2x: string;
    medium: string;
  };
  alt: string;
}

async function searchPhotos(query: string, perPage = 10): Promise<PexelsPhoto[]> {
  const response = await axios.get("https://api.pexels.com/v1/search", {
    headers: {
      Authorization: process.env.PEXELS_API_KEY,
    },
    params: {
      query,
      per_page: perPage,
    },
  });

  return response.data.photos;
}

async function searchVideos(query: string, perPage = 5) {
  const response = await axios.get("https://api.pexels.com/videos/search", {
    headers: {
      Authorization: process.env.PEXELS_API_KEY,
    },
    params: {
      query,
      per_page: perPage,
    },
  });

  return response.data.videos;
}

// Usage
const photos = await searchPhotos("mountains", 5);
console.log(photos.map(p => p.src.large2x));
```

### Giphy

```typescript
import axios from 'axios';

interface GiphyGif {
  id: string;
  url: string;
  images: {
    original: { url: string };
    downsized: { url: string };
  };
}

async function searchGifs(query: string, limit = 10): Promise<GiphyGif[]> {
  const response = await axios.get("https://api.giphy.com/v1/gifs/search", {
    params: {
      api_key: process.env.GIPHY_API_KEY,
      q: query,
      limit,
    },
  });

  return response.data.data;
}

// Usage
const gifs = await searchGifs("excited", 5);
console.log(gifs.map(g => g.images.original.url));
```

---

## Video Generation

### fal.ai Image-to-Video

```typescript
import { fal } from "@fal-ai/client";

fal.config({
  credentials: process.env.FAL_KEY,
});

async function imageToVideo(imageUrl: string, prompt: string) {
  const result = await fal.subscribe("fal-ai/minimax-video/image-to-video", {
    input: {
      image_url: imageUrl,
      prompt,
    },
  });

  return result.data.video.url;
}

// Usage
const videoUrl = await imageToVideo(
  "https://example.com/portrait.jpg",
  "A person smiling and waving"
);
console.log(videoUrl);
```

### D-ID Talking Avatar

```typescript
import axios from 'axios';

interface TalkingHeadResult {
  id: string;
  result_url: string;
}

async function createTalkingHead(
  sourceUrl: string,
  text: string
): Promise<TalkingHeadResult> {
  // Create the talk
  const createResponse = await axios.post(
    "https://api.d-id.com/talks",
    {
      source_url: sourceUrl,
      script: {
        type: "text",
        input: text,
        provider: {
          type: "microsoft",
          voice_id: "en-US-JennyNeural",
        },
      },
    },
    {
      headers: {
        Authorization: `Basic ${process.env.DID_API_KEY}`,
        "Content-Type": "application/json",
      },
    }
  );

  const talkId = createResponse.data.id;

  // Poll for completion
  let result;
  while (true) {
    const statusResponse = await axios.get(
      `https://api.d-id.com/talks/${talkId}`,
      {
        headers: {
          Authorization: `Basic ${process.env.DID_API_KEY}`,
        },
      }
    );

    if (statusResponse.data.status === "done") {
      result = statusResponse.data;
      break;
    } else if (statusResponse.data.status === "error") {
      throw new Error("Talk generation failed");
    }

    await new Promise((resolve) => setTimeout(resolve, 2000));
  }

  return {
    id: talkId,
    result_url: result.result_url,
  };
}

// Usage
const result = await createTalkingHead(
  "https://example.com/portrait.jpg",
  "Hello, I am an AI avatar!"
);
console.log(result.result_url);
```

---

## Transcription

### OpenAI Whisper

```typescript
import OpenAI from 'openai';
import fs from 'fs';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

async function transcribeAudio(audioPath: string) {
  const transcription = await openai.audio.transcriptions.create({
    file: fs.createReadStream(audioPath),
    model: "whisper-1",
  });

  return transcription.text;
}

// Usage
const text = await transcribeAudio("audio.mp3");
console.log(text);
```

### fal.ai Whisper

```typescript
import { fal } from "@fal-ai/client";

fal.config({
  credentials: process.env.FAL_KEY,
});

async function transcribeAudio(audioUrl: string) {
  const result = await fal.subscribe("fal-ai/whisper", {
    input: {
      audio_url: audioUrl,
    },
  });

  return result.data.text;
}

// Usage
const text = await transcribeAudio("https://example.com/audio.mp3");
console.log(text);
```

---

## Background Removal

### Remove.bg

```typescript
import axios from 'axios';
import fs from 'fs';
import FormData from 'form-data';

async function removeBackground(inputPath: string, outputPath: string) {
  const formData = new FormData();
  formData.append("image_file", fs.createReadStream(inputPath));
  formData.append("size", "auto");

  const response = await axios.post(
    "https://api.remove.bg/v1.0/removebg",
    formData,
    {
      headers: {
        "X-Api-Key": process.env.REMOVEBG_API_KEY,
        ...formData.getHeaders(),
      },
      responseType: "arraybuffer",
    }
  );

  await fs.promises.writeFile(outputPath, response.data);
  return outputPath;
}

// Usage
await removeBackground("input.jpg", "output.png");
```

---

## Video Editing

### Shotstack

```typescript
import axios from 'axios';

interface ShotstackClip {
  asset: {
    type: string;
    src: string;
  };
  start: number;
  length: number;
}

async function renderVideo(clips: ShotstackClip[]) {
  const response = await axios.post(
    "https://api.shotstack.io/stage/render",
    {
      timeline: {
        tracks: [{ clips }],
      },
      output: {
        format: "mp4",
        resolution: "hd",
      },
    },
    {
      headers: {
        "x-api-key": process.env.SHOTSTACK_API_KEY,
        "Content-Type": "application/json",
      },
    }
  );

  const renderId = response.data.response.id;

  // Poll for completion
  while (true) {
    const statusResponse = await axios.get(
      `https://api.shotstack.io/stage/render/${renderId}`,
      {
        headers: {
          "x-api-key": process.env.SHOTSTACK_API_KEY,
        },
      }
    );

    const status = statusResponse.data.response.status;

    if (status === "done") {
      return statusResponse.data.response.url;
    } else if (status === "failed") {
      throw new Error("Render failed");
    }

    await new Promise((resolve) => setTimeout(resolve, 3000));
  }
}

// Usage
const videoUrl = await renderVideo([
  {
    asset: { type: "video", src: "https://example.com/clip1.mp4" },
    start: 0,
    length: 5,
  },
  {
    asset: { type: "video", src: "https://example.com/clip2.mp4" },
    start: 5,
    length: 5,
  },
]);
console.log(videoUrl);
```

---

## Avatars

### DiceBear

```typescript
function getAvatarUrl(seed: string, style = "avataaars"): string {
  return `https://api.dicebear.com/7.x/${style}/svg?seed=${encodeURIComponent(seed)}`;
}

// Usage
const avatarUrl = getAvatarUrl("John Doe", "avataaars");
console.log(avatarUrl);
```

