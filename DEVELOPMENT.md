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
python -m venv venv
source venv/bin/activate
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

