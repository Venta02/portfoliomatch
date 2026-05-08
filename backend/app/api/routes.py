"""API route handlers."""

from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.core.logging import log
from app.models.schemas import (
    AnalyzeRequest,
    UserProfile,
    JobSearchRequest,
    JobPosting,
    MatchRequest,
    MatchResponse,
    GapAnalysisRequest,
    GapAnalysisResponse,
    HealthResponse,
)
from app.services.github_analyzer import get_github_analyzer
from app.services.job_scraper import get_job_scraper
from app.services.matcher import get_matcher
from app.services.gap_analyzer import get_gap_analyzer


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        github_available=settings.github_available,
        gemini_available=settings.gemini_available,
        embedding_model=settings.embedding_model,
    )


@router.post("/analyze", response_model=UserProfile)
async def analyze_github(request: AnalyzeRequest):
    """Analyze a GitHub user's profile and extract skills."""
    try:
        analyzer = get_github_analyzer()
        profile = analyzer.analyze_user(request.github_username, request.max_repos)
        return profile
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        log.exception(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")


@router.post("/jobs/search", response_model=list[JobPosting])
async def search_jobs(request: JobSearchRequest):
    """Search for jobs matching keywords and location."""
    scraper = get_job_scraper()
    jobs = scraper.search(request.role_keywords, request.location, request.limit)
    return jobs


@router.get("/jobs", response_model=list[JobPosting])
async def get_all_jobs():
    """Return all available jobs in the dataset."""
    scraper = get_job_scraper()
    return scraper.get_all_jobs()


@router.post("/match", response_model=MatchResponse)
async def match_profile_to_jobs(request: MatchRequest):
    """Match a user profile against a list of jobs."""
    matcher = get_matcher()
    matches = matcher.match(request.profile, request.jobs, request.top_k)
    return MatchResponse(
        matches=matches,
        total_jobs_evaluated=len(request.jobs),
    )


@router.post("/gap", response_model=GapAnalysisResponse)
async def analyze_gap(request: GapAnalysisRequest):
    """Generate skill gap analysis with project suggestions."""
    analyzer = get_gap_analyzer()
    return analyzer.analyze(request.profile, request.target_jobs)
