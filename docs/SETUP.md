# Setup Guide

Step-by-step guide to run PortfolioMatch locally.

## Prerequisites

- Python 3.11+
- Node.js 20+
- Git
- (Optional) Docker + Docker Compose

## 1. Get API keys

### GitHub Personal Access Token (required)

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Set name: `portfoliomatch`
4. Select scopes:
   - `public_repo` (read public repositories)
   - `read:user` (read user profile)
5. Click "Generate token"
6. Copy the token (starts with `ghp_...`)

### Google Gemini API Key (required for gap analysis)

1. Go to https://aistudio.google.com/apikey
2. Click "Create API Key"
3. Copy the key

## 2. Backend setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env, paste your tokens:
# GITHUB_TOKEN=ghp_...
# GEMINI_API_KEY=...

# Run server
uvicorn app.main:app --reload --port 8000
```

Verify backend is running:
```bash
curl http://localhost:8000/api/health
```

Expected output:
```json
{
  "status": "ok",
  "github_available": true,
  "gemini_available": true,
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
}
```

## 3. Frontend setup

In a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local

# Run dev server
npm run dev
```

Open http://localhost:3000

## 4. Test the flow

1. Type a GitHub username (e.g., `Venta02` or any public GitHub user)
2. Click "Analyze"
3. Wait ~30 seconds for:
   - Repo analysis (~5-10s)
   - Job matching (~5s)
   - Gap analysis (~10-15s)
4. View ranked job matches and skill gap suggestions

## 5. Run tests

```bash
cd backend
source .venv/bin/activate
pytest -v
```

## Troubleshooting

### "GitHub user not found"
- Verify username is correct
- Check GITHUB_TOKEN is valid
- Public profile must exist

### "Embedding model loading slow"
- First run downloads ~80MB model
- Cached after first run

### "Gemini quota exceeded"
- Free tier: 1500 requests/day for gemini-flash-lite
- Wait or use rule-based fallback (works without Gemini)

### Frontend can't connect to backend
- Check backend is running on port 8000
- Check NEXT_PUBLIC_API_URL in frontend/.env.local
- Check CORS_ORIGINS in backend/.env includes http://localhost:3000

## Docker setup (alternative)

```bash
cd portfoliomatch
cp backend/.env.example backend/.env
# Edit backend/.env with your tokens

docker-compose up --build
```

Wait for both services to start, then open http://localhost:3000
