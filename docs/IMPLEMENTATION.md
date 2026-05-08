# Implementation Guide

A walkthrough of how PortfolioMatch is built. Read this to understand the architecture and extend the codebase.

## High-level flow

```
1. User enters GitHub username
2. Backend fetches user repos via GitHub API
3. For each repo:
   - Read dependency files (requirements.txt, package.json, etc)
   - Pattern-match imports to known frameworks
   - Aggregate languages from GitHub stats
4. Build user profile: {bio, skills, repos, summary}
5. Load job postings from sample_jobs.json
6. For each job:
   - Compute embedding similarity (profile vs job description)
   - Compute skill overlap ratio
   - Combined score = 0.5 * semantic + 0.5 * overlap
7. Sort jobs by score, return top K
8. For top 5 jobs, send to Gemini for gap analysis:
   - Identify missing skills
   - Suggest projects to fill gaps
9. Display results to user
```

## Backend architecture

```
backend/app/
├── main.py              # FastAPI app entry, middleware setup
├── api/
│   └── routes.py        # HTTP endpoints (5 endpoints)
├── core/
│   ├── config.py        # Settings from .env via pydantic
│   └── logging.py       # Loguru setup
├── models/
│   └── schemas.py       # Pydantic models (request/response shapes)
└── services/
    ├── github_analyzer.py   # GitHub API + framework detection
    ├── job_scraper.py       # Load jobs from JSON dataset
    ├── matcher.py           # Embedding-based matching
    └── gap_analyzer.py      # Gemini-powered gap analysis
```

### Why these separations?

- **api/** is thin: just HTTP handling, validation, response formatting
- **services/** holds business logic, can be tested without HTTP
- **models/** are pure data shapes, no logic
- **core/** is cross-cutting (config, logs)

## Key implementation details

### Framework detection (github_analyzer.py)

Instead of using NLP on README, we read **dependency files** directly:
- `requirements.txt` for Python
- `package.json` for Node
- `Cargo.toml` for Rust
- `go.mod` for Go
- `pyproject.toml` for modern Python

We pattern-match against `FRAMEWORK_PATTERNS` dict (60+ frameworks). This is **deterministic and fast**, but limited to known frameworks. Extending: just add to the dict.

```python
FRAMEWORK_PATTERNS = {
    "torch": "PyTorch",
    "fastapi": "FastAPI",
    # add more here...
}
```

### Why sentence-transformers (matcher.py)

We use `all-MiniLM-L6-v2` (~80MB) because:
- Small enough for 8GB RAM laptop
- Fast on CPU (~50ms for batch of 20)
- Good quality for semantic similarity
- No GPU required

Alternatives if you want better quality:
- `all-mpnet-base-v2` (440MB, better quality)
- `text-embedding-3-small` (OpenAI API, paid)

### Why combined score (matcher.py)

```python
final_score = 0.5 * semantic_similarity + 0.5 * skill_overlap_ratio
```

Pure semantic similarity has problems:
- Job description mentions "Python" but candidate uses Python in every project → high similarity even if specific skill missing
- A senior role description rich in business jargon → embedding aligns with anyone who has business words in bio

Pure skill overlap has problems:
- Misses semantic similarity ("OCR engineer" matches "document AI engineer" even if exact keyword differs)
- Sensitive to skill labeling (PyTorch vs pytorch)

Combined score balances both. Tune weights in `matcher.py:79`.

### Why Gemini for gap analysis (gap_analyzer.py)

LLM is good for:
- Explaining **why** a skill is missing
- Suggesting **specific projects** with realistic timelines
- Adapting to user's level (junior advice differs from senior)

Rule-based gap analysis (when Gemini unavailable) just lists missing skills without context. The LLM adds reasoning.

### Why JSON for jobs (job_scraper.py)

For MVP, scraping is the wrong battle:
- LinkedIn aggressively blocks scrapers
- Glints/Kalibrr have rate limits
- Anti-bot measures change frequently

Curated JSON of 20 representative jobs lets us:
- Test matching pipeline cleanly
- Cover SEA + remote markets
- Iterate fast on matching algorithm

For v0.2, add real scraping in a separate service (so it can fail gracefully).

## Frontend architecture

```
frontend/src/
├── app/
│   ├── layout.tsx       # Root HTML wrapper, global styles
│   ├── page.tsx         # Main page with form + results
│   └── globals.css      # Tailwind + dark theme
├── components/
│   ├── ProfileCard.tsx  # Display user profile
│   ├── MatchList.tsx    # List of matched jobs with scores
│   └── GapAnalysis.tsx  # Gap analysis + project suggestions
└── lib/
    └── api.ts           # Backend API client (fetch wrapper)
```

### State machine in page.tsx

```
idle → analyzing → matching → gap → done
              ↓
            error
```

Each stage shows different button text. Async chain in `handleSubmit`.

## Extending the codebase

### Add new framework to detect

Edit `backend/app/services/github_analyzer.py`:
```python
FRAMEWORK_PATTERNS = {
    # ... existing
    "your-package": "YourFramework",
}
```

### Add new job source

Create `backend/app/services/glints_scraper.py`:
```python
class GlintsScraper:
    async def search(self, keywords, location) -> List[JobPosting]:
        # implement scraping
        pass
```

Then update `job_scraper.py` to call multiple sources.

### Change matching algorithm

Edit `backend/app/services/matcher.py:78`:
```python
# Try different weights
final_score = 0.7 * semantic_score + 0.3 * skill_overlap

# Or add experience match
if profile_years >= job.experience_years:
    final_score += 0.1
```

### Add new endpoint

1. Define schema in `models/schemas.py`
2. Add handler in `api/routes.py`
3. Add API client function in `frontend/src/lib/api.ts`
4. Use in component

### Improve gap analysis prompt

Edit `backend/app/services/gap_analyzer.py:21` (`SYSTEM_PROMPT`).

## Performance notes

- **GitHub API**: 5000 requests/hour with token, 60/hour without
- **Embedding**: Cache profile embedding to avoid recomputing
- **Gemini**: 1500 requests/day free tier (gemini-flash-lite)
- **Frontend**: All state client-side, no server-side caching yet

## Future improvements (v0.2+)

- [ ] Live job scraping (Glints, JobStreet)
- [ ] AST parsing for deeper code analysis
- [ ] Skill confidence scores
- [ ] User accounts + saved searches
- [ ] Browser extension
- [ ] Mobile app (Flutter)
- [ ] Multilingual job descriptions (Bahasa, Mandarin)
- [ ] Salary benchmarking
- [ ] Visa info for international roles

## Testing strategy

Currently:
- Unit tests for matcher, scraper (`backend/tests/`)
- Manual testing via UI

Future:
- Integration tests with mocked GitHub API
- E2E tests with Playwright
- Match quality benchmark (precision@k vs ground truth)
