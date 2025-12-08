# Python Examples

Copy-paste Python examples for integrating APIs.

## Setup

```bash
pip install openai fal-client requests python-dotenv
```

---

## Image Generation

### DALL-E 3

```python
from openai import OpenAI
import os

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def generate_image(prompt: str) -> str:
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    return response.data[0].url


# Usage
image_url = generate_image("A robot painting a sunset")
print(image_url)
```

### fal.ai Flux

```python
import fal_client
import os

fal_client.api_key = os.environ["FAL_KEY"]


def generate_image(prompt: str) -> str:
    result = fal_client.subscribe(
        "fal-ai/flux/dev",
        arguments={"prompt": prompt}
    )
    return result["images"][0]["url"]


# Usage
image_url = generate_image("A cyberpunk city at night")
print(image_url)
```

### Stability AI SDXL

```python
import requests
import os
import base64

API_HOST = "https://api.stability.ai"


def generate_image(prompt: str, output_path: str = "output.png") -> str:
    response = requests.post(
        f"{API_HOST}/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
        headers={
            "Authorization": f"Bearer {os.environ['STABILITY_API_KEY']}",
            "Content-Type": "application/json",
        },
        json={
            "text_prompts": [{"text": prompt}],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "steps": 30,
        }
    )
    
    data = response.json()
    image_data = base64.b64decode(data["artifacts"][0]["base64"])
    
    with open(output_path, "wb") as f:
        f.write(image_data)
    
    return output_path


# Usage
generate_image("A mountain landscape at dawn", "mountain.png")
```

---

## Text-to-Speech

### OpenAI TTS

```python
from openai import OpenAI
from pathlib import Path
import os

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def text_to_speech(text: str, output_path: str = "speech.mp3") -> str:
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    
    response.stream_to_file(output_path)
    return output_path


# Usage
text_to_speech("Hello, world!", "hello.mp3")
```

### ElevenLabs

```python
import requests
import os

VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel


def text_to_speech(text: str, output_path: str = "speech.mp3") -> str:
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
        headers={
            "xi-api-key": os.environ["ELEVENLABS_API_KEY"],
            "Content-Type": "application/json",
        },
        json={
            "text": text,
            "model_id": "eleven_monolingual_v1"
        }
    )
    
    with open(output_path, "wb") as f:
        f.write(response.content)
    
    return output_path


# Usage
text_to_speech("Hello from ElevenLabs!", "elevenlabs.mp3")
```

---

## Stock Assets

### Pexels

```python
import requests
import os
from typing import List, Dict


def search_photos(query: str, per_page: int = 10) -> List[Dict]:
    response = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": os.environ["PEXELS_API_KEY"]},
        params={"query": query, "per_page": per_page}
    )
    return response.json()["photos"]


def search_videos(query: str, per_page: int = 5) -> List[Dict]:
    response = requests.get(
        "https://api.pexels.com/videos/search",
        headers={"Authorization": os.environ["PEXELS_API_KEY"]},
        params={"query": query, "per_page": per_page}
    )
    return response.json()["videos"]


# Usage
photos = search_photos("mountains", 5)
for photo in photos:
    print(photo["src"]["large2x"])
```

### Giphy

```python
import requests
import os
from typing import List, Dict


def search_gifs(query: str, limit: int = 10) -> List[Dict]:
    response = requests.get(
        "https://api.giphy.com/v1/gifs/search",
        params={
            "api_key": os.environ["GIPHY_API_KEY"],
            "q": query,
            "limit": limit
        }
    )
    return response.json()["data"]


# Usage
gifs = search_gifs("excited", 5)
for gif in gifs:
    print(gif["images"]["original"]["url"])
```

### Unsplash

```python
import requests
import os
from typing import List, Dict


def search_photos(query: str, per_page: int = 10) -> List[Dict]:
    response = requests.get(
        "https://api.unsplash.com/search/photos",
        headers={
            "Authorization": f"Client-ID {os.environ['UNSPLASH_ACCESS_KEY']}"
        },
        params={"query": query, "per_page": per_page}
    )
    return response.json()["results"]


# Usage
photos = search_photos("ocean", 5)
for photo in photos:
    print(photo["urls"]["regular"])
```

---

## Video Generation

### fal.ai Image-to-Video

```python
import fal_client
import os

fal_client.api_key = os.environ["FAL_KEY"]


def image_to_video(image_url: str, prompt: str) -> str:
    result = fal_client.subscribe(
        "fal-ai/minimax-video/image-to-video",
        arguments={
            "image_url": image_url,
            "prompt": prompt
        }
    )
    return result["video"]["url"]


# Usage
video_url = image_to_video(
    "https://example.com/portrait.jpg",
    "A person smiling and waving"
)
print(video_url)
```

### D-ID Talking Avatar

```python
import requests
import time
import os
from typing import Dict


def create_talking_head(source_url: str, text: str) -> Dict:
    headers = {
        "Authorization": f"Basic {os.environ['DID_API_KEY']}",
        "Content-Type": "application/json"
    }
    
    # Create the talk
    create_response = requests.post(
        "https://api.d-id.com/talks",
        headers=headers,
        json={
            "source_url": source_url,
            "script": {
                "type": "text",
                "input": text,
                "provider": {
                    "type": "microsoft",
                    "voice_id": "en-US-JennyNeural"
                }
            }
        }
    )
    
    talk_id = create_response.json()["id"]
    
    # Poll for completion
    while True:
        status_response = requests.get(
            f"https://api.d-id.com/talks/{talk_id}",
            headers=headers
        )
        data = status_response.json()
        
        if data["status"] == "done":
            return {
                "id": talk_id,
                "result_url": data["result_url"]
            }
        elif data["status"] == "error":
            raise Exception("Talk generation failed")
        
        time.sleep(2)


# Usage
result = create_talking_head(
    "https://example.com/portrait.jpg",
    "Hello, I am an AI avatar!"
)
print(result["result_url"])
```

