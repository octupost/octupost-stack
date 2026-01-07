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
cd /Users/serhatcamici/dev/octupost-stack/api
source venv/bin/activate && python -m app.agent_os


**Tab 4 - INNGEST:**
npx inngest-cli@latest dev

---
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Forward webhooks to your local server
stripe listen --forward-to localhost:8000/api/billing/webhook

