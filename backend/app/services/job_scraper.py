"""Load job postings from manual dataset (MVP) or scrape live (future).

For MVP we use a curated dataset of 20 sample jobs covering ML/AI/Data
roles in SEA + remote. This proves the matching pipeline without dealing
with anti-scraping measures of LinkedIn/Glints.

Live scraping will be added in v0.2 for Glints and JobStreet.
"""

import json
from pathlib import Path
from typing import List, Optional
from app.core.logging import log
from app.models.schemas import JobPosting


SAMPLE_JOBS_PATH = Path(__file__).parent.parent.parent / "data" / "sample_jobs.json"


class JobScraper:
    """Loads job postings. Currently file-based, will support live scraping later."""

    def __init__(self):
        self._cache: List[JobPosting] = []

    def get_all_jobs(self) -> List[JobPosting]:
        if not self._cache:
            self._cache = self._load_sample_jobs()
        return self._cache

    def search(
        self,
        keywords: List[str],
        location: Optional[str] = None,
        limit: int = 20,
    ) -> List[JobPosting]:
        """Filter sample jobs by keywords and location."""
        jobs = self.get_all_jobs()

        keywords_lower = [k.lower() for k in keywords]
        results = []
        for job in jobs:
            text = f"{job.title} {job.description}".lower()
            if any(k in text for k in keywords_lower):
                if location is None or location.lower() in job.location.lower():
                    results.append(job)

        log.info(f"Job search: {len(keywords_lower)} keywords, {len(results)} results")
        return results[:limit]

    def _load_sample_jobs(self) -> List[JobPosting]:
        if not SAMPLE_JOBS_PATH.exists():
            log.warning(f"Sample jobs file not found: {SAMPLE_JOBS_PATH}")
            return []

        with open(SAMPLE_JOBS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        jobs = [JobPosting(**job) for job in data]
        log.info(f"Loaded {len(jobs)} sample jobs")
        return jobs


_scraper: JobScraper = None


def get_job_scraper() -> JobScraper:
    global _scraper
    if _scraper is None:
        _scraper = JobScraper()
    return _scraper
