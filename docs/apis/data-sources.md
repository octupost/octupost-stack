# Stock Asset Data Sources

APIs for free and premium stock images, videos, GIFs, and other media assets.

---

## Stock Images

### Pexels

**Website:** https://pexels.com  
**Docs:** https://www.pexels.com/api/documentation

**Authentication:** API key

**Pricing:** Free

**Rate Limits:** 200 requests/hour, 20,000/month

**Key Capabilities:**
- Millions of free stock photos
- Curated collections
- Search by keyword, color, orientation
- Multiple resolutions
- Video library included

**Limitations:**
- Rate limits for heavy use
- Some photos overused

**SDKs:** Python, JavaScript, REST

**Licensing:** Pexels License (free commercial, no attribution required)

**Sample Request:**
```bash
curl -H "Authorization: YOUR_API_KEY" \
  "https://api.pexels.com/v1/search?query=nature&per_page=10"
```

---

### Unsplash

**Website:** https://unsplash.com  
**Docs:** https://unsplash.com/documentation

**Authentication:** API key (OAuth for some features)

**Pricing:** Free

**Rate Limits:** 50 requests/hour (demo), 5000/hour (production)

**Key Capabilities:**
- 3M+ high-resolution photos
- Search, random, curated
- Collections and topics
- User profiles
- Download tracking

**Limitations:**
- Hotlinking not allowed (must download)
- Attribution encouraged (not required)

**SDKs:** JavaScript (`unsplash-js`), REST

**Licensing:** Unsplash License (free commercial)

**Sample Request:**
```javascript
import { createApi } from 'unsplash-js';

const unsplash = createApi({
  accessKey: 'YOUR_ACCESS_KEY',
});

const result = await unsplash.search.getPhotos({
  query: 'mountains',
  page: 1,
  perPage: 10,
});
```

---

### Pixabay

**Website:** https://pixabay.com  
**Docs:** https://pixabay.com/api/docs

**Authentication:** API key

**Pricing:** Free

**Rate Limits:** 100 requests/minute

**Key Capabilities:**
- 2.7M+ images, videos, music
- Search by type, category, colors
- Multiple sizes
- Vectors and illustrations
- Editor's choice

**Limitations:**
- Some content lower quality
- Safesearch mandatory by default

**SDKs:** REST

**Licensing:** Pixabay License (free commercial, no attribution)

**Sample Request:**
```bash
curl "https://pixabay.com/api/?key=YOUR_API_KEY&q=yellow+flowers&image_type=photo"
```

---

### Shutterstock

**Website:** https://shutterstock.com  
**Docs:** https://developers.shutterstock.com

**Authentication:** OAuth2 / API key

**Pricing:**
- API access requires subscription
- Images: From $29/month (10 images)
- Enterprise: Custom

**Key Capabilities:**
- 400M+ images, videos, music
- Premium quality
- AI-powered search
- Similar image search
- Contributor marketplace

**Limitations:**
- Paid only
- Complex licensing

**SDKs:** Python, JavaScript, REST

**Licensing:** Various (Standard, Enhanced)

---

### Adobe Stock

**Website:** https://stock.adobe.com  
**Docs:** https://developer.adobe.com/stock

**Authentication:** OAuth2 / API key

**Pricing:**
- Subscription required
- From $29.99/month

**Key Capabilities:**
- Premium stock library
- Adobe Creative Cloud integration
- Templates, 3D assets
- AI search

**Limitations:**
- Paid only
- Adobe ecosystem focus

**SDKs:** REST

**Licensing:** Adobe Stock license

---

## Stock Videos

### Pexels Videos

**Website:** https://pexels.com/videos  
**Docs:** https://www.pexels.com/api/documentation/#videos

**Authentication:** Same as Pexels images

**Pricing:** Free

**Rate Limits:** Same as images

**Key Capabilities:**
- HD and 4K videos
- Search and popular
- Multiple resolutions
- Download links

**SDKs:** Same as images

**Licensing:** Pexels License (free commercial)

**Sample Request:**
```bash
curl -H "Authorization: YOUR_API_KEY" \
  "https://api.pexels.com/videos/search?query=ocean&per_page=5"
```

---

### Pixabay Videos

**Website:** https://pixabay.com/videos  
**Docs:** https://pixabay.com/api/docs (video_type parameter)

**Authentication:** Same as images

**Pricing:** Free

**Key Capabilities:**
- Free stock videos
- Multiple resolutions
- Category filtering

**SDKs:** REST

**Licensing:** Pixabay License

---

### Coverr

**Website:** https://coverr.co  
**Docs:** No public API

**Authentication:** N/A

**Pricing:** Free

**Key Capabilities:**
- Curated free videos
- Weekly new content
- Categories

