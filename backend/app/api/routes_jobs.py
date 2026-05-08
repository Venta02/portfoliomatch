"""Job search and parsing endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_llm_service
from app.models.schemas import JobPosting, SearchJobsRequest
from app.services.jobs import SCRAPERS
from app.services.llm import LLMService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/search", response_model=list[JobPosting])
async def search_jobs(
    req: SearchJobsRequest,
    llm: LLMService = Depends(get_llm_service),
) -> list[JobPosting]:
    """Search jobs across configured sources, parse requirements with LLM."""
    all_results: list[JobPosting] = []

    for source in req.sources:
        scraper_cls = SCRAPERS.get(source)
        if not scraper_cls:
            logger.warning("Unknown source: %s", source)
            continue
        scraper = scraper_cls()
        try:
            jobs = await scraper.search(req.query, req.location, req.limit)
            all_results.extend(jobs)
        except Exception as e:
            logger.error("Scraper %s failed: %s", source, e)

    # Parse requirements via LLM if available
    if llm.is_available:
        for job in all_results:
            if job.description:
                job.requirements = llm.parse_job_requirements(job)
                job.skills_required = [r.name for r in job.requirements]

    return all_results
