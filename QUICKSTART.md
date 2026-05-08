# Quickstart

This walks you from zero to a running PortfolioMatch instance on your laptop.

## Prerequisites

- Python 3.11 or later
- Node.js 20 or later
- A GitHub personal access token (read-only `public_repo` scope)
  - Create at: https://github.com/settings/tokens
- A Google Gemini API key (free tier works)
  - Get at: https://aistudio.google.com/apikey

## Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

cp .env.example .env
# Edit .env and fill in:
#   GITHUB_TOKEN=ghp_...
#   GEMINI_API_KEY=...

uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000/docs to see the interactive API docs.
Hit http://localhost:8000/health to verify both API keys are picked up.

## Frontend setup

In a new terminal:

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open http://localhost:3000 and analyze your GitHub username.

## First run

1. Start backend on port 8000
2. Start frontend on port 3000
3. Type your GitHub username (e.g. `Venta02`) and click Analyze
4. The app will fetch your public repos and detect skills from imports and dependencies

## Troubleshooting

**`401 Unauthorized` from GitHub**: Your token is wrong or expired. Create a new one.

**Slow first analysis**: The embedding model downloads on first use (~80 MB). Subsequent runs are fast.

**`ModuleNotFoundError: torch`**: Run `pip install -r requirements.txt` again. sentence-transformers pulls in torch.

**Glints scraper returns empty**: Glints renders some pages with JS. The starter scraper hits the static HTML; you may need to update selectors or migrate to Playwright. See `app/services/jobs/glints.py`.

## Running with Docker

```bash
cp backend/.env.example backend/.env
# Fill in .env

docker compose up --build
```

Frontend on http://localhost:3000, backend on http://localhost:8000.
