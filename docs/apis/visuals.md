# Visual Generation APIs

APIs for generating images, avatars, graphics, and visual assets.

---

## Image Generation

### OpenAI DALL-E 3

**Website:** https://openai.com  
**Docs:** https://platform.openai.com/docs/guides/images

**Authentication:** Bearer token (API key)

**Pricing:**
- DALL-E 3 Standard 1024×1024: $0.040/image
- DALL-E 3 HD 1024×1024: $0.080/image
- DALL-E 3 HD 1792×1024: $0.120/image

**Rate Limits:** 7 images/min (tier 1), scales with tier

**Key Capabilities:**
- High-quality photorealistic and artistic images
- Strong prompt adherence
- Built-in content moderation
- Image editing (inpainting) with DALL-E 2

**Limitations:**
- No image-to-image (img2img) in DALL-E 3
- Cannot generate faces of real people
- Slower than some alternatives

**SDKs:** Python (`openai`), Node.js (`openai`), REST

**Licensing:** Commercial use allowed, you own generated images

---

### Stability AI (Stable Diffusion / SDXL)

**Website:** https://stability.ai  
**Docs:** https://platform.stability.ai/docs/api-reference

**Authentication:** API key (Bearer token)

**Pricing:**
- SDXL 1.0: ~$0.002–$0.006/image (varies by resolution)
- Stable Diffusion 3: ~$0.035/image
- Free tier: 25 credits on signup

**Rate Limits:** 150 requests/10 seconds

**Key Capabilities:**
- Text-to-image, image-to-image
- Inpainting, outpainting
- Upscaling (4x)
- Multiple model versions (SD 1.5, SDXL, SD3)
- ControlNet support

**Limitations:**
- Quality varies by model/settings
- Some models require more tuning

**SDKs:** Python, REST

**Licensing:** Open-weight models; API outputs commercial-friendly

---

### fal.ai (Flux, SDXL, and more)

**Website:** https://fal.ai  
**Docs:** https://docs.fal.ai/model-apis

**Authentication:** API key

**Pricing:**
- Flux Dev: ~$0.025/image
- Fast-SDXL: ~$0.0025/image (2.3s inference)
- Pay-per-second GPU billing

**Rate Limits:** Scales automatically

**Key Capabilities:**
- 600+ models available (Flux, SDXL, SD3, etc.)
- Fastest SDXL inference
- LoRA and embeddings support
- Image-to-video models

**Limitations:**
- Requires understanding of model selection

**SDKs:** JavaScript (`@fal-ai/client`), Python, REST

**Licensing:** Commercial use allowed

**Sample Request (TypeScript):**
```typescript
import { fal } from "@fal-ai/client";

const result = await fal.subscribe("fal-ai/flux/dev", {
  input: {
    prompt: "a cute puppy in pixar style",
  },
});
```

---

### Replicate

**Website:** https://replicate.com  
**Docs:** https://replicate.com/docs

**Authentication:** API token

**Pricing:**
- Pay per second of GPU time
- SDXL: ~$0.00115/second (A40 GPU)
- Free tier: Limited credits

**Rate Limits:** Based on plan

**Key Capabilities:**
- Run any open-source model
- SDXL, Flux, ControlNet, etc.
- Deploy custom models
- Webhooks for async results

**Limitations:**
- Cold starts on less popular models
- Pricing less predictable than per-image

**SDKs:** Python (`replicate`), Node.js, REST

**Licensing:** Depends on model license

---

### DeepAI

**Website:** https://deepai.org  
**Docs:** https://deepai.org/machine-learning-model/text2img

**Authentication:** API key

**Pricing:**
- Free tier: 5 API calls/month
- Paid: $4.99/100 calls

**Key Capabilities:**
- Text-to-image
- Image colorization
- Style transfer
- Super resolution

**Limitations:**
- Lower quality than newer models
- Limited customization

**SDKs:** REST, cURL

**Licensing:** Commercial use allowed

---

## Avatar Generation

### HeyGen

**Website:** https://heygen.com  
**Docs:** https://docs.heygen.com

**Authentication:** API key

**Pricing:**
- Free trial available
- Business: ~$30/month for 15 min/month video
- API pricing varies

**Key Capabilities:**
- Photorealistic AI avatars
- Text-to-video with lip sync
- 100+ stock avatars
- Custom avatar creation from photo/video
- 40+ languages

**Limitations:**
- Expensive for high volume
- Avatar customization limited on lower tiers

**SDKs:** REST API

**Licensing:** Commercial use allowed

---

### Synthesia

**Website:** https://synthesia.io  
**Docs:** https://docs.synthesia.io

**Authentication:** API key

**Pricing:**
- Starter: $22/month (10 min/month)
- Enterprise: Custom pricing
- API access on higher tiers

**Key Capabilities:**
- 150+ stock avatars
- Custom avatars from video
- 130+ languages
- Text-to-video generation
- Template library

**Limitations:**
- Expensive for API access
- Custom avatars require recording session

**SDKs:** REST API

**Licensing:** Commercial use allowed

---

### D-ID

**Website:** https://d-id.com  
**Docs:** https://docs.d-id.com

**Authentication:** API key

**Pricing:**
- Free trial: 5 min video
- Lite: $5.99/month (10 min)
- Pro: $49/month (45 min)

**Key Capabilities:**
- Talking head videos from single photo
- Lip sync to audio
- Multiple presenters
- Real-time streaming API

**Limitations:**
- Quality depends on input photo
- Limited expressions

**SDKs:** REST API, JavaScript

**Licensing:** Commercial use allowed

---

### DiceBear Avatars

**Website:** https://dicebear.com  
**Docs:** https://www.dicebear.com/how-to-use/

**Authentication:** None (open source)

**Pricing:** Free

**Key Capabilities:**
- Deterministic avatar generation from seed
- 20+ art styles
- SVG output
- Self-hostable

**Limitations:**
- Illustration style only (not photorealistic)
- Static images only

**SDKs:** JavaScript, REST API

**Licensing:** MIT / CC0 (varies by style)

**Sample Request:**
```bash
curl "https://api.dicebear.com/7.x/avataaars/svg?seed=Felix"
```

---

### Multiavatar

**Website:** https://multiavatar.com  
**Docs:** https://multiavatar.com

**Authentication:** None

**Pricing:** Free / $9 for API access

**Key Capabilities:**
- 12 billion unique avatars
- SVG/PNG output
- Deterministic from string input

**Limitations:**
- Cartoon style only
- No customization options

**SDKs:** JavaScript, REST

**Licensing:** Free for personal use; paid for commercial

---

## Icon & Illustration Generation

### Freepik API

**Website:** https://freepik.com  
**Docs:** https://www.freepik.com/api

**Authentication:** API key

**Pricing:**
- Premium subscription required
- API access on enterprise plans

**Key Capabilities:**
- Millions of vectors, icons, photos
- AI image generation
- Search and download

**Limitations:**
- Requires subscription
- Attribution on free tier

**SDKs:** REST

**Licensing:** Royalty-free with license

---

### Iconfinder API

**Website:** https://iconfinder.com  
**Docs:** https://developer.iconfinder.com

**Authentication:** API key

**Pricing:**
- Free tier: 100 requests/day
- Pro: Based on usage

**Key Capabilities:**
- 6 million+ icons
- SVG, PNG formats
- Search by style, category

**Limitations:**
- Some icons require purchase

**SDKs:** REST

**Licensing:** Various (per icon)

