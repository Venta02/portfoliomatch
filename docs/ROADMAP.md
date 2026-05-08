# Roadmap

What's done, what's next, and how to extend.

## v0.1 — MVP (current release)

Done:
- [x] Backend FastAPI + 5 endpoints
- [x] GitHub repo analyzer with framework detection from dependency files
- [x] 60+ frameworks pattern-matched
- [x] Curated dataset of 20 representative jobs (SEA + remote)
- [x] Sentence-transformer based job matching
- [x] Combined score (semantic + skill overlap)
- [x] Gemini-powered gap analysis with project suggestions
- [x] Rule-based fallback when Gemini unavailable
- [x] Next.js frontend with dark theme
- [x] 3 main components (ProfileCard, MatchList, GapAnalysis)
- [x] Docker Compose setup
- [x] Documentation (README, SETUP, IMPLEMENTATION, ARCHITECTURE)
- [x] Basic backend tests

## v0.2 — Live job scraping

Goals: Make it actually useful for daily job hunting.

- [ ] Glints scraper (Indonesia jobs)
- [ ] JobStreet scraper (Malaysia/Singapore)
- [ ] LinkedIn Jobs scraper (limited public data)
- [ ] We Work Remotely scraper (global remote)
- [ ] Job deduplication across sources
- [ ] Cache layer (Redis or SQLite) with 6-hour TTL
- [ ] Background job sync (run daily)
- [ ] Filter by location/salary/experience UI

## v0.3 — Better skill detection

Goals: Beyond pattern matching, understand actual code.

- [ ] AST parsing for Python (extract function patterns, decorators used)
- [ ] AST parsing for JavaScript/TypeScript
- [ ] Detect testing frameworks (pytest, jest, etc)
- [ ] Detect CI/CD (GitHub Actions configs, .gitlab-ci.yml)
- [ ] Detect containerization (Dockerfile complexity)
- [ ] Detect database use (from imports + connection strings)
- [ ] Skill confidence scoring (basic vs advanced)
- [ ] LOC and commit count weighting

## v0.4 — User experience

Goals: Make it personal and persistent.

- [ ] User accounts (GitHub OAuth)
- [ ] Save favorite jobs
- [ ] Application tracking (status, dates, notes)
- [ ] Email digest (weekly new matches)
- [ ] Skill progress tracking
- [ ] "What changed?" since last analysis

## v0.5 — Mobile + extension

- [ ] Browser extension (analyze any GitHub profile in 1 click)
- [ ] Flutter mobile app for job tracking
- [ ] Push notifications for new matches

## v0.6 — Multilingual

Goals: Open to non-English markets.

- [ ] Bahasa Indonesia job descriptions
- [ ] Bahasa Malaysia job descriptions
- [ ] Mandarin (Taiwan, Singapore tech firms)
- [ ] Translate user bio to match foreign jobs
- [ ] Detect language preference per role

## v0.7 — Advanced matching

Goals: Use LLMs more intelligently.

- [ ] LLM re-ranking of top 10 matches with reasoning
- [ ] Salary expectation matching
- [ ] Career path suggestions ("If you want X in 2 years, target Y now")
- [ ] Interview prep based on top match (likely questions)
- [ ] Cover letter draft generation

## v1.0 — Production ready

- [ ] Robust error handling for all sources
- [ ] Comprehensive test coverage (>70%)
- [ ] CI/CD with GitHub Actions
- [ ] Monitoring (Sentry, Prometheus)
- [ ] Rate limiting
- [ ] Public API documentation
- [ ] Deployed at portfoliomatch.dev (or similar)
- [ ] Privacy policy + GDPR compliance

## Stretch goals

- [ ] Browser extension for LinkedIn (auto-analyze profiles you view)
- [ ] Recruiter side (find candidates by code)
- [ ] Team dashboards (analyze whole team's skills)
- [ ] Open dataset of skill→job mappings for research

## How to contribute

This is a personal portfolio project, but contributions welcome:

1. Pick a roadmap item
2. Open an issue describing your approach
3. Fork, implement, PR
4. Be patient with reviews (this is a side project)

Good first issues:
- Add new frameworks to FRAMEWORK_PATTERNS dict
- Add new sample jobs to data/sample_jobs.json
- Improve UI component styling
- Add tests
