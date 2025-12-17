# Development Setup

Quick guide to run all services locally for development.

## One-Time Setup

### Fix npm Cache Permissions (if needed)

If you encounter npm permission errors, run:

```bash
sudo chown -R $(whoami) ~/.npm
```

## Port Reference

| Service  | URL                    | Port |
|----------|------------------------|------|
| Frontend | http://localhost:3000  | 3000 |
| API      | http://localhost:8000  | 8000 |
| Mixpost  | http://localhost:8080  | 8080 |

---

## 1. Mixpost (Laravel)

```bash
cd mixpost
php artisan serve --port=8080
```

Runs at: http://localhost:8080

---

## 2. Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

Runs at: http://localhost:3000

---

## 3. API (FastAPI)

```bash
cd api
Okay, I'm reading your plan. I think that sounds like a good plan. So like you're saying we're not competing. Yeah, we're not competing.

Like my aim is more like... So they have a big platform, yeah, for sure. But like my aim is like... My aim is agent.

So like I want also like I will add some like roadmap stuff, designing. So basically my aim will be guiding people to do like an app with like helping the people to do marketing videos or like create a mention for like YouTube channel or whatever. It has like some use case.

So okay type that down. Let's finalize the product then we will go ahead because we didn't have a proper product yet. So okay. The product is this. First of all, in the product we have like the main goal is make life easier for a month.

Okay one of the goal. A user might want to have a YouTube channel and he wants to stop from scratch. This is the one option. So those are good market.

So like we will be able to let them generate videos with AI. But also like for instance I want to create like a YouTube channel for transfer news for Arsenal for instance. So I will be able to do that easily. This is one thing.

The second thing is like the marketing videos. So like let's say my friend is like he wants to create videos and do marketing. So I will be able to help like this tool will be able to help him. So I will be able to use this tool and help him.

This is the second thing. The third thing is the third thing is yeah that's pretty much it. Or you're a video editor. You can use like AI features of this video.

Plus I want to add some templates for like popular AI videos. So like there are some AI videos that those are popular. And I will be able to add them. So okay those are the main features.

And dubbing will come later on. Although dubbing would be a good thing too. The only problem I don't have clients. So like if I have a client who is looking for dubbing I would go for them.

But now I want to do like something proper and I will use it. So in the AI studio also there will be dubbing. So now I think that's a good plan. So like what we can do.

So okay let me just break it down. So they have a playground. I have a playground. So let me just run my playground.

Let me just open it into where the terminal. Guys open it into where the terminal. Okay. source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Runs at: http://localhost:8000

---

## Running All Services

Open 3 terminal tabs and run each service in its own tab:

**Tab 1 - Mixpost:**
```bash
cd mixpost && php artisan serve --port=8080
```

**Tab 2 - Frontend:**
```bash
cd frontend && npm run dev
```

**Tab 3 - API:**
```bash
cd api && source venv/bin/activate && uvicorn app.main:app --reload --port 8000
cd api && source venv/bin/activate && python agent_os.py
```


npx inngest-cli@latest dev

---

## Cursor MCP Servers

MCP (Model Context Protocol) servers provide AI capabilities in Cursor. Configuration is stored in `~/.cursor/mcp.json`.

### Configured MCP Servers

| Server | Package | Purpose |
|--------|---------|---------|
| Supabase | URL-based | Database operations |
| fal | URL-based | AI image/video generation |
| TwelveLabs | `@jine9323/twelvelabs` | Video understanding & search |
| ElevenLabs | `elevenlabs-mcp` | Text-to-speech |
| HeyGen | `heygen-mcp` | AI avatar videos |
| RunwayML | `runway-mcp-server` | Video generation |
| MiniMax | `minimax-mcp` | AI generation |
| Replicate | `replicate-mcp` | ML model inference |
| PostHog | URL-based | Analytics |
| Sentry | URL-based | Error tracking |

### Adding a New MCP Server

Edit `~/.cursor/mcp.json` and add your server configuration:

```json
{
  "mcpServers": {
    "your-server": {
      "command": "npx",
      "args": ["-y", "package-name"],
      "env": {
        "API_KEY": "your-api-key"
      }
    }
  }
}
```

After editing, restart Cursor for changes to take effect.

# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Forward webhooks to your local server
stripe listen --forward-to localhost:8000/api/billing/webhook

---

## Model Configuration System

AI model configurations are stored in the `octupost.model_configs` Supabase table. This replaces the previous static `provider.json` file and eliminates runtime FAL Schema API calls.

### Admin UI

Manage models at `/admin/models`:
- **List models**: View all configured models with filters
- **Add new model**: Enter FAL endpoint, fetch schema, configure display settings
- **Edit model**: Update configuration, sync parameters from FAL
- **Toggle active**: Enable/disable models for users

### How It Works

1. **Database-driven**: All model data stored in Supabase
2. **No runtime API calls**: Parameters stored in `parameters` JSONB column
3. **UI configuration in DB**: `inline_params`, `hidden_params`, `param_overrides`
4. **Sync with FAL**: Admin can compare and update from FAL's OpenAPI schema

### Key Files

| File | Purpose |
|------|---------|
| `frontend/lib/types/model-config.ts` | TypeScript types |
| `frontend/lib/hooks/use-model-configs.ts` | React hooks |
| `frontend/app/api/admin/model-configs/` | API routes |
| `frontend/app/(app)/admin/models/` | Admin UI pages |
| `frontend/scripts/import-models.ts` | Migration script |

### Adding a New Model

1. Go to `/admin/models/new`
2. Enter FAL endpoint ID (e.g., `fal-ai/gpt-image-1-mini`)
3. Click "Fetch Schema" to get parameters from FAL
4. Configure inline/hidden params
5. Save

### Syncing Parameters

1. Go to `/admin/models/[id]`
2. Click "Sync from FAL"
3. Review side-by-side comparison
4. Select changes to apply
5. Save

### Migration from provider.json

Run the import script to migrate existing models:

```bash
cd frontend
npx tsx scripts/import-models.ts
```

Note: Requires `NEXT_PUBLIC_SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in `.env.local`.