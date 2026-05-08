# Roadmap

## v0.1 — MVP scaffold (this commit)

- [x] Project structure
- [x] FastAPI backend skeleton with all routes
- [x] GitHub repo analyzer (imports, dependencies, frameworks)
- [x] Glints scraper (starter, may need Playwright upgrade)
- [x] Gemini-based job parser and gap analyzer
- [x] Embedding-based matcher (sentence-transformers)
- [x] Next.js frontend with analyze flow
- [x] Docker Compose
- [x] Tests skeleton

## v0.2 — Make it actually work end to end

- [ ] Verify Glints scraper against current HTML, or migrate to Playwright
- [ ] Add JobStreet scraper
- [ ] Add We Work Remotely scraper
- [ ] Cache scraping results in SQLite to avoid re-hitting sites
- [ ] Job posting detail fetcher (search returns cards, fetch full description per click)
- [ ] Frontend: search jobs panel, match view, gap view
- [ ] Frontend: skill radar chart with Recharts
- [ ] CI: GitHub Actions for backend tests

## v0.3 — Make it good

- [ ] Better skill detection: parse Python AST for actual imports per file, not just text matching
- [ ] Detect testing maturity (presence of tests/ folder, coverage)
- [ ] Detect CI/CD setup (.github/workflows, Dockerfile, docker-compose)
- [ ] Multi-language JD parsing (Indonesian, Malay)
- [ ] Salary benchmarks per location
- [ ] Save analyses to local DB so the user can see history

## v0.4 — Make it shareable

- [ ] Hugging Face Spaces deploy
- [ ] LinkedIn launch post template
- [ ] Public demo video
- [ ] Sample analyses for popular GitHub users (anonymized)

## v1.0 — Production-grade

- [ ] User accounts (optional, for saved analyses)
- [ ] Email alerts for new matching jobs
- [ ] Browser extension (analyze any GitHub profile from its page)
- [ ] Public API