**Limitations:**
- No API
- Manual download

**SDKs:** None

**Licensing:** Free commercial use

---

### Mixkit

**Website:** https://mixkit.co  
**Docs:** No public API

**Authentication:** N/A

**Pricing:** Free

**Key Capabilities:**
- Free HD videos
- Music and sound effects
- Video templates

**Limitations:**
- No API
- Manual download

**SDKs:** None

**Licensing:** Mixkit License (free commercial)

---

## GIFs & Stickers

### Giphy

**Website:** https://giphy.com  
**Docs:** https://developers.giphy.com/docs/api

**Authentication:** API key

**Pricing:** Free

**Rate Limits:** 100 requests/hour (beta), 1000/day (production)

**Key Capabilities:**
- Largest GIF library
- Search, trending, random
- Stickers
- Categories and tags
- Upload API

**SDKs:** JavaScript, Python, REST

**Licensing:** Giphy's terms (attribution required)

**Sample Request:**
```bash
curl "https://api.giphy.com/v1/gifs/search?api_key=YOUR_KEY&q=funny&limit=10"
```

---

### Tenor

**Website:** https://tenor.com  
**Docs:** https://tenor.com/gifapi/documentation

**Authentication:** API key

**Pricing:** Free (Google owned)

**Rate Limits:** Based on usage

**Key Capabilities:**
- Large GIF library
- Search, featured, categories
- Stickers
- GIF Keyboard integration
- Anonymous sharing

**SDKs:** REST

**Licensing:** Tenor terms (free to use)

**Sample Request:**
```bash
curl "https://tenor.googleapis.com/v2/search?q=excited&key=YOUR_KEY&limit=8"
```

---

### Gfycat

**Website:** https://gfycat.com  
**Docs:** https://developers.gfycat.com

**Authentication:** OAuth2 / API key

**Pricing:** Free tier available

**Key Capabilities:**
- High-quality GIFs
- Video-to-GIF conversion
- Search and upload

**Limitations:**
- Owned by Snap now
- API may be deprecated

**SDKs:** REST

**Licensing:** Gfycat terms

---

## Icons & Vectors

### Flaticon

**Website:** https://flaticon.com  
**Docs:** https://api.flaticon.com

**Authentication:** API key

**Pricing:**
- Free tier: Limited
- Premium: From $9.99/month

**Key Capabilities:**
- 8M+ icons
- SVG, PNG, EPS formats
- Search by keyword, style
- Icon packs

**SDKs:** REST

**Licensing:** Attribution (free) / Flaticon license (premium)

---

### The Noun Project

**Website:** https://thenounproject.com  
**Docs:** https://api.thenounproject.com

**Authentication:** OAuth

**Pricing:**
- Free tier with attribution
- Pro: $39.99/year

**Key Capabilities:**
- 3M+ icons
- Collections
- SVG/PNG

**SDKs:** REST

**Licensing:** CC-BY (free) / Royalty-free (Pro)

---

### Iconify

**Website:** https://iconify.design  
**Docs:** https://iconify.design/docs/api

**Authentication:** None

**Pricing:** Free

**Key Capabilities:**
- 150,000+ icons from 100+ sets
- SVG API
- Search across sets
- On-demand loading

**SDKs:** JavaScript, REST

**Licensing:** Varies by icon set

**Sample Request:**
```bash
curl "https://api.iconify.design/mdi/home.svg"
```

---

## Fonts

### Google Fonts

**Website:** https://fonts.google.com  
**Docs:** https://developers.google.com/fonts

**Authentication:** API key (optional)

**Pricing:** Free

**Key Capabilities:**
- 1500+ font families
- CSS and download
- Font metadata
- Variable fonts

**SDKs:** REST, CSS embed

**Licensing:** Open source (SIL OFL, Apache 2.0)

---

### Adobe Fonts

**Website:** https://fonts.adobe.com  
**Docs:** https://developer.adobe.com/fonts

**Authentication:** Adobe ID

**Pricing:** Included with Creative Cloud

**Key Capabilities:**
- 20,000+ fonts
- Web and desktop
- Sync to apps

**Limitations:**
- CC subscription required

**SDKs:** REST

**Licensing:** Adobe subscription

---

## Background Patterns & Textures

### Hero Patterns

**Website:** https://heropatterns.com  
**Docs:** N/A (CSS generator)

**Pricing:** Free

**Key Capabilities:**
- SVG background patterns
- Customizable colors
- CSS export

**Licensing:** CC-BY 4.0

---

### Subtle Patterns

**Website:** https://subtlepatterns.com  
**Docs:** N/A

**Pricing:** Free

**Key Capabilities:**
- Tileable textures
- PNG format

**Licensing:** Free commercial use

