# Architecture

## System overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Next.js Frontend                             │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────────┐    │
│  │  Input   │ → │ Profile  │ → │  Match   │ → │     Gap      │    │
│  │   Form   │   │   Card   │   │   List   │   │   Analysis   │    │
│  └──────────┘   └──────────┘   └──────────┘   └──────────────┘    │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend (Python)                        │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                   API Routes (api/routes.py)                  │  │
│  │  /analyze  /jobs/search  /match  /gap  /health                │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │ GitHubAnalyzer  │  │   JobScraper    │  │   JobMatcher    │    │
│  │                 │  │                 │  │                 │    │
│  │ - PyGithub      │  │ - JSON dataset  │  │ - sentence-     │    │
│  │ - Pattern match │  │ - Filter logic  │  │   transformers  │    │
│  │ - Skill extract │  │                 │  │ - Cosine sim    │    │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘    │
│           │                    │                    │              │
│           ▼                    ▼                    ▼              │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                    GapAnalyzer                              │   │
│  │  - Gemini API (gemini-flash-lite)                           │   │
│  │  - Rule-based fallback                                      │   │
│  └────────────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────┬───────────────────────────┘
                       │                  │
                       ▼                  ▼
              ┌─────────────────┐  ┌─────────────────┐
              │   GitHub API    │  │   Gemini API    │
              │  (5k req/hr)    │  │ (1500 req/day)  │
              └─────────────────┘  └─────────────────┘
```

## Data flow

### Step 1: Profile analysis

```
User Input: github_username
        ↓
┌──────────────────────────────────────────────┐
│  GitHubAnalyzer.analyze_user()              │
│                                              │
│  1. Fetch user via PyGithub                  │
│  2. Get top N repos (sorted by stars)        │
│  3. For each repo:                           │
│     a. Get languages from GitHub API         │
│     b. Try to read dependency files:         │
│        - requirements.txt                    │
│        - package.json                        │
│        - Cargo.toml                          │
│        - pyproject.toml                      │
│     c. Match content against patterns:       │
│        "torch" → PyTorch                     │
│        "fastapi" → FastAPI                   │
│  4. Aggregate skills across all repos        │
│  5. Build natural language summary           │
└──────────────────────────────────────────────┘
        ↓
Output: UserProfile
  - bio, name, public_repos
  - aggregated_skills: [Python, PyTorch, ...]
  - skill_summary: "ML engineer with..."
  - repos: [...]
```

### Step 2: Job matching

```
Input: UserProfile + List[JobPosting]
        ↓
┌──────────────────────────────────────────────┐
│  JobMatcher.match()                         │
│                                              │
│  1. Build profile text:                      │
│     bio + summary + skills + repo_descriptions│
│                                              │
│  2. Build job texts:                         │
│     title + description + requirements       │
│                                              │
│  3. Compute embeddings (sentence-transformers)│
│     - profile_embedding (384-dim)            │
│     - job_embeddings (384-dim each)          │
│                                              │
│  4. For each job:                            │
│     a. Cosine similarity (embeddings)        │
│     b. Skill overlap ratio:                  │
│        |matched| / |required|                │
│     c. Combined: 0.5 * sem + 0.5 * overlap   │
│                                              │
│  5. Sort descending, take top K              │
└──────────────────────────────────────────────┘
        ↓
Output: List[MatchResult]
  - job, score (0-1)
  - matched_skills: [Python, PyTorch]
  - missing_skills: [AWS, Spark]
```

### Step 3: Gap analysis

```
Input: UserProfile + Top 5 Jobs
        ↓
┌──────────────────────────────────────────────┐
│  GapAnalyzer.analyze()                      │
│                                              │
│  1. Build context:                           │
│     - User's current skills                  │
│     - 5 target jobs with requirements        │
│                                              │
│  2. Send to Gemini with structured prompt    │
│     - Identify common missing skills         │
│     - Rank by priority                       │
│     - Suggest 3 concrete projects            │
│       (name, weeks, difficulty, skills)      │
│                                              │
│  3. Parse JSON response                      │
│     (fallback to rule-based if fails)        │
└──────────────────────────────────────────────┘
        ↓
Output: GapAnalysisResponse
  - common_missing_skills
  - skill_priority_ranking
  - suggested_projects
  - overall_assessment
```

## Storage

Currently no persistent storage. Each request is stateless.

Future: Add SQLite for:
- Caching analyzed profiles (1 hour TTL)
- Saving user's favorite jobs
- Tracking application history

## Deployment topology

### Development

```
localhost:3000 (Next.js dev) ─→ localhost:8000 (Uvicorn dev)
```

### Production options

**Option A: Docker on VPS**
```
Caddy/Nginx → Docker Compose
  ├─ frontend (port 3000)
  └─ backend (port 8000)
```

**Option B: Hosted services**
```
Vercel (frontend) ─→ Railway/Render (backend)
                         ├─ GitHub API
                         └─ Gemini API
```

**Option C: Hugging Face Spaces (demo)**
```
Single Space hosting backend + minimal frontend
Free tier sufficient for demo
```

## Tech choices

| Component | Choice | Why |
|-----------|--------|-----|
| Backend framework | FastAPI | Async, type-safe, fast |
| Embedding model | all-MiniLM-L6-v2 | Small (80MB), CPU-friendly |
| LLM | Gemini Flash Lite | Free tier 1500/day |
| Frontend | Next.js 15 | App Router, server components |
| Styling | Tailwind CSS | Rapid iteration |
| State | React useState | Sufficient for MVP, no Redux needed |
| Type system | TypeScript + Pydantic | End-to-end type safety |
| Container | Docker Compose | Reproducible local dev |

## Performance characteristics

- **GitHub analysis**: 5-15 seconds (depends on repo count, network)
- **Job matching**: 200-500 ms (20 jobs)
- **Gap analysis**: 5-15 seconds (Gemini latency)
- **Total user-facing time**: 30-45 seconds first request

## Security notes

- API keys stored in `.env` (gitignored)
- No user authentication in v0.1 (single-user local)
- Rate limiting via FastAPI dependencies (TODO)
- CORS restricted to known origins