---

## Transcription

### OpenAI Whisper

```python
from openai import OpenAI
import os

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def transcribe_audio(audio_path: str) -> str:
    with open(audio_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcription.text


# Usage
text = transcribe_audio("audio.mp3")
print(text)
```

### fal.ai Whisper

```python
import fal_client
import os

fal_client.api_key = os.environ["FAL_KEY"]


def transcribe_audio(audio_url: str) -> str:
    result = fal_client.subscribe(
        "fal-ai/whisper",
        arguments={"audio_url": audio_url}
    )
    return result["text"]


# Usage
text = transcribe_audio("https://example.com/audio.mp3")
print(text)
```

### AssemblyAI

```python
import requests
import time
import os


def transcribe_audio(audio_url: str) -> str:
    headers = {"authorization": os.environ["ASSEMBLYAI_API_KEY"]}
    
    # Start transcription
    response = requests.post(
        "https://api.assemblyai.com/v2/transcript",
        headers=headers,
        json={"audio_url": audio_url}
    )
    transcript_id = response.json()["id"]
    
    # Poll for completion
    while True:
        response = requests.get(
            f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
            headers=headers
        )
        data = response.json()
        
        if data["status"] == "completed":
            return data["text"]
        elif data["status"] == "error":
            raise Exception("Transcription failed")
        
        time.sleep(2)


# Usage
text = transcribe_audio("https://example.com/audio.mp3")
print(text)
```

---

## Background Removal

### Remove.bg

```python
import requests
import os


def remove_background(input_path: str, output_path: str) -> str:
    with open(input_path, "rb") as image_file:
        response = requests.post(
            "https://api.remove.bg/v1.0/removebg",
            headers={"X-Api-Key": os.environ["REMOVEBG_API_KEY"]},
            files={"image_file": image_file},
            data={"size": "auto"}
        )
    
    with open(output_path, "wb") as out_file:
        out_file.write(response.content)
    
    return output_path


# Usage
remove_background("input.jpg", "output.png")
```

### Rembg (Local/Self-hosted)

```python
from rembg import remove
from PIL import Image
import io


def remove_background(input_path: str, output_path: str) -> str:
    with Image.open(input_path) as img:
        output = remove(img)
        output.save(output_path)
    return output_path


# Usage
remove_background("input.jpg", "output.png")
```

---

## Video Editing

### Shotstack

```python
import requests
import time
import os
from typing import List, Dict


def render_video(clips: List[Dict]) -> str:
    headers = {
        "x-api-key": os.environ["SHOTSTACK_API_KEY"],
        "Content-Type": "application/json"
    }
    
    # Start render
    response = requests.post(
        "https://api.shotstack.io/stage/render",
        headers=headers,
        json={
            "timeline": {
                "tracks": [{"clips": clips}]
            },
            "output": {
                "format": "mp4",
                "resolution": "hd"
            }
        }
    )
    
    render_id = response.json()["response"]["id"]
    
    # Poll for completion
    while True:
        response = requests.get(
            f"https://api.shotstack.io/stage/render/{render_id}",
            headers=headers
        )
        data = response.json()["response"]
        
        if data["status"] == "done":
            return data["url"]
        elif data["status"] == "failed":
            raise Exception("Render failed")
        
        time.sleep(3)


# Usage
video_url = render_video([
    {
        "asset": {"type": "video", "src": "https://example.com/clip1.mp4"},
        "start": 0,
        "length": 5
    },
    {
        "asset": {"type": "video", "src": "https://example.com/clip2.mp4"},
        "start": 5,
        "length": 5
    }
])
print(video_url)
```

---

## Avatars

### DiceBear

```python
def get_avatar_url(seed: str, style: str = "avataaars") -> str:
    from urllib.parse import quote
    return f"https://api.dicebear.com/7.x/{style}/svg?seed={quote(seed)}"


# Usage
avatar_url = get_avatar_url("John Doe", "avataaars")
print(avatar_url)
```

---

## Complete Workflow Example

### Social Media Video Generator

```python
import os
from typing import List
from dataclasses import dataclass


@dataclass
class VideoConfig:
    script: str
    voice: str = "alloy"
    music_mood: str = "upbeat"
    stock_query: str = "business"


async def generate_social_video(config: VideoConfig) -> str:
    """
    Complete workflow to generate a social media video:
    1. Generate TTS from script
    2. Transcribe for captions
    3. Fetch stock footage
    4. Fetch background music
    5. Compose final video
    """
    import asyncio
    
    # 1. Generate voiceover
    tts_path = text_to_speech(config.script)
    
    # 2. Get word-level timestamps for captions
    # (Using AssemblyAI for word timestamps)
    
    # 3. Fetch stock footage
    videos = search_pexels_videos(config.stock_query, 3)
    
    # 4. Generate background music
    # music_url = generate_mubert_track(config.music_mood, duration=30)
    
    # 5. Compose with Shotstack
    clips = []
    start_time = 0
    for video in videos:
        clips.append({
            "asset": {
                "type": "video",
                "src": video["video_files"][0]["link"]
            },
            "start": start_time,
            "length": 5
        })
        start_time += 5
    
    # Add voiceover track
    # Add music track (ducked)
    # Add caption track
    
    video_url = render_video(clips)
    return video_url


# Usage
# video_url = await generate_social_video(VideoConfig(
#     script="Welcome to our product launch...",
#     voice="nova",
#     stock_query="technology"
# ))
```

