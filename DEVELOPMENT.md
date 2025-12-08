# Octupost Stack - Development Guide

This monorepo contains the complete Octupost application stack, managed using **Turborepo** for centralized orchestration.

## 🏗️ Architecture Overview

| App | Technology | Port | Description |
|-----|-----------|------|-------------|
| `octupost` | Next.js 16 | 3000 | Main web application |
| `octupost-studio` | Next.js 14 | 3001 | Video studio editor |
| `octupost-api` | Python/FastAPI | 8000 | Backend API server |
| `octupost-mixpost` | Laravel/PHP | 8001 | Social media management (separate) |

## 🚀 Quick Start

### Run All Apps (Centralized)

From the root directory, run:

```bash
npm run dev
```

This single command starts all 3 Turborepo-managed apps in parallel:
- **@octupost/app** → http://localhost:3000
- **@octupost/studio** → http://localhost:3001
- **@octupost/api** → http://localhost:8000

### Run Laravel App (Separately)

The Laravel app is not part of Turborepo workspaces and must be run separately:

```bash
cd octupost-mixpost
php artisan serve --port=8001
```

---

## 📦 Initial Setup (First Time Only)

### 1. Install Node.js Dependencies

```bash
# From root directory
npm install
```

This installs dependencies for all workspace packages.

### 2. Set Up Python Virtual Environment (API)

```bash
cd octupost-api
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or: venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

### 3. Set Up Laravel (Mixpost)

```bash
cd octupost-mixpost
composer install
php artisan migrate
```

### 4. Environment Variables

Create the following files in the **root directory**:

- `.env.local` - Local secrets (Supabase keys, API keys, etc.)
- `.env.development` - Development-specific variables
- `.env.production` - Production variables (for builds)

Example `.env.local`:
```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Other services
SENTRY_DSN=your_sentry_dsn
```

The frontend expects `NEXT_PUBLIC_API_URL`. If you already have `OCTUPOST_API_URL` set, it will be reused automatically at build time to avoid localhost fallbacks.

---

## 🛠️ Available Commands

### Root Level (Turborepo)

| Command | Description |
|---------|-------------|
| `npm run dev` | Start all apps in development mode |
| `npm run build` | Build all apps for production |
| `npm run lint` | Run linting on all apps |

### Individual Apps

You can also run commands for specific apps:

```bash
# Run only the main app
cd octupost && npm run dev

# Run only the studio
cd octupost-studio && npm run dev

# Run only the API
cd octupost-api && source venv/bin/activate && python -m uvicorn app.main:app --reload --port 8000
```

---

## 📁 Project Structure

```
octupost-stack/
├── package.json          # Root workspace config
├── turbo.json            # Turborepo configuration
├── .env.local            # Local environment variables
├── .env.development      # Development environment
│
├── packages/
│   └── shared/           # Shared utilities (@octupost/shared)
│       └── src/
│           ├── config/   # Centralized URLs, ports, domains
│           └── supabase/ # Shared Supabase client utilities
│
├── octupost/             # Main Next.js app (port 3000)
│   ├── app/              # App router pages
│   ├── components/       # React components
│   └── lib/              # Utilities & helpers
│
├── octupost-studio/      # Studio Next.js app (port 3001)
│   ├── app/              # App router pages
│   └── components/       # Studio components
│
├── octupost-api/         # Python FastAPI (port 8000)
│   ├── app/              # FastAPI application
│   │   ├── api/          # API routes
│   │   ├── inngest/      # Background job functions
│   │   ├── models/       # Data models
│   │   └── services/     # Business logic
│   └── venv/             # Python virtual environment
│
└── octupost-mixpost/     # Laravel app (port 8001)
    ├── app/              # Laravel application
    ├── routes/           # API & web routes
    └── database/         # Migrations & seeders
```

---

## 🔧 Troubleshooting

### Issue: "Missing packageManager field"
Add this to root `package.json`:
```json
"packageManager": "npm@10.9.4"
```

### Issue: "Module not found: @supabase/ssr"
Install the missing dependency:
```bash
cd octupost && npm install @supabase/ssr @supabase/supabase-js
```

### Issue: Port conflicts
If ports are already in use:
```bash
# Find and kill process on port
lsof -i :3000 | grep LISTEN
kill -9 <PID>
```

### Issue: Python venv not activating
Ensure you're using the correct shell command:
```bash
# bash/zsh
source venv/bin/activate

# fish
source venv/bin/activate.fish
```

---

## 🚢 Production Build

```bash
# Build all apps
npm run build

# Build outputs:
# - octupost/.next/
# - octupost-studio/.next/
```

---

## 📦 Shared Package (@octupost/shared)

The `packages/shared` package contains centralized configuration and utilities used across all apps.

### Configuration Constants

```typescript
import { URLS, PORTS, DOMAIN, getAppUrl, getCookieDomain } from "@octupost/shared/config"

// Get URL for any app
const studioUrl = getAppUrl("studio") // Returns prod or dev URL based on NODE_ENV

// Get cookie domain
const cookieDomain = getCookieDomain() // ".octupost.com" in prod, undefined in dev
```

### Supabase Clients

```typescript
// Browser client
import { createClient } from "@octupost/shared/supabase/client"

// Server client (async)
import { createClient } from "@octupost/shared/supabase/server"

// Middleware utilities
import { updateSession, getSignInUrl } from "@octupost/shared/supabase/middleware"
```

### Centralized Values

| Constant | Value |
|----------|-------|
| `DOMAIN` | `octupost.com` |
| `COOKIE_DOMAIN` | `.octupost.com` |
| `PORTS.app` | `3000` |
| `PORTS.studio` | `3001` |
| `PORTS.social` | `3002` |
| `PORTS.api` | `8000` |
| `PORTS.mixpost` | `8001` |

---

## 📝 Additional Notes

- **Inngest Dev Server**: If you're using Inngest for background jobs, run it separately:
  ```bash
  npx inngest-cli@latest dev
  ```

- **Database**: The API uses Supabase. Make sure your environment variables are configured.

- **Hot Reload**: All apps support hot reload in development mode.

---

*Last updated: December 6, 2025*

